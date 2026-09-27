# Algorithm Status

Snapshot: 2026-09-06; primary scope is Windows desktop x86-64.

The labels below are intentionally conservative. An algorithm without complete
runtime evidence is not described as 100% production-ready.

| Family | Status | Notes |
|---|---|---|
| Resize (bicubic/bilinear/area/nearest) | **QUALIFIED** | Qualified only on the documented desktop smoke/parity targets |
| Gaussian, gradients, Canny | **QUALIFIED** | Fast hardware gate 5/5 on the documented devices; other drivers require their own gate |
| Bilinear, DCB, Hamilton, ARM demosaic | **EXPERIMENTAL** | Artifacts and focused evidence exist, but the full target/device matrix is not complete. Hamilton gained a quality/artifact tuning pass on CPU with a synthetic ground-truth suite plus a real-DNG artifact proxy; see *Demosaic Quality Evidence* below |
| MLRI-ADMM demosaic | **EXPERIMENTAL** | Portable Vulkan reconstruction was corrected; broader parity and lifecycle evidence remains required |
| Remap, perspective warp, affine warp | **QUALIFIED** | Qualified only for the recorded desktop paths and shapes |
| Optical flow and block matching | **EXPERIMENTAL** | Native implementations and recovery paths exist; fused/block variants remain target-gated |
| RANSAC/homography, OFB, AKAZE | **EXPERIMENTAL** | CPU/native graph work is present; cross-backend runtime evidence is incomplete |
| Box, median, bilateral, guided, NLM, BM3D | **EXPERIMENTAL** | CPU/reference parity exists; native graphics paths retain per-operation guards |
| FFT, phase correlation, NCC/ZNCC | **EXPERIMENTAL** | Focused CPU evidence exists; universal backend support is not established |
| HDR, tone mapping, inpaint, SFM/MVS | **EXPERIMENTAL** | Research artifacts and CPU evidence exist; target/device qualification remains incomplete |
| Compression and RAW pipeline | **EXPERIMENTAL** | Artifacts and focused pipeline evidence exist; complete native matrix is pending |

The label applies to the family as a whole. A narrower operation/backend gate
may still be **QUALIFIED** when its evidence explicitly names the backend,
device, shape, dtype, command, metric, lifecycle, and memory result.

## Demosaic Quality Evidence (2026-09-23)

Hamilton was re-tuned and the demosaic family gained a ground-truth quality
suite. The family label stays **EXPERIMENTAL**: this evidence is CPU-only and
does not cover the target/device matrix.

Harness: `taichi_algorithm/demosaicing/tests/demosaic_quality_harness.py` (scene
generation, sensor simulation, metrics; NumPy/scipy only) with the runner
`run_demosaic_quality.py`. Synthetic scenes carry ground truth; the scoring
reference is the **optical** image (after lens PSF and lateral chromatic
aberration, before mosaicing), never the sharp scene.

Synthetic gate, 7 scenes (4 tuning + 3 held-out), realistic sensor model
(PSF sigma 0.6, lateral CA 0.0015, full well 12000 e-, read noise 2.4 e-),
mean over scenes, tuned versus initial constants:

```
backend=cpu device=Windows x86-64 host shape=256,256 dtype=float32
command=run_demosaic_quality.py --backend cpu --methods hamilton --size 256 --include-held-out
result=mae 0.008826 -> 0.007924 (-10.2%)          psnr_db 36.93 -> 37.88 (+2.6%)
       p99_abs 0.0878 -> 0.0634 (-27.8%)          false_pixel_rate 0.0390 -> 0.0292 (-25.0%)
       chroma_error_mean 0.01230 -> 0.01069 (-13.1%)   edge_mae 0.01410 -> 0.01256 (-11.0%)
       zipper_score -8.6%   zipper_p99 -33.0%     fringing_score -9.7%
       halo_energy -22.8%   halo_p99 -6.2%        halo_rate +8.1%  (the one regression)
       latency 6.6 ms dispatch vs RawPy AHD ~50 ms end to end
```

Head-to-head against RawPy AHD on the same scenes: 12 of 49 metric/scene cells
won before and after, so the tuning improved absolute quality but did **not**
close the gap to AHD on near-Nyquist detail.

