#!/usr/bin/env python3
"""
Pipeline script to generate a movie script using local Ollama model
based on brainstormed topics from the movie theme matrix.
"""

import os
import asyncio
import json
from pathlib import Path
from datetime import datetime

from autonomousmoviemaker import MovieMaker
from autonomousmoviemaker.core.theme_selector import generate_movie_concept
from autonomousmoviemaker.integrations.ollama_generator import OllamaTextGenerator
from autonomousmoviemaker.integrations.mock_generator import MockImageGenerator, MockVideoGenerator

async def main():
    # 1. Brainstorm concept from matrix
    print("🎲 Step 1: Brainstorming movie concept from theme matrix...")
    concept = generate_movie_concept()
    print(f"   Selected Theme: {concept['theme']}")
    print(f"   Setting: {concept['setting']}")
    print(f"   Title Idea: {concept['title']}")
            
    # 2. Get environment variables for Ollama
    ollama_model = os.getenv("OLLAMA_MODEL", "qwen2.5-coder:7b") # Good default for orchestration
    ollama_url = os.getenv("OLLAMA_URL", "http://localhost:11434")
    video_model = os.getenv("OLLAMA_VIDEO_MODEL", "wan-video:14b") # 2026 video model placeholder
    
    print(f"\n🤖 Step 2: Initializing Generators...")
    print(f"   Text Model: {ollama_model}")
    print(f"   Video Model: {video_model}")
    
    text_gen = OllamaTextGenerator(
        model_name=ollama_model,
        api_base=ollama_url
    )
    
    # In a real GH Action with GPU, these would be real. For now, we mock for the pipeline structure.
    image_gen = MockImageGenerator("mock/sdxl")
    video_gen = MockVideoGenerator(video_model)
    
    maker = MovieMaker(
        text_generator=text_gen,
        image_generator=image_gen,
        video_generator=video_gen
    )
    
    # Create the output directory
    output_dir = Path("./output")
    output_dir.mkdir(exist_ok=True)
    
    # 3. Generate Script
    print(f"\n✍️ Step 3: Writing full movie script (Target: {maker.config.pipeline.movie_duration / 60:.1f} minutes)...")
    script = await maker.generate_script(concept["prompt"])
    print(f"   Title: {script.title}")
    print(f"   Total Scenes: {len(script.scenes)}")
    print(f"   Estimated Duration: {script.total_duration / 60:.1f} minutes")
    
    # 4. Generate Trailer
    print(f"\n🎬 Step 4: Creating movie trailer (Target: {maker.config.pipeline.trailer_duration} seconds)...")
    trailer = await maker.generate_trailer(script)
    print(f"   Trailer Scenes: {len(trailer.scenes)}")
    print(f"   Trailer Duration: {trailer.duration} seconds")
    
    # 5. Generate Full Movie
    print("\n🎞️ Step 5: Generating full movie scenes and stitching...")
    # This would normally generate actual video files
    movie = await maker.generate_full_movie(script)
    
    # 6. Save and Present
    print("\n🎉 Step 6: Finalizing and Saving Project...")
    slug = script.title.lower().replace(" ", "_").replace(":", "").replace("'", "").replace("\"", "")
    project_dir = output_dir / slug
    maker.save_project(project_dir)
    
    # Stitch Trailer and Movie info for presentation
    # In a real scenario, we'd use utils.video.concatenate_videos
    from autonomousmoviemaker.utils.video import concatenate_videos
    
    final_video_path = project_dir / "final_package.txt"
    with open(final_video_path, "w") as f:
        f.write(f"AUTONOMOUS MOVIE PACKAGE: {script.title}\n")
        f.write("="*40 + "\n")
        f.write(f"PART 1: TRAILER ({trailer.duration}s)\n")
        f.write(f"PART 2: MOVIE ({script.total_duration/60:.1f}m)\n")
        f.write("="*40 + "\n")
        f.write(f"Generated at: {datetime.now().isoformat()}\n")

    # Move movie file to project dir
    if movie.video_path and movie.video_path.exists():
        final_mp4 = project_dir / f"{slug}_full.mp4"
        import shutil
        shutil.move(movie.video_path, final_mp4)
        print(f"🎞️ Movie file moved to {final_mp4}")

    # Move trailer file to project dir
    if trailer.video_path and trailer.video_path.exists():
        final_trailer_mp4 = project_dir / f"{slug}_trailer.mp4"
        import shutil
        shutil.move(trailer.video_path, final_trailer_mp4)
        print(f"🎬 Trailer file moved to {final_trailer_mp4}")

    print(f"✅ Saved project files to {project_dir}")
    
    # Create a nice markdown screenplay presentation
    screenplay_file = project_dir / "README.md"
    with open(screenplay_file, "w") as f:
        f.write(f"# 🎬 {script.title}\n\n")
        f.write(f"> **Logline:** {script.logline}\n\n")
        f.write(f"## 📊 Movie Stats\n")
        f.write(f"- **Genre:** {', '.join(script.genre)}\n")
        f.write(f"- **Total Runtime:** {script.total_duration / 60:.1f} minutes\n")
        f.write(f"- **Trailer Runtime:** {trailer.duration} seconds\n")
        f.write(f"- **Scene Count:** {len(script.scenes)}\n\n")
        
        f.write(f"## 📝 Synopsis\n{script.synopsis}\n\n")
        
        f.write("## 🎥 Trailer Scene Breakdown\n")
        for i, scene in enumerate(trailer.scenes):
            f.write(f"{i+1}. **{scene.location}** ({scene.duration}s) - *{scene.description[:100]}...*\n")
        f.write("\n")
        
        f.write("## 🎭 Characters\n")
        for char in script.characters:
            f.write(f"- **{char.name}** ({char.role}): {char.description}\n")
        f.write("\n")
        
        f.write("## 🎞️ Full Screenplay\n")
        for scene in script.scenes:
            f.write(f"### Scene {scene.scene_number}: {scene.location}\n")
            f.write(f"**Type:** {scene.scene_type.value.upper()} | **Mood:** {scene.mood.value.upper()} | **Duration:** {scene.duration}s\n\n")
            f.write(f"{scene.description}\n\n")
            if scene.dialogue:
                for dial in scene.dialogue:
                    speaker = dial.get("character", "Speaker")
                    line = dial.get("line", "")
                    f.write(f"> **{speaker}:** \"{line}\"\n\n")
            f.write(f"--- \n\n")
            
    print(f"📝 Project README written to {screenplay_file}")

if __name__ == "__main__":
    asyncio.run(main())
