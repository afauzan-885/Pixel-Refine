# Inspector Feedback — Iterasi 2, Static Review

## Verdict

**BLOCKED — belum dapat dinyatakan siap untuk build.** Perubahan berada dalam scope Fase 0 karena menambah override toolchain dan SDK pada [build_wheel.bat](../../fork_taichi/build_wheel.bat), yang mendukung pembekuan command build/provenance. Secara statis, path VS dan SDK yang dibutuhkan cocok dengan filesystem saat ini. Namun, [user steering](./status.json) melarang kompilasi dan meminta klarifikasi terpisah tentang JIT; pemanggilan `VsDevCmd`, discovery SDK oleh CMake/Clang, serta hasil build tidak dijalankan dan tetap belum terverifikasi.

## Temuan statis

- `fork_taichi` tetap pada HEAD `92bfb3ab88805872faa727a6521a3da8c37c2039`; `build_wheel.bat` adalah file tracked yang berubah. `Pixel-Refine` HEAD `06a15119c22d3b8941d8747d353843e5fb521905`. Review ini tidak mengubah file fork.
- Override `TI_VSDEVCMD` dapat menunjuk ke `D:\Program Files\Microsoft Visual Studio\2022\BuildTools\Common7\Tools\VsDevCmd.bat`, dan file itu ada. `cl.exe`, `link.exe`, `vcruntime.h`, `msvcprt.lib`, dan `libcmt.lib` pada instalasi BuildTools 14.42.34433 di path D: juga ada. Script tetap memakai default C: jika override tidak diberikan; path root `D:\Program Files\Microsoft Visual Studio` saja bukan path batch yang diterima. Ini pemeriksaan keberadaan path, bukan bukti environment MSVC berhasil disiapkan.
- `TI_WINDOWS_SDK_DIR` yang dibutuhkan script cocok dengan root ekstraksi `E:\APP Developer\Eel-Dance\builder-tools\windows-sdk-10.0.26100\extracted\Windows Kits\10`; `TI_WINDOWS_SDK_VERSION` harus `10.0.26100.0`. File `Windows.h`, `corecrt.h`, `sdkddkver.h`, `kernel32.lib`, dan `ucrt.lib` serta direktori `winrt` dan `cppwinrt` ada di lokasi yang dirujuk. Preflight script sendiri hanya mengecek `Windows.h` dan `kernel32.lib`; ia tidak mengecek `ucrt.lib` atau setiap direktori include yang kemudian ditambahkan.
- Perubahan drive mapping memperbaiki perilaku lama yang menjalankan `subst U: /d` tanpa syarat. Patch memeriksa apakah drive pilihan sudah ada, gagal dengan error bila terpakai, lalu hanya menghapus mapping setelah `subst` milik script berhasil dibuat. Saat review, `subst` tidak menampilkan mapping aktif dan drive fisik yang tampak adalah C:, D:, dan E:. Ini penilaian source dan snapshot lokal; tidak menguji race dengan proses lain atau perilaku pada mapped drive yang tidak tersedia.

## Risiko dan hal yang belum diverifikasi

- Checkout fork sudah memiliki [build](../../fork_taichi/build/), [_skbuild](../../fork_taichi/_skbuild/), dan [dist](../../fork_taichi/dist/). Direktori `dist` berisi [taichi-1.7.4+llvm20-cp312-cp312-win_amd64.whl](../../fork_taichi/dist/taichi-1.7.4+llvm20-cp312-cp312-win_amd64.whl), sama dengan default `TI_WHEEL_TAG=+llvm20` pada script. Perintah `bdist_wheel` tidak menetapkan direktori keluaran terisolasi dan script mengumumkan keluaran di `SOURCE_DIR\dist`; build berikutnya berisiko menimpa artefak dengan nama sama. Perilaku overwrite aktual belum dijalankan.
- Script mempertahankan blok `if defined TI_CLEAN` yang menghapus `SHORT_DRIVE\_skbuild`; karena drive tersebut dipetakan ke checkout source, ini menghapus `_skbuild` yang sudah ada jika variabel tersebut bernilai apa pun, termasuk nilai teks `0`. Jangan menganggap output saat ini terjaga jika `TI_CLEAN` diwarisi dari environment.
- Nama dan sintaks `TI_BUILD_DRIVE` tidak divalidasi sebagai huruf drive sebelum disisipkan ke perintah `subst`. Nilai salah diperkirakan menyebabkan `subst` gagal, tetapi alur gagal tidak dieksekusi.
- Env override SDK telah dibentuk sesuai root ekstraksi, tetapi tidak ada bukti statis bahwa CMake/Clang pada build aktual akan memakai variabel tersebut untuk semua komponen toolchain. Tidak ada JIT, tes, build, instalasi, atau modifikasi environment global yang dilakukan.

## Tindakan berikutnya

Sebelum build diizinkan, isolasi atau lindungi output `dist`/`build` yang ada dan ubah cleanup agar hanya berjalan pada nilai eksplisit yang benar-benar berarti aktif. Dokumentasikan bahwa `TI_VSDEVCMD` harus berisi path lengkap ke `VsDevCmd.bat`, serta validasi format `TI_BUILD_DRIVE` dan prasyarat SDK yang dipakai. Setelah user menjawab batas JIT dan mengizinkan eksekusi, uji di staging terpisah; jangan gunakan hasil statis ini sebagai bukti build, backend, akurasi, performa, atau readiness.
