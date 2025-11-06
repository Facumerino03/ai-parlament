"""
LLM Client for connecting to OpenRouter.
Uses OpenAI SDK for compatibility with OpenRouter API.
"""

from openai import OpenAI
from typing import List, Dict, Optional, Iterator
import logging
import time
from app.core.config import settings

logger = logging.getLogger(__name__)


class LLMClient:
    """Client for making requests to LLMs via OpenRouter."""

    def __init__(self, api_key: str = None, base_url: str = None):
        """
        Initialize the LLM client.

        Args:
            api_key: OpenRouter API key (uses settings if not provided)
            base_url: OpenRouter base URL (uses settings if not provided)
        """
        self.api_key = api_key or settings.openrouter_api_key
        self.base_url = base_url or settings.openrouter_base_url

        if not self.api_key:
            raise ValueError("OpenRouter API key is required. Set OPENROUTER_API_KEY in .env")

        # Initialize OpenAI client pointing to OpenRouter
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )

        logger.info(f"LLMClient initialized with base_url: {self.base_url}")

    def generar_respuesta(
        self,
        model: str,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 500,
        retries: int = None
    ) -> str:
        """
        Generate a response from the LLM.

        Args:
            model: Model identifier (e.g., "google/gemini-flash-1.5")
            messages: List of message dicts with 'role' and 'content'
            temperature: Sampling temperature (0-1)
            max_tokens: Maximum tokens in response
            retries: Number of retries on failure (uses settings if not provided)

        Returns:
            Generated text response

        Raises:
            Exception: If all retries fail
        """
        if retries is None:
            retries = settings.max_retries

        last_error = None

        for attempt in range(retries):
            try:
                logger.debug(
                    f"Making LLM request (attempt {attempt + 1}/{retries}): "
                    f"model={model}, temperature={temperature}, max_tokens={max_tokens}"
                )

                start_time = time.time()

                response = self.client.chat.completions.create(
                    model=model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens
                )

                elapsed_time = time.time() - start_time

                result = response.choices[0].message.content

                logger.info(
                    f"LLM response received: model={model}, "
                    f"tokens={response.usage.total_tokens if hasattr(response, 'usage') else 'N/A'}, "
                    f"time={elapsed_time:.2f}s"
                )

                # Add delay to respect rate limits
                time.sleep(settings.api_call_delay)

                return result

            except Exception as e:
                last_error = e
                logger.warning(
                    f"LLM request failed (attempt {attempt + 1}/{retries}): {e}"
                )

                if attempt < retries - 1:
                    # Exponential backoff
                    wait_time = (2 ** attempt) * settings.api_call_delay
                    logger.info(f"Waiting {wait_time:.1f}s before retry...")
                    time.sleep(wait_time)
                else:
                    logger.error(
                        f"All {retries} attempts failed for model {model}: {last_error}"
                    )

        # If we get here, all retries failed
        raise Exception(f"LLM request failed after {retries} attempts: {last_error}")

    def generar_respuesta_streaming(
        self,
        model: str,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 500
    ) -> Iterator[str]:
        """
        Generate a streaming response from the LLM.

        Args:
            model: Model identifier
            messages: List of message dicts
            temperature: Sampling temperature
            max_tokens: Maximum tokens in response

        Yields:
            Text chunks as they are generated
        """
        try:
            logger.debug(
                f"Making streaming LLM request: model={model}, "
                f"temperature={temperature}, max_tokens={max_tokens}"
            )

            start_time = time.time()

            stream = self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=True
            )

            total_chunks = 0
            for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    total_chunks += 1
                    yield chunk.choices[0].delta.content

            elapsed_time = time.time() - start_time

            logger.info(
                f"Streaming response completed: model={model}, "
                f"chunks={total_chunks}, time={elapsed_time:.2f}s"
            )

            # Add delay after streaming
            time.sleep(settings.api_call_delay)

        except Exception as e:
            logger.error(f"Streaming LLM request failed: {e}")
            raise

    def generar_respuesta_con_fallback(
        self,
        model_primary: str,
        model_fallback: str,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 500
    ) -> str:
        """
        Generate response with fallback to alternative model if primary fails.

        Args:
            model_primary: Primary model to try
            model_fallback: Fallback model if primary fails
            messages: List of message dicts
            temperature: Sampling temperature
            max_tokens: Maximum tokens

        Returns:
            Generated text response
        """
        try:
            return self.generar_respuesta(
                model=model_primary,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                retries=2  # Fewer retries before fallback
            )
        except Exception as e:
            logger.warning(
                f"Primary model {model_primary} failed, falling back to {model_fallback}: {e}"
            )
            return self.generar_respuesta(
                model=model_fallback,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )

    def verificar_conectividad(self, model: str = None) -> bool:
        """
        Verify connectivity to OpenRouter with a test request.

        Args:
            model: Model to test (uses default if not provided)

        Returns:
            True if successful, False otherwise
        """
        test_model = model or settings.model_gemini

        try:
            logger.info(f"Testing connectivity with model: {test_model}")

            response = self.generar_respuesta(
                model=test_model,
                messages=[
                    {"role": "system", "content": "You are a test assistant."},
                    {"role": "user", "content": "Respond with 'OK' if you can read this."}
                ],
                temperature=0.1,
                max_tokens=10,
                retries=1
            )

            logger.info(f"Connectivity test successful: {response[:50]}")
            return True

        except Exception as e:
            logger.error(f"Connectivity test failed: {e}")
            return False

    def contar_tokens_aproximado(self, text: str) -> int:
        """
        Approximate token count for text.
        Uses rough estimate: 1 token ≈ 4 characters.

        Args:
            text: Text to count tokens for

        Returns:
            Approximate token count
        """
        return len(text) // 4

    def truncar_texto_por_tokens(self, text: str, max_tokens: int) -> str:
        """
        Truncate text to fit within max tokens.

        Args:
            text: Text to truncate
            max_tokens: Maximum tokens allowed

        Returns:
            Truncated text
        """
        max_chars = max_tokens * 4
        if len(text) <= max_chars:
            return text
        return text[:max_chars] + "..."
