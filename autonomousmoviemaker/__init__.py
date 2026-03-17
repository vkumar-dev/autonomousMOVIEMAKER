"""
autonomousMOVIEMAKER - The Ultimate AI-Powered Movie Generation Framework

Transform your ideas into cinematic masterpieces with autonomous story generation,
scene visualization, and video production capabilities.

Usage:
    from autonomousmoviemaker import MovieMaker
    
    maker = MovieMaker(
        text_model="openai/gpt-4",
        image_model="stability-ai/sdxl",
        video_model="runway/gen2"
    )
    
    movie = maker.create_movie("A sci-fi epic about AI consciousness")
"""

__version__ = "1.0.0"
__author__ = "autonomousMOVIEMAKER Team"
__license__ = "MIT"

from .core.movie_maker import MovieMaker
from .core.pipeline import MoviePipeline
from .core.config import Config
from .generators.base import BaseTextGenerator, BaseImageGenerator, BaseVideoGenerator

__all__ = [
    "MovieMaker",
    "MoviePipeline", 
    "Config",
    "BaseTextGenerator",
    "BaseImageGenerator",
    "BaseVideoGenerator",
]
