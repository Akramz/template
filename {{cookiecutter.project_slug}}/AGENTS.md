# Agent contract

- Follow existing project patterns; use the root `README.md` as the repository map.
- Treat data and external systems as read-only unless the task explicitly authorizes a write.

## Verification

- Run targeted checks while iterating, then the `verify` skill (`.claude/skills/verify/SKILL.md`) before handoff.
- Do not weaken, skip, mock away, or special-case a check to make it pass.
- Add deterministic tests for fixed regressions and observable behavior: end-to-end, differential, or property tests. No unit tests.
- Report commands actually run, failures, skipped work, and remaining uncertainty.
- Use independent review for high-risk changes.
- Reviews follow `REVIEW.md`.
