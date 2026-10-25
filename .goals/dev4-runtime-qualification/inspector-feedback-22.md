# Inspector feedback 22 — CUDA bridge and Gaussian TCM compile

Tanggal: 2026-10-25 (Asia/Jakarta)  
Model Inspector: GPT-6 (fallback; dedicated Goal Inspector model unavailable)  
Verdict: **PASS_FOR_CUDA_STATIC_BRIDGE_AND_COMPILE_ONLY**

## CUDA bridge static gate

I inspected the staged bridge build logs and saved `dumpbin` reports. The
`cuda baseline` build has exit record `0`, ends with `Finished generating
code`, and has empty stderr. The staged bridge SHA-256 is
`2B4068BA92093635023635B0887A3492B9BF4B6A9C37DBF9BC9CBC05FE3E2462` (451,584
bytes); its adjacent Dev4 `taichi_c_api.dll` is
`B29073835F7496B5A08307ADF7C088651FC17A14BF469C46319D3C50F213CBCF` and
matches the venv DLL. Static PE header reports AMD64/PE32+. The bridge exports
the memory-control C names plus `init_aot_engine`/`load_aot_module`; its 16
imports from `taichi_c_api.dll` all appear in the paired 809-name C API export
listing (I independently compared the names; 0 missing). This is PE/name
closure only, not runtime ABI or CUDA driver compatibility.

## CUDA Gaussian compile and archive

The one compile command used the project venv for exact target
`cuda_x86_64_windows_nvidia`, job `gaussian`, with manifest attachment and
`PIXEL_REFINE_AOT_TCM_ROOT` set to the new external iter22 artifact root.
The report is 8,227 bytes, SHA-256
`172FFB579E307C3F6903EBF71608D375DFCF5E3CCA7D0D5BC13422A23F48763A`; it
reports `status=compiled`, `gaussian:artifact_missing`, run total 34.382568
s, and worker total 28.777493 s. The worker schema-2 metric boundaries and
null/unavailable backend-init, lowering, codegen, archive, and per-graph
phases are explicitly recorded. Inventory shows 15 archive entries, eight
LLVM payloads, no SPIR-V payloads, 173,454 artifact bytes and 1,073,764
uncompressed bytes; graph/kernel/dispatch counts are null because there is no
`graphs.json`.

The child compile exit file contains numeric `0`, and stdout reports
`[PASS] gaussian`; stderr is empty. The bridge build's `bridge.exit.txt` also
contains `0`. I found no separate wrapper-exit artifact, so I rely on the
recorded child statuses and output/report rather than claim an independently
captured outer wrapper status.

The only staged TCM is `gaussian_cuda_x86_64_windows_nvidia.tcm`, 173,454
bytes, SHA-256
`4B80591E0E4F597EB63BFFE11BAA9FD70729630FD36F9BD2C06D4151B582469F`. Its
sidecar SHA-256 is
`A18315B5358A5C2E065362EDF37749F1055513B1B4471ECC1C5A7CC6D8FD5C4D` and its
artifact size/hash match. The embedded manifest is `PIXEL_REFINE_TCM`, schema
1, TCM format 1, minimum runtime ABI 1, target Windows/x86_64/CUDA/NVIDIA,
with no required features. I independently opened the archive and verified
all eight LLVM payload sizes and hashes against the manifest; all eight
declare `nvptx64-nvidia-cuda`. The payload identity and TCM manifest validate
the static target envelope, not execution on a particular GPU.

## Warnings, device identity, and isolation

The report tail records six Taichi warnings: the two 3-channel integer
Gaussian passes assign `f32` accumulators to `i32` destinations at
`gaussian.py:46–48` and `:94–96`. This is a potentially lossy conversion
path, not an observed error measurement; compile success proves no accuracy
claim.

The worker does not report GPU name, ordinal, or CUDA runtime identity.
`CUDA_DEVICE=0`, `AOT_DEVICE=0`, and NVIDIA target variables are requested
configuration/provenance only. Although prior host inventory reported an
MX150, I do **not** infer that this compile used that GPU. The target is
NVIDIA-qualified because the manifest/toolchain requires it, but actual
compiler device is unknown/unverified.

The artifact/report roots are external. I rechecked the canonical TCM tree
at 1,694 files / 74,689,912 bytes and current hashes for the active bridge,
packaged CPU/CUDA bridge and C APIs, target manifest, and staged inputs;
they match the recorded identities. Git status contains only the existing
unrelated user changes. No CUDA bridge/C API/TCM was loaded; no runtime,
graph, parity, or performance test occurred. No source or production
artifact changed; this review was read-only.

## Next bounded gate

After separate coordinator approval, use one fresh-process staged CUDA
device/init preflight before attempting TCM load: preload the iter22 staged
Dev4 C API, select `cuda_x86_64_windows_nvidia` with explicit device 0, and
verify the actual CUDA renderer/name and compute capability, bridge/C API
Win32 loaded paths and hashes, and absence of CPU fallback. Keep all paths
in scratch and capture stdout/stderr/child exit separately. If the selected
device is not a real NVIDIA GPU or any identity/target check differs, stop
without loading the TCM. If init and ABI preflight pass, a separately
reviewed one-case float32 Gaussian smoke may use the iter22 staged bridge,
C API, and CUDA TCM against OpenCV; capture actual device, resolver path,
output hashes, max/mean error and tolerance. Do not test or claim the
warning-affected `i32` paths from that float32 case, infer the compile device
from runtime device identity, retry, or promote artifacts.

This passes one CUDA bridge static gate and one CUDA-target Gaussian compile
artifact gate only. It does not qualify CUDA runtime, device-specific
compilation, graph execution, parity, performance, or production readiness.
