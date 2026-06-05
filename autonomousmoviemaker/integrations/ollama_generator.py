"""
Ollama integration for autonomousMOVIEMAKER.

Provides offline text generation using a local Ollama instance.
"""

import asyncio
import json
import logging
from typing import List, Optional, Dict, Any
import aiohttp

from ..generators.base import (
    BaseTextGenerator,
    TextGenerationResult,
)

logger = logging.getLogger(__name__)

class OllamaTextGenerator(BaseTextGenerator):
    """
    Ollama Text Generator.
    
    Uses local Ollama instance for keyless, offline inference.
    
    Usage:
        generator = OllamaTextGenerator(
            model_name="ollama/mistral",
            api_base="http://localhost:11434"
        )
        result = await generator.generate("Write a script about...")
    """
    
    def __init__(self, model_name: str = "ollama/mistral", api_base: Optional[str] = None, **kwargs):
        super().__init__(model_name, **kwargs)
        self.api_base = api_base or "http://localhost:11434"
        
        # Clean model name (remove prefix "ollama/" if present)
        self.actual_model = self.model_name.split("/")[-1] if "/" in self.model_name else self.model_name
        
    async def generate(self, prompt: str, **kwargs) -> TextGenerationResult:
        """Generate text using Ollama API."""
        url = f"{self.api_base}/api/generate"
        
        # Determine if we should request JSON format
        format_type = kwargs.get("format", None)
        if not format_type and ("json" in prompt.lower() or "json array" in prompt.lower() or "json format" in prompt.lower()):
            format_type = "json"
            
        payload = {
            "model": self.actual_model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": kwargs.get("temperature", self.config.get("temperature", 0.7)),
                "num_predict": kwargs.get("max_tokens", kwargs.get("num_predict", self.config.get("max_tokens", 4096))),
            }
        }
        if format_type:
            payload["format"] = format_type
            
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload, timeout=kwargs.get("timeout", 300)) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        return TextGenerationResult(
                            success=False,
                            error=f"Ollama API returned status {response.status}: {error_text}",
                            metadata={"model": self.actual_model}
                        )
                    
                    data = await response.json()
                    response_text = data.get("response", "")
                    
                    # Try parsing the JSON to populate result.data if format is json
                    parsed_data = None
                    if format_type == "json" or "json" in prompt.lower():
                        try:
                            # Clean markdown code block wraps if present
                            clean_text = response_text.strip()
                            if clean_text.startswith("```"):
                                lines = clean_text.splitlines()
                                if lines[0].startswith("```"):
                                    lines = lines[1:]
                                if lines[-1].startswith("```"):
                                    lines = lines[:-1]
                                clean_text = "\n".join(lines).strip()
                            parsed_data = json.loads(clean_text)
                        except Exception as json_err:
                            logger.warning(f"Failed to parse generated text as JSON: {json_err}")
                    
                    return TextGenerationResult(
                        success=True,
                        text=response_text,
                        data=parsed_data if parsed_data is not None else response_text,
                        tokens_used=data.get("eval_count", 0),
                        metadata={
                            "model": self.actual_model,
                            "eval_duration": data.get("eval_duration", 0),
                            "prompt_eval_count": data.get("prompt_eval_count", 0)
                        }
                    )
        except Exception as e:
            return TextGenerationResult(
                success=False,
                error=f"Ollama connection error: {str(e)}",
                metadata={"model": self.actual_model}
            )
            
    async def generate_batch(self, prompts: List[str], **kwargs) -> List[TextGenerationResult]:
        """Generate text for multiple prompts in parallel."""
        tasks = [self.generate(prompt, **kwargs) for prompt in prompts]
        return await asyncio.gather(*tasks)
