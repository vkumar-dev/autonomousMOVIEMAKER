#!/usr/bin/env python3
"""
Example: Creating a custom generator for autonomousMOVIEMAKER.

This example shows how to create your own text, image, or video generator
by implementing the base interfaces. This allows you to integrate any AI model
or service with autonomousMOVIEMAKER.
"""

import asyncio
from pathlib import Path
from typing import List, Optional

from autonomousmoviemaker import MovieMaker
from autonomousmoviemaker.generators.base import (
    BaseTextGenerator,
    BaseImageGenerator,
    BaseVideoGenerator,
    TextGenerationResult,
    ImageGenerationResult,
    VideoGenerationResult,
)


# ============================================================
# Example 1: Custom Text Generator using a local LLM
# ============================================================

class LocalLLMGenerator(BaseTextGenerator):
    """
    Example: Custom text generator using a local LLM (e.g., llama.cpp, Ollama).
    
    This demonstrates how to integrate any text generation service.
    """
    
    def __init__(self, model_path: str, api_url: Optional[str] = None, **kwargs):
        super().__init__(f"local/{model_path}", **kwargs)
        self.model_path = model_path
        self.api_url = api_url or "http://localhost:11434"  # Ollama default
    
    async def generate(self, prompt: str, **kwargs) -> TextGenerationResult:
        """Generate text using local LLM."""
        try:
            # Example using Ollama API
            import aiohttp
            
            payload = {
                "model": self.model_path.split("/")[-1],
                "prompt": prompt,
                "stream": False,
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.api_url}/api/generate",
                    json=payload
                ) as response:
                    result = await response.json()
                    
                    return TextGenerationResult(
                        success=True,
                        text=result.get("text", ""),
                        tokens_used=result.get("eval_count", 0),
                        metadata={"model": self.model_path}
                    )
        except Exception as e:
            return TextGenerationResult(
                success=False,
                error=str(e),
                metadata={"model": self.model_path}
            )
    
    async def generate_batch(self, prompts: List[str], **kwargs) -> List[TextGenerationResult]:
        """Generate text for multiple prompts."""
        tasks = [self.generate(prompt, **kwargs) for prompt in prompts]
        return await asyncio.gather(*tasks)


# ============================================================
# Example 2: Custom Image Generator using Replicate API
# ============================================================

class ReplicateImageGenerator(BaseImageGenerator):
    """
    Example: Custom image generator using Replicate API.
    
    Replicate hosts many image generation models including SDXL, Midjourney, etc.
    """
    
    def __init__(self, model_name: str, api_key: str, **kwargs):
        super().__init__(f"replicate/{model_name}", api_key=api_key, **kwargs)
        self.api_key = api_key
        self._client = None
    
    def _get_client(self):
        """Lazy load Replicate client."""
        if self._client is None:
            try:
                import replicate
                import os
                os.environ["REPLICATE_API_TOKEN"] = self.api_key
                self._client = replicate
            except ImportError:
                raise ImportError("Please install replicate: pip install replicate")
        return self._client
    
    async def generate(self, prompt: str, **kwargs) -> ImageGenerationResult:
        """Generate image using Replicate."""
        try:
            client = self._get_client()
            
            # Run the model
            output = client.run(
                self.model_name.split("/")[-1],
                input={"prompt": prompt, **kwargs}
            )
            
            # Replicate returns a URL to the generated image
            image_url = output[0] if isinstance(output, list) else output
            
            # Download and save
            import aiohttp
            import tempfile
            import hashlib
            
            async with aiohttp.ClientSession() as session:
                async with session.get(image_url) as resp:
                    image_data = await resp.read()
            
            temp_dir = Path(tempfile.gettempdir()) / "autonomousmoviemaker"
            temp_dir.mkdir(exist_ok=True)
            
            filename = f"replicate_{hashlib.md5(prompt.encode()).hexdigest()[:8]}.png"
            image_path = temp_dir / filename
            
            with open(image_path, "wb") as f:
                f.write(image_data)
            
            return ImageGenerationResult(
                success=True,
                image_path=image_path,
                image_url=image_url,
                metadata={"model": self.model_name}
            )
        except Exception as e:
            return ImageGenerationResult(
                success=False,
                error=str(e),
                metadata={"model": self.model_name}
            )
    
    async def generate_batch(self, prompts: List[str], **kwargs) -> List[ImageGenerationResult]:
        """Generate multiple images."""
        results = []
        for prompt in prompts:
            result = await self.generate(prompt, **kwargs)
            results.append(result)
        return results


