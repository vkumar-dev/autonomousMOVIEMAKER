"""
Integrations module for autonomousMOVIEMAKER.

This module provides ready-to-use integrations with popular AI services:
- OpenAI (GPT-4, DALL-E 3)
- Anthropic (Claude)
- Stability AI (SDXL, Stable Video)
- Runway ML (Gen-2)
- Mock generators for testing

Usage:
    from autonomousmoviemaker.integrations import (
        OpenAIGenerator,
        DALLEGenerator,
        StabilityGenerator,
        RunwayGenerator,
    )
    
    # Or use mock generators for testing
    from autonomousmoviemaker.integrations.mock_generator import (
        MockTextGenerator,
        MockImageGenerator,
        MockVideoGenerator,
    )
"""

# Text generators
try:
    from .openai_generator import OpenAIGenerator, DALLEGenerator
except ImportError:
    pass

try:
    from .anthropic_generator import AnthropicGenerator
except ImportError:
    pass

# Image generators
try:
    from .stability_generator import StabilityGenerator
except ImportError:
    pass

# Video generators
try:
    from .runway_generator import RunwayGenerator
except ImportError:
    pass

# Mock generators (always available)
from .mock_generator import MockTextGenerator, MockImageGenerator, MockVideoGenerator

__all__ = [
    # Text
    "OpenAIGenerator",
    "AnthropicGenerator",
    "MockTextGenerator",
    # Image
    "DALLEGenerator",
    "StabilityGenerator",
    "MockImageGenerator",
    # Video
    "RunwayGenerator",
    "MockVideoGenerator",
]
