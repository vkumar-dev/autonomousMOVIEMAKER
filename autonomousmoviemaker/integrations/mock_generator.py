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
        
        import json
        data = None
        if "scene" in prompt.lower() or "json array" in prompt.lower():
            text = """[
    {"scene_number": 1, "location": "EXT. CITY STREET - NIGHT", "description": "Establishing shot of neon-lit cityscape", "scene_type": "establishing", "mood": "mysterious", "characters": [], "duration": 30},
    {"scene_number": 2, "location": "INT. APARTMENT - NIGHT", "description": "Protagonist discovers mysterious device", "scene_type": "action", "mood": "tense", "characters": ["ALEX"], "duration": 60},
    {"scene_number": 3, "location": "INT. LABORATORY - DAY", "description": "Climactic confrontation", "scene_type": "climax", "mood": "epic", "characters": ["ALEX", "DR. CHEN"], "duration": 120}
]"""
            try:
                data = json.loads(text)
            except:
                pass
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
            try:
                data = json.loads(text)
            except:
                pass
        else:
            text = "Generated content based on: " + prompt[:100] + "..."
            data = text
        
        return TextGenerationResult(
            success=True,
            text=text,
            data=data,
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
        filename = f"image_{hashlib.md5(prompt.encode()).hexdigest()[:8]}.png"
        image_path = temp_dir / filename
        
        try:
            from PIL import Image, ImageDraw
            
            # Generate a consistent color based on the prompt
            h = int(hashlib.md5(prompt.encode()).hexdigest(), 16)
            r = ((h & 0xff0000) >> 16) % 128 + 64
            g = ((h & 0x00ff00) >> 8) % 128 + 64
            b = (h & 0x0000ff) % 128 + 64
            
            # Create a 1024x1024 image
            img = Image.new("RGB", (1024, 1024), color=(r, g, b))
            draw = ImageDraw.Draw(img)
            
            # Draw some stylized text to simulate the image scene
            text_lines = [
                "SCENE VISUALIZATION PLACEHOLDER",
                f"Model: {self.model_name}",
                f"Prompt: {prompt[:80]}"
            ]
            if len(prompt) > 80:
                text_lines.append(f"...{prompt[80:160]}")
            
            y_offset = 450
            for line in text_lines:
                draw.text((100, y_offset), line, fill=(255, 255, 255))
                y_offset += 30
                
            img.save(image_path)
        except Exception as e:
            # Fallback to write plain text if PIL isn't available
            filename_fallback = f"image_{hashlib.md5(prompt.encode()).hexdigest()[:8]}.txt"
            image_path = temp_dir / filename_fallback
            with open(image_path, "w") as f:
                f.write(f"MOCK IMAGE\nPrompt: {prompt}\nModel: {self.model_name}\nError: {e}\n")
        
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
        filename = f"video_{hashlib.md5(prompt.encode()).hexdigest()[:8]}.mp4"
        video_path = temp_dir / filename
        
        try:
            from PIL import Image, ImageDraw
            
            # Generate a temporary image first
            image_filename = f"video_temp_{hashlib.md5(prompt.encode()).hexdigest()[:8]}.png"
            image_path = temp_dir / image_filename
            
            h = int(hashlib.md5(prompt.encode()).hexdigest(), 16)
            r = ((h & 0xff0000) >> 16) % 128 + 64
            g = ((h & 0x00ff00) >> 8) % 128 + 64
            b = (h & 0x0000ff) % 128 + 64
            
            # HD Resolution
            img = Image.new("RGB", (1920, 1080), color=(r, g, b))
            draw = ImageDraw.Draw(img)
            
            text_lines = [
                "MOCK VIDEO CLIP",
                f"Model: {self.model_name}",
                f"Duration: {duration}s",
                f"Prompt: {prompt[:80]}"
            ]
            if len(prompt) > 80:
                text_lines.append(f"...{prompt[80:160]}")
                
            y_offset = 450
            for line in text_lines:
                draw.text((100, y_offset), line, fill=(255, 255, 255))
                y_offset += 35
                
            img.save(image_path)
            
            # Use utility function to create video from image using ffmpeg
            from ..utils.video import create_video_from_image
            await create_video_from_image(image_path, video_path, duration=duration)
            
            # Clean up temporary image
            try:
                image_path.unlink()
            except:
                pass
                
        except Exception as e:
            # Fallback to write plain text if PIL/ffmpeg fails
            filename_fallback = f"video_{hashlib.md5(prompt.encode()).hexdigest()[:8]}.txt"
            video_path = temp_dir / filename_fallback
            with open(video_path, "w") as f:
                f.write(f"MOCK VIDEO\nPrompt: {prompt}\nDuration: {duration}s\nModel: {self.model_name}\nError: {e}\n")
        
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