Real captures (3 DNGs from `test_algorithm/`, 768x768 centred crop, margin 8):

```
backend=cpu device=Windows x86-64 host shape=768,768 dtype=uint16
command=run_demosaic_quality.py --backend cpu --real --crop 768 --limit 3
result=cfa_checkerboard_chroma -5.2%   chroma_hp_energy -9.2%
       sample_site_fidelity_mean -1.8%   sample_site_fidelity_max -0.5%
       (cfa_halo_energy/rate change only at 1e-8 magnitude, i.e. no ringing either way)
```

Block parity after the kernel change:

```
backend=cpu device=Windows x86-64 host shape=2449,3266 dtype=float32 block=512
command=stress_demosaic_block_parity.py --method hamilton --sizes 8 --block-size 512
result=max_abs_error=0.0 (full-frame versus compute-block, bitwise identical)
```

Behaviour-preserving refactors, each verified by capturing all six Hamilton graph
outputs before and after and requiring bitwise equality: removing an unread
full-resolution `wb_bayer` scratch plane plus an unused `cmatrix` upload from
`hamilton_demosaic_3channel`, and lifting the tuning constants into named
`HA_*` constants.

Scope caveat that must not be lost: the tuning targets frames with real sensor
conditioning. On an ideal sensor (no PSF, no CA, no noise) at 128 px the same
constants make `mae` +0.4%, `zipper_score` +6.3%, and `halo_energy` +11.0%
*worse*. Making the constants noise-adaptive is the identified follow-up.

Not yet covered: no GPU target has been recompiled or validated for the tuned
constants, the remaining demosaic families are untouched, and the
`halo_rate` increase is unresolved.

## Demosaic Full-Frame Work (2026-09-24)

CFA-phase specialisation, Hamilton pass 1.  The green pass previously derived the
pixel parity with `r % 2` / `c % 2` and three nested selects, then performed
eight separate gain lookups through `_sample_raw_wb`, which clamps both indices
for every sample.  The kernel now iterates the 2x2 CFA block with compile-time
phase constants, so parity is known at compile time, the two neighbour gains are
hoisted out of what used to be eight lookups, and the interior - where clamping
is a provable no-op - uses direct indexing.  Only the 4-pixel border ring keeps
the clamped sampler.

```
CPU Windows x86-64, 1024x1024, control-normalised process-CPU time
  hamilton  250.00 -> 218.75 ms   1.22x        (control bilinear reads 1.00x)
accuracy   0 quality regressions over 7 scenes; deltas +-0.00%
           max|diff| 5.4e-07, zero pixels above 1e-06 (FMA rounding only)
parity     full-frame versus block max_abs_error = 0.0 at 8 MP
tests      47 passed
```

This is a real but modest gain, and it is **not** the 2x target.  The emitted IR
explains why the headroom is limited: the hot bodies are scalar load and
address-arithmetic bound (71 loads, 72 getelementptr, 28 sext, 25 shl per body)
with no vector operations at all, so removing branch and parity work can only
recover the share of instructions that work represents.  Pass 2
(`_ha_red_blue_direct_kernel`, 26 conditional branches, 144 calls, 14 fdiv) runs
over every pixel and has not been specialised yet; it is the larger remaining
half.  Whether 2x is reachable at all is still open and must be measured, not
assumed.

Artifact size grew 50069 -> 68598 bytes from the duplicated body, which is the
expected cost of the unroll.

Pass 2 taken through the same transformation.  `_ha_red_blue_direct_kernel` now
iterates the 2x2 phase at compile time, derives `colour_h` statically so
`is_red_horizontal` is a colour test rather than a parity test, and reads the
three `colour_self` sites directly.  Unlike pass 1 this is **bit-exact**: every
captured variant differs by `mean = p99 = max = 0.0`.

```
CPU Windows x86-64, 1024x1024, paired per-round control-normalised CPU time
  hamilton  pass 1 + pass 2 vs pre-specialisation   1.30x
  bilinear  byte-identical control                  1.00x  (raw 1.09x, spread 1.35/1.45x)
accuracy  0 quality regressions over 7 scenes; pass 2 bit-exact
parity    full-frame versus block max_abs_error = 0.0 at 8 MP
tests     47 passed
artifact  68598 -> 89938 bytes
```

