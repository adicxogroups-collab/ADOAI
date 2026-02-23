from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Dict


@dataclass
class ConversationMemory:
    history: List[Dict[str, str]] = field(default_factory=list)

    def add(self, role: str, content: str) -> None:
        self.history.append({"role": role, "content": content})

    def clear(self) -> None:
        self.history.clear()

    def as_messages(self, system_prompt: str) -> List[Dict[str, str]]:
        return [{"role": "system", "content": system_prompt}, *self.history]

    def save(self, path: str | Path) -> None:
        Path(path).write_text(json.dumps(self.history, indent=2), encoding="utf-8")

    def load(self, path: str | Path) -> None:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        if not isinstance(data, list):
            raise ValueError("Conversation file must contain a list of messages")
        self.history = [
            {"role": str(msg.get("role", "user")), "content": str(msg.get("content", ""))}
            for msg in data
            if isinstance(msg, dict)
        ]
