#!/usr/bin/env python3
"""
Elpida Unified LLM Client
==========================

Single source of truth for all LLM provider calls.
Every module that needs to talk to an LLM imports from here.

Providers supported:
  - Claude (Anthropic)
  - OpenAI (GPT)
  - Gemini (Google)
  - Grok (xAI)
  - Mistral
  - Cohere
  - Perplexity
  - OpenRouter (failsafe)
  - Groq
  - HuggingFace
"""

import os
import time
import json
import logging
import requests
from dataclasses import dataclass, field
from typing import Optional, Dict, Any
from enum import Enum

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

logger = logging.getLogger("elpida.llm_client")


# ---------------------------------------------------------------------------
# Provider registry
# ---------------------------------------------------------------------------

class Provider(str, Enum):
    CLAUDE = "claude"
    OPENAI = "openai"
    GEMINI = "gemini"
    GROK = "grok"
    MISTRAL = "mistral"
    COHERE = "cohere"
    PERPLEXITY = "perplexity"
    OPENROUTER = "openrouter"
    GROQ = "groq"
    HUGGINGFACE = "huggingface"


# Default models per provider — can be overridden per-call
DEFAULT_MODELS: Dict[str, str] = {
    Provider.CLAUDE:      "claude-sonnet-4-20250514",
    Provider.OPENAI:      "gpt-4o-mini",
    Provider.GEMINI:      "gemini-2.0-flash",
    Provider.GROK:        "grok-3",
    Provider.MISTRAL:     "mistral-small-latest",
    Provider.COHERE:      "command-a-03-2025",
    Provider.PERPLEXITY:  "sonar",
    Provider.OPENROUTER:  "anthropic/claude-sonnet-4",
    Provider.GROQ:        "llama-3.3-70b-versatile",
    Provider.HUGGINGFACE: "Qwen/Qwen2.5-72B-Instruct",
}

# Env var name for each provider's API key
API_KEY_ENV: Dict[str, str] = {
    Provider.CLAUDE:      "ANTHROPIC_API_KEY",
    Provider.OPENAI:      "OPENAI_API_KEY",
    Provider.GEMINI:      "GEMINI_API_KEY",
    Provider.GROK:        "XAI_API_KEY",
    Provider.MISTRAL:     "MISTRAL_API_KEY",
    Provider.COHERE:      "COHERE_API_KEY",
    Provider.PERPLEXITY:  "PERPLEXITY_API_KEY",
    Provider.OPENROUTER:  "OPENROUTER_API_KEY",
    Provider.GROQ:        "GROQ_API_KEY",
    Provider.HUGGINGFACE: "HUGGINGFACE_API_KEY",
}

# Cost per output token (approximate, for budget tracking)
COST_PER_TOKEN: Dict[str, float] = {
    Provider.CLAUDE:     0.000003,
    Provider.OPENAI:     0.0,        # gpt-4o-mini — negligible
    Provider.GEMINI:     0.0,
    Provider.GROK:       0.0000003,
    Provider.MISTRAL:    0.000001,
    Provider.COHERE:     0.0000005,
    Provider.PERPLEXITY: 0.0,
    Provider.OPENROUTER: 0.0,
    Provider.GROQ:       0.0,
    Provider.HUGGINGFACE:0.0,
}


# ---------------------------------------------------------------------------
# Stats tracking
# ---------------------------------------------------------------------------

@dataclass
class ProviderStats:
    """Usage stats for a single provider."""
    requests: int = 0
    tokens: int = 0
    cost: float = 0.0
    failures: int = 0

    def to_dict(self) -> dict:
        return {"requests": self.requests, "tokens": self.tokens,
                "cost": round(self.cost, 6), "failures": self.failures}


# ---------------------------------------------------------------------------
# The unified client
# ---------------------------------------------------------------------------

