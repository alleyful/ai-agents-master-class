---
name: assignment-scaffold
description: Plan or create the correct folder structure for a study assignment, choosing between lesson-local assignments and standalone deployable agent services.
---

# Assignment Scaffold

Use this skill when the user receives a new study assignment or asks where/how to create assignment files.

## Classification

- Use `NN-topic-name/assignments/<assignment-name>/` for small lesson extensions, prompt changes, refactors, notebook variants, guardrail tweaks, or feature additions tied to one lesson.
- Use `assignments/<assignment-name>/` or `NN-assignment-<topic>/` for standalone services, deployable apps, independent agents, or projects with their own dependencies, `.env`, README, and verification flow.

## Required Outputs

For lesson-local assignments:

- assignment README with goal, source lesson, run command, and verification notes
- implementation files close to the related lesson context

For standalone assignments:

- self-contained `README.md`
- dependency file such as `pyproject.toml` when needed
- `.env.example` when environment variables are required
- explicit run and verification commands
- notes linking back to relevant course lesson folders

## Rule

If the assignment can be deployed or demoed as its own app, treat it as standalone.

