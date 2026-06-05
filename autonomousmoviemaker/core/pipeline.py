"""
Movie generation pipeline for autonomousMOVIEMAKER.

Orchestrates the full workflow from prompt to final movie.
"""

import asyncio
import json
import logging
from pathlib import Path
from typing import Optional, Callable, Dict, Any, List
from datetime import datetime

from .config import Config
from .models import Script, Scene, Trailer, Movie, GenerationProgress, Character, SceneType, Mood
from ..generators.base import BaseTextGenerator, BaseImageGenerator, BaseVideoGenerator, TextGenerationResult

logger = logging.getLogger(__name__)


class MoviePipeline:
    """
    Main pipeline for autonomous movie generation.
    
    The pipeline follows these stages:
    1. Story Generation - Create story concept and outline
    2. Script Writing - Generate full screenplay with scenes
    3. Scene Visualization - Generate images for each scene
    4. Trailer Creation - Create preview trailer
    5. Full Movie - Generate complete movie (after trailer approval)
    
    Example:
        pipeline = MoviePipeline(text_gen, image_gen, video_gen, config)
        
        # Generate story and script
        script = await pipeline.generate_script("A cyberpunk thriller about memory hackers")
        
        # Generate trailer
        trailer = await pipeline.generate_trailer(script)
        
        # If approved, generate full movie
        if user_approves(trailer):
            movie = await pipeline.generate_full_movie(script)
    """
    
    def __init__(
        self,
        text_generator: BaseTextGenerator,
        image_generator: BaseImageGenerator,
        video_generator: BaseVideoGenerator,
        config: Optional[Config] = None,
    ):
        self.text_generator = text_generator
        self.image_generator = image_generator
        self.video_generator = video_generator
        self.config = config or Config()
        
        self._progress_callback: Optional[Callable[[GenerationProgress], None]] = None
        self._current_progress: GenerationProgress = None
        
    def set_progress_callback(self, callback: Callable[[GenerationProgress], None]):
        """Set callback for progress updates."""
        self._progress_callback = callback
        
    def _update_progress(self, stage: str, progress: float, message: str, current_step: str = "", total_steps: int = 0, completed_steps: int = 0):
        """Update and emit progress."""
        self._current_progress = GenerationProgress(
            stage=stage,
            progress=progress,
            message=message,
            current_step=current_step,
            total_steps=total_steps,
            completed_steps=completed_steps,
        )
        if self._progress_callback:
            self._progress_callback(self._current_progress)
    
    async def generate_story(self, prompt: str) -> Dict[str, str]:
        """
        Generate story concept from initial prompt.
        
        Args:
            prompt: User's movie idea/prompt
            
        Returns:
            Dictionary with title, logline, synopsis, genre, characters
        """
        self._update_progress("story", 0.0, "Generating story concept...")
        
        story_prompt = f"""You are a master storyteller and film developer. Create a compelling movie concept from this prompt: "{prompt}"

Generate the following in JSON format:
{{
    "title": "Movie Title",
    "logline": "One sentence summary that captures the essence of the film",
    "synopsis": "Detailed 2-3 paragraph synopsis of the story",
    "genre": ["genre1", "genre2"],
    "tone": "The overall tone/mood of the film",
    "setting": "Time period and location",
    "themes": ["theme1", "theme2"],
    "characters": [
        {{"name": "Character Name", "role": "protagonist/antagonist/supporting", "description": "Character description and arc"}}
    ]
}}

Make it cinematic, emotionally engaging, and visually compelling."""

        self._update_progress("story", 0.1, "Sending to text generator...", "Generating story", 5, 1)
        result = await self.text_generator.generate(story_prompt)
        
        if not result.success:
            raise Exception(f"Story generation failed: {result.error}")
        
        self._update_progress("story", 1.0, "Story concept generated successfully!")
        return result.data  # Should be parsed JSON
    
    async def generate_script(self, prompt: str) -> Script:
        """
        Generate full screenplay from prompt.
        
        Args:
            prompt: User's movie idea/prompt
            
        Returns:
            Complete Script object with all scenes
        """
        self._update_progress("script", 0.0, "Starting script generation...")
        
        # First generate the story concept
        story_data = await self.generate_story(prompt)
        
        self._update_progress("script", 0.2, "Story created, generating scenes...", "Creating scenes", 10, 2)
        
        # Generate scene breakdown
        scenes_prompt = f"""Based on this movie concept, create a detailed scene-by-scene breakdown for a SHORT MOVIE (EXACTLY 20 minutes total).

Title: {story_data.get('title', 'Untitled')}
Synopsis: {story_data.get('synopsis', '')}
Characters: {story_data.get('characters', [])}

IMPORTANT: You MUST create at least 25 scenes. Do not stop until you have a full 20-minute arc.
Each scene should be between 30 and 60 seconds long.
For each scene include:
- Scene number
- Location
- Brief description of action (be visual and cinematic!)
- Scene type (establishing, action, dialogue, montage, climax, resolution)
- Mood (happy, sad, tense, romantic, mysterious, epic, comedic, dramatic)
- Characters present
- Key dialogue (if any)
- Estimated duration in seconds (aim for a total of 1200 seconds across all scenes)

Output as a VALID JSON array of scenes. Do not include any text outside the JSON array."""

        scenes_result = await self.text_generator.generate(scenes_prompt)
        
        if not scenes_result.success:
            raise Exception(f"Scene generation failed: {scenes_result.error}")
        
        self._update_progress("script", 0.5, "Scenes created, generating image prompts...", "Creating prompts", 10, 5)
        
        # Generate image prompts for each scene
        image_prompts_prompt = """For each scene, create a detailed image generation prompt that would create a stunning cinematic still. Include:
- Visual style and cinematography
- Lighting and color palette
- Composition and camera angle
- Key visual elements
- Mood and atmosphere

Output as JSON with scene_number and image_prompt fields."""

        prompts_result = await self.text_generator.generate(image_prompts_prompt)
        
        self._update_progress("script", 0.8, "Finalizing script...", "Finalizing", 10, 8)
        
        # Parse scenes
        scenes_list = []
        try:
            raw_scenes = scenes_result.data if hasattr(scenes_result, 'data') and scenes_result.data else None
            if not raw_scenes:
                text_clean = scenes_result.text.strip()
                if text_clean.startswith("```"):
                    lines = text_clean.splitlines()
                    if lines[0].startswith("```"):
                        lines = lines[1:]
                    if lines[-1].startswith("```"):
                        lines = lines[:-1]
                    text_clean = "\n".join(lines).strip()
                raw_scenes = json.loads(text_clean)
                
            if not isinstance(raw_scenes, list):
                if isinstance(raw_scenes, dict) and "scenes" in raw_scenes:
                    raw_scenes = raw_scenes["scenes"]
                else:
                    raise ValueError("Scenes output is not a list")
                    
            for s in raw_scenes:
                s_type_str = s.get("scene_type", "action").lower()
                try:
                    s_type = SceneType(s_type_str)
                except ValueError:
                    s_type = SceneType.ACTION
                    
                mood_str = s.get("mood", "dramatic").lower()
                try:
                    mood_val = Mood(mood_str)
                except ValueError:
                    mood_val = Mood.DRAMATIC
                    
                scene_obj = Scene(
                    scene_number=int(s.get("scene_number", len(scenes_list) + 1)),
                    location=s.get("location", "INT. SCENE - DAY"),
                    description=s.get("description", ""),
                    scene_type=s_type,
                    mood=mood_val,
                    characters=s.get("characters", []),
                    dialogue=s.get("dialogue", []),
                    duration=float(s.get("duration", 5.0)),
                )
                scenes_list.append(scene_obj)
        except Exception as e:
            logger.error(f"Failed to parse scenes JSON: {e}. Raw output: {scenes_result.text}")
            scenes_list = [
                Scene(
                    scene_number=1,
                    location="INT. SCENE - DAY",
                    description=f"Movie screenplay scene. Plot: {story_data.get('synopsis', '')}",
                    duration=10.0
                )
            ]

        # Parse image prompts and attach to scenes
        prompts_dict = {}
        try:
            raw_prompts = prompts_result.data if hasattr(prompts_result, 'data') and prompts_result.data else None
            if not raw_prompts and prompts_result.success:
                text_clean = prompts_result.text.strip()
                if text_clean.startswith("```"):
                    lines = text_clean.splitlines()
                    if lines[0].startswith("```"):
                        lines = lines[1:]
                    if lines[-1].startswith("```"):
                        lines = lines[:-1]
                    text_clean = "\n".join(lines).strip()
                raw_prompts = json.loads(text_clean)
                
            if isinstance(raw_prompts, list):
                for p in raw_prompts:
                    num = int(p.get("scene_number", 0))
                    if num:
                        prompts_dict[num] = p.get("image_prompt", "")
            elif isinstance(raw_prompts, dict):
                if "scenes" in raw_prompts and isinstance(raw_prompts["scenes"], list):
                    for p in raw_prompts["scenes"]:
                        num = int(p.get("scene_number", 0))
                        if num:
                            prompts_dict[num] = p.get("image_prompt", "")
                else:
                    for k, v in raw_prompts.items():
                        try:
                            num = int(k)
                            if isinstance(v, str):
                                prompts_dict[num] = v
                            elif isinstance(v, dict):
                                prompts_dict[num] = v.get("image_prompt", "")
                        except ValueError:
                            pass
        except Exception as e:
            logger.error(f"Failed to parse image prompts JSON: {e}. Raw output: {prompts_result.text}")

        # Attach image/video prompts to scenes
        for scene in scenes_list:
            scene.image_prompt = prompts_dict.get(scene.scene_number, f"Cinematic still of {scene.description}")
            scene.video_prompt = f"{scene.image_prompt}, cinematic camera movement, slow motion video"

        # Create Script object
        script = Script(
            title=story_data.get('title', 'Untitled'),
            logline=story_data.get('logline', ''),
            synopsis=story_data.get('synopsis', ''),
            genre=story_data.get('genre', []),
            characters=[Character(**c) for c in story_data.get('characters', [])],
            scenes=scenes_list,
        )
        
        self._update_progress("script", 1.0, "Script generation complete!")
        return script
    
    async def generate_scene_images(self, scenes: List[Scene]) -> List[Scene]:
        """
        Generate images for all scenes.
        
        Args:
            scenes: List of scenes to generate images for
            
        Returns:
            List of scenes with generated images
        """
        total = len(scenes)
        self._update_progress("images", 0.0, f"Starting image generation for {total} scenes...", "Generating images", total, 0)
        
        # Generate images in batches
        batch_size = self.config.pipeline.max_workers
        completed = 0
        
        for i in range(0, len(scenes), batch_size):
            batch = scenes[i:i + batch_size]
            prompts = [scene.image_prompt or scene.description for scene in batch]
            
            results = await self.image_generator.generate_batch(prompts)
            
            for scene, result in zip(batch, results):
                if result.success:
                    scene.generated_image = result.image_path
                completed += 1
                self._update_progress(
                    "images",
                    completed / total,
                    f"Generated {completed}/{total} images",
                    "Generating images",
                    total,
                    completed
                )
        
        return scenes
    
    async def generate_trailer(self, script: Script) -> Trailer:
        """
        Generate movie trailer from script.
        
        Args:
            script: The movie script
            
        Returns:
            Generated Trailer object
        """
        self._update_progress("trailer", 0.0, "Creating trailer...")
        
        # Select best scenes for trailer
        trailer_scenes = script.get_trailer_scenes(
            max_scenes=self.config.pipeline.max_trailer_scenes,
            target_duration=self.config.pipeline.trailer_duration
        )
        
        self._update_progress("trailer", 0.2, f"Selected {len(trailer_scenes)} scenes for trailer", "Generating trailer scenes", len(trailer_scenes), 0)
        
        # Generate videos for trailer scenes
        completed = 0
        trailer_videos = []
        
        for scene in trailer_scenes:
            video_prompt = scene.video_prompt or scene.image_prompt or scene.description
            result = await self.video_generator.generate(video_prompt, duration=3)  # 3 second clips for trailer
            
            if result.success:
                scene.generated_video = result.video_path
                trailer_videos.append(result.video_path)
            
            completed += 1
            self._update_progress(
                "trailer",
                0.2 + (completed / len(trailer_scenes)) * 0.6,
                f"Generated {completed}/{len(trailer_scenes)} trailer clips",
                "Generating trailer",
                len(trailer_scenes),
                completed
            )
        
        self._update_progress("trailer", 0.9, "Compiling trailer...", "Finalizing trailer")
        
        # Create trailer object
        trailer = Trailer(
            title=f"{script.title} - Trailer",
            scenes=trailer_scenes,
            duration=len(trailer_scenes) * 3,  # Approximate
        )
        
        self._update_progress("trailer", 1.0, "Trailer generation complete!")
        return trailer
    
    async def generate_full_movie(self, script: Script) -> Movie:
        """
        Generate complete movie from approved script.
        
        Args:
            script: The approved movie script
            
        Returns:
            Complete Movie object
        """
        self._update_progress("full_movie", 0.0, "Starting full movie generation...")
        
        # Generate all scene images if not already done
        scenes_with_images = await self.generate_scene_images(script.scenes)
        
        self._update_progress("full_movie", 0.3, "Images complete, generating videos...", "Generating scene videos", len(scenes_with_images), 0)
        
        # Generate videos for all scenes
        completed = 0
        for scene in scenes_with_images:
            video_prompt = scene.video_prompt or scene.image_prompt or scene.description
            result = await self.video_generator.generate(
                video_prompt,
                duration=scene.duration or 5.0
            )
            
            if result.success:
                scene.generated_video = result.video_path
            
            completed += 1
            self._update_progress(
                "full_movie",
                0.3 + (completed / len(scenes_with_images)) * 0.5,
                f"Generated {completed}/{len(scenes_with_images)} scene videos",
                "Generating videos",
                len(scenes_with_images),
                completed
            )
        
        self._update_progress("full_movie", 0.9, "Compiling final movie...", "Finalizing movie")
        
        # Create final movie object
        movie = Movie(
            title=script.title,
            script=script,
            duration=script.total_duration,
        )
        
        self._update_progress("full_movie", 1.0, "Movie generation complete!")
        return movie
    
    async def create_movie(self, prompt: str, require_trailer_approval: bool = True) -> Movie:
        """
        Complete movie creation workflow.
        
        Args:
            prompt: User's movie idea
            require_trailer_approval: If True, pause after trailer for approval
            
        Returns:
            Complete Movie object
        """
        # Stage 1: Generate script
        script = await self.generate_script(prompt)
        
        # Stage 2: Generate trailer
        trailer = await self.generate_trailer(script)
        
        if require_trailer_approval:
            # Return trailer for approval
            # Caller should call generate_full_movie if approved
            movie = Movie(title=script.title, script=script, trailer=trailer)
            return movie
        
        # Stage 3: Generate full movie
        movie = await self.generate_full_movie(script)
        movie.trailer = trailer
        
        return movie
