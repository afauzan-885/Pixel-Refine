"""Rule-based, actionable hints for taichi runtime failures.

Rules are matched against ``"<ExceptionType>: <message>"`` (lower case) plus a
small context snapshot.  Each rule is data, so new knowledge can be appended
without touching the tracer.  Text is Indonesian to match project policy;
identifiers stay English.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from typing import Any, Callable, Iterable

_PY = sys.executable or "python"


@dataclass(frozen=True)
class Hint:
    id: str
    title: str
    severity: str
    causes: tuple[str, ...]
    checks: tuple[str, ...]
    docs: str = ""
    priority: int = 50


def _check_backend() -> str:
    return (
        f'"{_PY}" -c "import taichi, taichi.aot_engine as e; '
        "print(taichi.backend_info()); print(e.get_memory_status(force=True))\""
    )


def _check_artifacts() -> str:
    return (
        f'"{_PY}" -m taichi_fault_trace --artifacts '
        "pixel_refine_desktop/ui/data/aot_assets/neural"
    )


def _check_native_error() -> str:
    return (
        f'"{_PY}" -c "import taichi.aot_engine as e; '
        "eng=e.get_engine(); import taichi.native_bridge as b; "
        "print(b.last_error(eng.runtime), b.context_backend(eng.runtime), b.device_name(eng.runtime))\""
    )


def _check_fresh_process() -> str:
    return (
        f'"{_PY}" -X faulthandler -c "import taichi, taichi.aot_engine as e; '
        'print(taichi.backend_info()); print(e.get_engine().gpu_name)"'
    )


def _unknown_native_empty(context: dict[str, Any]) -> bool:
    native = context.get("native") or {}
    return not str(native.get("last_error") or "").strip()


HINT_RULES: tuple[tuple[Callable[[str, dict[str, Any]], bool], Hint], ...] = (
    (
        lambda text, ctx: "python is likely shutting down" in text
        or "sys.meta_path is none" in text,
        Hint(
            id="TAICHI-SHUTDOWN",
            title="Pemanggilan runtime terjadi saat interpreter shutdown",
            severity="informasi",
            causes=(
                "Objek runtime (buffer/sesi) di-`__del__` setelah modul di-unload.",
                "`close()` dipanggil lagi dari finalizer setelah kegagalan pertama.",
            ),
            checks=(
                "Panggil `close()`/`release()` eksplisit sebelum proses berakhir.",
                "Jangan mengandalkan `__del__` untuk melepas resource native.",
            ),
            priority=20,
        ),
    ),
    (
        lambda text, ctx: "is not supported yet" in text
        and ("in kernel" in text or "ti.ndrange" in text or "ti.static" in text),
        Hint(
            id="TAICHI-FRONTEND-STUB",
            title="Fitur front end Taichi tidak didukung build Rust ini",
            severity="informasi",
            causes=(
                "Kernel memakai `ti.ndrange` atau `ti.static` yang belum "
                "diimplementasikan front end Rust.",
                "Kernel tersebut memang di-dekorasi saat import lalu pemanggil "
                "jatuh ke jalur fallback.",
            ),
            checks=(
                "Gunakan `for i in range(N)` atau tulis kernel sebagai AOT/TCM.",
                "Bila fallback sudah tersedia, kegagalan ini bukan fault runtime.",
                "Aktifkan `TAICHI_FAULT_ALL=1` untuk tetap melihat laporan.",
            ),
            priority=30,
        ),
    ),
    (
        lambda text, ctx: "unknown native failure" in text and _unknown_native_empty(ctx),
        Hint(
            id="TAICHI-NATIVE-EMPTY",
            title="Error native dilaporkan tanpa pesan (slot error kosong)",
            severity="tinggi",
            causes=(
                "Python memanggil helper yang selalu raise, misalnya "
                "taichi.aot_engine._raise_native_engine_error(), tanpa memeriksa apakah "
                "native_bridge.last_error() benar-benar berisi pesan.",
                "Pesan native sudah dikonsumsi (clear_last_error) sebelum dilaporkan.",
                "Kegagalan terjadi di sisi Python (lifecycle/teardown), bukan di kernel.",
            ),
            checks=(
                "Baca ulang pemanggil helper: bila last_error kosong, jangan perlakukan sebagai fault native.",
                _check_native_error(),
                "Tambahkan guard: `msg = native_bridge.last_error(handle); if msg: raise ...`.",
                _check_fresh_process(),
            ),
            docs="ai_governance/engine_audit_observations.md",
            priority=99,
        ),
    ),
    (
        lambda text, ctx: "native aot error" in text,
        Hint(
            id="TAICHI-NATIVE-ERROR",
            title="Runtime native AOT mengembalikan error",
            severity="tinggi",
            causes=(
                "Artefak TCM tidak cocok target/ABI backend aktif.",
                "Context GPU hilang (TDR/driver reset) atau memori perangkat habis.",
                "Argument graph tidak sesuai kontrak DynamicArg (shape/dtype/vector).",
            ),
            checks=(
                _check_native_error(),
                _check_backend(),
                "Jalankan ulang di proses baru dengan artefak target yang sama.",
                "Validasi ABI: `python -m taichi_vision.taichi_algorithm.aot_py.validate_tcm_abi --help`",
            ),
            docs="ai_governance/TCM_ABI_ROADMAP.md",
            priority=90,
        ),
    ),
    (
        lambda text, ctx: "could not load" in text or "load_aot_module" in text,
        Hint(
            id="TAICHI-TCM-LOAD",
            title="Artefak TCM gagal dimuat ke runtime native",
            severity="tinggi",
            causes=(
                "TCM dibangun untuk arch/OS/vendor/ABI berbeda.",
                "TI_LIB_DIR atau DLL bridge tidak menunjuk ke runtime yang benar.",
                "File TCM korup/terpotong atau bukan arsip yang didukung.",
            ),
            checks=(
                _check_artifacts(),
                "Pastikan `AOT_ARCH` sama dengan target saat kompilasi TCM.",
                "Hindari mencampur artefak dari profil build berbeda.",
                _check_native_error(),
            ),
            docs="taichi_vision/documentation/BUILD_AND_VALIDATION.md",
            priority=88,
        ),
    ),
    (
        lambda text, ctx: "no native aot bridge for target" in text,
        Hint(
            id="TAICHI-BRIDGE-MISSING",
            title="DLL bridge native tidak ditemukan untuk target aktif",
            severity="kritis",
            causes=(
                "`AOT_ENGINE_DLL` salah/typo.",
                "Folder `aot_dll/<backend>` tidak memuat DLL untuk arch proses (x64 vs arm64).",
                "Backend aktif tidak memiliki bridge terpasang.",
            ),
            checks=(
                "Cetak path kandidat: `python -c \"import taichi.native_bridge as b; "
                "print(list(b._bridge_candidates('cuda','cuda_x86_64_windows_nvidia')))\"",
                "Pastikan proses Python dan DLL sama-sama 64-bit.",
                "Set `AOT_ENGINE_DLL` ke path DLL yang benar lalu ulangi.",
            ),
            docs="taichi_vision/documentation/ARCHITECTURE.md",
            priority=95,
        ),
    ),
    (
        lambda text, ctx: any(
            token in text
            for token in ("out of memory", "outofmemory", "allocation failed", "oom")
        ),
        Hint(
            id="TAICHI-OOM",
            title="Alokasi memori perangkat/host gagal (OOM)",
            severity="tinggi",
            causes=(
                "Ukuran frame x jumlah burst melebihi VRAM/RAM pada device aktif.",
                "Buffer resident lama belum dilepas sebelum alokasi baru.",
                "Tile/patch size terlalu besar untuk perangkat.",
            ),
            checks=(
                _check_backend(),
                "Kurangi jumlah frame per batch atau aktifkan pemrosesan tile.",
                "Reclaim buffer resident sebelum upload batch berikutnya.",
                "Pastikan setiap buffer intermediate di-release setelah sync.",
            ),
            docs="taichi_vision/documentation/ARCHITECTURE.md",
            priority=85,
        ),
    ),
    (
        lambda text, ctx: any(
            token in text
            for token in (
                "illegal memory access",
                "device lost",
                "unspecified launch failure",
                "cuda error",
                "tdr",
                "driver reset",
            )
        ),
        Hint(
            id="TAICHI-DEVICE-LOST",
            title="Device GPU mengalami fault atau context hilang",
            severity="kritis",
            causes=(
                "Kernel melewati batas waktu driver (TDR) karena tile terlalu besar.",
                "Akses memori di luar batas (out-of-bounds) di graph native.",
                "Driver GPU crash/reset; context native tidak berlaku lagi.",
            ),
            checks=(
                "Ulangi di proses baru; context lama tidak dapat dipulihkan.",
                "Turunkan ukuran tile/overlap dan bandingkan dengan full-frame.",
                "Periksa log Event Viewer NVIDIA/AMD pada waktu kejadian.",
                _check_fresh_process(),
            ),
            docs="ai_governance/engine_audit_observations.md",
            priority=92,
        ),
    ),
    (
        lambda text, ctx: any(
            token in text
            for token in (
                "no longer valid",
                "old runtime generation",
                "already released",
                "was already transferred",
                "closed, reinitialized",
            )
        ),
        Hint(
            id="TAICHI-BUFFER-STALE",
            title="Buffer/handle dipakai setelah release atau lintas generasi runtime",
            severity="tinggi",
            causes=(
                "Buffer dipakai setelah `release()`/`destroy()`.",
                "Engine di-reinit sehingga `engine_generation` berubah.",
                "Ownership buffer dipindahkan (mis. ResidentConfidence.device()).",
            ),
            checks=(
                "Cek `_released`, `handle is None`, dan `engine_generation` sebelum akses.",
                "Pastikan `engine.sync()` selesai sebelum melepas buffer intermediate.",
                "Jangan mencampur buffer dari engine/backend berbeda.",
            ),
            docs="taichi_vision/documentation/ARCHITECTURE.md",
            priority=84,
        ),
    ),
    (
        lambda text, ctx: any(
            token in text
            for token in (
                "shape mismatch",
                "channel mismatch",
                "size mismatch",
                "expected ",
                "got ",
                "requires same-owner",
            )
        )
        and ("mismatch" in text or "expected" in text or "requires" in text),
        Hint(
            id="TAICHI-CONTRACT",
            title="Kontrak shape/dtype/ownership tidak terpenuhi",
            severity="sedang",
            causes=(
                "Shape/dtype input tidak sesuai metadata model atau artefak TCM.",
                "Buffer berasal dari engine/owner lain.",
                "Vector layout (is_vector/vector_dim) tidak konsisten dengan ABI.",
            ),
            checks=(
                "Bandingkan `shape`, `dtype`, `is_vector`, `vector_dim` dengan metadata artefak.",
                "Cetak `session.get_inputs()` dan metadata graph sebelum dispatch.",
                "Gunakan `scale_homography` bila koordinat berasal dari resolusi berbeda.",
            ),
            docs="taichi_vision/documentation/API_USAGE.md",
            priority=70,
        ),
    ),
    (
        lambda text, ctx: any(
            token in text
            for token in (
                "graph not found",
                "has no graph",
                "has no attribute",
                "aot_graph_available",
                "unsupported argument type",
            )
        ),
        Hint(
            id="TAICHI-GRAPH-CONTRACT",
            title="Nama graph/tipe argumen tidak cocok dengan artefak",
            severity="sedang",
            causes=(
                "Nama graph tidak mengikuti `{family}_{operation}_{variant}` di tiga tempat "
                "(compiler, registry, wrapper).",
                "Artefak tidak memuat graph yang dipanggil.",
                "Tipe argumen bukan GraphBuffer/int/float sesuai ABI.",
            ),
            checks=(
                _check_artifacts(),
                "Pastikan nama graph identik di compiler, job registry, dan pemanggil.",
                "Periksa daftar graph di dalam TCM (graphs.tcb/graphs.json).",
            ),
            docs="ai_governance/GLOBAL_RULES.md",
            priority=72,
        ),
    ),
    (
        lambda text, ctx: any(
            token in text
            for token in ("unsupported backend", "backend mismatch", "vendor mismatch")
        ),
        Hint(
            id="TAICHI-BACKEND-MISMATCH",
            title="Backend/vendor aktif tidak sesuai artefak atau konfigurasi",
            severity="tinggi",
            causes=(
                "Env backend diubah setelah `import taichi` pertama.",
                "Artefak untuk backend lain dimuat (mis. `_cuda.tcm` di CPU).",
                "Vendor terdeteksi berbeda dari target build.",
            ),
            checks=(
                "Set `AOT_ARCH` sebelum import pertama.",
                "Cocokkan nama artefak `<model>_<backend>.tcm` dengan backend aktif.",
                _check_backend(),
            ),
            docs="taichi_vision/AOT_BACKEND_MATRIX.md",
            priority=80,
        ),
    ),
    (
        lambda text, ctx: any(
            token in text
            for token in (
                "winerror",
                "dll load failed",
                "permission denied",
                "access is denied",
                "file is being used",
            )
        ),
        Hint(
            id="TAICHI-FILE-LOCK",
            title="DLL/artefak terkunci atau gagal dimuat oleh OS",
            severity="sedang",
            causes=(
                "DLL masih dipetakan proses lain (build ulang saat app berjalan).",
                "Hak akses file/folder terbatas.",
                "Dependensi DLL (CUDA/Vulkan loader) tidak ditemukan.",
            ),
            checks=(
                "Tutup proses yang memakai DLL/artefak lalu ulangi.",
                "Gunakan `Get-ChildItem -Force` untuk memeriksa ACL folder.",
                "Pastikan loader CUDA/Vulkan tersedia di PATH atau TI_LIB_DIR.",
            ),
            priority=60,
        ),
    ),
    (
        lambda text, ctx: "recursion" in text,
        Hint(
            id="TAICHI-RECURSION",
            title="Rekursi tak terbatas di lapisan Python runtime",
            severity="tinggi",
            causes=(
                "Dua helper saling memanggil (mis. `_decide_memory_domain` dan "
                "`get_memory_status`).",
                "`__getattr__`/property saling merujuk tanpa guard.",
            ),
            checks=(
                "Cari pasangan fungsi yang saling memanggil di traceback.",
                "Tambahkan parameter status yang sudah dihitung atau guard reentrancy.",
            ),
            docs=".commandcode/skills/pixel-refine-governance/SKILL.md",
            priority=75,
        ),
    ),
    (
        lambda text, ctx: "watchdog" in text or "stale" in text and "watch" in text,
        Hint(
            id="TAICHI-WATCHDOG",
            title="Watchdog runtime menganggap sesi idle/stale",
            severity="sedang",
            causes=(
                "Sesi tanpa aktivitas melewati batas idle sehingga resource direklaim.",
                "Watchdog berjalan di thread yang salah.",
            ),
            checks=(
                "Nonaktifkan sementara idle reclamation lewat env watchdog untuk isolasi.",
                "Pastikan reklamasi tidak dipanggil dari thread watchdog.",
            ),
            priority=55,
        ),
    ),
    (
        lambda text, ctx: "native bridge allocation failed" in text,
        Hint(
            id="TAICHI-BRIDGE-ALLOC",
            title="Bridge native gagal mengalokasikan buffer",
            severity="tinggi",
            causes=(
                "VRAM tidak cukup pada device aktif.",
                "Flag host-accessible tidak cocok dengan driver.",
            ),
            checks=(
                _check_backend(),
                "Kurangi ukuran buffer dan ulangi untuk memastikan batas memori.",
            ),
            priority=82,
        ),
    ),
)

_GENERIC = Hint(
    id="TAICHI-GENERIC",
    title="Fault runtime taichi tanpa pola yang dikenali",
    severity="sedang",
    causes=(
        "Kombinasi state runtime belum pernah tercatat di registry hint.",
        "Fault berasal dari lapisan aplikasi yang memanggil runtime.",
    ),
    checks=(
        "Periksa laporan JSON: frames, argumen, env, dan native error.",
        "Reproduksi di proses baru dengan artefak target yang sama.",
        _check_backend(),
    ),
    docs="taichi_vision/documentation/ARCHITECTURE.md",
    priority=10,
)


def resolve_hints(
    exc_type: str, message: str, context: dict[str, Any]
) -> list[Hint]:
    """Return matching hints ordered by priority (highest first)."""

    text = f"{exc_type}: {message}".lower()
    matched: list[Hint] = []
    for predicate, hint in HINT_RULES:
        try:
            if predicate(text, context):
                matched.append(hint)
        except Exception:
            continue
    if not matched:
        matched.append(_GENERIC)
    matched.sort(key=lambda hint: hint.priority, reverse=True)
    return matched


def iter_hints() -> Iterable[Hint]:
    for _predicate, hint in HINT_RULES:
        yield hint
    yield _GENERIC
