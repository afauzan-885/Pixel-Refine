# Taichi Library

Taichi Library is the AOT algorithm and native-runtime layer used by Pixel
Refine. Start with the [`documentation/`](documentation/) folder.

## Start here

1. [`documentation/README.md`](documentation/README.md) — documentation map.
2. [`documentation/API_USAGE.md`](documentation/API_USAGE.md) — backend
   selection and public API calls.
3. [`documentation/ARCHITECTURE.md`](documentation/ARCHITECTURE.md) — runtime
   architecture, data flow, cache, memory, and block planner.
4. [`documentation/ALGORITHM_STATUS.md`](documentation/ALGORITHM_STATUS.md) —
   algorithm status and unfinished-work markers.
5. [`documentation/BUILD_AND_VALIDATION.md`](documentation/BUILD_AND_VALIDATION.md)
   — TCM build, ABI validation, parity, and runtime evidence.
6. [`AOT_BACKEND_MATRIX.md`](AOT_BACKEND_MATRIX.md) — canonical backend contract.

The algorithm source tree intentionally contains no duplicate documentation;
all usage, architecture, status, and build guidance is centralized under
`documentation/`.
