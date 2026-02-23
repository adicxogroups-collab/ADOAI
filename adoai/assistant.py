from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Dict, Any

from .memory import ConversationMemory
from .providers import build_provider_from_env, BaseProvider
from .tools import build_default_registry, ToolRegistry


TOOL_PATTERN = re.compile(r"<tool_call>\s*(\{.*?\})\s*</tool_call>", re.DOTALL)


@dataclass
class AssistantConfig:
    name: str = "Adoai"
    mission: str = (
        "Deliver elite assistant quality: precise reasoning, clear communication, actionable outputs, "
        "and relentless user-focus."
    )
    style: str = "confident, practical, and concise"
    temperature: float = 0.3


class AdoaiAssistant:
    def __init__(
        self,
        config: AssistantConfig | None = None,
        provider: BaseProvider | None = None,
        memory: ConversationMemory | None = None,
        tools: ToolRegistry | None = None,
    ) -> None:
        self.config = config or AssistantConfig()
        self.provider = provider or build_provider_from_env()
        self.memory = memory or ConversationMemory()
        self.tools = tools or build_default_registry()

    def system_prompt(self) -> str:
        return (
            f"You are {self.config.name}, an advanced AI assistant. Mission: {self.config.mission}. "
            f"Response style: {self.config.style}.\n"
            "When useful, you may request a tool call using XML format:\n"
            "<tool_call>{\"name\":\"calculator\",\"args\":{\"expression\":\"2+2\"}}</tool_call>\n"
            "Available tools:\n"
            f"{self.tools.prompt_manifest()}\n"
            "If a tool is called, incorporate its result into your final answer."
        )

    def ask(self, user_text: str) -> str:
        self.memory.add("user", user_text)
        response = self.provider.chat(
            self.memory.as_messages(self.system_prompt()),
            temperature=self.config.temperature,
        ).text

        final = self._resolve_tool_calls(response)
        self.memory.add("assistant", final)
        return final

    def _resolve_tool_calls(self, response_text: str) -> str:
        matches = TOOL_PATTERN.findall(response_text)
        if not matches:
            return response_text

        augmented = response_text
        for raw in matches:
            try:
                payload: Dict[str, Any] = json.loads(raw)
                tool_name = str(payload.get("name", ""))
                args = payload.get("args", {})
                if not isinstance(args, dict):
                    args = {"value": args}
                result = self.tools.call(tool_name, args)
            except Exception as exc:  # noqa: BLE001
                result = f"Tool parsing failed: {exc}"
            augmented += f"\n\n[tool_result:{result}]"
        return augmented
