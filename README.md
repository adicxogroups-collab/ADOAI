# Adoai

Adoai is a production-ready starter for your own AI assistant with:

- **Configurable identity** (name, mission, style, temperature)
- **Long-form memory** (save/load/reset conversation state)
- **Tooling layer** (calculator, datetime, JSON pretty printer)
- **Pluggable model providers**
  - OpenAI-compatible API mode (`OPENAI_API_KEY` + optional base URL/model)
  - Offline fallback mode (no API key required)

## Quick start

```bash
python3 main.py
```

## Power mode (real model)

```bash
export OPENAI_API_KEY="your_key"
export OPENAI_BASE_URL="https://api.openai.com"   # optional
export OPENAI_MODEL="gpt-4o-mini"                  # optional
python3 main.py
```

## REPL commands

- `/help` – command help
- `/reset` – clear active memory
- `/save ./session.json` – persist memory
- `/load ./session.json` – restore memory
- `/exit` – quit

## Architecture

- `adoai/assistant.py`: orchestration, prompting, tool call parsing
- `adoai/providers.py`: model adapters and env-based provider selection
- `adoai/tools.py`: tool registry and safe calculator
- `adoai/memory.py`: conversation persistence
- `main.py`: interactive CLI

## Notes

- The assistant recognizes tool calls in this XML wrapper:

```xml
<tool_call>{"name":"calculator","args":{"expression":"12/3"}}</tool_call>
```

- You can add your own tools in `build_default_registry()`.
- You can swap provider logic without changing the assistant core.