The estimator itself was corrected here.  Normalising *medians across rounds*
let drift occurring inside a round leak into the answer and produced a
contradictory 1.18x for a superset of the earlier 1.22x change.  Pairing inside
each round - `(A/B)_method / (A/B)_control` per round, then taking the median -
makes the byte-identical control read exactly 1.00x, so the effect is now
resolved against a validated instrument.  Note that this host slowed by roughly
4x over the session (hamilton 250 -> 1100 CPU ms for the same work), which is
exactly why absolute numbers are unusable.

Still short of the 2x target, and the reason is unchanged: the transformation
removes branch, parity, and gain-lookup work, but the emitted bodies remain load
and address-arithmetic bound with no vector operations.  The remaining levers
are structural rather than arithmetic - a gate-free interior kernel that the
backend could vectorise, fewer loads through reuse across neighbouring pixels,
and `rsqrt` for the sigmoid in place of three divisions and three square roots.

## Demosaic Peak Memory at 4K (2026-09-24)

Measured per family in a fresh process at 3840x2160, engine resident counter
sampled by a thread while the call is in flight.  One frame plane is 33.2 MB, so
the counts below are the number of full-resolution planes held simultaneously:

```
family      before   frames   after   frames   dispatch ms
bilinear     132.7      4.0     -        -        120
hamilton     165.9      5.0     -        -        430
arm          331.8     10.0     -        -       1002
dcb          398.1     12.0   298.6     9.0       620
mlri-admm    331.8     10.0     -        -       5714
```

**DCB was reduced by 25% (99.5 MB) by aliasing `rgb_b` onto `dst` on every
path.**  `_dcb_refine_chroma` writes `rgb_b`, and both consumers
(`_dcb_copy_rgb` and `_dcb_copy_rgb_headroom`) are elementwise: they read only
`src[y, x, *]` and write that same pixel back, so no pixel is read after another
pixel has written it.  `rgb_a` cannot be aliased the same way because
`_dcb_refine_chroma` reads a 3x3 neighbourhood of it.  This needs no
recompilation because the graph ABI is unchanged; the six-variant capture after
the change is bitwise identical to the capture before it.

The other families are already at their structural minimum: Hamilton needs
input + green + output, so five planes; ARM and MLRI each need six one-plane
work buffers whose consumers read neighbourhoods (`_arm` median 3x3, MLRI ADMM
scratch), which is what forbids aliasing them.

**Measurement trap worth recording**: reading the resident counter for several
methods in one process overstates the later ones, because the engine pools
released buffers.  DCB first read 398.1 MB *after* the alias change until it was
measured in its own process, where it correctly read 298.6 MB.  Allocation
tracing (wrapping `engine.allocate`) is the other half of the evidence: DCB now
makes 5 allocations totalling 9.0 planes, down from 12.0.

## DCB and MLRI Specialisation (2026-09-24)

DCB has three passes that each recomputed the CFA parity per pixel, so all three
were specialised: `_dcb_green`, `_dcb_initial_rgb` and `_dcb_refine_chroma`.  In
`_dcb_initial_rgb` the left-neighbour colour also had to be proven: it sits at
parity `(i, 1 - j)` while `x > 0`, and at `x == 0` it clamps onto the pixel's own
column, so its colour is the pixel's own.  That makes
`left_colour = select(x > 0, colour_left, colour_self)` exactly equivalent to the
`_cfa_color(y, xl, ...)` call it replaces.

```
family   paired B/A   control (byte-identical)   quality gate      4 backends
dcb        1.40x              1.00x              0 regressions        PASS
mlri       0.94x              1.00x              0 regressions        PASS
```

DCB's 1.40x is the largest of the three families done so far, because three
passes were specialised instead of one, and because its kernel operates on an
already white-balanced mosaic so each pass pays the parity cost without any
offsetting work.

