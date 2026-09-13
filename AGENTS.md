# Pixel Refine Agent Entry Point & Global Governance

Dokumen ini adalah aturan global dan entry point terikat untuk setiap AI agent yang bekerja di Pixel Refine (termasuk Gemini, Antigravity, Codex, dan DeepSeek). Aturan ini otomatis dimuat pada setiap sesi percakapan.

Kontrak proyek lengkap tertera pada [`agen.md`](agen.md), dan tata kelola normatif berada di [`ai_governance/`](ai_governance/).

---

## 1. Urutan Otoritas Aturan

1. Instruksi langsung platform dan pengguna.
2. `AGENTS.md` (Aturan ini).
3. Dokumen normatif dalam `ai_governance/` (`GLOBAL_RULES.md`, `OPERATING_PROTOCOL.md`, `MULTI_AGENT_PROTOCOL.md`, dll.).
4. Dokumen arsitektur/kontrak proyek (`agen.md`, `skill.md`, `blueprint_project.md`).
5. Source code, konfigurasi aktif, dan bukti pengujian terkini.

---

## 2. Batas Perubahan (Change Boundaries)

- **Inspeksi Sebelum Berubah**: Selalu periksa `git status`, target, pemanggil (caller), import, konfigurasi, dan artefak terkait sebelum menyentuh kode.
- **Kompatibilitas API Publik**: Jaga API publik dan signature fungsi tetap kompatibel kecuali pengguna memberikan izin perubahan secara eksplisit.
- **Runtime Source of Truth**: `taichi_vision/taichi_aot/engine.py` adalah sumber kebenaran runtime tunggal. Dilarang mengubahnya tanpa persetujuan eksplisit pengguna.
- **Integritas di Atas Kecepatan**: Jalur block-compute yang belum tervalidasi wajib menggunakan jalur full-frame pada backend yang sama atau mengembalikan error yang jelas. **Dilarang keras melakukan silent fallback dari GPU ke CPU**.
- **Perlindungan Artefak**: Dilarang menghapus source, TCM, DLL/SO, BC, atau artefak target tanpa memverifikasi referensi runtime dan peran packaging-nya.

---

## 3. Kebenaran Teknis, Bukti, dan Pengujian

- **Klaim Wajib Berbukti**: Nyatakan backend, perangkat aktual, bentuk input (shape), dtype, perintah eksekusi, dan hasil yang diamati untuk setiap klaim performa, kompatibilitas, akurasi, atau kesiapan produksi.
- **Diferensiasi Backend**: Bedakan secara tegas hasil CPU, CUDA, Vulkan, dan OpenGL; hasil pada satu backend tidak membuktikan backend lain.
- **Tingkatan Bukti**: Bedakan 5 level bukti yang tidak setara: (1) artefak tersedia, (2) validasi statis, (3) eksekusi perangkat, (4) parity numerik, dan (5) validasi aplikasi.
- **Asumsi Komputasi**: Jangan menganggap preload batching sebagai komputasi GPU paralel, dan jangan memutuskan suatu graph aman ditile tanpa memeriksa halo, konteks global, reduksi, dan batas memori.
- **Taichi AOT & ABI**: Patuhi panduan di `ai_governance/skills/taichi-aot-dev/SKILL.md`. Jangan mencampur ABI LLVM/Taichi/bridge/TCM yang berbeda.
- **Lingkungan Pengujian**: Gunakan venv proyek (`venv`) untuk semua eksekusi dan pengujian Python.

---

## 4. Git dan Worktree Hygiene

- **Hormati Pekerjaan Pengguna**: Worktree dapat berisi uncommitted work milik pengguna. Dilarang mengubah, men-stage, me-revert, atau meng-commit file di luar lingkup tugas yang diminta.
- **DILARANG `git add -A` / `git add .`**: Selalu stage hanya file spesifik yang telah ditinjau dan relevan dengan tugas.
- **Validasi Pre-Commit**: Sebelum commit, jalankan validasi terkecil yang relevan dan periksa `git diff --check`.
- **Pencatatan Keputusan**: Jika ada keputusan desain yang mengubah kontrak proyek, dokumentasikan pada file aktif di `ai_governance/`.
- **Status Arsip**: Direktori `.qoder` dan `agen-docs` telah dipensiunkan; semua aturan dan knowledge baru wajib berada di `ai_governance/`.

---

## 5. Protokol Multi-Agent

- **Default Single-Agent**: Pixel Refine beroperasi dalam mode single-agent secara default.
- **Syarat Multi-Agent**: Sub-agent hanya boleh diluncurkan jika:
  1. Pengguna memberikan izin eksplisit untuk peluncuran multi-agent.
  2. Pengguna memberikan batas jumlah agent (`user_agent_limit`).
  3. Coordinator merumuskan cakupan kerja (coverage) tanpa tumpang tindih (dua agent tidak boleh mengedit file yang sama).
  4. Seluruh temuan dan penggabungan hasil diverifikasi oleh single coordinator.

---

## 6. Format Komunikasi dan Pelaporan Metrik (Wajib)

- Saat menyajikan hasil pengujian, benchmark, atau perbandingan performa/metrik kepada pengguna:
  - Gunakan format teks atau poin-poin langsung yang ringkas, bersih, dan mudah dibaca secara cepat.
  - **DILARANG** menggunakan format tabel Markdown yang rumit atau simbol LaTeX berlebihan (seperti `$\sim$`, `\text{...}`, dll.) yang menyulitkan pembacaan.
  - **Format Standar Wajib**:
    * **[Nama Metrik/Kategori]**:
      - Sebelum: `X ms` atau `X px`
      - Sesudah: **`Y ms`** atau **`Y px`** (keterangan peningkatan/status)
