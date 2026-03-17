#!/usr/bin/env python3
"""
Advanced example using real API integrations.

This example shows how to use autonomousMOVIEMAKER with actual AI services:
- OpenAI GPT-4 for story/script
- Stability AI SDXL for images
- Runway Gen-2 for videos

Requires API keys for each service.
"""

import asyncio
import os
from pathlib import Path

from autonomousmoviemaker import MovieMaker, Config
from autonomousmoviemaker.integrations import (
    OpenAIGenerator,
    StabilityGenerator,
    RunwayGenerator,
)


async def main():
    # Load API keys from environment
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    STABILITY_API_KEY = os.getenv("STABILITY_API_KEY")
    RUNWAY_API_KEY = os.getenv("RUNWAY_API_KEY")
    
    if not all([OPENAI_API_KEY, STABILITY_API_KEY, RUNWAY_API_KEY]):
        print("❌ Missing API keys!")
        print("Set the following environment variables:")
        print("  - OPENAI_API_KEY")
        print("  - STABILITY_API_KEY")
        print("  - RUNWAY_API_KEY")
        return
    
    # Create generators with real APIs
    text_gen = OpenAIGenerator(
        model_name="openai/gpt-4-turbo",
        api_key=OPENAI_API_KEY,
    )
    
    image_gen = StabilityGenerator(
        model_name="stability-ai/sdxl",
        api_key=STABILITY_API_KEY,
        width=1920,
        height=1080,
    )
    
    video_gen = RunwayGenerator(
        model_name="runway/gen2",
        api_key=RUNWAY_API_KEY,
        duration=5,
    )
    
    # Create MovieMaker with custom generators
    maker = MovieMaker(
        text_generator=text_gen,
        image_generator=image_gen,
        video_generator=video_gen,
    )
    
    # Set up progress callback
    def on_progress(progress):
        bar_length = 40
        filled = int(bar_length * progress.progress)
        bar = "█" * filled + "░" * (bar_length - filled)
        print(f"\r[{bar}] {progress.progress*100:.1f}% - {progress.message}", end="")
    
    maker.set_progress_callback(on_progress)
    
    # Movie prompt
    prompt = """
    A heartwarming animated short about a lonely robot who discovers 
    a small flower growing in a post-apocalyptic wasteland. The robot 
    cares for the flower, protecting it from harsh storms, until one day 
    the flower blooms and releases seeds that spread life across the 
    barren landscape.
    """
    
    print("🎬 autonomousMOVIEMAKER - Advanced Example")
    print("=" * 60)
    print(f"Prompt:{prompt.strip()}")
    print("=" * 60)
    
    # Generate script
    print("\n📝 Stage 1: Generating script...")
    script = await maker.generate_script(prompt)
    print(f"\n✅ Script complete: {script.title}")
    print(f"   Scenes: {len(script.scenes)}")
    
    # Generate trailer
    print("\n🎬 Stage 2: Generating trailer...")
    trailer = await maker.generate_trailer(script)
    print(f"\n✅ Trailer complete!")
    print(f"   Duration: ~{trailer.duration}s")
    
    # In production, you would:
    # 1. Save trailer to a viewable format
    # 2. Present to user for approval
    # 3. Collect feedback if needed
    
    print("\n📋 Trailer Approval Workflow:")
    print("""
    # Show trailer to user
    display_trailer(trailer.video_path)
    
    # Get feedback
    feedback = get_user_feedback()
    
    if feedback == "approve":
        movie = await maker.generate_full_movie(script)
    elif feedback == "regenerate":
        trailer = await maker.regenerate_trailer()
    else:
        # Modify script based on feedback
        new_prompt = f"{original_prompt} But make it {feedback}"
        script = await maker.generate_script(new_prompt)
    """)
    
    # Generate full movie
    print("\n🎥 Stage 3: Generating full movie...")
    movie = await maker.generate_full_movie(script)
    
    print(f"\n🎉 MOVIE COMPLETE!")
    print(f"   Title: {movie.title}")
    print(f"   Total Duration: {movie.duration}s")
    
    # Save project
    output_dir = Path("./output/production_movie")
    project_path = maker.save_project(output_dir)
    print(f"   Project saved: {project_path}")


if __name__ == "__main__":
    asyncio.run(main())