**MLRI is reported as no measurable change, not as a win.**  `0.94x` sits inside
the band this host can resolve — the control's own raw drift that round was
0.933, the same magnitude as the reading.  The reason is structural: MLRI runs
about fifteen dispatches and its cost is dominated by the ADMM iterations (three
step1/step2 rounds), so specialising one non-dominant kernel cannot move it.
`_gbtf_green_interpolation_kernel` was the kernel named as highest priority, and
it is done, but the four `_admm_step2_*` kernels plus
`_mlri_suppress_opponent_outliers_kernel` still carry runtime parities and are
where MLRI's remaining opportunity is.

**Bilinear was deliberately left alone.**  It does carry runtime parity logic,
but it is already the cheapest kernel in the family, and it is the byte-identical
control that every speed number above depends on; specialising it would destroy
the instrument's baseline.  That trade-off is flagged rather than taken silently.

Accuracy for both families is at float32 ULP scale (0 pixels above 1e-03; DCB max
1.2e-06, MLRI max 3.6e-07), and the untouched variants stayed bitwise identical.

## ARM Green Pass Specialisation (2026-09-24)

The CFA-phase technique from Hamilton was applied to
`_arm_preprocess_and_green_interpolation_kernel`.  ARM already hoisted its four
gains and already split interior from border, so the remaining redundancy was
that all twelve `_sample_raw` calls recomputed a gain from runtime parities
through `_get_gain_fast`.  Unrolling the 2x2 phase into `ti.static` loops makes
both parities compile-time, so every one of those twelve selections folds to a
direct scalar.

Result on CPU at 1024x1024, paired per-round estimator:

```
method     paired B/A   raw B/A   control (bilinear, byte-identical)   max|diff|
arm           1.18x       1.08x              1.00x                        0.0
```

The byte-identical control reading exactly 1.00x is what bounds this host's
resolution; the 1.18x is therefore attributable, not drift.

Accuracy and gates:

- Six-variant capture against the pre-specialisation artifact: 0 pixels above
  1e-03, mean 1.2e-08, p99 1.8e-07, max 1.0e-06 (float32 ULP scale).  The
  untouched 1channel / half-res / rgb-half-res variants are bitwise identical,
  which bounds the change to the green kernel.
- Quality harness, 7 scenes, 192 px: **0 regressions, 5 improvements**.
- Block parity at 8 MP: `max_abs_error` 0.0, both sides finite.
- Artifacts rebuilt for all four backends: cpu 68313 B, cuda 94930 B,
  vulkan 83442 B, opengl 83442 B.

ARM and Hamilton now share the technique.  DCB (`_dcb_green`) and MLRI
(`_gbtf_green_interpolation_kernel`) still use runtime parities, and each also
has a second pass that Hamilton has already specialised.

## Demosaic Readback Investigation (2026-09-24)

Readback dominates end-to-end time on every GPU backend at 4K (356 ms Vulkan,
348 ms OpenGL, 135 ms CUDA against 114 / 47 / 24 ms of dispatch), so it was
investigated directly.  Both candidate levers were measured with the paired
per-round estimator and **both failed**:

```
lever                        vulkan   opengl   cuda    verdict
force output host-visible     0.663x   1.050x   1.101x  dispatch penalty exceeds
  (paired dispatch ratio)                              the readback gain
force output host-visible     1.123x   1.029x   0.973x  readback only
  (paired readback ratio)
convert to uint8 then read    0.600x   0.421x   0.770x  costs more than the
  (paired total ratio)                                  bytes it saves
```

Readings are paired ratios of the current default against the candidate, so a
value above 1.0 means the candidate is better.  Making the output host-visible
does speed the host copy on Vulkan (1.123x) but slows dispatch to 0.663x, so the
total loses; on OpenGL and CUDA it loses outright.  Converting to uint8 before
the readback loses on all three because `cast(host_accessible=True)` adds a
conversion kernel and a host-visible write before the copy.

Earlier single-shot probes suggested the opposite for OpenGL and CUDA.  They were
wrong: readback on this host varies by up to 4.89x between runs, so an A-then-B
comparison cannot attribute anything here.  Every number above comes from
alternating both variants inside the same round.

Result: the engine's existing `_decide_memory_domain` policy is already the best
of the three tested, and no readback win is available from buffer domain or
output dtype.  The remaining lever is the transfer primitive itself
(`read_from_gpu_buffer`, staging reuse, chunking, or overlapping the copy with
compute), which lives in `taichi_vision/taichi_aot/engine.py` and the native
bridge.  Both are the runtime source of truth and are barred from change without
explicit user approval.

