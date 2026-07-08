---
description: Review a local lesson against the Nomad Coders AI Agents Masterclass source and summarize local changes, assignment work, run commands, and remaining risks.
---

# Lesson Sync Review

Use this skill when the user asks to compare a lesson with the course source, summarize what changed, prepare study notes, or review a lesson folder.

## Steps

1. Identify the local lesson folder and its upstream source folder from `AGENTS.md`.
2. Read the lesson README, `pyproject.toml`, key entrypoints, and assignment notes if present.
3. If upstream access is needed, ask before fetching or syncing. Do not mutate remotes or local files during review unless explicitly asked.
4. Summarize:
   - source lesson and local folder
   - main agent/app behavior
   - local deviations from the course
   - assignment files and purpose
   - run command and environment variables
   - risks or missing verification
5. Keep the summary study-friendly and actionable.

## Output

Return concise sections: `Source`, `Local Behavior`, `Local Changes`, `Assignments`, `Run`, and `Risks`.

