"""
Configuration module for autonomousMOVIEMAKER.

Provides flexible configuration for all aspects of movie generation.
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List
from pathlib import Path


@dataclass
class TextModelConfig:
    """Configuration for text generation models."""
    model_name: str = "openai/gpt-4"
    api_key: Optional[str] = None
    api_base: Optional[str] = None
    max_tokens: int = 4096
    temperature: float = 0.8
    timeout: int = 120
    extra_params: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ImageModelConfig:
    """Configuration for image generation models."""
    model_name: str = "stability-ai/sdxl"
    api_key: Optional[str] = None
    api_base: Optional[str] = None
    width: int = 1920
    height: int = 1080
    steps: int = 50
    guidance_scale: float = 7.5
    timeout: int = 300
    extra_params: Dict[str, Any] = field(default_factory=dict)


@dataclass
class VideoModelConfig:
    """Configuration for video generation models."""
    model_name: str = "runway/gen2"
    api_key: Optional[str] = None
    api_base: Optional[str] = None
    duration: int = 5  # seconds per clip
    fps: int = 24
    resolution: str = "1080p"
    timeout: int = 600
    extra_params: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PipelineConfig:
    """Configuration for the movie generation pipeline."""
    output_dir: Path = Path("./output")
    temp_dir: Path = Path("./temp")
    max_scenes: int = 50
    max_trailer_scenes: int = 10
    trailer_duration: int = 60  # seconds
    enable_audio: bool = True
    enable_subtitles: bool = True
    parallel_generation: bool = True
    max_workers: int = 4
    keep_intermediates: bool = False


@dataclass
class Config:
    """
    Main configuration class for autonomousMOVIEMAKER.
    
    Example:
        config = Config(
            text_model=TextModelConfig(model_name="anthropic/claude-3"),
            image_model=ImageModelConfig(model_name="midjourney/v6"),
            video_model=VideoModelConfig(model_name="pika/v1"),
        )
    """
    text_model: TextModelConfig = field(default_factory=TextModelConfig)
    image_model: ImageModelConfig = field(default_factory=ImageModelConfig)
    video_model: VideoModelConfig = field(default_factory=VideoModelConfig)
    pipeline: PipelineConfig = field(default_factory=PipelineConfig)
    
    # Project metadata
    project_name: str = "Untitled Movie"
    author: Optional[str] = None
    description: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Config":
        """Create Config from dictionary."""
        config = cls()
        
        if "text_model" in data:
            config.text_model = TextModelConfig(**data["text_model"])
        if "image_model" in data:
            config.image_model = ImageModelConfig(**data["image_model"])
        if "video_model" in data:
            config.video_model = VideoModelConfig(**data["video_model"])
        if "pipeline" in data:
            config.pipeline = PipelineConfig(**data["pipeline"])
        if "project_name" in data:
            config.project_name = data["project_name"]
        if "author" in data:
            config.author = data["author"]
        if "description" in data:
            config.description = data["description"]
            
        return config
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert Config to dictionary."""
        return {
            "text_model": {
                "model_name": self.text_model.model_name,
                "max_tokens": self.text_model.max_tokens,
                "temperature": self.text_model.temperature,
            },
            "image_model": {
                "model_name": self.image_model.model_name,
                "width": self.image_model.width,
                "height": self.image_model.height,
            },
            "video_model": {
                "model_name": self.video_model.model_name,
                "duration": self.video_model.duration,
                "fps": self.video_model.fps,
            },
            "pipeline": {
                "output_dir": str(self.pipeline.output_dir),
                "max_scenes": self.pipeline.max_scenes,
                "trailer_duration": self.pipeline.trailer_duration,
            },
            "project_name": self.project_name,
            "author": self.author,
        }
