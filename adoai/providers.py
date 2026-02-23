from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import List, Dict


@dataclass
class ProviderResponse:
    text: str


class BaseProvider:
    def chat(self, messages: List[Dict[str, str]], temperature: float = 0.3) -> ProviderResponse:
        raise NotImplementedError


class OpenAICompatibleProvider(BaseProvider):
    """Uses an OpenAI-compatible /v1/chat/completions endpoint."""

    def __init__(self, base_url: str, api_key: str, model: str) -> None:
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.model = model

    def chat(self, messages: List[Dict[str, str]], temperature: float = 0.3) -> ProviderResponse:
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
        }
        req = urllib.request.Request(
            url=f"{self.base_url}/v1/chat/completions",
            data=json.dumps(payload).encode("utf-8"),
            method="POST",
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
        )
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                body = json.loads(resp.read().decode("utf-8"))
        except urllib.error.URLError as exc:
            raise RuntimeError(f"LLM request failed: {exc}") from exc

        try:
            text = body["choices"][0]["message"]["content"]
        except Exception as exc:  # noqa: BLE001
            raise RuntimeError(f"Unexpected LLM response format: {body}") from exc
        return ProviderResponse(text=text)


class HeuristicProvider(BaseProvider):
    """Offline fallback when no API credentials are present."""

    def chat(self, messages: List[Dict[str, str]], temperature: float = 0.3) -> ProviderResponse:
        last_user = ""
        for msg in reversed(messages):
            if msg.get("role") == "user":
                last_user = msg.get("content", "")
                break

        text = (
            "I am Adoai in local fallback mode. "
            "I can still help with planning, drafting, and structured reasoning, "
            "but for deep model intelligence set OPENAI_API_KEY, OPENAI_BASE_URL, and OPENAI_MODEL.\n\n"
            f"You asked: {last_user}"
        )
        return ProviderResponse(text=text)


def build_provider_from_env() -> BaseProvider:
    api_key = os.getenv("OPENAI_API_KEY")
    base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com")
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    if api_key:
        return OpenAICompatibleProvider(base_url=base_url, api_key=api_key, model=model)
    return HeuristicProvider()
