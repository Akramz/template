---
name: verify
description: Check that this project works end to end, not only that its tests pass. Use before you call a change done, and when asked to verify.
---

# Verify

1. Run `make verify` (lint, types, tests, security). It must pass in under 30 seconds.
2. Run each flow below on small real inputs and compare the result with "Expect". Save the
   evidence (a figure, a table, a log) to `artifacts/verify/`.
3. Report each flow as pass or fail, with its evidence path. Show the user one figure when it fits.

## Flows

<!-- Propose flows from README.md and ROADMAP.md; the user edits them. Keep 1 to 5. -->

- **Main run**: `<command>` → Expect: `<what a person would check>` → Evidence: `<path>`

## Keep this file useful

- If a bug gets past these flows, add the flow that would have caught it.
- Remove a flow that never fails and costs time.
