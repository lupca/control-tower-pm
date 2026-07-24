# Review Toolchain Convention

Each repo can define a `.claude/review-toolchain.md` file to specify its review pipeline. This file tells reviewers which tools to run (beyond the basic `/code-review`) before verifying AC items.

## Purpose

- Centralizes the review tool list for a repo — reviewers don't need to know which linters/analyzers are installed.
- OCR and other static-analysis tools auto-detect changed files from the git range, so no manual file selection.
- Tests are NOT part of the toolchain — they're already in the review sheet's `## Test gợi ý` section and the task's `tests:` field.

## Template

Create `.claude/review-toolchain.md` in your repo:

```markdown
# Review Toolchain

Run these tools before verifying AC items.

## Tools

1. **OCR Review**
   ```bash
   ocr review --from main --to $RESULT_REF --format json
   ```
   OCR auto-detects changed files from the git range.

2. **Linter** (if applicable)
   ```bash
   npm run lint -- --files <changed files>
   # or: ruff check <changed files>
   ```

## Aggregation

- Run all tools, collect findings.
- Map findings to AC items where relevant.
- Include tool output in the verdict report.
```

## Fallback

If a repo has no `.claude/review-toolchain.md`, reviewers use `/code-review` as the default.

## What NOT to include

- Test commands (`pytest`, `npm test`) — these belong in `## Test gợi ý` of the review sheet, not the toolchain.
- Build commands — reviewers shouldn't need to rebuild.
- Deployment steps — out of scope for review.

## OCR Integration

OCR is the primary tool in most toolchains:

```bash
ocr review --from main --to $RESULT_REF --format json
```

Where `$RESULT_REF` is the branch/commit/PR being reviewed (from the review sheet's `result_ref`). OCR scans only changed files between `main` and the result ref — no need to specify paths manually.