# ============================================================
# Example 3: Custom Video Generator using Hugging Face
# ============================================================

class HuggingFaceVideoGenerator(BaseVideoGenerator):
    """
    Example: Custom video generator using Hugging Face Inference API.
    
    Supports models like ModelScope, Damo, etc.
    """
    
    def __init__(self, model_name: str, api_key: str, **kwargs):
        super().__init__(f"hf/{model_name}", api_key=api_key, **kwargs)
        self.api_key = api_key
    
    async def generate(self, prompt: str, **kwargs) -> VideoGenerationResult:
        """Generate video using Hugging Face API."""
        try:
            import aiohttp
            import tempfile
            import hashlib
            
            headers = {"Authorization": f"Bearer {self.api_key}"}
            
            # Call Hugging Face Inference API
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"https://api-inference.huggingface.co/models/{self.model_name.split('/')[-1]}",
                    headers=headers,
                    json={"inputs": prompt}
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        return VideoGenerationResult(
                            success=False,
                            error=f"API error: {response.status} - {error_text}"
                        )
                    
                    video_data = await response.read()
                    
                    # Save video
                    temp_dir = Path(tempfile.gettempdir()) / "autonomousmoviemaker"
                    temp_dir.mkdir(exist_ok=True)
                    
                    filename = f"hf_{hashlib.md5(prompt.encode()).hexdigest()[:8]}.mp4"
                    video_path = temp_dir / filename
                    
                    with open(video_path, "wb") as f:
                        f.write(video_data)
                    
                    return VideoGenerationResult(
                        success=True,
                        video_path=video_path,
                        duration=kwargs.get("duration", 4.0),
                        metadata={"model": self.model_name}
                    )
        except Exception as e:
            return VideoGenerationResult(
                success=False,
                error=str(e),
                metadata={"model": self.model_name}
            )
    
    async def generate_batch(self, prompts: List[str], **kwargs) -> List[VideoGenerationResult]:
        """Generate multiple videos."""
        results = []
        for prompt in prompts:
            result = await self.generate(prompt, **kwargs)
            results.append(result)
        return results


# ============================================================
# Usage Example
# ============================================================

async def main():
    """Demonstrate using custom generators."""
    
    print("=" * 60)
    print("Custom Generator Example")
    print("=" * 60)
    
    # Example 1: Using local LLM (requires Ollama running locally)
    # text_gen = LocalLLMGenerator(model_path="llama2")
    
    # Example 2: Using Replicate (requires API key)
    # image_gen = ReplicateImageGenerator(
    #     model_name="stability-ai/sdxl",
    #     api_key="your-replicate-key"
    # )
    
    # Example 3: Using Hugging Face (requires API key)
    # video_gen = HuggingFaceVideoGenerator(
    #     model_name="damo-vilab/text-to-video-synthesis",
    #     api_key="your-hf-key"
    # )
    
    # For this demo, we'll use mock generators
    from autonomousmoviemaker.integrations import (
        MockTextGenerator,
        MockImageGenerator,
        MockVideoGenerator,
    )
    
    # Create MovieMaker with custom generators
    maker = MovieMaker(
        text_generator=MockTextGenerator("custom/llm"),
        image_generator=MockImageGenerator("custom/sdxl"),
        video_generator=MockVideoGenerator("custom/video"),
    )
    
    # Create a movie
    prompt = "A space adventure about the first human colony on Mars"
    print(f"\n🎬 Creating movie: {prompt}")
    
    result = await maker.create_movie(prompt, auto_approve=True)
    
    print(f"\n✅ Movie created: {result['movie'].title}")
    
    print("\n" + "=" * 60)
    print("To use your own generators:")
    print("=" * 60)
    print("""
1. Inherit from the appropriate base class:
   - BaseTextGenerator for story/script generation
   - BaseImageGenerator for scene images
   - BaseVideoGenerator for video clips

2. Implement the required methods:
   - generate(prompt, **kwargs) -> Result
   - generate_batch(prompts, **kwargs) -> List[Result]

3. Pass your custom generator to MovieMaker:
   maker = MovieMaker(
       text_generator=MyCustomTextGenerator(),
       image_generator=MyCustomImageGenerator(),
       video_generator=MyCustomVideoGenerator(),
   )

See the documentation for more details on each method's signature.
""")


if __name__ == "__main__":
    asyncio.run(main())
