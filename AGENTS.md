# AI Agents Masterclass Study Repository

## Repository Purpose

- This repository is a personal study and assignment workspace based on the Nomad Coders AI Agents Masterclass.
- Upstream course repository: `https://github.com/nomadcoders/ai-agents-masterclass.git`
- Local `origin` is the personal implementation repository. Treat the course repository as the reference source, not as the place to commit local assignment work.
- The goal is to clone, understand, extend, and complete assignments from the course while keeping local changes easy to compare against the original lesson.

## Repository Layout

- Keep the existing numbered lesson folder style: `00-topic-name/`, `01-topic-name/`, etc.
- When adding a new course lesson locally, use the next number plus a readable topic name.
- If the upstream folder name differs from the local folder name, record the upstream folder in that lesson's README.

Current lesson mapping:

| Local folder | Upstream folder | Notes |
| --- | --- | --- |
| `00-environment` | environment/setup material | Local environment setup practice |
| `01-your-first-ai-agent` | `my-first-agent` | First OpenAI API and notebook exercises |
| `02-chatgpt-clone` | `chatgpt-clone` | Streamlit ChatGPT clone with tools |
| `03-customer-support-agent` | `customer-support-agent` | OpenAI Agents SDK handoff and guardrails |
| `04-story-book-maker` | related ADK/content pipeline material | Google ADK sequential storybook pipeline |

Recommended upstream remote:

```bash
git remote add upstream https://github.com/nomadcoders/ai-agents-masterclass.git
git fetch upstream
```

Do not run upstream sync commands automatically unless the user asks.

## Assignment Folder Policy

- Put small lesson extensions inside the related lesson: `NN-topic-name/assignments/<assignment-name>/`.
- Use the lesson-local assignment path for refactors, notebook/script variants, prompt changes, guardrail tweaks, and small feature additions.
- Put standalone services or standalone agents at the repository root as their own deployable unit: `assignments/<assignment-name>/` or `NN-assignment-<topic>/`.
- A standalone assignment is anything with its own app boundary, deployment target, `.env`, dependency file, README, or independent verification flow.
- Standalone assignments must include `README.md`, setup instructions, run command, required environment variables, and verification notes.

## Python And Tooling

- This is a Python-first learning repository. Prefer the tooling already used by each lesson.
- Use `uv` inside each lesson folder when a `pyproject.toml` and `uv.lock` are present.
- Do not merge lesson environments into one root environment unless the user explicitly asks.
- Keep generated virtual environments, local `.env` files, Streamlit secrets, runtime DB files, and cache files out of git.
- Do not commit API keys, vector store secrets, session memory databases, or generated credentials.

Common run commands:

```bash
cd 02-chatgpt-clone && uv run streamlit run main.py
cd 03-customer-support-agent && uv run streamlit run main.py
cd 04-story-book-maker && uv run adk web
```

## Implementation Guidelines

- Preserve course intent when cloning a lesson; clearly document any local improvement or assignment-specific deviation.
- Prefer small, explainable changes that are useful for study notes and review.
- For agent work, keep prompts, tool definitions, handoffs, guardrails, and session state easy to inspect.
- For Streamlit apps, verify both import/runtime behavior and the visible user workflow when possible.
- For ADK apps, verify state keys, artifact output, tool behavior, and model/provider assumptions.
- Use structured models such as Pydantic for agent I/O when the surrounding lesson already uses them.
- Avoid hardcoded external IDs unless they are clearly marked as course placeholders or documented setup values.

## Review Guidelines

- Check for leaked secrets, committed `.env` files, Streamlit secrets, runtime DBs, and generated artifacts.
- Check that lesson README files explain the source lesson, local changes, run command, and assignment notes.
- For OpenAI Agents SDK examples, review handoff wiring, guardrails, session isolation, async boundaries, and tool access.
- For Google ADK examples, review state flow, artifact naming, tool idempotency, and provider configuration.
- Treat missing verification steps as a real issue for standalone services and deployable assignments.

