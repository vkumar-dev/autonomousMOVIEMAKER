"""
Runway ML integration for autonomousMOVIEMAKER.

Provides video generation via Runway Gen-2.
"""

import asyncio
from pathlib import Path
from typing import List, Optional
import tempfile

from ..generators.base import (
    BaseVideoGenerator,
    VideoGenerationResult,
)


class RunwayGenerator(BaseVideoGenerator):
    """
    Runway Gen-2 video generator.
    
    Usage:
        generator = RunwayGenerator(
            model_name="runway/gen2",
            api_key="your-api-key"
        )
        result = await generator.generate("A cyberpunk cityscape at night")
    
    Note: Runway API access may require enterprise access.
    Check https://docs.runwayml.com for latest API documentation.
    """
    
    def __init__(self, model_name: str = "runway/gen2", api_key: Optional[str] = None, **kwargs):
        super().__init__(model_name, api_key=api_key, **kwargs)
        self.api_key = api_key
        self._session = None
    
    async def _get_session(self):
        """Get aiohttp session."""
        if self._session is None:
            import aiohttp
            self._session = aiohttp.ClientSession(
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                }
            )
        return self._session
    
    async def close(self):
        """Close session."""
        if self._session:
            await self._session.close()
    
    async def generate(self, prompt: str, **kwargs) -> VideoGenerationResult:
        """Generate video using Runway Gen-2."""
        session = await self._get_session()
        
        try:
            url = "https://api.runwayml.com/v1/video/generations"
            
            payload = {
                "prompt": prompt,
                "model": "gen2",
                "duration_seconds": kwargs.get("duration", 4),
                "resolution": kwargs.get("resolution", "1280x720"),
                "seed": kwargs.get("seed", None),
            }
            
            async with session.post(url, json=payload) as response:
                if response.status not in [200, 201, 202]:
                    error_text = await response.text()
                    return VideoGenerationResult(
                        success=False,
                        error=f"API error: {response.status} - {error_text}"
                    )
                
                result = await response.json()
                task_id = result.get("id")
                
                # Poll for completion
                video_url = await self._poll_for_video(session, task_id)
                
                if video_url:
                    # Download video
                    async with session.get(video_url) as video_response:
                        video_data = await video_response.read()
                    
                    temp_dir = Path(tempfile.gettempdir()) / "autonomousmoviemaker"
                    temp_dir.mkdir(exist_ok=True)
                    
                    import hashlib
                    filename = f"runway_{hashlib.md5(prompt.encode()).hexdigest()[:8]}.mp4"
                    video_path = temp_dir / filename
                    
                    with open(video_path, "wb") as f:
                        f.write(video_data)
                    
                    return VideoGenerationResult(
                        success=True,
                        video_path=video_path,
                        duration=kwargs.get("duration", 4),
                        metadata={"model": "gen2", "task_id": task_id}
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
    
    async def _poll_for_video(self, session, task_id: str, max_attempts: int = 60) -> Optional[str]:
        """Poll for video generation completion."""
        for _ in range(max_attempts):
            await asyncio.sleep(5)
            
            url = f"https://api.runwayml.com/v1/video/generations/{task_id}"
            async with session.get(url) as response:
                if response.status == 200:
                    result = await response.json()
                    status = result.get("status", "")
                    if status in ["SUCCEEDED", "COMPLETE", "completed"]:
                        return result.get("output", {}).get("video_url")
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
