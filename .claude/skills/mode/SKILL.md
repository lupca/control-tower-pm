---
name: mode
description: Show or change the control-tower coordination mode used by Spec, Plan, Dispatch, Review-order, and Verdict Gates.
argument-hint: "[plan-only|supervised|bypass]"
allowed-tools: Read, Edit, Write
---

# /mode — inspect or change coordination mode

The canonical state file is `state/mode.md`.

## No argument

1. Read `state/mode.md`.
2. If it contains exactly one supported `mode:` value, print that value.
3. If it is missing or invalid, report `supervised` as the fail-safe effective
   mode and tell the User the state file needs repair. Do not rewrite it during
   a read-only `/mode` call.

## With an argument

1. Accept exactly one of: `plan-only`, `supervised`, `bypass`. If the value is
   unsupported, stop without changing state and show the valid values.
2. Read the current effective mode, using `supervised` if the file is missing or
   invalid.
3. Replace `state/mode.md` with the single YAML mapping
   `mode: <requested-level>`.
4. Append one `mode` entry to `log.md` using `AGENTS-REFERENCE.md` §7. Include
   the previous and new values, rationale `User requested /mode`, files touched
   `state/mode.md, log.md`, and `Commit: n/a`.
5. Report the new mode in one terse sentence.

Changing mode is an explicit User command, so it does not have another Gate.
It never overrides protected-action prompts or the hard
`reviewer == executor` refusal in `AGENTS.md` §4.
