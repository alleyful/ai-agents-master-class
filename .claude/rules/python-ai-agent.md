# Python AI Agent Rules

- Keep lesson-specific dependencies inside that lesson folder.
- Prefer `uv run ...` commands when a lesson has `pyproject.toml` and `uv.lock`.
- Do not expose API keys, Streamlit secrets, vector store IDs that are private, or generated session databases.
- For streaming agents, verify async behavior and UI state updates together.
- For handoff-based agents, verify that the handoff destination, user-facing notice, and context/session state remain consistent.
- For guardrails, verify both allowed and blocked examples.
- For image or artifact generation, document expected output files and whether the command may incur API cost.

