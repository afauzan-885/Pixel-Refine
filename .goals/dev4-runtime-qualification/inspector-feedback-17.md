# Inspector feedback 17 — CPU Gaussian runtime smoke

Tanggal: 2026-10-25 (Asia/Jakarta)  
Model Inspector: GPT-6 (fallback; dedicated Goal Inspector model unavailable)  
Verdict: **PASS_FOR_ONE_CPU_FLOAT32_GAUSSIAN_SMOKE**

## Runtime evidence

I read the exact iter17 runner, smoke script, stdout, stderr, and exit file.
The command invokes the project venv Python once through `cmd.exe`; stdout,
stderr, and child exit code are redirected separately. The recorded Python
exit is `0`. Stderr is 46 bytes; stdout is 5,948 bytes. Their SHA-256 values
match handoff 17: stdout
`2109E8B1EC52DA9A1B91E8BDE87AFC48F4DDB48CB04CA92B351AD17039B1E85B`, stderr
`3779DD9A886B5032F3DF128A95FB24223C72999CA750A3A172D5A3B757D1C800`, and
exit file `13BF7B3039C63BF5A50491FA3CFD8EB4E699D1BA1436315AEF9CBE5711530354`.
The smoke script asserts its exact environment, including CPU selection,
`TI_LIB_DIR`, `AOT_TCM_ABI_PREFLIGHT=1`, `AOT_TCM_ABI_ALLOW_LEGACY=0`,
`AOT_COMPILE_ONLY=0`, the iter14 bridge, and the iter15 TCM root.

Before AOT import it verifies staged bridge/C API/TCM hashes and pins the
staged C API with an absolute-path `ctypes.WinDLL` load. Win32 module-path
checks confirm that exact staged C API path. After backend initialization,
the script again calls `GetModuleFileNameW` for both modules and confirms:

- Bridge: iter14 scratch `taichi_aot_engine_baseline.dll`, SHA-256
  `E484881C4ADF1B192C02ED95AA6BFED5C9C3D682A8D2FC43E8010BB3CA3ED6D9`.
- C API: the adjacent iter14 scratch `taichi_c_api.dll`, SHA-256
  `B29073835F7496B5A08307ADF7C088651FC17A14BF469C46319D3C50F213CBCF`.
- Backend and runtime architecture are `cpu`; bridge logs `Backend siap: CPU
  (perangkat 0)`. The runtime device and CPU context-backend strings are
  empty, so no physical CPU model or nonempty context name is claimed.

The resolver reports `cpu_x86_64_windows`, the iter15 scratch artifact root,
and exactly `gaussian_cpu_x86_64_windows.tcm`; the artifact SHA is
`C80DBE770578D144DD6E89494DB9E37710C33EA10C5BCB966018BAA1558E1A7B`. ABI
preflight is enabled with legacy acceptance disabled, no target/ABI error is
reported, and runtime logs the TCM module as loaded. Its 15-entry
materialization cache is under the same external scratch root and totals
495,203 bytes. No canonical TCM path is involved. The public AOT call
`gaussian_blur(..., sigma=1.0, kernel_size=5, return_gpu=False)` returns a
finite NumPy float32 array for a deterministic 64x64 float32 input. The
script confirms that module key `gaussian` was loaded and the native module
path is confined to the staged cache. It does not log each internal graph
name individually; the observed claim is one successful public Gaussian
operation backed by that loaded module.

The OpenCV reference is `cv2.GaussianBlur` with 5x5 kernel, sigma X/Y 1.0,
and `BORDER_REFLECT_101`. Reported max absolute error is
`1.1920928955078125e-07`, mean absolute error is
`1.4468241715803742e-08`, and `np.allclose` passes at `rtol=1e-5`,
`atol=1e-5`. Output shape/dtype are 64x64/float32 and all values are finite.
This supports parity for this one CPU float32 sample only. It does not
validate the warned integer specializations, other shapes, all Gaussian
inputs, other operations, performance, or application integration.

## Isolation and limits

Post-run hashes in the JSON result exactly match the pre-run bridge, C API,
and TCM hashes. Handoff 17 reports unchanged active/packaged bridge and C API,
venv/import library, manifest, and canonical TCM inventory fingerprint. The
materialized cache remains in iter15 staging; there is no canonical cache
change. Git status has only pre-existing unrelated user paths. This review
was read-only; I did not load a DLL, run runtime, compile, or run tests.

Verdict is limited to one CPU float32 Gaussian runtime/parity sample. It
cannot be generalized to CUDA, Vulkan, OpenGL, integer dtypes, or other
operations.

## GPU next step

The earlier baseline inventory found an NVIDIA MX150 and Intel UHD 620, and
`vulkaninfo` enumerated both. Those are hardware/loader observations, not
Taichi GPU initialization or C API runtime qualification. This iter17 run is
CPU-only and does not establish a GPU device ordinal, backend readiness, or
GPU bridge pairing. Therefore it does **not** justify a GPU TCM load/runtime
smoke yet.

The safest next GPU action is one fresh-process **Vulkan device-init
preflight only**, using the venv Dev4 runtime and explicit staged bridge/C API
paths, with robust separate stdout/stderr/exit capture. Enumerate Vulkan
devices first and record the actual Taichi-selected ordinal/name/vendor;
require backend `vulkan` and a real device identity before selecting a
manifest target. Do not resolve/load TCM or dispatch a graph in this probe.
If it fails or selects no known device, record Vulkan as unavailable and
stop. If it succeeds, review the device and target mapping, then separately
authorize a single `vulkan_x86_64_windows` Gaussian TCM compile to a fresh
external root. A subsequent GPU runtime smoke still needs a target-compatible
staged bridge/C API static gate and its own review. The existing inventory
alone does not support skipping these gates.
