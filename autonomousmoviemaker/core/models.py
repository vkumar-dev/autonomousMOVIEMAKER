"""
Data models for movie elements in autonomousMOVIEMAKER.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from pathlib import Path
from enum import Enum
from datetime import datetime


class SceneType(Enum):
    """Types of scenes in a movie."""
    ESTABLISHING = "establishing"
    ACTION = "action"
    DIALOGUE = "dialogue"
    MONTAGE = "montage"
    CLIMAX = "climax"
    RESOLUTION = "resolution"


class Mood(Enum):
    """Mood/tone of a scene."""
    HAPPY = "happy"
    SAD = "sad"
    TENSE = "tense"
    ROMANTIC = "romantic"
    MYSTERIOUS = "mysterious"
    EPIC = "epic"
    COMEDIC = "comedic"
    DRAMATIC = "dramatic"


@dataclass
class Character:
    """Represents a character in the movie."""
    name: str
    description: str
    role: str  # protagonist, antagonist, supporting, etc.
    appearance: str = ""
    personality: str = ""
    arc: str = ""


@dataclass
class Scene:
    """Represents a single scene in the movie."""
    scene_number: int
    location: str
    description: str
    scene_type: SceneType = SceneType.ACTION
    mood: Mood = Mood.DRAMATIC
    characters: List[str] = field(default_factory=list)
    dialogue: List[Dict[str, str]] = field(default_factory=list)
    duration: float = 0.0  # seconds
    image_prompt: str = ""
    video_prompt: str = ""
    generated_image: Optional[Path] = None
    generated_video: Optional[Path] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert scene to dictionary."""
        return {
            "scene_number": self.scene_number,
            "location": self.location,
            "description": self.description,
            "scene_type": self.scene_type.value,
            "mood": self.mood.value,
            "characters": self.characters,
            "dialogue": self.dialogue,
            "duration": self.duration,
            "image_prompt": self.image_prompt,
            "video_prompt": self.video_prompt,
        }


@dataclass
class Script:
    """Represents the full movie script."""
    title: str
    logline: str
    synopsis: str
    genre: List[str]
    characters: List[Character]
    scenes: List[Scene]
    total_duration: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        if self.total_duration == 0.0 and self.scenes:
            self.total_duration = sum(scene.duration for scene in self.scenes)
    
    def get_trailer_scenes(self, max_scenes: int = 10) -> List[Scene]:
        """Select best scenes for trailer."""
        # Prioritize action, climax, and establishing scenes
        priority_order = {
            SceneType.CLIMAX: 1,
            SceneType.ACTION: 2,
            SceneType.ESTABLISHING: 3,
            SceneType.MONTAGE: 4,
            SceneType.DIALOGUE: 5,
            SceneType.RESOLUTION: 6,
        }
        sorted_scenes = sorted(self.scenes, key=lambda s: priority_order.get(s.scene_type, 99))
        return sorted_scenes[:max_scenes]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert script to dictionary."""
        return {
            "title": self.title,
            "logline": self.logline,
            "synopsis": self.synopsis,
            "genre": self.genre,
            "characters": [{"name": c.name, "description": c.description, "role": c.role} for c in self.characters],
            "scenes": [scene.to_dict() for scene in self.scenes],
            "total_duration": self.total_duration,
        }


@dataclass
class Trailer:
    """Represents a movie trailer."""
    title: str
    scenes: List[Scene]
    video_path: Optional[Path] = None
    duration: float = 0.0
    music_style: str = ""
    voiceover_script: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert trailer to dictionary."""
        return {
            "title": self.title,
            "scenes": [scene.to_dict() for scene in self.scenes],
            "duration": self.duration,
            "music_style": self.music_style,
            "voiceover_script": self.voiceover_script,
            "created_at": self.created_at.isoformat(),
        }


@dataclass
class Movie:
    """Represents the final complete movie."""
    title: str
    script: Script
    trailer: Optional[Trailer] = None
    video_path: Optional[Path] = None
    duration: float = 0.0
    resolution: str = "1080p"
    format: str = "mp4"
    audio_track: Optional[Path] = None
    subtitles: Optional[Path] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert movie to dictionary."""
        return {
            "title": self.title,
            "script": self.script.to_dict(),
            "duration": self.duration,
            "resolution": self.resolution,
            "format": self.format,
            "created_at": self.created_at.isoformat(),
        }


@dataclass
class GenerationProgress:
    """Tracks progress of movie generation."""
    stage: str  # story, script, images, trailer, full_movie
    progress: float  # 0.0 to 1.0
    current_step: str = ""
    total_steps: int = 0
    completed_steps: int = 0
    estimated_time_remaining: float = 0.0  # seconds
    message: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert progress to dictionary."""
        return {
            "stage": self.stage,
            "progress": self.progress,
            "current_step": self.current_step,
            "completed_steps": self.completed_steps,
            "total_steps": self.total_steps,
            "estimated_time_remaining": self.estimated_time_remaining,
            "message": self.message,
        }
