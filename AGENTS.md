# Pixel Refine Agent Entry Point

This file remains the versioned entry point for every AI agent. The complete
project contract is consolidated in [`agen.md`](agen.md); normative governance
remains under `ai_governance/`.

Before changing code, read `ai_governance/README.md`, `agen.md`, `skill.md`,
`blueprint_project.md`, and the relevant Taichi AOT skill. Inspect the target,
callers, configuration, tests, and Git status. For multi-agent work, follow
`ai_governance/MULTI_AGENT_PROTOCOL.md` and launch agents only with explicit
approval and a user-provided limit.

The consolidated barriers are: preserve public API compatibility; treat
`taichi_library/taichi_aot/engine.py` as runtime source of truth; recover an
unvalidated block path through same-backend full-frame or report an error; and
make no backend, accuracy, performance, or production claim without
reproducible evidence. Do not stage unrelated changes or use `git add -A`.
