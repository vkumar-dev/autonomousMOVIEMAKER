#!/usr/bin/env python3
"""
Interactive CLI for autonomousMOVIEMAKER.

Usage:
    python examples/cli_example.py
    
Or run directly:
    python -m autonomousmoviemaker.cli "Your movie idea"
"""

import asyncio
import argparse
import sys
from pathlib import Path

from autonomousmoviemaker import MovieMaker
from autonomousmoviemaker.integrations import (
    MockTextGenerator,
    MockImageGenerator,
    MockVideoGenerator,
)


class MovieMakerCLI:
    """Interactive command-line interface for autonomousMOVIEMAKER."""
    
    def __init__(self, auto_approve: bool = False, output_dir: str = "./output"):
        self.maker = MovieMaker(
            text_generator=MockTextGenerator("mock/gpt"),
            image_generator=MockImageGenerator("mock/sdxl"),
            video_generator=MockVideoGenerator("mock/gen2"),
        )
        self.auto_approve = auto_approve
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    async def run(self, prompt: str):
        """Run the movie creation workflow."""
        print("\n" + "🎬 " * 20)
        print("   autonomousMOVIEMAKER CLI")
        print("🎬 " * 20 + "\n")
        
        print(f"📝 Prompt: {prompt}\n")
        
        # Stage 1: Generate script
        print("📝 Stage 1/3: Generating story and script...")
        script = await self.maker.generate_script(prompt)
        
        print(f"\n✅ Script Generated!")
        print(f"   Title: {script.title}")
        print(f"   Logline: {script.logline[:100]}...")
        print(f"   Genre: {', '.join(script.genre)}")
        print(f"   Scenes: {len(script.scenes)}")
        print(f"   Characters: {len(script.characters)}")
        
        # Stage 2: Generate trailer
        print("\n\n🎬 Stage 2/3: Generating trailer...")
        trailer = await self.maker.generate_trailer(script)
        
        print(f"\n✅ Trailer Generated!")
        print(f"   Scenes in trailer: {len(trailer.scenes)}")
        print(f"   Estimated duration: {trailer.duration}s")
        
        # Stage 3: Approval workflow
        if not self.auto_approve:
            approved = self._get_user_approval()
            if not approved:
                feedback = self._get_feedback()
                if feedback:
                    print("\n🔄 Regenerating with feedback...")
                    # In full implementation, this would use feedback
                    trailer = await self.maker.regenerate_trailer(feedback)
                else:
                    print("❌ Movie generation cancelled.")
                    return None
        else:
            print("\n⏭️  Auto-approve enabled, proceeding to full movie...")
        
        # Stage 4: Generate full movie
        print("\n\n🎥 Stage 3/3: Generating full movie...")
        movie = await self.maker.generate_full_movie(script)
        
        print(f"\n🎉 MOVIE COMPLETE!")
        print(f"   Title: {movie.title}")
        print(f"   Duration: {movie.duration}s")
        print(f"   Resolution: {movie.resolution}")
        
        # Save project
        project_name = script.title.lower().replace(" ", "_").replace(":", "")
        project_path = self.maker.save_project(self.output_dir / project_name)
        print(f"   Saved to: {project_path}")
        
        return movie
    
    def _get_user_approval(self) -> bool:
        """Get user approval for trailer."""
        print("\n" + "=" * 60)
        print("TRAILER REVIEW")
        print("=" * 60)
        print("\nIn a production environment, the trailer would be displayed here.")
        print("\nWould you like to proceed with generating the full movie?")
        
        if self.auto_approve:
            return True
        
        while True:
            choice = input("\n[y] Approve and continue\n[n] Reject\n[f] Provide feedback\n> ").lower()
            if choice in ['y', 'yes']:
                return True
            elif choice in ['n', 'no']:
                return False
            elif choice in ['f', 'feedback']:
                return None  # Signal for feedback
    
    def _get_feedback(self) -> str:
        """Get feedback from user."""
        print("\n" + "=" * 60)
        print("FEEDBACK")
        print("=" * 60)
        print("\nWhat would you like to change?")
        print("(e.g., 'more action scenes', 'darker tone', 'shorter trailer')")
        
        feedback = input("\nYour feedback: ").strip()
        return feedback if feedback else None


def main():
    parser = argparse.ArgumentParser(
        description="autonomousMOVIEMAKER CLI - Create movies from text prompts"
    )
    parser.add_argument(
        "prompt",
        nargs="?",
        default=None,
        help="Your movie idea/prompt"
    )
    parser.add_argument(
        "--auto-approve", "-y",
        action="store_true",
        help="Skip trailer approval and generate full movie automatically"
    )
    parser.add_argument(
        "--output", "-o",
        default="./output",
        help="Output directory for generated files"
    )
    
    args = parser.parse_args()
    
    if not args.prompt:
        # Interactive mode
        print("Enter your movie idea (or 'quit' to exit):")
        while True:
            prompt = input("\n🎬 > ").strip()
            if prompt.lower() in ['quit', 'exit', 'q']:
                print("Goodbye!")
                break
            if prompt:
                cli = MovieMakerCLI(auto_approve=args.auto_approve, output_dir=args.output)
                asyncio.run(cli.run(prompt))
    else:
        # Single prompt mode
        cli = MovieMakerCLI(auto_approve=args.auto_approve, output_dir=args.output)
        asyncio.run(cli.run(args.prompt))


if __name__ == "__main__":
    main()
