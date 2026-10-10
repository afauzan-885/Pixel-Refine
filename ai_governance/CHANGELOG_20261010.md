# Changelog — 2026-10-10

Ringkasan perubahan working tree sejak `79c9327`, disiapkan untuk commit.

## Perubahan

- Satukan katalog algoritma alignment, denoising, super-resolution, dan HDR beserta alias, batas konteks, provider parameter, dan routing worker.
- Tambahkan runtime pipeline streaming dengan batas prefetch/in-processing, pembatalan, lifecycle resource, dan telemetry queue; provider RAW/RGB mendukung input byte dan reuse buffer CFA.
- Perbaiki alur Bulk: materialisasi batch bertahap, thumbnail berbasis viewport, cache panel terbatas, progress lintas format, ETA hingga export, reuse output lengkap dengan identitas nama yang tepat, serta copy export yang diverifikasi ukuran dan SHA-256.
- Samakan dispatch dan parameter antara halaman batch/bulk; worker menyiapkan environment backend/device serta penanganan kompatibilitas backend. Tambahkan Block Flow prefilter dan jalur routing terkait.
- Pertahankan pemisahan analysis proxy dari carrier RAW/RGB pada pemrosesan resident, reuse workspace plane CFA, dan kembalikan path output Splat SR secara eksplisit.
- Tambahkan `AOTEngine.write_into()` untuk menulis ke buffer yang sudah dialokasikan. Sesuaikan `box_filter()` untuk storage RGB HWC/vec3 dan pastikan buffer temporer dilepas setelah graph selesai atau gagal.
- Hapus hasil cache CPU AOT yang telah diminta dibersihkan. Artefak target `spatial_rgb_mean_v1` dipertahankan.
- Jadikan `UILibrary` entry point kanonik untuk GenericUILibrary PySide6; tambahkan `StyleSpec`, fixture kontrak, dan pemeriksaan conformance API, behavior, serta style. Perbarui panel, settings, dan layout terkait.
- Perbaiki project archive agar snapshot kosong tetap valid dan error schema parsial ditangani eksplisit. Tambahkan penyimpanan snapshot pengaturan saat Start dan opsi queue di settings.
- Hapus salinan eksperimen `raw-native-development/` yang sudah tidak dipakai.
- Arsipkan snapshot registry memori assistant, aturan kerja, dan skills secara lokal di `ai_governance/assistant_backup/20261010/`; folder backup diabaikan Git sesuai permintaan.
- Tambahkan tes fokus untuk katalog, worker, pipeline, bulk ETA/progress/export, archive, resident quality, Block Flow, Splat SR, AOT buffer layout, dan GenericUILibrary.

## Verifikasi dan batas bukti

- `git diff --check` diperiksa sebelum staging.
- Tes tidak dijalankan untuk commit ini. Tes yang ditambahkan tercatat sebagai perubahan, bukan hasil verifikasi baru.
- Cache `.cpu_aot_cache` berisi file yang dilacak Git; penghapusannya tercatat sebagai penghapusan file. Empat artefak `.tcm` `spatial_rgb_mean_v1` dipulihkan dan dipertahankan.
- Snapshot pemulihan di `backups/` tidak dimasukkan ke commit.
