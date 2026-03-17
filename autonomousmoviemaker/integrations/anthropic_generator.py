"""
Anthropic integration for autonomousMOVIEMAKER.

Provides text generation via Claude models.
"""

import asyncio
from typing import List, Optional

from ..generators.base import (
    BaseTextGenerator,
    TextGenerationResult,
)


class AnthropicGenerator(BaseTextGenerator):
    """
    Anthropic Claude text generator.
    
    Supports latest models: Claude Opus 4.6, Claude Sonnet 4.5, Claude Haiku 4.5
    
    Usage:
        generator = AnthropicGenerator(
            model_name="anthropic/claude-opus-4.6",
            api_key="your-api-key"
        )
        result = await generator.generate("Write a story about...")
    """
    
    def __init__(self, model_name: str = "anthropic/claude-opus-4.6", api_key: Optional[str] = None, **kwargs):
        super().__init__(model_name, api_key=api_key, **kwargs)
        self.api_key = api_key
        self._client = None
    
    def _get_client(self):
        """Lazy load Anthropic client."""
        if self._client is None:
            try:
                import anthropic
                self._client = anthropic.AsyncAnthropic(api_key=self.api_key)
            except ImportError:
                raise ImportError("Please install anthropic: pip install anthropic")
        return self._client
    
    async def generate(self, prompt: str, **kwargs) -> TextGenerationResult:
        """Generate text using Anthropic Claude."""
        client = self._get_client()
        
        try:
            max_tokens = kwargs.get("max_tokens", self.config.get("max_tokens", 4096))
            
            message = await client.messages.create(
                model=self.model_name.split("/")[-1] if "/" in self.model_name else self.model_name,
                max_tokens=max_tokens,
                messages=[{"role": "user", "content": prompt}],
            )
            
            return TextGenerationResult(
                success=True,
                text=message.content[0].text,
                tokens_used=message.usage.input_tokens + message.usage.output_tokens,
                metadata={"model": message.model, "usage": {"input": message.usage.input_tokens, "output": message.usage.output_tokens}}
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
