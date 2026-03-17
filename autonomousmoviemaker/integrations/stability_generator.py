"""
Stability AI integration for autonomousMOVIEMAKER.

Provides image generation via Stable Diffusion and video generation via Stable Video.
"""

import asyncio
from pathlib import Path
from typing import List, Optional
import tempfile

from ..generators.base import (
    BaseImageGenerator,
    BaseVideoGenerator,
    ImageGenerationResult,
    VideoGenerationResult,
)


class StabilityGenerator(BaseImageGenerator):
    """
    Stability AI Stable Diffusion image generator.
    
    Usage:
        generator = StabilityGenerator(
            model_name="stability-ai/sdxl",
            api_key="your-api-key"
        )
        result = await generator.generate("A cyberpunk cityscape at night")
    """
    
    def __init__(self, model_name: str = "stability-ai/sdxl", api_key: Optional[str] = None, **kwargs):
        super().__init__(model_name, api_key=api_key, **kwargs)
        self.api_key = api_key
        self._session = None
    
    async def _get_session(self):
        """Get aiohttp session."""
        if self._session is None:
            import aiohttp
            self._session = aiohttp.ClientSession(
                headers={"Authorization": f"Bearer {self.api_key}"}
            )
        return self._session
    
    async def close(self):
        """Close session."""
        if self._session:
            await self._session.close()
    
    async def generate(self, prompt: str, **kwargs) -> ImageGenerationResult:
        """Generate image using Stability AI."""
        session = await self._get_session()
        
        try:
            # Map model names to Stability AI endpoints
            engine_id = "stable-diffusion-xl-1024-v1-0"
            if "sdxl" in self.model_name.lower():
                engine_id = "stable-diffusion-xl-1024-v1-0"
            elif "sd-1.5" in self.model_name.lower():
                engine_id = "stable-diffusion-v1-5"
            
            url = f"https://api.stability.ai/v1/generation/{engine_id}/text-to-image"
            
            payload = {
                "text_prompts": [{"text": prompt}],
                "cfg_scale": kwargs.get("guidance_scale", 7),
                "width": kwargs.get("width", 1024),
                "height": kwargs.get("height", 1024),
                "samples": 1,
                "steps": kwargs.get("steps", 30),
            }
            
            async with session.post(url, json=payload) as response:
                if response.status != 200:
                    error_text = await response.text()
                    return ImageGenerationResult(
                        success=False,
                        error=f"API error: {response.status} - {error_text}"
                    )
                
                result = await response.json()
                
                # Save image
                import base64
                image_data = base64.b64decode(result["artifacts"][0]["base64"])
                
                temp_dir = Path(tempfile.gettempdir()) / "autonomousmoviemaker"
                temp_dir.mkdir(exist_ok=True)
                
                import hashlib
                filename = f"stability_{hashlib.md5(prompt.encode()).hexdigest()[:8]}.png"
                image_path = temp_dir / filename
                
                with open(image_path, "wb") as f:
                    f.write(image_data)
                
                return ImageGenerationResult(
                    success=True,
                    image_path=image_path,
                    metadata={"model": engine_id, "seed": result["artifacts"][0].get("seed")}
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


class StableVideoGenerator(BaseVideoGenerator):
    """
    Stability AI Stable Video Diffusion generator.
    
    Usage:
        generator = StableVideoGenerator(
            model_name="stability-ai/svd",
            api_key="your-api-key"
        )
        result = await generator.generate("A cyberpunk cityscape at night")
    """
    
    def __init__(self, model_name: str = "stability-ai/svd", api_key: Optional[str] = None, **kwargs):
        super().__init__(model_name, api_key=api_key, **kwargs)
        self.api_key = api_key
        self._session = None
    
    async def _get_session(self):
        """Get aiohttp session."""
        if self._session is None:
            import aiohttp
            self._session = aiohttp.ClientSession(
                headers={"Authorization": f"Bearer {self.api_key}"}
            )
        return self._session
    
    async def close(self):
        """Close session."""
        if self._session:
            await self._session.close()
    
    async def generate(self, prompt: str, **kwargs) -> VideoGenerationResult:
        """Generate video using Stability AI."""
        session = await self._get_session()
        
        try:
            # For text-to-video, we may need to first generate an image
            # This is a simplified implementation
            url = "https://api.stability.ai/v2beta/image-to-video"
            
            # First generate an image from the prompt
            image_gen = StabilityGenerator(self.model_name.replace("svd", "sdxl"), self.api_key)
            image_result = await image_gen.generate(prompt)
            
            if not image_result.success:
                return VideoGenerationResult(
                    success=False,
                    error=f"Failed to generate source image: {image_result.error}"
                )
            
            # Then create video from image
            with open(image_result.image_path, "rb") as f:
                image_bytes = f.read()
            
            form_data = aiohttp.FormData()
            form_data.add_field("image", image_bytes, filename="source.png")
            form_data.add_field("seed", 0)
            form_data.add_field("cfg_scale", kwargs.get("guidance_scale", 1.8))
            form_data.add_field("motion_bucket_id", kwargs.get("motion_bucket", 127))
            
            async with session.post(url, data=form_data) as response:
                if response.status != 200:
                    error_text = await response.text()
                    return VideoGenerationResult(
                        success=False,
                        error=f"API error: {response.status} - {error_text}"
                    )
                
                result = await response.json()
                generation_id = result.get("id")
                
                # Poll for completion
                video_url = await self._poll_for_video(session, generation_id)
                
                if video_url:
                    # Download video
                    async with session.get(video_url) as video_response:
                        video_data = await video_response.read()
                    
                    temp_dir = Path(tempfile.gettempdir()) / "autonomousmoviemaker"
                    temp_dir.mkdir(exist_ok=True)
                    
                    import hashlib
                    filename = f"svd_{hashlib.md5(prompt.encode()).hexdigest()[:8]}.mp4"
                    video_path = temp_dir / filename
                    
                    with open(video_path, "wb") as f:
                        f.write(video_data)
                    
                    return VideoGenerationResult(
                        success=True,
                        video_path=video_path,
                        duration=kwargs.get("duration", 4.0),
                        metadata={"model": "svd", "generation_id": generation_id}
                    )
                else:
                    return VideoGenerationResult(
                        success=False,
                        error="Video generation timed out"
                    )
        except Exception as e:
            return VideoGenerationResult(
                success=False,
                error=str(e),
                metadata={"model": self.model_name}
            )
    
    async def _poll_for_video(self, session, generation_id: str, max_attempts: int = 30) -> Optional[str]:
        """Poll for video generation completion."""
        import asyncio
        
        for _ in range(max_attempts):
            await asyncio.sleep(5)  # Wait 5 seconds between polls
            
            url = f"https://api.stability.ai/v2beta/image-to-video/result/{generation_id}"
            async with session.get(url) as response:
                if response.status == 200:
                    result = await response.json()
                    if result.get("status") == "COMPLETE":
                        return result.get("result")
                elif response.status != 202:
                    break
        
        return None
    
    async def generate_batch(self, prompts: List[str], **kwargs) -> List[VideoGenerationResult]:
        """Generate multiple videos."""
        results = []
        for prompt in prompts:
            result = await self.generate(prompt, **kwargs)
            results.append(result)
        return results
