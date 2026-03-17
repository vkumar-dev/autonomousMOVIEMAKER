# 🎬 autonomousMOVIEMAKER

<div align="center">

**Transform Your Ideas Into Cinematic Masterpieces — Autonomously**

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code Style: Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

[Installation](#-installation) • [Quick Start](#-quick-start) • [Documentation](#-documentation) • [Examples](#-examples) • [Contributing](#-contributing)

</div>

---

## 🌟 Overview

**autonomousMOVIEMAKER** is the ultimate AI-powered movie generation framework that transforms text prompts into complete cinematic experiences. From story conception to final cut, automate your entire film production pipeline with state-of-the-art AI models.

### ✨ Key Features

- 📝 **Autonomous Story Generation** — AI-powered scriptwriting with character development, scene breakdowns, and dialogue
- 🎨 **Scene Visualization** — Generate stunning cinematic stills for every scene
- 🎬 **Trailer-First Workflow** — Preview your movie with an AI-generated trailer before committing to full production
- 🔄 **Iterative Feedback Loop** — Refine your movie based on trailer feedback
- 🔌 **Model Agnostic** — Integrate with any text, image, or video generation model
- ⚡ **Async-First Design** — Built for high-performance parallel generation
- 🧩 **Extensible Architecture** — Easy to add custom model integrations

### 🎯 Use Cases

- **Content Creators** — Rapidly prototype video content ideas
- **Filmmakers** — Create storyboards, pre-visualizations, and pitch trailers
- **Game Developers** — Generate cutscenes and narrative content
- **Marketers** — Produce promotional videos at scale
- **Educators** — Create educational content and visualizations
- **AI Researchers** — Framework for experimenting with generative video pipelines

---

## 🚀 Quick Start

### Installation

```bash
# Install from PyPI (coming soon)
pip install autonomous-moviemaker

# Or install from source
git clone https://github.com/yourusername/autonomousMOVIEMAKER.git
cd autonomousMOVIEMAKER
pip install -e .
```

### 5-Minute Example

```python
import asyncio
from autonomousmoviemaker import MovieMaker

async def main():
    # Initialize with default (mock) generators
    maker = MovieMaker()
    
    # Create a movie from a prompt
    result = await maker.create_movie(
        "A heartwarming tale of a robot who learns to love"
    )
    
    # Review the trailer
    print(f"Title: {result['script'].title}")
    print(f"Trailer ready: {result['trailer']}")
    
    # Approve and generate full movie
    if user_approves_trailer():
        movie = await maker.generate_full_movie(result['script'])
        print(f"🎉 Movie complete: {movie.video_path}")

asyncio.run(main())
```

---

## 📦 Installation

### Basic Installation

```bash
pip install autonomous-moviemaker
```

### With Optional Dependencies

```bash
# Full installation with all integrations
pip install autonomous-moviemaker[all]

# Specific integrations
pip install autonomous-moviemaker[openai]    # OpenAI GPT & DALL-E
pip install autonomous-moviemaker[stability] # Stability AI
pip install autonomous-moviemaker[runway]    # Runway ML
pip install autonomous-moviemaker[anthropic] # Anthropic Claude
```

### Development Installation

```bash
git clone https://github.com/yourusername/autonomousMOVIEMAKER.git
cd autonomousMOVIEMAKER
pip install -e ".[dev]"
```

---

## 🎯 Core Concepts

### The Movie Generation Pipeline

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   PROMPT    │ ──► │   STORY     │ ──► │   SCRIPT    │
│   Input     │     │  Concept    │     │  + Scenes   │
└─────────────┘     └─────────────┘     └──────┬──────┘
                                               │
                                               ▼
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   MOVIE     │ ◄── │    FULL     │ ◄── │   TRAILER   │
│   Output    │     │   MOVIE     │     │  Preview    │
└─────────────┘     └─────────────┘     └──────┬──────┘
                                               │
                              ┌────────────────┘
                              │
                              ▼
                       ┌─────────────┐
                       │   APPROVE?  │
                       │  Yes / No   │
                       └─────────────┘
```

### Architecture Overview

```
autonomousmoviemaker/
├── core/
│   ├── movie_maker.py    # Main interface
│   ├── pipeline.py       # Generation pipeline
│   ├── config.py         # Configuration
│   └── models.py         # Data models
├── generators/
│   └── base.py           # Base generator interfaces
├── integrations/
│   ├── openai_generator.py
│   ├── stability_generator.py
│   ├── runway_generator.py
│   └── mock_generator.py
└── utils/
    └── ...
```

---

## 📖 Documentation

### MovieMaker Class

The `MovieMaker` class is your primary interface for creating movies.

#### Basic Usage

```python
from autonomousmoviemaker import MovieMaker

# Simple initialization
maker = MovieMaker(
    text_model="openai/gpt-4",
    image_model="stability-ai/sdxl",
    video_model="runway/gen2"
)
```

#### With Custom Generators

```python
from autonomousmoviemaker import MovieMaker
from autonomousmoviemaker.integrations import (
    OpenAIGenerator,
    StabilityGenerator,
    RunwayGenerator
)

# Create custom generators
text_gen = OpenAIGenerator(api_key="your-openai-key")
image_gen = StabilityGenerator(api_key="your-stability-key")
video_gen = RunwayGenerator(api_key="your-runway-key")

# Initialize with custom generators
maker = MovieMaker(
    text_generator=text_gen,
    image_generator=image_gen,
    video_generator=video_gen
)
```

### Configuration

```python
from autonomousmoviemaker import Config, MovieMaker

config = Config(
    text_model={
        "model_name": "anthropic/claude-3-opus",
        "max_tokens": 8192,
        "temperature": 0.8
    },
    image_model={
        "model_name": "stability-ai/sdxl",
        "width": 1920,
        "height": 1080
    },
    video_model={
        "model_name": "runway/gen2",
        "duration": 5,
        "fps": 24
    },
    pipeline={
        "max_scenes": 50,
        "trailer_duration": 60,
        "parallel_generation": True
    }
)

maker = MovieMaker(config=config)
```

### API Reference

#### `MovieMaker.create_movie(prompt, auto_approve=False)`

Complete movie creation workflow with trailer approval.

```python
result = await maker.create_movie(
    "A sci-fi epic about first contact",
    auto_approve=False  # Set True to skip trailer approval
)

# Access results
script = result['script']
trailer = result['trailer']
movie = result['movie']  # None if not auto-approved
```

#### `MovieMaker.generate_script(prompt)`

Generate a complete screenplay from a prompt.

```python
script = await maker.generate_script("A romantic comedy set in Paris")

print(script.title)        # Movie title
print(script.logline)      # One-sentence summary
print(script.synopsis)     # Detailed synopsis
print(script.scenes)       # List of Scene objects
print(script.characters)   # List of Character objects
```

#### `MovieMaker.generate_trailer(script)`

Generate a trailer from an existing script.

```python
trailer = await maker.generate_trailer(script)

print(trailer.scenes)      # Scenes selected for trailer
print(trailer.duration)    # Trailer duration in seconds
```

#### `MovieMaker.generate_full_movie(script)`

Generate the complete movie from an approved script.

```python
movie = await maker.generate_full_movie(script)

print(movie.video_path)    # Path to final movie
print(movie.duration)      # Total duration
print(movie.resolution)    # Video resolution
```

### Progress Tracking

```python
def on_progress(progress):
    print(f"Stage: {progress.stage}")
    print(f"Progress: {progress.progress * 100:.1f}%")
    print(f"Message: {progress.message}")

maker.set_progress_callback(on_progress)
await maker.create_movie("Your prompt")
```

---

## 🔌 Available Integrations

### Text Generation

| Provider | Models | Usage |
|----------|--------|-------|
| OpenAI | GPT-4, GPT-4-Turbo | `OpenAIGenerator` |
| Anthropic | Claude 3 Opus/Sonnet/Haiku | `AnthropicGenerator` |
| Local | llama.cpp, Ollama | Custom implementation |

### Image Generation

| Provider | Models | Usage |
|----------|--------|-------|
| Stability AI | SDXL, SD 1.5 | `StabilityGenerator` |
| OpenAI | DALL-E 3 | `DALLEGenerator` |
| Replicate | Various | Custom implementation |

### Video Generation

| Provider | Models | Usage |
|----------|--------|-------|
| Runway ML | Gen-2 | `RunwayGenerator` |
| Stability AI | Stable Video | `StableVideoGenerator` |
| Hugging Face | Various | Custom implementation |

---

## 💡 Examples

### Basic Example

```python
import asyncio
from autonomousmoviemaker import MovieMaker

async def main():
    maker = MovieMaker()
    result = await maker.create_movie("A cyberpunk detective story")
    print(f"Created: {result['script'].title}")

asyncio.run(main())
```

### Advanced Example with Real APIs

```python
import asyncio
import os
from autonomousmoviemaker import MovieMaker
from autonomousmoviemaker.integrations import (
    OpenAIGenerator,
    StabilityGenerator,
    RunwayGenerator
)

async def main():
    # Initialize with real API generators
    maker = MovieMaker(
        text_generator=OpenAIGenerator(api_key=os.getenv("OPENAI_API_KEY")),
        image_generator=StabilityGenerator(api_key=os.getenv("STABILITY_API_KEY")),
        video_generator=RunwayGenerator(api_key=os.getenv("RUNWAY_API_KEY"))
    )
    
    # Set progress callback
    def on_progress(p):
        print(f"[{p.stage}] {p.message}")
    
    maker.set_progress_callback(on_progress)
    
    # Create movie
    result = await maker.create_movie(
        "An animated short about a lonely robot who finds a flower"
    )
    
    # Review and approve
    display_trailer(result['trailer'])
    
    if get_user_approval():
        movie = await maker.generate_full_movie(result['script'])
        save_movie(movie)

asyncio.run(main())
```

### Custom Generator Example

```python
from autonomousmoviemaker.generators.base import BaseTextGenerator, TextGenerationResult

class MyCustomGenerator(BaseTextGenerator):
    async def generate(self, prompt: str, **kwargs) -> TextGenerationResult:
        # Your implementation here
        return TextGenerationResult(success=True, text="Generated text")
    
    async def generate_batch(self, prompts: list, **kwargs) -> list:
        return [await self.generate(p, **kwargs) for p in prompts]

# Use with MovieMaker
maker = MovieMaker(text_generator=MyCustomGenerator())
```

---

## 🧪 Testing

```bash
# Run tests
pytest tests/

# Run with coverage
pytest tests/ --cov=autonomousmoviemaker

# Run specific test file
pytest tests/test_movie_maker.py
```

---

## 🤝 Contributing

We welcome contributions! Here's how you can help:

1. **Fork the repository**
2. **Create a feature branch** (`git checkout -b feature/amazing-feature`)
3. **Make your changes**
4. **Run tests** (`pytest tests/`)
5. **Commit your changes** (`git commit -m 'Add amazing feature'`)
6. **Push to the branch** (`git push origin feature/amazing-feature`)
7. **Open a Pull Request**

### Development Guidelines

- Follow [PEP 8](https://pep8.org/) style guidelines
- Write tests for new features
- Update documentation
- Use descriptive commit messages

---

## 📄 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- Built with ❤️ by the autonomousMOVIEMAKER team
- Thanks to all AI model providers for their amazing APIs
- Inspired by the future of autonomous content creation

---

## 📬 Contact

- **GitHub Issues**: [Report bugs or request features](https://github.com/yourusername/autonomousMOVIEMAKER/issues)
- **Discussions**: [Join the conversation](https://github.com/yourusername/autonomousMOVIEMAKER/discussions)
- **Twitter**: [@autonomousMovie](https://twitter.com/autonomousMovie)

---

<div align="center">

**Made with 🎬 and 🤖**

[⭐ Star this repo](https://github.com/yourusername/autonomousMOVIEMAKER) if you find it useful!

</div>
