## Workflow & Tooling

### Write-First, Verify-Once
- For educational templates, comments, scaffolds, and docs: author **all** target files first using `write_file`/`edit_file`, then run **one** batched verification pass (`odin check`) at the end and iron out only failing files.
- Limit checks to what the task requires (`odin check`); add standalone test harnesses, manifests, or multi-stage review/audit pipelines only when explicitly requested.

### Repo Scope & Low-Noise Tooling
- Keep every path relative and strictly inside the workspace root.
- Read files with `read_file` and reserve `run_command` for batched compiler checks (`odin check`/`build`/`test`) or single-shot workspace listings rather than per-file shell calls.

## Agent skills

### Issue tracker

Local markdown files under `.scratch/<feature>/`. See `docs/agents/issue-tracker.md`.

### Triage labels

Default canonical triage labels (`needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`). See `docs/agents/triage-labels.md`.

### Domain docs

Single-context (`GLOSSARY.md` and `docs/adr/` at the repo root). See `docs/agents/domain.md`.
