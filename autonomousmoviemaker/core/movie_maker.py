"""
Main MovieMaker class - the primary interface for autonomousMOVIEMAKER.
"""

import asyncio
from pathlib import Path
from typing import Optional, Callable, Dict, Any, Union
from datetime import datetime

from .config import Config
from .models import Script, Trailer, Movie, GenerationProgress
from .pipeline import MoviePipeline
from .generators.base import BaseTextGenerator, BaseImageGenerator, BaseVideoGenerator


class MovieMaker:
    """
    Main class for autonomous movie generation.
    
    This is the primary interface for creating movies from text prompts.
    It handles model initialization, pipeline orchestration, and output management.
    
    Features:
    - Multi-model support (text, image, video)
    - Trailer-first workflow with approval step
    - Progress tracking and callbacks
    - Flexible configuration
    - Async/await support
    
    Example:
        # Basic usage
        maker = MovieMaker(
            text_model="openai/gpt-4",
            image_model="stability-ai/sdxl", 
            video_model="runway/gen2"
        )
        
        # Create movie with trailer approval
        result = await maker.create_movie("A romantic comedy set in Paris")
        
        # Review trailer
        print(f"Trailer ready: {result.trailer.video_path}")
        
        # If approved, generate full movie
        if user_approves:
            movie = await maker.generate_full_movie(result.script)
            print(f"Movie complete: {movie.video_path}")
    
    Advanced usage with custom generators:
        from autonomousmoviemaker.integrations import OpenAIGenerator, StableDiffusionGenerator
        
        maker = MovieMaker(
            text_generator=OpenAIGenerator(api_key="..."),
            image_generator=StableDiffusionGenerator(api_key="..."),
            video_generator=RunwayGenerator(api_key="..."),
        )
    """
    
    def __init__(
        self,
        text_model: Optional[str] = None,
        image_model: Optional[str] = None,
        video_model: Optional[str] = None,
        text_generator: Optional[BaseTextGenerator] = None,
        image_generator: Optional[BaseImageGenerator] = None,
        video_generator: Optional[BaseVideoGenerator] = None,
        config: Optional[Config] = None,
        **kwargs,
    ):
        """
        Initialize MovieMaker.
        
        Args:
            text_model: Name of text generation model (e.g., "openai/gpt-4")
            image_model: Name of image generation model (e.g., "stability-ai/sdxl")
            video_model: Name of video generation model (e.g., "runway/gen2")
            text_generator: Custom text generator instance (overrides text_model)
            image_generator: Custom image generator instance (overrides image_model)
            video_generator: Custom video generator instance (overrides video_model)
            config: Configuration object
            **kwargs: Additional configuration options
        """
        self.config = config or Config()
        
        # Update config from kwargs
        if text_model:
            self.config.text_model.model_name = text_model
        if image_model:
            self.config.image_model.model_name = image_model
        if video_model:
            self.config.video_model.model_name = video_model
        
        # Initialize generators
        self.text_generator = text_generator or self._create_text_generator()
        self.image_generator = image_generator or self._create_image_generator()
        self.video_generator = video_generator or self._create_video_generator()
        
        # Create pipeline
        self.pipeline = MoviePipeline(
            text_generator=self.text_generator,
            image_generator=self.image_generator,
            video_generator=self.video_generator,
            config=self.config,
        )
        
        # State
        self._current_script: Optional[Script] = None
        self._current_trailer: Optional[Trailer] = None
        self._current_movie: Optional[Movie] = None
        self._progress_callback: Optional[Callable[[GenerationProgress], None]] = None
    
    def _create_text_generator(self) -> BaseTextGenerator:
        """Create default text generator from config."""
        # Try to import and create generator based on model name
        model_name = self.config.text_model.model_name.lower()
        
        # Lazy import to avoid dependency errors
        try:
            if "openai" in model_name or "gpt" in model_name:
                from .integrations.openai_generator import OpenAIGenerator
                return OpenAIGenerator(
                    model_name=self.config.text_model.model_name,
                    api_key=self.config.text_model.api_key,
                )
            elif "anthropic" in model_name or "claude" in model_name:
                from .integrations.anthropic_generator import AnthropicGenerator
                return AnthropicGenerator(
                    model_name=self.config.text_model.model_name,
                    api_key=self.config.text_model.api_key,
                )
            else:
                # Default to a mock generator for demonstration
                from .integrations.mock_generator import MockTextGenerator
                return MockTextGenerator(model_name=self.config.text_model.model_name)
        except ImportError:
            from .integrations.mock_generator import MockTextGenerator
            return MockTextGenerator(model_name=self.config.text_model.model_name)
    
    def _create_image_generator(self) -> BaseImageGenerator:
        """Create default image generator from config."""
        model_name = self.config.image_model.model_name.lower()
        
        try:
            if "stability" in model_name or "sdxl" in model_name or "stable" in model_name:
                from .integrations.stability_generator import StabilityGenerator
                return StabilityGenerator(
                    model_name=self.config.image_model.model_name,
                    api_key=self.config.image_model.api_key,
                )
            elif "midjourney" in model_name:
                from .integrations.midjourney_generator import MidjourneyGenerator
                return MidjourneyGenerator(
                    model_name=self.config.image_model.model_name,
                    api_key=self.config.image_model.api_key,
                )
            elif "dall-e" in model_name or "dalle" in model_name:
                from .integrations.openai_generator import DALLEGenerator
                return DALLEGenerator(
                    model_name=self.config.image_model.model_name,
                    api_key=self.config.image_model.api_key,
                )
            else:
                from .integrations.mock_generator import MockImageGenerator
                return MockImageGenerator(model_name=self.config.image_model.model_name)
        except ImportError:
            from .integrations.mock_generator import MockImageGenerator
            return MockImageGenerator(model_name=self.config.image_model.model_name)
    
    def _create_video_generator(self) -> BaseVideoGenerator:
        """Create default video generator from config."""
        model_name = self.config.video_model.model_name.lower()
        
        try:
            if "runway" in model_name:
                from .integrations.runway_generator import RunwayGenerator
                return RunwayGenerator(
                    model_name=self.config.video_model.model_name,
                    api_key=self.config.video_model.api_key,
                )
            elif "pika" in model_name:
                from .integrations.pika_generator import PikaGenerator
                return PikaGenerator(
                    model_name=self.config.video_model.model_name,
                    api_key=self.config.video_model.api_key,
                )
            elif "stability" in model_name or "stable" in model_name:
                from .integrations.stability_generator import StableVideoGenerator
                return StableVideoGenerator(
                    model_name=self.config.video_model.model_name,
                    api_key=self.config.video_model.api_key,
                )
            else:
                from .integrations.mock_generator import MockVideoGenerator
                return MockVideoGenerator(model_name=self.config.video_model.model_name)
        except ImportError:
            from .integrations.mock_generator import MockVideoGenerator
            return MockVideoGenerator(model_name=self.config.video_model.model_name)
    
    def set_progress_callback(self, callback: Callable[[GenerationProgress], None]):
        """
        Set callback for progress updates.
        
        Args:
            callback: Function to call with GenerationProgress updates
        """
        self._progress_callback = callback
        self.pipeline.set_progress_callback(callback)
    
    async def generate_script(self, prompt: str) -> Script:
        """
        Generate a movie script from a prompt.
        
        Args:
            prompt: Description of the movie idea
            
        Returns:
            Complete Script object
        """
        self._current_script = await self.pipeline.generate_script(prompt)
        return self._current_script
    
    async def generate_trailer(self, script: Optional[Script] = None) -> Trailer:
        """
        Generate a trailer from a script.
        
        Args:
            script: Script to create trailer from (uses last generated if None)
            
        Returns:
            Generated Trailer object
        """
        if script is None:
            if self._current_script is None:
                raise ValueError("No script available. Generate a script first or provide one.")
            script = self._current_script
        
        self._current_trailer = await self.pipeline.generate_trailer(script)
        return self._current_trailer
    
    async def generate_full_movie(self, script: Optional[Script] = None) -> Movie:
        """
        Generate the full movie from an approved script.
        
        Args:
            script: Script to create movie from (uses last generated if None)
            
        Returns:
            Complete Movie object
        """
        if script is None:
            if self._current_script is None:
                raise ValueError("No script available. Generate a script first or provide one.")
            script = self._current_script
        
        self._current_movie = await self.pipeline.generate_full_movie(script)
        if self._current_trailer:
            self._current_movie.trailer = self._current_trailer
        
        return self._current_movie
    
    async def create_movie(self, prompt: str, auto_approve: bool = False) -> Dict[str, Any]:
        """
        Complete movie creation workflow with trailer approval.
        
        This is the main method for creating movies. It follows this workflow:
        1. Generate story and script from prompt
        2. Generate trailer
        3. If auto_approve=True or user approves, generate full movie
        4. Return results
        
        Args:
            prompt: Description of the movie idea
            auto_approve: If True, skip trailer approval and generate full movie
            
        Returns:
            Dictionary with script, trailer, movie (if approved), and approval status
            
        Example:
            result = await maker.create_movie("A sci-fi epic about AI consciousness")
            
            # Review trailer
            print(f"Trailer: {result['trailer'].video_path}")
            
            # If not auto-approved, get user feedback
            if not result['approved']:
                feedback = input("Approve trailer? (yes/no/feedback): ")
                if feedback == "yes":
                    movie = await maker.generate_full_movie(result['script'])
                elif feedback.startswith("no:"):
                    # Provide feedback for new trailer
                    new_trailer = await maker.generate_trailer_with_feedback(feedback)
        """
        # Generate script
        script = await self.generate_script(prompt)
        
        # Generate trailer
        trailer = await self.generate_trailer(script)
        
        result = {
            "script": script,
            "trailer": trailer,
            "approved": auto_approve,
            "movie": None,
            "next_steps": {
                "approve": "Call generate_full_movie() to create the full movie",
                "regenerate_trailer": "Call generate_trailer() again with different parameters",
                "modify_script": "Call generate_script() with modified prompt",
            }
        }
        
        if auto_approve:
            movie = await self.generate_full_movie(script)
            result["movie"] = movie
            result["approved"] = True
        
        self._current_movie = result["movie"]
        return result
    
    async def regenerate_trailer(self, feedback: Optional[str] = None) -> Trailer:
        """
        Regenerate trailer with optional feedback.
        
        Args:
            feedback: User feedback for improvement
            
        Returns:
            New Trailer object
        """
        if self._current_script is None:
            raise ValueError("No script available. Generate a script first.")
        
        # TODO: Incorporate feedback into trailer generation
        # For now, just regenerate
        self._current_trailer = await self.pipeline.generate_trailer(self._current_script)
        return self._current_trailer
    
    def get_progress(self) -> Optional[GenerationProgress]:
        """Get current generation progress."""
        return self.pipeline._current_progress
    
    def save_project(self, path: Path) -> Path:
        """
        Save current project state to disk.
        
        Args:
            path: Directory to save project
            
        Returns:
            Path to saved project
        """
        project_path = Path(path)
        project_path.mkdir(parents=True, exist_ok=True)
        
        # Save script
        if self._current_script:
            import json
            script_path = project_path / "script.json"
            with open(script_path, "w") as f:
                json.dump(self._current_script.to_dict(), f, indent=2)
        
        # Save trailer info
        if self._current_trailer:
            import json
            trailer_path = project_path / "trailer.json"
            with open(trailer_path, "w") as f:
                json.dump(self._current_trailer.to_dict(), f, indent=2)
        
        return project_path
    
    def __repr__(self) -> str:
        return (
            f"MovieMaker("
            f"text_model='{self.config.text_model.model_name}', "
            f"image_model='{self.config.image_model.model_name}', "
            f"video_model='{self.config.video_model.model_name}'"
            f")"
        )
