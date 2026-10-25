# Inspector feedback 15 — isolated CPU Gaussian TCM compile

Tanggal: 2026-10-25 (Asia/Jakarta)  
Model Inspector: GPT-6 (fallback; dedicated Goal Inspector model unavailable)  
Verdict: **PASS_FOR_STAGED_CPU_COMPILE_ONLY**

## Command, target, metrics, and isolation

I reviewed the exact invocation in Builder handoff 15. It uses
`E:\APP Developer\Eel-Dance\Pixel-Refine\venv\Scripts\python.exe` and
`compile_aot_backend_suite.py --target cpu_x86_64_windows --only gaussian
--with-tcm-manifest --tcm-compiler-version
taichi-1.7.4.dev4+LLVM20.1.5`. `PIXEL_REFINE_AOT_TCM_ROOT` points to the new
external `D:\temp\pixel_refine_dev4_runtime_qualification_20261025_7ab5e244_iter15_cpu_tcm\artifacts`
root; the report directory is a sibling under the same unique scratch parent.
Both output roots were absent before the run. Exit code is 0, console reports
`[PASS] gaussian`, and `gaussian:artifact_missing` confirms a fresh compile
rather than cache reuse. Target manifest has one exact matching row:
Windows/CPU/x86_64/unknown vendor, and the registry selector is
`cpu_x86_64_windows`.

The actual schema-1 report
`.aot_compile_reports/compile-1792903933661068400.json` has SHA-256
`CD1F39DE63D947CA7E9459FA1F87522A96F5E2AC14D3D1396FDDF0D46E0CC5CB`. It
records run total 29.387746 s (preflight 10.282027 s; worker wall 19.104632 s)
and schema-2 worker metrics: compiler-call 11.723228 s, module-import
1.216018 s, Taichi import 1.150220 s, fingerprint 3.476238 s, manifest
0.085867 s, payload validation 0.014906 s, normalization 0.030466 s,
promotion 0.000616 s, post-promotion integrity 0.005686 s, inventory
0.000604 s, provenance 0.005375 s, worker total 18.487573 s. The report
labels the module-import boundary precisely; it excludes context import,
Taichi import, and architecture/package selection. Backend-init,
frontend-lowering, backend-codegen, archive, and per-graph timings are null
with explicit reasons. Native-context import is also null for CPU. Graph,
dispatch-node, and kernel counts are null because inventory is unavailable;
they must remain unknown, not inferred from the archive.

## TCM manifest, provenance, and payloads

The only staged `.tcm` is
`artifacts/cpu_x86_64_windows/gaussian_cpu_x86_64_windows.tcm`, 81,543 bytes,
SHA-256 `C80DBE770578D144DD6E89494DB9E37710C33EA10C5BCB966018BAA1558E1A7B`.
Its sidecar SHA-256 is
`766AF4A3007BD35E2AE9F81EA1836D999F8FC45B3CE164662E648E411989B788` and
matches artifact size/hash. Embedded manifest is `PIXEL_REFINE_TCM`, schema
1, format 1, minimum runtime ABI 1, exact CPU/x86_64/Windows target, and has
no required runtime features. The sidecar source fingerprint is
`6b51946d1ee8b38caf4965c46b8fc111a97a1208baabd9d1b3f77ed9c70980bc`; its
target-manifest hash is the checked-in manifest SHA
`485A813D70768435D78C0B596EE874D2577516C7DDB2C102AE7ED68B1C2323E3`.
The contract validator accepted the manifest for the requested target.

I independently opened the scratch archive read-only and recomputed each
LLVM payload's size and SHA-256 against `tcm_manifest.json`: all 8/8 match.
The archive has 15 entries and an 81,543-byte normalized payload. The
manifest's `kernels` list is empty. The contract permits an empty list, and
the report correctly leaves graph/kernel inventory unknown; the presence of
`graphs.tcb` and LLVM files does not give me a graph-name/count claim. The
compiler identity `taichi-1.7.4.dev4+LLVM20.1.5` is the supplied manifest
label; handoff confirms Taichi metadata's LLVM major version 20 but says minor
and patch were not independently queried. Treat `20.1.5` as an unverified
label, not established runtime provenance.

The six compile warnings are three channel assignments in each of the
horizontal and vertical 3-channel `i32` kernels: `f32` accumulators assigned
to `i32` destinations at `gaussian.py:46–48` and `:94–96`. They establish a
potentially lossy conversion path in those integer specializations. They do
not establish the observed error, its size, or behavior on any input; compile
success is not accuracy evidence. No parity or accuracy claim is made here.

## No-mutation and verdict limits

Preflight/postflight report the canonical TCM inventory unchanged at 1,694
files / 74,689,912 bytes and metadata fingerprint
`2F0045FF8FD4E36D01DCC622463A5FEA656961F9AEF188073DF7AE75002B3A8A`.
Recorded hashes for the manifest, compiler/registry/contract sources,
committed bridge source/header, active and packaged bridges/C APIs, venv
Dev4 DLL/import library/headers, and wheel metadata are identical before and
after. The only current Git status entries are pre-existing unrelated user
changes; this compile added no repository artifact. No bridge DLL was loaded,
no runtime smoke/parity or GPU work occurred, and no production TCM was
replaced.

This passes the staged CPU `gaussian` compile/provenance gate only. It does
not qualify runtime ABI, application execution, parity, accuracy, performance,
or any other backend.

## Next bounded runtime gate

The next step may be one fresh-process, CPU-only Gaussian smoke using the
already staged pair from iteration 14 and the iteration-15 TCM. Before the
process, recheck hashes and set `AOT_ENGINE_DLL` to the iteration-14
`bridge/cpu/taichi_aot_engine_baseline.dll` (with its adjacent matching
`taichi_c_api.dll`) and `PIXEL_REFINE_AOT_TCM_ROOT` to the iteration-15
`artifacts` directory. Load only the exact target-matched Gaussian TCM; do
not consult or modify the canonical TCM tree. Exercise one documented
float32 Gaussian graph on CPU in a clean process, with fixed shape/dtype,
sigma, kernel size, exact command, and NumPy/OpenCV reference. Capture the
actual backend/device, load/graph result, output hash, max/mean error and
tolerance, plus bridge/C API/TCM/source hashes. Because of the integer-kernel
warnings, do not use this float32 smoke to claim `i32` parity. Stop on a load,
target, dependency, or graph error; no fallback backend, retry, DLL/TCM
promotion, or additional operation is covered by this gate.

The runtime goal remains incomplete pending that separately bounded smoke,
parity, broader C2/C5 target coverage, and remaining acceptance criteria.
