# Inspector feedback 13 — declaration-side export fixture

Tanggal: 2026-10-25 (Asia/Jakarta)  
Model Inspector: GPT-6 (fallback; dedicated Goal Inspector model unavailable)  
Verdict: **PASS_FOR_DECLARATION_SIDE_FIXTURE_ONLY**

## Verifikasi

Handoff 13 reports the same MSVC 19.42.34435.0 toolchain, x64 `vcvars64.bat`
environment, empty `CL`, and five-root `INCLUDE` used in iterations 11c/12.
The compile command is `/Tp /c` to a scratch `.obj` with `/showIncludes /FC`;
the log confirms the scratch-local header and MSVC `stdint.h`. The TU hash
`DAA2007D...4F7A97` matches the no-export baseline, contains no export
attributes, and places the exact C signatures inside the outer `extern "C"`
block. The scratch header hash `84DE59D8...0DFFA` differs from Pixel's
`9775DB46...BC116`; handoff's reversible-token check says removing exactly
three `__declspec(dllexport)` insertions restores the original text. The
compile exits 0 and emits the reported 976-byte scratch object. Thus the
declaration-side variant compiles while the matched definition-side export
variant from iteration 12 emitted C2375.

The original Pixel header still has no export attributes at lines 49–54, and
the definitions in `taichi_aot_engine.cpp:2054`, `:2112`, and `:2135` still
carry `extern "C" EXPORT`; `EXPORT` is `__declspec(dllexport)` on Windows and
empty elsewhere (`taichi_aot_engine.cpp:27–54`). Handoff 13 reports unchanged
hashes for product source/header, bridge, C API, venv DLL/import library and
manifest. The scratch result did not link, inspect an export table, load a
DLL, compile a TCM, or exercise runtime/ABI behavior.

## Penilaian dan langkah berikutnya

The paired reproducer supports the hypothesis that placing the export
attribute on the declaration, with an unannotated matching definition,
avoids this MSVC C2375. It does **not by itself justify blindly copying the
fixture's unconditional `__declspec(dllexport)` into the public header**:
that header is intended to be C-compatible and the current production export
macro is platform-conditional. A narrowly scoped production correction is now
reasonable to propose, provided it preserves the existing non-Windows and
consumer behavior (for example, a private conditional export macro applied
once at the declaration, with the definition no longer independently
annotated). The edit should remain limited to these three symbols and avoid
changing signatures or ABI layout.

Next gate: after the scoped source change is reviewed, run **one** full CPU
bridge build to a unique external staging directory with the established
Dev4 toolchain and no active artifact replacement. Require successful link,
then inspect the staged PE export table for all three undecorated C names and
record hashes. Stop on any compile/link/export discrepancy; do not load the
DLL or compile/load TCM in that gate. A successful object-only fixture is not
export-table or runtime qualification.

This is a source-level diagnosis and proposed next validation gate only. The
runtime goal remains incomplete; no backend, ABI/runtime, parity, or
performance qualification is claimed.
