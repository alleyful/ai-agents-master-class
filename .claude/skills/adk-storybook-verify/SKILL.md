---
description: Verify Google ADK storybook or content-pipeline agents, including ADK Web launch, state output, tool execution, and generated artifacts.
---

# ADK Storybook Verification

Use this skill for `04-story-book-maker` or standalone Google ADK assignments.

## Checklist

1. Confirm the ADK app package and `root_agent`.
2. Check model/provider configuration and required environment variables.
3. Verify structured output schemas and `output_key` state flow.
4. Launch from the ADK project folder:

   ```bash
   uv run adk web
   ```

5. In ADK Web, send a simple Korean story theme.
6. Verify:
   - state contains `story_book`
   - story has title, theme, and 5 pages
   - each page has text and visual description
   - artifacts are saved as predictable image files
   - reruns do not duplicate existing artifacts unexpectedly
7. Record whether image generation may incur API cost.

## Output

Report setup, state, artifact, and cost-related findings separately.