class LLMClient:
    """
    Unified LLM client for Elpida.

    Usage:
        client = LLMClient()
        text = client.call("claude", prompt)
        text = client.call("openai", prompt, max_tokens=800, model="gpt-4o")
    """

    def __init__(
        self,
        rate_limit_seconds: float = 1.5,
        default_max_tokens: int = 600,
        default_timeout: int = 60,
        openrouter_failsafe: bool = True,
    ):
        self.rate_limit_seconds = rate_limit_seconds
        self.default_max_tokens = default_max_tokens
        self.default_timeout = default_timeout
        self.openrouter_failsafe = openrouter_failsafe

        # Load API keys from environment
        self.api_keys: Dict[str, Optional[str]] = {
            provider: os.getenv(env_var)
            for provider, env_var in API_KEY_ENV.items()
        }

        # Per-provider stats
        self.stats: Dict[str, ProviderStats] = {
            p.value: ProviderStats() for p in Provider
        }

        # Rate-limit timestamps
        self._last_call: Dict[str, float] = {}

        # Dispatch table
        self._dispatch = {
            Provider.CLAUDE:      self._call_claude,
            Provider.OPENAI:      self._call_openai_compat,
            Provider.GEMINI:      self._call_gemini,
            Provider.GROK:        self._call_openai_compat,
            Provider.MISTRAL:     self._call_openai_compat,
            Provider.COHERE:      self._call_cohere,
            Provider.PERPLEXITY:  self._call_openai_compat,
            Provider.OPENROUTER:  self._call_openai_compat,
            Provider.GROQ:        self._call_openai_compat,
            Provider.HUGGINGFACE: self._call_openai_compat,
        }

    # ----- public API -------------------------------------------------------

    def call(
        self,
        provider: str,
        prompt: str,
        *,
        model: Optional[str] = None,
        max_tokens: Optional[int] = None,
        timeout: Optional[int] = None,
        system_prompt: Optional[str] = None,
    ) -> Optional[str]:
        """
        Send a prompt to *provider* and return the text response, or None.

        If the primary provider fails and openrouter_failsafe is enabled,
        automatically retries via OpenRouter.
        """
        provider = provider.lower().strip()
        if provider not in {p.value for p in Provider}:
            logger.warning("Unknown provider '%s', routing to OpenRouter", provider)
            provider = Provider.OPENROUTER.value

        self._rate_limit(provider)

        _model = model or DEFAULT_MODELS.get(provider, "")
        _max = max_tokens or self.default_max_tokens
        _timeout = timeout or self.default_timeout

        result = None
        try:
            handler = self._dispatch.get(Provider(provider))
            if handler:
                result = handler(
                    provider=provider,
                    prompt=prompt,
                    model=_model,
                    max_tokens=_max,
                    timeout=_timeout,
                    system_prompt=system_prompt,
                )
        except Exception as e:
            logger.error("%s exception: %s", provider, e)
            self.stats[provider].failures += 1

        # Failsafe
        if result is None and self.openrouter_failsafe and provider != Provider.OPENROUTER.value:
            logger.info("%s failed — trying OpenRouter failsafe", provider)
            result = self._openrouter_failsafe(prompt, _max, _timeout)

        return result

    def get_stats(self) -> Dict[str, dict]:
        """Return all provider stats as a serialisable dict."""
        return {k: v.to_dict() for k, v in self.stats.items() if v.requests or v.failures}

    def available_providers(self) -> list[str]:
        """Return list of providers that have API keys configured."""
        return [p for p, key in self.api_keys.items() if key]

    # ----- rate limiter -----------------------------------------------------

    def _rate_limit(self, provider: str):
        now = time.time()
        last = self._last_call.get(provider, 0)
        wait = self.rate_limit_seconds - (now - last)
        if wait > 0:
            time.sleep(wait)
        self._last_call[provider] = time.time()

    # ----- provider implementations -----------------------------------------

    # Endpoints for OpenAI-compatible providers
    _OPENAI_COMPAT_ENDPOINTS = {
        Provider.OPENAI:      "https://api.openai.com/v1/chat/completions",
        Provider.GROK:        "https://api.x.ai/v1/chat/completions",
        Provider.MISTRAL:     "https://api.mistral.ai/v1/chat/completions",
        Provider.PERPLEXITY:  "https://api.perplexity.ai/chat/completions",
        Provider.OPENROUTER:  "https://openrouter.ai/api/v1/chat/completions",
        Provider.GROQ:        "https://api.groq.com/openai/v1/chat/completions",
        Provider.HUGGINGFACE: "https://router.huggingface.co/v1/chat/completions",
    }

    def _call_openai_compat(
        self, *, provider: str, prompt: str, model: str,
        max_tokens: int, timeout: int, system_prompt: Optional[str],
    ) -> Optional[str]:
        """
        Generic handler for all OpenAI-compatible chat/completions APIs.
        Covers: OpenAI, Grok, Mistral, Perplexity, OpenRouter, Groq, HuggingFace.
        """
        key = self.api_keys.get(provider)
        if not key:
            logger.warning("%s: no API key (%s)", provider, API_KEY_ENV.get(provider, "?"))
            return None

        endpoint = self._OPENAI_COMPAT_ENDPOINTS.get(Provider(provider))
        if not endpoint:
            logger.error("%s: no endpoint configured", provider)
            return None

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        try:
            response = requests.post(
                endpoint,
                headers={
                    "Authorization": f"Bearer {key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": model,
                    "messages": messages,
                    "max_tokens": max_tokens,
                },
                timeout=timeout,
            )
            if response.status_code == 200:
                data = response.json()
                text = data["choices"][0]["message"]["content"]
                tokens = data.get("usage", {}).get("total_tokens", len(text) // 4)
                self.stats[provider].requests += 1
                self.stats[provider].tokens += tokens
                self.stats[provider].cost += tokens * COST_PER_TOKEN.get(provider, 0)
                return text
            else:
                logger.warning("%s: HTTP %d — %s", provider, response.status_code, response.text[:200])
                self.stats[provider].failures += 1
                return None
        except Exception as e:
            logger.error("%s exception: %s", provider, e)
            self.stats[provider].failures += 1
            return None

    def _call_claude(
        self, *, provider: str, prompt: str, model: str,
        max_tokens: int, timeout: int, system_prompt: Optional[str],
    ) -> Optional[str]:
        """Anthropic Messages API (non-OpenAI-compatible)."""
        key = self.api_keys.get(Provider.CLAUDE)
        if not key:
            logger.warning("Claude: no API key (ANTHROPIC_API_KEY)")
            return None

        messages = [{"role": "user", "content": prompt}]
        body: Dict[str, Any] = {
            "model": model,
            "max_tokens": max_tokens,
            "messages": messages,
        }
        if system_prompt:
            body["system"] = system_prompt

        try:
            response = requests.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": key,
                    "anthropic-version": "2023-06-01",
                    "Content-Type": "application/json",
                },
                json=body,
                timeout=timeout,
            )
            if response.status_code == 200:
                data = response.json()
                text = data["content"][0]["text"]
                tokens = data.get("usage", {}).get("output_tokens", len(text) // 4)
                self.stats[Provider.CLAUDE].requests += 1
                self.stats[Provider.CLAUDE].tokens += tokens
                self.stats[Provider.CLAUDE].cost += tokens * COST_PER_TOKEN.get(Provider.CLAUDE, 0)
                return text
            else:
                logger.warning("Claude: HTTP %d — %s", response.status_code, response.text[:200])
                self.stats[Provider.CLAUDE].failures += 1
                return None
        except Exception as e:
            logger.error("Claude exception: %s", e)
            self.stats[Provider.CLAUDE].failures += 1
            return None

    def _call_gemini(
        self, *, provider: str, prompt: str, model: str,
        max_tokens: int, timeout: int, system_prompt: Optional[str],
    ) -> Optional[str]:
        """Google Generative AI API (non-OpenAI-compatible)."""
        key = self.api_keys.get(Provider.GEMINI)
        if not key:
            logger.warning("Gemini: no API key (GEMINI_API_KEY)")
            return None

        contents = []
        if system_prompt:
            contents.append({"parts": [{"text": system_prompt}], "role": "user"})
            contents.append({"parts": [{"text": "Understood."}], "role": "model"})
        contents.append({"parts": [{"text": prompt}]})

        try:
            response = requests.post(
                f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={key}",
                headers={"Content-Type": "application/json"},
                json={
                    "contents": contents,
                    "generationConfig": {"maxOutputTokens": max_tokens},
                },
                timeout=timeout,
            )
            if response.status_code == 200:
                data = response.json()
                text = data["candidates"][0]["content"]["parts"][0]["text"]
                tokens = len(text) // 4  # Gemini doesn't reliably report usage
                self.stats[Provider.GEMINI].requests += 1
                self.stats[Provider.GEMINI].tokens += tokens
                return text
            else:
                logger.warning("Gemini: HTTP %d — %s", response.status_code, response.text[:200])
                self.stats[Provider.GEMINI].failures += 1
                return None
        except Exception as e:
            logger.error("Gemini exception: %s", e)
            self.stats[Provider.GEMINI].failures += 1
            return None

    def _call_cohere(
        self, *, provider: str, prompt: str, model: str,
        max_tokens: int, timeout: int, system_prompt: Optional[str],
    ) -> Optional[str]:
        """Cohere v2 Chat API (non-OpenAI-compatible response format)."""
        key = self.api_keys.get(Provider.COHERE)
        if not key:
            logger.warning("Cohere: no API key (COHERE_API_KEY)")
            return None

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        try:
            response = requests.post(
                "https://api.cohere.com/v2/chat",
                headers={
                    "Authorization": f"Bearer {key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": model,
                    "messages": messages,
                    "max_tokens": max_tokens,
                },
                timeout=timeout,
            )
            if response.status_code == 200:
                data = response.json()
                # Cohere v2 nests: data["message"]["content"][0]["text"]
                if "message" in data and "content" in data["message"]:
                    text = data["message"]["content"][0]["text"]
                else:
                    logger.warning("Cohere: unexpected response format: %s", str(data)[:200])
                    self.stats[Provider.COHERE].failures += 1
                    return None
                tokens = (data.get("usage", {})
                              .get("billed_units", {})
                              .get("output_tokens", len(text) // 4))
                self.stats[Provider.COHERE].requests += 1
                self.stats[Provider.COHERE].tokens += tokens
                self.stats[Provider.COHERE].cost += tokens * COST_PER_TOKEN.get(Provider.COHERE, 0)
                return text
            else:
                logger.warning("Cohere: HTTP %d — %s", response.status_code, response.text[:200])
                self.stats[Provider.COHERE].failures += 1
                return None
        except Exception as e:
            logger.error("Cohere exception: %s", e)
            self.stats[Provider.COHERE].failures += 1
            return None

    # ----- OpenRouter failsafe ----------------------------------------------

    def _openrouter_failsafe(
        self, prompt: str, max_tokens: int, timeout: int
    ) -> Optional[str]:
        """Last-resort call via OpenRouter."""
        return self._call_openai_compat(
            provider=Provider.OPENROUTER.value,
            prompt=prompt,
            model=DEFAULT_MODELS[Provider.OPENROUTER],
            max_tokens=max_tokens,
            timeout=timeout,
            system_prompt=None,
        )


# ---------------------------------------------------------------------------
# Module-level convenience
# ---------------------------------------------------------------------------

_default_client: Optional[LLMClient] = None


def get_client(**kwargs) -> LLMClient:
    """Return (or create) the module-level default LLMClient singleton."""
    global _default_client
    if _default_client is None:
        _default_client = LLMClient(**kwargs)
    return _default_client


def call(provider: str, prompt: str, **kwargs) -> Optional[str]:
    """Shortcut: call a provider using the default client."""
    return get_client().call(provider, prompt, **kwargs)
