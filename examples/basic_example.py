#!/usr/bin/env python3
"""
Basic example of using autonomousMOVIEMAKER.

This example demonstrates the simplest way to create a movie from a prompt.
Uses mock generators for demonstration (no API keys required).
"""

import asyncio
from pathlib import Path

from autonomousmoviemaker import MovieMaker, Config
from autonomousmoviemaker.integrations import (
    MockTextGenerator,
    MockImageGenerator,
    MockVideoGenerator,
)


async def main():
    # Create MovieMaker with mock generators (for testing)
    # In production, replace with real API-based generators
    maker = MovieMaker(
        text_generator=MockTextGenerator("mock/gpt"),
        image_generator=MockImageGenerator("mock/sdxl"),
        video_generator=MockVideoGenerator("mock/gen2"),
    )
    
    # Your movie prompt
    prompt = "A cyberpunk thriller about a hacker who discovers a conspiracy"
    
    print(f"🎬 Creating movie from prompt: {prompt}")
    print("-" * 60)
    
    # Create movie with trailer approval workflow
    result = await maker.create_movie(prompt, auto_approve=False)
    
    print(f"\n✅ Script generated!")
    print(f"   Title: {result['script'].title}")
    print(f"   Logline: {result['script'].logline}")
    print(f"   Scenes: {len(result['script'].scenes)}")
    
    print(f"\n🎬 Trailer ready!")
    print(f"   Duration: ~{result['trailer'].duration} seconds")
    print(f"   Scenes in trailer: {len(result['trailer'].scenes)}")
    
    # In a real application, you would show the trailer to the user
    # and ask for approval
    print("\n" + "=" * 60)
    print("TRAILER APPROVAL WORKFLOW")
    print("=" * 60)
    print("""
At this point, you would:
1. Show the trailer to the user
2. Get feedback: approve, reject, or request changes

Options:
- To approve and generate full movie:
    movie = await maker.generate_full_movie(result['script'])

- To regenerate trailer with feedback:
    new_trailer = await maker.regenerate_trailer("Make it more action-packed")

- To modify the script:
    new_script = await maker.generate_script("Same concept but more comedic")
""")
    
    # For this example, let's auto-approve and generate the full movie
    print("\n🎬 Generating full movie (auto-approved for demo)...")
    
    movie = await maker.generate_full_movie(result['script'])
    
    print(f"\n🎉 MOVIE COMPLETE!")
    print(f"   Title: {movie.title}")
    print(f"   Duration: {movie.duration} seconds")
    print(f"   Format: {movie.format}")
    
    # Save project
    project_path = maker.save_project(Path("./output/example_movie"))
    print(f"   Project saved to: {project_path}")


if __name__ == "__main__":
    asyncio.run(main())
