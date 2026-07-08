---
name: streamlit-agent-verify
description: Verify Streamlit-based AI agent lessons or assignments, including imports, environment setup, app launch command, chat flow, tools, and session behavior.
---

# Streamlit Agent Verification

Use this skill for Streamlit AI apps such as `02-chatgpt-clone`, `03-customer-support-agent`, or standalone Streamlit assignments.

## Checklist

1. Confirm the app folder, `pyproject.toml`, and entrypoint.
2. Check required environment variables and whether `.env.example` or README instructions exist.
3. Run syntax/import checks when possible without spending API credits.
4. Launch with the lesson's documented command, usually:

   ```bash
   uv run streamlit run main.py
   ```

5. Verify visible behavior:
   - initial UI renders
   - chat input works
   - streaming text updates correctly
   - tool status messages are understandable
   - reset/session controls do not mix users or stale memory
6. For agent handoffs, verify the user-facing notice and final agent state.
7. For guardrails, test one allowed input and one blocked input.

## Output

Report `Passed`, `Failed`, `Skipped`, and `Follow-up` items. Mention when API keys or paid model calls prevented full verification.

