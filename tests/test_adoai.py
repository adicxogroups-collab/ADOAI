from __future__ import annotations

from adoai.assistant import AdoaiAssistant
from adoai.memory import ConversationMemory
from adoai.providers import HeuristicProvider
from adoai.tools import SafeEvaluator


def test_safe_evaluator_math() -> None:
    evaluator = SafeEvaluator()
    assert evaluator.evaluate("2*(3+4)") == 14


def test_assistant_offline_response_contains_prompt_echo() -> None:
    assistant = AdoaiAssistant(provider=HeuristicProvider())
    answer = assistant.ask("Design a launch plan")
    assert "Design a launch plan" in answer


def test_memory_round_trip(tmp_path) -> None:
    memory = ConversationMemory()
    memory.add("user", "hello")
    file_path = tmp_path / "session.json"
    memory.save(file_path)

    restored = ConversationMemory()
    restored.load(file_path)
    assert restored.history[0]["content"] == "hello"
