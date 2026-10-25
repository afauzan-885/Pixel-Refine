# Inspector feedback 19 — generic Vulkan Gaussian TCM compile

Tanggal: 2026-10-25 (Asia/Jakarta)  
Model Inspector: GPT-6 (fallback; dedicated Goal Inspector model unavailable)  
Verdict: **PASS_FOR_VULKAN_COMPILE_ARTIFACT_ONLY**

## Command, target, and C2 evidence

The recorded command uses the project venv and one exact job:
`compile_aot_backend_suite.py --target vulkan_x86_64_windows --only gaussian
--with-tcm-manifest --tcm-compiler-version
taichi-1.7.4.dev4+LLVM20.1.5`. `PIXEL_REFINE_AOT_TCM_ROOT` is the new external
iter19 `artifacts` directory and the report is in its sibling
`.aot_compile_reports`; both were absent before invocation. `AOT_DEVICE=0`
and Intel vendor variables express selection intent only. The exact profile
is the manifest's generic Windows/x86_64/Vulkan row with `vendor=unknown`.

The report `compile-1792907103400616600.json` is 8,229 bytes, SHA-256
`56D7C49A272B7E5555843C3AD221C4C1C4B1D4613F95E7436BA2CAC370E146C5`. It
reports backend Vulkan, target `vulkan_x86_64_windows`, job `gaussian`,
`status=compiled`, cache reason `gaussian:artifact_missing`, run total
25.541729 s and worker wall 22.724808 s. Worker schema-2 metrics include
module import 1.242058 s, compiler call 13.691600 s, Taichi import 1.558823
s, fingerprint 2.564499 s, manifest 0.208145 s, payload validation
0.042526 s, normalization 0.205101 s, promotion 0.001305 s,
post-promotion integrity 0.015401 s, inventory 0.001563 s, provenance
0.011171 s, and worker total 21.214275 s. The report describes the module
import boundary and leaves native-context import, backend init, lowering,
codegen, archive, and per-graph timings null with reasons. The inventory
reports 8 graphs, dispatch nodes, and kernels; 16 SPIR-V payloads; and zero
LLVM payloads. These are compile/inventory facts, not execution evidence.

The wrapper's `compile.exit.txt` is empty, so a child process exit code is
unavailable. The captured stdout contains `[PASS] gaussian` and the metrics
report path; the report status is `compiled`, and the staged artifact plus
validated manifest exist. Those independent artifacts support accepting the
compile result, but I do not claim a recorded exit code of zero. Device name
and renderer are not reported by the worker. The prior iter18 init process
selected Intel UHD 620 ordinal 0, but that separate invocation does not prove
which device the iter19 compiler process used. Keep the device of compilation
unknown/unverified.

## Archive, ABI, and warnings

The scratch archive is
`artifacts/vulkan_x86_64_windows/gaussian_vulkan_x86_64_windows.tcm`, 157,804
bytes, SHA-256
`B7888052FCF05C0FB3622E70C7B9744164D9193AFDDFB2AD655AD360BCEB92BA`. Its
sidecar is SHA-256
`1F970F076D3FC6E35E3BB885D7C603E1A7C8FA931EE5CC5C9FC99B4CAA346374` and
records matching artifact size/hash, build fingerprint, target-manifest
hash, source/toolchain fingerprints, and `aot_device=0`. The embedded
manifest is `PIXEL_REFINE_TCM`, schema 1, TCM format 1, minimum runtime ABI 1,
target Windows/x86_64/Vulkan/vendor unknown, and required features
`COMPUTE`/`SSBO`. I independently read the archive and recomputed size and
SHA-256 for all 16 SPIR-V manifest payloads: 16/16 match. `graphs.json`
contains 8 graphs. The manifest's `kernels` list is empty; the report does
provide graph/kernel inventory from `graphs.json`, but no kernel metadata is
inferred from the manifest. Target and payload validation are static; no
runtime ABI interaction was tested.

The six warnings are assignments from `f32` accumulators to `i32` output
channels in the 3-channel horizontal/vertical Gaussian integer kernels at
`gaussian.py:46–48` and `:94–96`. The warnings are explicitly present in the
captured report tail. They identify a potentially lossy conversion path, not
an observed error magnitude or an accuracy result. No parity or accuracy
claim is supported.

## Isolation and scope limits

I independently checked the current canonical TCM tree: 1,694 files and
74,689,912 bytes, matching the recorded baseline. The target manifest,
compiler suite, target registry, TCM contract, active bridge, packaged CPU /
Vulkan bridges and C APIs still match the recorded hashes. Git status shows
only pre-existing unrelated user changes. The output root is external; no
TCM was loaded, no graph dispatched, and no parity test run. This passes the
generic Vulkan Gaussian compile and static archive gate only. It is not
device-specific compilation proof, runtime ABI/load proof, GPU execution,
parity, performance, or application qualification.

## Next bounded gate

After a separate coordinator approval, run one fresh-process, staged Vulkan
Gaussian runtime smoke using the iter18 Vulkan bridge/C API pair and iter19
TCM. Before any load, verify bridge/C API/TCM hashes, use explicit
`AOT_DEVICE=0` plus Intel selection, require the initialized renderer to be
Intel UHD 620, and require resolver target/root/path to match the generic
`vulkan_x86_64_windows` manifest and iter19 scratch artifact. The compile
device remains unknown; the runtime must report its own actual device. Use
the isolated Intel probe/compatibility settings only as explicit test
conditions, and retain the known native-destructor skip as a lifecycle limit.
If selection, path, ABI preflight, or artifact validation differs, stop
before load/dispatch. If all gates pass, execute one float32 single-channel
Gaussian case against the same OpenCV `BORDER_REFLECT_101` reference and
capture exact input/output hashes, shape/dtype, tolerance and error metrics.
Do not exercise or claim the warning-affected `i32` kernels in that case; no
fallback device, retry, promotion, or broader GPU qualification is included.