## Demosaic 4K Per-Backend Profile (2026-09-24)

All four desktop backends execute the demosaic at runtime on this host, which
makes per-backend optimisation measurable rather than assumed.  Hamilton,
3840x2160 (8.29 MP), median of 3 runs:

```
backend  device                    upload   dispatch  readback    e2e
cpu      Windows x86-64 host         5.3      331.2      47.2    383.8 ms
vulkan   Intel UHD Graphics 620      5.2      114.0     355.9    475.1 ms
cuda     NVIDIA MX150 (device 0)    40.8       24.1     135.4    200.3 ms
opengl   NVIDIA MX150               5.0       47.4     348.2    400.6 ms
```

Two conclusions that decide where per-backend work belongs:

- Dispatch, the part the algorithm controls, is fastest on CUDA (24.1 ms,
  13.7x faster than CPU) and the GPU backends are already an order of magnitude
  ahead of CPU.  CPU dispatch remains the only backend where kernel work still
  dominates end to end.
- On Vulkan and OpenGL the **readback dominates**: 356 ms and 348 ms against
  114 ms and 47 ms of dispatch.  End-to-end time there is a transfer problem,
  not a kernel problem, so kernel optimisation cannot move it.  Any further work
  on those two backends has to attack the host copy.

Engine resident bytes at 4K are identical on every backend, 165,888,000 B
(158 MB) = input 33 MB + green scratch 33 MB + output 100 MB.

Per-backend input path, measured on CUDA at the same resolution:

```
bayer dtype   upload    dispatch   upload+dispatch
float32       39.481     24.791        64.272 ms
uint16        20.210     32.866        53.076 ms     1.21x faster
```

The CUDA-only `hamilton_demosaic_u16` graph is reachable and halves the upload,
which more than pays for its slower dispatch because the kernel converts to f32
internally.  Since camera RAW arrives as integers, passing it through unchanged
is the natural per-backend policy on CUDA rather than a special case.

## Demosaic Cross-Backend Rebuild (2026-09-24)

Every demosaic family whose source changed was rebuilt for all four desktop
targets, not just CPU.  Compile command per target:

```
compile_aot_backend_suite.py --target <target_id> --only arm,dcb,mlri_admm --force
```

```
family              cpu        cuda       opengl     vulkan
hamilton            89928      239841     129862     129862     (all rebuilt 09-23)
arm                 57989       79003      65600      65600
dcb                106105      162653     133474     133474
mlri_admm          118865      165028     143585     147989
bilinear_demosaice  36574       49684      44572      44572     (source unchanged)
```

This is **compile evidence only**.  Governance is explicit that a successful
compilation or the presence of an artifact is not evidence of runtime support,
and no GPU device was exercised for these rebuilds: the tuned constants and the
phase specialisation are validated by execution on CPU alone.  Each GPU target
still needs its own runtime gate before any claim about it.

Note also that a GPU-enabled environment is not actually required for this: the
stable venv compiled all four targets, contrary to the older note in
`ai_governance/CURRENT_IMPLEMENTATION.md` that GPU compilation depends on a
separate development bundle.  The development tree at
`D:\development_build\taichi_runtime_llvm20` contains package overlays but no
interpreter, so it was not used.

## Demosaic Family-Wide Work (2026-09-23)

Follow-up covering the hot path, memory, and the other four families.

Final division collapse.  The kernels carried the pattern
`w = 1/(eps + d)` followed by `(w1*a + w2*b)/(w1 + w2)`; expanding it removes
both reciprocals and leaves a single division, which is algebraically exact and
removes the most expensive operation in the kernel.  Applied to Hamilton
(pass 1, both R/B sites, both green-site branches), ARM (four sites), DCB (two
sites) and MLRI (one site).  Evidence is the emitted IR, which is deterministic
and therefore immune to the timing noise on this host:

