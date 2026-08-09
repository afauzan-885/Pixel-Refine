# Pixel Refine Agent Entry Point

This file is the versioned entry point for every AI agent working in this
repository. Platform/system instructions always take precedence.

Before changing code:

1. Read `ai_governance/README.md`.
2. Read the relevant project documents in `agen.md`, `skill.md`, and
   `blueprint_project.md`.
3. For Taichi AOT, read
   `ai_governance/skills/taichi-aot-dev/SKILL.md`.
4. Inspect the target file, callers, and current Git status before editing.

Non-negotiable project barriers:

- Keep public Taichi APIs backward compatible unless the user explicitly
  authorizes an API change.
- Treat `taichi_library/taichi_aot/engine.py` as the runtime source of truth;
  do not change it without explicit approval.
- Preserve correctness over speed. An unvalidated block path must use its
  established same-backend full-frame path, never silently substitute CPU.
- Do not stage or commit unrelated dirty-worktree changes. Avoid `git add -A`.
- Do not claim backend, performance, or accuracy support without a reproducible
  command and observed result.
