"""
Base classes for all generators in autonomousMOVIEMAKER.

These abstract base classes define the interface that all model integrations must implement.
"""

from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any, Union
from pathlib import Path
from dataclasses import dataclass
import asyncio


@dataclass
class GenerationResult:
    """Base class for all generation results."""
    success: bool
    data: Any = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class TextGenerationResult(GenerationResult):
    """Result from text generation."""
    text: str = ""
    tokens_used: int = 0


@dataclass
class ImageGenerationResult(GenerationResult):
    """Result from image generation."""
    image_path: Optional[Path] = None
    image_url: Optional[str] = None


@dataclass
class VideoGenerationResult(GenerationResult):
    """Result from video generation."""
    video_path: Optional[Path] = None
    video_url: Optional[str] = None
    duration: float = 0.0


class BaseTextGenerator(ABC):
    """
    Abstract base class for text generation models.
    
    Implement this class to integrate any LLM for story and script generation.
    
    Example:
        class OpenAIGenerator(BaseTextGenerator):
            async def generate(self, prompt, **kwargs):
                # Implement OpenAI API call
                return TextGenerationResult(success=True, text=response)
    """
    
    def __init__(self, model_name: str, **kwargs):
        self.model_name = model_name
        self.config = kwargs
    
    @abstractmethod
    async def generate(self, prompt: str, **kwargs) -> TextGenerationResult:
        """
        Generate text from a prompt.
        
        Args:
            prompt: The input prompt for generation
            **kwargs: Additional generation parameters
            
        Returns:
            TextGenerationResult with generated text
        """
        pass
    
    @abstractmethod
    async def generate_batch(self, prompts: List[str], **kwargs) -> List[TextGenerationResult]:
        """
        Generate text for multiple prompts in batch.
        
        Args:
            prompts: List of input prompts
            **kwargs: Additional generation parameters
            
        Returns:
            List of TextGenerationResult
        """
        pass
    
    async def generate_stream(self, prompt: str, **kwargs):
        """
        Generate text with streaming output.
        
        Args:
            prompt: The input prompt
            **kwargs: Additional parameters
            
        Yields:
            Chunks of generated text
        """
        raise NotImplementedError("Streaming not supported by this generator")


class BaseImageGenerator(ABC):
    """
    Abstract base class for image generation models.
    
    Implement this class to integrate any image generation model for scene visualization.
    
    Example:
        class StableDiffusionGenerator(BaseImageGenerator):
            async def generate(self, prompt, **kwargs):
                # Implement SD API call
                return ImageGenerationResult(success=True, image_path=path)
    """
    
    def __init__(self, model_name: str, **kwargs):
        self.model_name = model_name
        self.config = kwargs
    
    @abstractmethod
    async def generate(self, prompt: str, **kwargs) -> ImageGenerationResult:
        """
        Generate an image from a text prompt.
        
        Args:
            prompt: Text description of the image
            **kwargs: Additional generation parameters (width, height, steps, etc.)
            
        Returns:
            ImageGenerationResult with generated image
        """
        pass
    
    @abstractmethod
    async def generate_batch(self, prompts: List[str], **kwargs) -> List[ImageGenerationResult]:
        """
        Generate multiple images from prompts.
        
        Args:
            prompts: List of text prompts
            **kwargs: Additional generation parameters
            
        Returns:
            List of ImageGenerationResult
        """
        pass
    
    async def generate_variation(self, image_path: Path, prompt: str, **kwargs) -> ImageGenerationResult:
        """
        Generate a variation of an existing image.
        
        Args:
            image_path: Path to the source image
            prompt: Additional prompt for variation
            **kwargs: Additional parameters
            
        Returns:
            ImageGenerationResult with varied image
        """
        raise NotImplementedError("Image variation not supported by this generator")


class BaseVideoGenerator(ABC):
    """
    Abstract base class for video generation models.
    
    Implement this class to integrate any video generation model for scene/trailer creation.
    
    Example:
        class RunwayGenerator(BaseVideoGenerator):
            async def generate(self, prompt, **kwargs):
                # Implement Runway API call
                return VideoGenerationResult(success=True, video_path=path)
    """
    
    def __init__(self, model_name: str, **kwargs):
        self.model_name = model_name
        self.config = kwargs
    
    @abstractmethod
    async def generate(self, prompt: str, **kwargs) -> VideoGenerationResult:
        """
        Generate a video from a text prompt or image.
        
        Args:
            prompt: Text description or path to source image
            **kwargs: Additional parameters (duration, fps, etc.)
            
        Returns:
            VideoGenerationResult with generated video
        """
        pass
    
    @abstractmethod
    async def generate_batch(self, prompts: List[str], **kwargs) -> List[VideoGenerationResult]:
        """
        Generate multiple videos from prompts.
        
        Args:
            prompts: List of text prompts
            **kwargs: Additional generation parameters
            
        Returns:
            List of VideoGenerationResult
        """
        pass
    
    async def extend_video(self, video_path: Path, duration: float = 5.0) -> VideoGenerationResult:
        """
        Extend an existing video.
        
        Args:
            video_path: Path to source video
            duration: Additional duration in seconds
            
        Returns:
            VideoGenerationResult with extended video
        """
        raise NotImplementedError("Video extension not supported by this generator")
    
    async def interpolate(self, start_image: Path, end_image: Path, **kwargs) -> VideoGenerationResult:
        """
        Generate video interpolation between two images.
        
        Args:
            start_image: Path to starting image
            end_image: Path to ending image
            **kwargs: Additional parameters
            
        Returns:
            VideoGenerationResult with interpolated video
        """
        raise NotImplementedError("Video interpolation not supported by this generator")
