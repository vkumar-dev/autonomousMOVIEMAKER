import asyncio
import os
from pathlib import Path
from autonomousmoviemaker.core.movie_maker import MovieMaker
from autonomousmoviemaker.integrations.mock_generator import MockTextGenerator, MockImageGenerator, MockVideoGenerator
from autonomousmoviemaker.core.theme_selector import generate_movie_concept

async def test_dry_run():
    print("🚀 Starting Local Dry Run...")
    
    # 1. Brainstorm
    concept = generate_movie_concept()
    print(f"   Concept: {concept['title']}")
    
    # 2. Setup with ALL MOCK generators for local testing
    text_gen = MockTextGenerator("mock/text")
    image_gen = MockImageGenerator("mock/image")
    video_gen = MockVideoGenerator("mock/video")
    
    maker = MovieMaker(
        text_generator=text_gen,
        image_generator=image_gen,
        video_generator=video_gen
    )
    
    # 3. Pipeline
    print("   Generating Script...")
    script = await maker.generate_script(concept["prompt"])
    print(f"   Script duration: {script.total_duration}s")
    
    print("   Generating Trailer...")
    trailer = await maker.generate_trailer(script)
    print(f"   Trailer duration: {trailer.duration}s")
    
    print("   Generating Movie...")
    movie = await maker.generate_full_movie(script)
    
    # 4. Finalize
    output_dir = Path("./test_output")
    output_dir.mkdir(exist_ok=True)
    slug = "test_movie"
    project_dir = output_dir / slug
    maker.save_project(project_dir)
    
    print(f"✅ Dry run successful. Project saved to {project_dir}")

if __name__ == "__main__":
    asyncio.run(test_dry_run())