```
kernel                                  fdiv change   instructions
_ha_green_direct_kernel                    4  ->  2     unchanged (102)
_ha_red_blue_direct_kernel                26 -> 14     unchanged (136)
_arm_preprocess_and_green_interpolation     4  ->  2     unchanged
_dcb_green                                  6  ->  2     unchanged
_gbtf_green_interpolation                   9  ->  7     unchanged
```

Numerics for the three newly changed families: every captured output differs
from the pre-change capture by at most one float32 rounding step
(arm 1.0e-6, dcb 1.2e-6, mlri 3.6e-7), and the variants whose kernels were not
touched are bitwise identical.  Hamilton was checked against the independent
float64 model instead: `mean_abs_diff=2.39e-08`, `p99=1.19e-07`, and zero pixels
above 1e-3, i.e. no decision-boundary flips at all.

Wall-clock attribution is not available on this shared host.  Repeating the same
measurement gave a 1.6-1.7x swing for *unchanged* bilinear code, so cross-run
timings cannot be attributed to a change here.  The IR reduction is the evidence
that is offered; the speed claim is not.

Quality is unchanged by these rewrites.  A 192 px run over 7 scenes with the
realistic sensor model reproduced the previous table exactly:

```
method        mae     psnr_db   p99_abs   false_pix  chroma_err  zipper   fringing  halo_E   vs AHD
hamilton    0.00903    36.85    0.0717    0.03605    0.0123     0.0250    0.0224   0.00057   10/42
dcb         0.00991    36.01    0.0972    0.04426    0.0137     0.0277    0.0231   0.00075   11/42
mlri_admm   0.01182    34.86    0.1250    0.06093    0.0160     0.0291    0.0188   0.00108   11/42
arm         0.01534    33.09    0.1582    0.08583    0.0150     0.0567    0.0180   0.00052    9/42
bilinear    0.07116    20.18    0.2359    0.56072    0.0770     0.0540    0.0427   0.04118    0/42
```

Block parity was extended to every family and passes at 8 MP (2449x3266, block
512, CPU) with `max_abs_error = 0.0` and both paths finite: hamilton, dcb,
bilinear, arm, mlri-admm.  The probe previously hard-rejected ARM and MLRI, so
their block paths had no parity harness at all.

Memory at 12 MP (4000x3000), peak process RSS sampled during the call:

```
mode    tile   peak RSS MB   tile working set MB   engine resident delta MB   ms
full      -        514.38              -                    +228.88          3773
block   512        846.25             4.52                  +176.91          6024
block  1024        845.79            17.02                    0.00          1878
```

The block path bounds the *engine* working set (0 versus +229 MB resident delta)
and its device-side tile footprint is 4.5-17 MB, which is what makes 50/100 MP
feasible.  It does **not** reduce process RSS at 12 MP: 846 MB versus 514 MB,
because host-side tile assembly and the stitched output dominate.  Tile size
matters more than the mode: at 1024 the block path was 2.0x faster than
full-frame in the same process, while at 512 it was 1.6x slower.

Dispatch defects fixed.  The method-error message in `aot_api.demosaic`
advertised aliases that the dispatcher rejects earlier in the same function
(`hamilton-adams`, `ppg`, `dcb-demosaic`, `mlri`) and omitted `dcb` and
`bilinear`, which do resolve.  The message now matches the code, and all
fourteen spellings it lists were verified to resolve while the four rejected
ones are still rejected.

Still not done for the other families: no quality tuning.  The confirmed
constants search for Hamilton relied on a float64 model of its two kernels;
ARM, DCB and MLRI have their own kernels and constants and would each need an
equivalent model before a search means anything.  Their constants remain at
their original values, so this family group is now cheaper but not better.


The latest recorded native desktop evidence is limited to the devices and
commands that were actually run:

- CPU Windows x86-64: fast hardware matrix 5/5.
- NVIDIA GeForce MX150 CUDA: fast hardware matrix 5/5.
- NVIDIA GeForce MX150 native OpenGL ICD: fast hardware matrix 5/5 and
  comprehensive native OpenGL gate 29/29.
- Intel UHD Graphics 620 native Vulkan API 1.3.215, driver 101.2115:
  75/75 target-qualified TCM loads, 940/940 SPIR-V shader validations,
  28/28 algorithm checks, and lifecycle/graph parity MAE
  `3.7529832752625225e-07`.
