# Inspector feedback 21 — staged Intel Vulkan Gaussian smoke

Tanggal: 2026-10-25 (Asia/Jakarta)  
Model Inspector: GPT-6 (fallback; dedicated Goal Inspector model unavailable)  
Verdict: **PASS_FOR_ONE_INTEL_VULKAN_FLOAT32_GAUSSIAN_SMOKE**

## Device, bridge, and C API

I independently read the iter21 script, runner, stdout, stderr, and numeric
exit file. The child exit file contains `0` and is one byte; stdout, stderr,
and exit hashes match the handoff. The script inserts the repo path before
project imports and records `scan_vulkan_device_records(fresh=True)` before
importing the AOT facade. The fresh list contains native Intel UHD 620 at
ordinal 0 (`0x8086:0x3EA0`, driver 101.2145, not a translation adapter) and
NVIDIA MX150 at ordinal 1; the script selects only the Intel record and sets
both device variables to 0.

The script verifies staged sizes/hashes before preload, preloads the C API by
absolute path, then checks Win32 module paths after bridge initialization.
Runtime reports Vulkan, strict/explicit Intel selection, ordinal 0, and
renderer `Intel(R) UHD Graphics 620`. The actual loaded bridge path is the
iter18 scratch Vulkan bridge, SHA-256
`644F3111DF639AD4D96846BC4FCBFB49677E35F9ECC9D0DE512CD64DDEC2E1DC`; the
actual loaded C API is its adjacent staged Dev4 C API, SHA-256
`B29073835F7496B5A08307ADF7C088651FC17A14BF469C46319D3C50F213CBCF`.
These match the expected staged pair. I rehashed both plus the iter19 TCM
after the run and obtained the same hashes.

## Resolver, ABI gate, and graph dispatch

The runtime `TargetSpec` is Intel-specific
`vulkan_x86_64_windows_intel`; the vendor-neutral resolver selects the exact
iter19 TCM at
`artifacts/vulkan_x86_64_windows/gaussian_vulkan_x86_64_windows.tcm`, SHA-256
`B7888052FCF05C0FB3622E70C7B9744164D9193AFDDFB2AD655AD360BCEB92BA`. The
active TCM root is exactly the iter19 scratch artifact root. The script
checks backend/architecture/OS, root, resolved path, and hash before
explicitly calling `aot.load_tcm("gaussian")`. With
`AOT_TCM_ABI_PREFLIGHT=1` and legacy ABI acceptance disabled, that load
returns `AOTModuleWrapper`, the Gaussian module cache contains `gaussian`,
and runtime logs the module loaded without target/ABI error. This supports
one successful staged TCM load through the configured ABI preflight; it does
not establish a separate universal ABI guarantee.

The actual public call is `aot.gaussian_blur` with `aot.InputArray` and a 2D
float32 image. Source inspection of the API path confirms this buffer case
selects `gaussian_blur_x_1ch_f32` and `gaussian_blur_y_1ch_f32` and calls
`_mod("gaussian").run` for both passes. Runtime output logs the loaded
Gaussian module and a result only after that API call returns. This is
evidence of one successful Gaussian graph operation, not a count of all
internal kernels or coverage of other graph families.

## Numerical result and lifecycle limit

Input is deterministic NumPy seed `20261025`, contiguous float32, shape
64x64, SHA-256
`796B56442BB61536966F730813958E06E1A1F388C0D5FBCFAAC3F16701BD4214`. The
reference is OpenCV 5.0.0 `GaussianBlur` with a 5x5 kernel, sigma X/Y 1.0,
and `BORDER_REFLECT_101`. Output is finite float32 64x64, SHA-256
`EF10B1BFE020BD76E35DB80BD8933C7140D6885C7742A66EA7F96C5121777A30`.
Maximum absolute error is `8.940696716308594e-08`; mean absolute error is
`6.803020369261503e-09`; `allclose` passes at `rtol=1e-5`, `atol=1e-5`.
This establishes parity only for this one Intel Vulkan single-channel
float32 sample. It does not test the warning-affected i32 kernels or prove
accuracy for other values, dtypes, shapes, graphs, or applications.

Intel compatibility mode is active, `AOT_SAFE_TEARDOWN=1`, and shutdown
logs that the native Vulkan context destructor was skipped. The process
exited 0 and cleanup message was captured, but this does not qualify normal
Intel driver teardown/lifecycle. It is an isolated test-mode runtime result,
not production readiness. No GPU fallback occurred: backend and renderer
remain Vulkan/Intel in the recorded result.

## Mutation check and remaining scope

Current post-run hashes for the bridge/C API/TCM match the pre-run values;
active and packaged Vulkan bridge/C API, venv C API/import library, target
manifest and canonical TCM inventory remain at their recorded identities.
I independently confirmed the canonical TCM tree still has 1,694 files and
74,689,912 bytes. Git status contains only pre-existing unrelated user
changes. The runtime cache and TCM remain in iter19 external staging. No
source, production artifact, venv, manifest, or status file changed. This
Inspector only read artifacts and source; no runtime, build, or test was
rerun.

This passes one staged Intel UHD 620 Vulkan float32 Gaussian runtime/parity
smoke. Remaining gaps include the Intel destructor skip, integer Gaussian
parity, other shapes/operations, other GPU devices/backends, performance,
application integration, and the broader C2/C5 acceptance coverage. The
iter19 compiler's actual renderer remains unrecorded; this smoke proves the
runtime used Intel, not that the prior compile ran on Intel. Do not generalize
the result or promote the staged artifacts.
