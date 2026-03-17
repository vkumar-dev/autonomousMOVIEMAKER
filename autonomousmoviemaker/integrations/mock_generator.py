"""
Mock generators for testing and demonstration.

These generators simulate API calls without requiring actual API keys.
Useful for testing the framework and understanding the interface.
"""

import asyncio
from pathlib import Path
from typing import List, Optional
import tempfile

from ..generators.base import (
    BaseTextGenerator,
    BaseImageGenerator,
    BaseVideoGenerator,
    TextGenerationResult,
    ImageGenerationResult,
    VideoGenerationResult,
)


class MockTextGenerator(BaseTextGenerator):
    """Mock text generator for testing."""
    
    async def generate(self, prompt: str, **kwargs) -> TextGenerationResult:
        """Generate mock text response."""
        await asyncio.sleep(0.5)  # Simulate API delay
        
        # Simple mock response based on prompt type
        if "scene" in prompt.lower() or "json array" in prompt.lower():
            text = """[
    {"scene_number": 1, "location": "EXT. CITY STREET - NIGHT", "description": "Establishing shot of neon-lit cityscape", "scene_type": "establishing", "mood": "mysterious", "characters": [], "duration": 5},
    {"scene_number": 2, "location": "INT. APARTMENT - NIGHT", "description": "Protagonist discovers mysterious device", "scene_type": "action", "mood": "tense", "characters": ["ALEX"], "duration": 8},
    {"scene_number": 3, "location": "INT. LABORATORY - DAY", "description": "Climactic confrontation", "scene_type": "climax", "mood": "epic", "characters": ["ALEX", "DR. CHEN"], "duration": 12}
]"""
        elif "character" in prompt.lower() or "story" in prompt.lower():
            text = """{
    "title": "The Memory Thief",
    "logline": "A hacker who steals memories discovers one that could bring down a corrupt corporation.",
    "synopsis": "In a near-future world where memories can be extracted and sold, Alex Chen is the best memory thief in the business. But when Alex steals what appears to be a routine corporate secret, they uncover a memory that reveals a conspiracy threatening millions of lives.",
    "genre": ["Sci-Fi", "Thriller"],
    "tone": "Dark, suspenseful, with moments of hope",
    "setting": "Near-future neo-Tokyo, 2087",
    "themes": ["Identity", "Corporate greed", "Technology and humanity"],
    "characters": [
        {"name": "Alex Chen", "role": "protagonist", "description": "A skilled memory thief in their 30s, haunted by their own lost memories"},
        {"name": "Dr. Sarah Chen", "role": "supporting", "description": "Alex's estranged sister, a neuroscientist who created the memory extraction technology"},
        {"name": "Marcus Kane", "role": "antagonist", "description": "CEO of Mnemosyne Corp, will stop at nothing to protect his secrets"}
    ]
}"""
        else:
            text = "Generated content based on: " + prompt[:100] + "..."
        
        return TextGenerationResult(
            success=True,
            text=text,
            tokens_used=len(text) // 4,
            metadata={"model": self.model_name}
        )
    
    async def generate_batch(self, prompts: List[str], **kwargs) -> List[TextGenerationResult]:
        """Generate batch of mock responses."""
        results = []
        for prompt in prompts:
            result = await self.generate(prompt, **kwargs)
            results.append(result)
        return results


class MockImageGenerator(BaseImageGenerator):
    """Mock image generator for testing."""
    
    async def generate(self, prompt: str, **kwargs) -> ImageGenerationResult:
        """Generate mock image."""
        await asyncio.sleep(0.3)  # Simulate API delay
        
        # Create a placeholder file
        temp_dir = Path(tempfile.gettempdir()) / "autonomousmoviemaker"
        temp_dir.mkdir(exist_ok=True)
        
        import hashlib
        filename = f"image_{hashlib.md5(prompt.encode()).hexdigest()[:8]}.txt"
        image_path = temp_dir / filename
        
        # Write mock image data (in real implementation, this would be actual image)
        with open(image_path, "w") as f:
            f.write(f"MOCK IMAGE\nPrompt: {prompt}\nModel: {self.model_name}\n")
        
        return ImageGenerationResult(
            success=True,
            image_path=image_path,
            metadata={"model": self.model_name, "prompt": prompt}
        )
    
    async def generate_batch(self, prompts: List[str], **kwargs) -> List[ImageGenerationResult]:
        """Generate batch of mock images."""
        results = []
        for prompt in prompts:
            result = await self.generate(prompt, **kwargs)
            results.append(result)
        return results


class MockVideoGenerator(BaseVideoGenerator):
    """Mock video generator for testing."""
    
    async def generate(self, prompt: str, **kwargs) -> VideoGenerationResult:
        """Generate mock video."""
        await asyncio.sleep(0.5)  # Simulate API delay
        
        duration = kwargs.get("duration", 5.0)
        
        # Create a placeholder file
        temp_dir = Path(tempfile.gettempdir()) / "autonomousmoviemaker"
        temp_dir.mkdir(exist_ok=True)
        
        import hashlib
        filename = f"video_{hashlib.md5(prompt.encode()).hexdigest()[:8]}.txt"
        video_path = temp_dir / filename
        
        # Write mock video data
        with open(video_path, "w") as f:
            f.write(f"MOCK VIDEO\nPrompt: {prompt}\nDuration: {duration}s\nModel: {self.model_name}\n")
        
        return VideoGenerationResult(
            success=True,
            video_path=video_path,
            duration=duration,
            metadata={"model": self.model_name, "prompt": prompt}
        )
    
    async def generate_batch(self, prompts: List[str], **kwargs) -> List[VideoGenerationResult]:
        """Generate batch of mock videos."""
        results = []
        for prompt in prompts:
            result = await self.generate(prompt, **kwargs)
            results.append(result)
        return results