- Intel UHD Graphics 620 native `ig11icd64.dll` OpenGL ICD, driver 101.2115:
  29/29 comprehensive checks and the recorded 8122x2966 float32 stress gate.

These are qualification records for exact device/driver combinations, not a
universal claim for all Intel/NVIDIA driver versions. Dozen/D3D12 translation
adapters are excluded from production selection, and no CPU fallback was used
for these native records.

## Historical Qualification Evidence (2026-08-30)

### Test Results Summary

**CPU Backend (primary qualification target):**
- Comprehensive test: 27/27 passed
- Research test: 25/25 passed (worst error: plane_sweep_cost_oracle=2.1e-6)
- Fast hardware gate: 5/5 passed

**CUDA Backend (NVIDIA MX150):**
- Fast hardware gate: 5/5 passed
- Resize: 0.583ms, Gaussian: 2.803ms, Gradients: 1.068ms, Canny: 136.278ms, Remap: 1.192ms

**OpenGL Backend (NVIDIA MX150 ICD):**
- Fast hardware gate: 5/5 passed
- Resize: 2.407ms, Gaussian: 12.561ms, Gradients: 2.929ms, Canny: 196.355ms, Remap: 3.650ms

**Vulkan Backend (NVIDIA MX150):**
- Initialization validated; driver-specific issues on full test (known limitation)

### Per-Algorithm Evidence

**Denoising Family:**
```
backend=cpu device=CPU shape=512,52,3 dtype=float32
command=test_comprehensif.py --run-logic
result=PASS Box Filter MAE=0.000028, Median MAE=0.001905, Bilateral Grid MAE=0.070729
       Guided Filter MAE=0.0, NLM MAE=0.0, BM3D MAE=0.0
       JBF MAE=0.0, JBLU MAE=0.0
```

**Demosaic Family:**
```
backend=cpu device=CPU shape=32,32 dtype=float32
command=test_comprehensif.py --run-logic
result=PASS MLRI-ADMM 5-API parity MAE=0.000016
       Bilinear/DCB/Hamilton/ARM TCMs validated on all 4 desktop backends
```

**Optical Flow Family:**
```
backend=cpu device=CPU shape=128,128,2 dtype=float32
command=test_comprehensif.py --run-logic
result=PASS Block Matching, Lucas-Kanade, Farneback all produce valid (H,W,2) flow
       All finite, correct dtype, correct shape
```

**Alignment Family:**
```
backend=cpu device=CPU shape=512,512 dtype=float32
command=test_comprehensif.py --run-logic
result=PASS Phase Correlation MAE=0.0 (shift 5,-3 detected exactly)
       NCC Alignment MAE=0.0 (zero shift detected exactly)
       RANSAC Flow Cleanup MAE=0.0
```

**Image Processing Family:**
```
backend=cpu device=CPU shape=128,128 dtype=float32
command=test_comprehensif.py --run-logic
result=PASS CLAHE MAE=0.168091, Otsu MAE=0.0, Hough Lines detected
       Inpaint MAE=0.0, Seamless Clone MAE=0.0
```

**Research Suite (HDR, Tone Mapping, SFM, Camera):**
```
backend=cpu device=CPU shape=various dtype=float32
command=test_research_aot
result=PASS 25/25 checks, worst error=2.14577e-06
```

### Historical TCM Artifact Coverage

All algorithms have compiled TCM artifacts for all 4 desktop targets:
- `cpu_x86_64_windows/`: 74 artifacts
- `cuda_x86_64_windows_nvidia/`: 74 artifacts
- `vulkan_x86_64_windows/`: 74 artifacts
- `opengl_x86_64_windows/`: 73 artifacts

### Promotion Rule

For each operation, record backend, device, shape, dtype, command, parity/error
metric, lifecycle, and memory telemetry. TCM compilation alone is insufficient.
Promote operations individually after their evidence is complete.

### Next Steps

- Run full comprehensive test on Vulkan when driver issues are resolved
- Collect per-algorithm MAE thresholds for formal documentation
- Add stress test evidence for block mode operations
- Document OpenGL safety gate exceptions for specific algorithms
