# Inspector feedback 20 — Vulkan smoke harness bootstrap failure

Tanggal: 2026-10-25 (Asia/Jakarta)  
Model Inspector: GPT-6 (fallback; dedicated Goal Inspector model unavailable)  
Verdict: **PASS_FOR_ONE_CORRECTED_RETRY_ONLY**

## Invocation result and safety

I read the iter20 scratch script, runner, stdout, stderr, and exit file. The
script imports `taichi_vision.device_selection` before adding the Pixel Refine
root to `sys.path`, so Python stops with `ModuleNotFoundError` at the first
import. The traceback confirms it stops before `scan_vulkan_device_records`,
staged C API preload, AOT facade/engine import, bridge load, TCM resolver or
graph. The staged identity checks also occur only after the scan, so they did
not run in this attempt. This is a harness bootstrap failure, not evidence
for or against Vulkan runtime support.

The runner's exit file contains the literal `ECHO is off.` rather than a
numeric child code. Its stdout contains only the traceback/error JSON and its
stderr is empty. The child result is clearly a Python import failure, but the
recorded status is malformed and must not be reported as a valid numeric exit
code. There was no native load, TCM materialization, graph, or parity result.

I independently rehashed the staged inputs: iter18 Vulkan bridge
`644F3111DF639AD4D96846BC4FCBFB49677E35F9ECC9D0DE512CD64DDEC2E1DC`, Dev4
C API `B29073835F7496B5A08307ADF7C088651FC17A14BF469C46319D3C50F213CBCF`,
and iter19 Vulkan Gaussian TCM
`B7888052FCF05C0FB3622E70C7B9744164D9193AFDDFB2AD655AD360BCEB92BA`. The
canonical TCM tree remains 1,694 files / 74,689,912 bytes. Current Git status
contains only pre-existing user changes. No source, production artifact,
venv, canonical TCM, or goal status was changed by the failed attempt or this
Inspector.

## Target mapping and retry decision

Read-only source review confirms the vendor-unknown Vulkan manifest target
can resolve for an Intel `TargetSpec` when Vulkan backend, x86_64 architecture,
and Windows OS match. `TargetSpec` forms a vendor-qualified runtime ID for
Intel, while `resolve_artifact` tries the equivalent vendor-neutral Vulkan
candidate; it validates the archive target/payload rather than silently
switching backend. The iter19 TCM is explicitly generic Vulkan with
`COMPUTE`/`SSBO` requirements. This mapping supports the intended staged
Intel runtime smoke, subject to the script asserting the resolver returns
the exact iter19 generic artifact and ABI preflight passes before dispatch.

The corrected invocation is safe to approve once because this attempt ended
before the first native or AOT import and made no artifact mutation. The
current goal and coordinator memory allow the controlled correction/retry;
the retry must preserve the same staged bridge, C API, TCM, Intel-only
selection and stop conditions. Do not widen the scope or repeat after this
single corrected attempt.

## Required constraints for the corrected attempt

1. In `smoke_vulkan_gaussian.py`, insert the exact repo root at `sys.path[0]`
   **before** importing `taichi_vision.device_selection`. Keep the fresh
   `scan_vulkan_device_records(fresh=True)` before importing the AOT facade.
   Select only a native, non-translation Intel record; set both device
   variables from that record's ordinal and log the complete scan and
   selection.
2. Preserve the existing iter18 bridge/C API and iter19 TCM paths and hashes,
   `TI_LIB_DIR`, Intel probe/unsafe flags, Vulkan-only selection, and disabled
   translation/fallback settings. Recheck sizes/hashes before preload. After
   AOT initialization verify the actual renderer/vendor/ordinal and Win32
   bridge/C API module paths and hashes. Before any graph, require ABI
   preflight success and resolver target/root/path exactly compatible with
   `vulkan_x86_64_windows` and the iter19 artifact. If any identity differs,
   stop before TCM load/dispatch.
3. Repair the runner so stdout, stderr, and the child Python exit code are
   captured independently. Prefer a `ProcessStartInfo`/`Process` wrapper with
   both streams redirected and use its numeric `ExitCode`; alternatively
   correct the batch expansion and verify `python-exit-code.txt` contains
   only a decimal status. Propagate that status to the outer command. Never
   interpret `ECHO is off.` as an exit code.
4. If all checks pass, perform only the existing single float32 Gaussian
   input and OpenCV `BORDER_REFLECT_101` comparison. Capture shape/dtype,
   hashes, max/mean error, tolerance, actual renderer, target, and loaded
   paths. Retain the iter18 Intel compatibility mode and skipped native
   destructor as explicit limitations; do not claim normal lifecycle safety,
   integer parity, or any wider Vulkan readiness.

Stop after one corrected invocation regardless of outcome. A new import,
scan, DLL path, target, ABI, graph, parity, or child-exit failure is a failed
checkpoint requiring review; no second retry, backend fallback, compile, or
artifact promotion is approved by this feedback.
