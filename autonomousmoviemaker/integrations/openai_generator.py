"""
OpenAI integration for autonomousMOVIEMAKER.

Provides text generation via GPT models and image generation via DALL-E.
"""

import asyncio
from pathlib import Path
from typing import List, Optional, Dict, Any
import tempfile

from ..generators.base import (
    BaseTextGenerator,
    BaseImageGenerator,
    TextGenerationResult,
    ImageGenerationResult,
)


class OpenAIGenerator(BaseTextGenerator):
    """
    OpenAI GPT text generator.
    
    Usage:
        generator = OpenAIGenerator(
            model_name="openai/gpt-4",
            api_key="your-api-key"
        )
        result = await generator.generate("Write a story about...")
    """
    
    def __init__(self, model_name: str = "openai/gpt-4", api_key: Optional[str] = None, **kwargs):
        super().__init__(model_name, api_key=api_key, **kwargs)
        self.api_key = api_key
        self._client = None
    
    def _get_client(self):
        """Lazy load OpenAI client."""
        if self._client is None:
            try:
                from openai import AsyncOpenAI
                self._client = AsyncOpenAI(api_key=self.api_key)
            except ImportError:
                raise ImportError("Please install openai: pip install openai")
        return self._client
    
    async def generate(self, prompt: str, **kwargs) -> TextGenerationResult:
        """Generate text using OpenAI."""
        client = self._get_client()
        
        try:
            response = await client.chat.completions.create(
                model=self.model_name.split("/")[-1] if "/" in self.model_name else self.model_name,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=kwargs.get("max_tokens", self.config.get("max_tokens", 4096)),
                temperature=kwargs.get("temperature", self.config.get("temperature", 0.8)),
            )
            
            return TextGenerationResult(
                success=True,
                text=response.choices[0].message.content,
                tokens_used=response.usage.total_tokens,
                metadata={"model": response.model, "usage": dict(response.usage)}
            )
        except Exception as e:
            return TextGenerationResult(
                success=False,
                error=str(e),
                metadata={"model": self.model_name}
            )
    
    async def generate_batch(self, prompts: List[str], **kwargs) -> List[TextGenerationResult]:
        """Generate text for multiple prompts."""
        tasks = [self.generate(prompt, **kwargs) for prompt in prompts]
        return await asyncio.gather(*tasks)


class DALLEGenerator(BaseImageGenerator):
    """
    DALL-E image generator.
    
    Usage:
        generator = DALLEGenerator(
            model_name="openai/dall-e-3",
            api_key="your-api-key"
        )
        result = await generator.generate("A cyberpunk cityscape at night")
    """
    
    def __init__(self, model_name: str = "openai/dall-e-3", api_key: Optional[str] = None, **kwargs):
        super().__init__(model_name, api_key=api_key, **kwargs)
        self.api_key = api_key
        self._client = None
    
    def _get_client(self):
        """Lazy load OpenAI client."""
        if self._client is None:
            try:
                from openai import AsyncOpenAI
                self._client = AsyncOpenAI(api_key=self.api_key)
            except ImportError:
                raise ImportError("Please install openai: pip install openai")
        return self._client
    
    async def generate(self, prompt: str, **kwargs) -> ImageGenerationResult:
        """Generate image using DALL-E."""
        client = self._get_client()
        
        try:
            size = kwargs.get("size", "1024x1024")
            quality = kwargs.get("quality", "standard")
            
            response = await client.images.generate(
                model=self.model_name.split("/")[-1] if "/" in self.model_name else self.model_name,
                prompt=prompt,
                size=size,
                quality=quality,
                n=1,
            )
            
            image_url = response.data[0].url
            
            # Download image
            import aiohttp
            async with aiohttp.ClientSession() as session:
                async with session.get(image_url) as resp:
                    image_data = await resp.read()
            
            # Save to temp file
            temp_dir = Path(tempfile.gettempdir()) / "autonomousmoviemaker"
            temp_dir.mkdir(exist_ok=True)
            
            import hashlib
            filename = f"dalle_{hashlib.md5(prompt.encode()).hexdigest()[:8]}.png"
            image_path = temp_dir / filename
            
            with open(image_path, "wb") as f:
                f.write(image_data)
            
            return ImageGenerationResult(
                success=True,
                image_path=image_path,
                image_url=image_url,
                metadata={"model": response.data[0].revised_prompt or prompt}
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
