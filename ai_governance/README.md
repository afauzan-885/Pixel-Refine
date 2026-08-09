# Pixel Refine AI Governance

This directory is the Git-tracked, tool-neutral contract for Codex, DeepSeek,
and future AI agents. It complements the local `.qoder/` and `agen-docs/`
directories, which may be ignored by Git and are therefore not sufficient as a
portable source of instructions.

## Document order

1. Instructions supplied by the AI platform or user.
2. `AGENTS.md` in this repository.
3. This directory.
4. Project architecture references: `agen.md`, `skill.md`, and
   `blueprint_project.md`.
5. Task-specific source code, tests, and runtime evidence.

When instructions conflict, follow the higher item and state the conflict.

## Required working contract

- Inspect before editing: current Git status, target source, its imports, and
  its callers.
- Keep each task scoped. Preserve unrelated changes in a dirty worktree.
- Prefer existing helpers and one maintained implementation over duplicate
  wrappers or parallel code paths.
- Treat test output as evidence, not as proof of universal support. State the
  backend, device, input shape, dtype, command, and observed result.
- Never silently turn a requested GPU backend into CPU. If recovery is
  necessary, use the same backend's full-frame/reference route or surface a
  clear error according to the API contract.
- Do not delete source, runtime artifacts, or target-qualified TCM files until
  their references and packaging role have been checked. Caches and compiler
  intermediates may be removed only after their exact paths are verified.
- Before a commit, run the smallest relevant validation and `git diff --check`.
  Stage only the intentional paths; commit messages must describe the scope.

## Taichi AOT work

Use `skills/taichi-aot-dev/SKILL.md` for all AOT compilation, graph/API parity,
backend capability, artifact, and runtime tasks.

## DeepSeek

Use `DEEPSEEK_PROMPT.md` as the initial instruction message for a DeepSeek
session that works on this repository.
