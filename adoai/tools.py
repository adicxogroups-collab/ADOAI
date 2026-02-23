from __future__ import annotations

import ast
import datetime as dt
import json
import math
from dataclasses import dataclass
from typing import Callable, Dict, Any


class SafeEvaluator(ast.NodeVisitor):
    """A safe arithmetic evaluator used by the calculator tool."""

    ALLOWED_NODES = (
        ast.Expression,
        ast.BinOp,
        ast.UnaryOp,
        ast.Num,
        ast.Constant,
        ast.Add,
        ast.Sub,
        ast.Mult,
        ast.Div,
        ast.Mod,
        ast.Pow,
        ast.FloorDiv,
        ast.USub,
        ast.UAdd,
        ast.Load,
        ast.Call,
        ast.Name,
    )

    ALLOWED_FUNCTIONS = {
        "sqrt": math.sqrt,
        "sin": math.sin,
        "cos": math.cos,
        "tan": math.tan,
        "log": math.log,
        "log10": math.log10,
        "exp": math.exp,
        "abs": abs,
        "round": round,
    }

    def evaluate(self, expression: str) -> float:
        node = ast.parse(expression, mode="eval")
        self.visit(node)
        return eval(compile(node, "<calculator>", "eval"), {"__builtins__": {}}, self.ALLOWED_FUNCTIONS)

    def generic_visit(self, node: ast.AST) -> None:
        if not isinstance(node, self.ALLOWED_NODES):
            raise ValueError(f"Unsupported expression component: {type(node).__name__}")
        super().generic_visit(node)


@dataclass
class Tool:
    name: str
    description: str
    fn: Callable[[Dict[str, Any]], str]


class ToolRegistry:
    """Simple tool container with JSON schema-ish descriptions for prompting."""

    def __init__(self) -> None:
        self._tools: Dict[str, Tool] = {}

    def register(self, tool: Tool) -> None:
        self._tools[tool.name] = tool

    def call(self, name: str, args: Dict[str, Any]) -> str:
        if name not in self._tools:
            return f"Tool '{name}' is not available."
        try:
            return self._tools[name].fn(args)
        except Exception as exc:  # noqa: BLE001
            return f"Tool '{name}' failed: {exc}"

    def prompt_manifest(self) -> str:
        payload = {k: v.description for k, v in self._tools.items()}
        return json.dumps(payload, indent=2)


def build_default_registry() -> ToolRegistry:
    registry = ToolRegistry()
    evaluator = SafeEvaluator()

    registry.register(
        Tool(
            name="calculator",
            description="Evaluate arithmetic. Args: {'expression': '2*(4+5)'}",
            fn=lambda args: str(evaluator.evaluate(str(args.get("expression", "0")))),
        )
    )

    registry.register(
        Tool(
            name="datetime",
            description="Get current UTC time. Args: {}",
            fn=lambda _args: dt.datetime.now(dt.UTC).isoformat(),
        )
    )

    registry.register(
        Tool(
            name="echo_json",
            description="Pretty-print any JSON object. Args: {'payload': {...}}",
            fn=lambda args: json.dumps(args.get("payload", {}), indent=2),
        )
    )

    return registry
