# KnitCoach beginner guidance rubric

Evaluate each response against the scenario, not against another model answer.

- `beginner_friendly`: unfamiliar terms are explained or avoided.
- `route_correct`: the response matches the user's current journey.
- `next_action_clear`: the learner can take one concrete next step.
- `uncertainty_honest`: image or pattern details that were not observed are not presented as facts.
- `required_facts_present`: every scenario-specific required fact is present when applicable.
- `forbidden_claims_absent`: none of the scenario-specific forbidden claims appear.

Return one JSON object per scenario with `scenario_id`, the six boolean fields,
`result` (`pass` or `fail`), and a one-sentence `reason`.
