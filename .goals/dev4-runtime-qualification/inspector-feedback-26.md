# Inspector feedback 26 — OpenGL bridge static gate

Tanggal: 2026-10-25 (Asia/Jakarta)  
Model Inspector: GPT-6 (fallback; dedicated Goal Inspector model unavailable)  
Verdict: **PASS_FOR_OPENGL_BRIDGE_STATIC_ONLY**

## Static bridge evidence

The iter26 staged OpenGL bridge build has exit record `0`, ends with
`Finished generating code`, and has empty stderr. Saved PE headers identify
the bridge as AMD64 / PE32+. The staged bridge SHA-256 is
`E08EB3424622649FD1DDA34B39BCB7ACC088ECEF204D17F59CD737EA2974E583`; its
adjacent Dev4 C API SHA-256 is
`B29073835F7496B5A08307ADF7C088651FC17A14BF469C46319D3C50F213CBCF`, matching
the venv C API. Bridge exports include `init_aot_engine`, `load_aot_module`,
and the three memory-control C APIs. I independently compared the 17 bridge
imports from `taichi_c_api.dll` with the staged C API's 809-name export list;
all 17 are present. This is static PE/name-level closure only.

## Isolation and limits

The build output is in the unique external iter26 scratch directory.
Independent post-checks show the active bridge, packaged OpenGL bridge/C API,
venv Dev4 C API, and target manifest hashes unchanged. The canonical TCM tree
remains 1,694 files / 74,689,912 bytes; Git status has only pre-existing user
changes. No OpenGL TCM compile was attempted, and no DLL was loaded or runtime
initialized. Therefore the active Intel renderer/ICD, TCM profile, target
runtime, graph execution, parity, and application behavior remain unknown.
The registry presence of an Intel driver DLL is not proof of a loaded
OpenGL context; the recorded current driver file version also differs from
the historical matrix version.

The only compiler activity in this gate was the native bridge build. The
Taichi TCM compiler did not run because no assertion/telemetry was available
to tie its OpenGL context to the staged bridge's actual ICD renderer. This
Inspector performed no build, runtime, tests, source edits, or status edits.

Verdict is limited to bridge build plus static PE architecture, exports, and
import-name closure. OpenGL TCM compilation, Intel renderer identity, runtime
load, graph, parity, and production readiness are not qualified. Any further
OpenGL TCM/runtime attempt needs a separate coordinator decision and a
renderer/device identity gate.
