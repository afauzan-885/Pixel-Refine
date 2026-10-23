# Kontrol memori native ABI v1

Status: implementasi source S2 untuk review. C++ belum dikompilasi, native unit/integration test belum dijalankan, dan tidak ada bukti keuntungan performa atau coherency perangkat dari slice ini.

Header C publik tambahan: [native_memory_control.h](native_memory_control.h). Binding opsional: [native_memory_control.py](../../taichi_aot/native_memory_control.py). ABI lama dan signature export existing dipertahankan. Binary existing belum memuat export baru; binding memberi `NativeMemoryControlUnavailable` jika dipakai pada bridge lama.

## Memakai owner yang sudah ada

```python
from taichi_vision.taichi_aot.native_memory_control import NativeMemoryControl

# existing_engine adalah AOTEngine yang telah dimiliki aplikasi.
# Modul kontrol tidak membuat engine, menginisialisasi Taichi, atau memilih backend.
controls = NativeMemoryControl(existing_engine)
status = controls.snapshot()

# Batas dipilih aplikasi/MemoryPolicy yang sudah ada, bukan policy baru di binding.
controls.configure(
    budget_bytes=chosen_native_cap,
    cache_max_bytes=16 * 1024 * 1024,
    cache_max_entries=2,
)
trimmed = controls.trim()  # Target 0 byte/0 entry: kosongkan hanya cache idle privat.
```

Binding mengambil lock dan thread-ownership guard engine serta membaca runtime aktif pada setiap panggilan. Ia memakai `_LIB` dari modul engine yang **sudah dimuat**, tanpa import/lazy-init engine. Backend/runtime reinitialization memperoleh default native limits baru; binding tidak menerapkan ulang budget lama otomatis. Caller dapat menyediakan `library=` untuk bridge yang sudah dimuat, dan bertanggung jawab memasangkannya dengan owner runtime yang benar.

MemoryPolicy/MemoryGovernor dan pool caller Python tetap pemilik keputusan aplikasi. Kontrol baru adalah hard cap/logical telemetry serta cache scratch privat native; tidak mengubah allocator/policy pada protected engine. Tidak ada fallback CPU atau eviction buffer caller untuk memenuhi batas.

## Arti counter dan budget

Semua byte merupakan **ukuran requested/logical bridge**, bukan byte fisik driver atau peak VRAM. Cakupan adalah allocation yang melewati registry bridge, termasuk WIC image producer dan scratch readback privat. Allocation internal AOT module, kernel/RHI/driver scratch, metadata, allocator rounding/pool backing dan resource dari luar bridge tidak diukur atau dibatasi oleh cap ini.

- `retained_bytes`: kapasitas logis seluruh handle terdaftar, termasuk caller, staging privat, cache, mapped dan quarantine.
- `budget_charge_bytes = retained_bytes + pending_bytes + unresolved_bytes`. Semua kategori tersebut tetap memakai budget. `budget_bytes=0` berarti unlimited; overflow uint64 tetap ditolak.
- `live_bytes`: handle terdaftar yang bukan cached dan bukan quarantined. `caller_bytes` dan `private_staging_bytes` membagi retained berdasarkan provenance, termasuk quarantine. `idle_cache_bytes`, `mapped_bytes`, `quarantined_bytes`, `leased_private_bytes` adalah kategori state yang dapat overlap dengan provenance; jangan menjumlahkan seluruh field sebagai total baru. Count mengikuti kategori yang sama.
- `allocation_requests` dan `allocation_requested_bytes_total` menghitung request native allocation nonzero yang masuk ledger, termasuk yang ditolak budget dan cache misses; cache hits tidak membuat allocation baru. Counter kumulatif saturate dengan flag, tidak wrap.
- High water retained adalah known handle requested bytes. High water budget charge juga mencakup reservation yang mungkin dibatalkan. Keduanya bukan physical peak.
- `physical_bytes`, `driver_budget_bytes`, `in_flight_bytes` berisi `UINT64_MAX` dengan flag UNKNOWN; binding mengembalikan `None`. Nilai unknown tidak dilaporkan sebagai nol terukur.

Budget reservation disiapkan sebelum registry node/native allocation. Kegagalan host bookkeeping sebelum native dipanggil membatalkan reservation. Setelah native dipanggil, kegagalan **tanpa handle** tidak dapat dibedakan dari partial-output quarantine lower API. Requested charge tersebut menjadi `unresolved_bytes`/count secara konservatif. Ia tidak dihitung lagi sebagai known handle dan tidak bisa di-trim, di-reset dengan setter, atau dianggap safe-to-free.

Jika ada unresolved charge atau accounting invariant error, teardown menahan context beserta accounting dan memberikan error jelas. Known failed-free handles juga tetap quarantined seperti S1. Ini dapat mempertahankan resource/context sampai proses berakhir; recovery/reclamation universal tidak diklaim. Peningkatan budget atau unlimited tidak menghapus status unknown. Konteks baru tidak dibuat otomatis.

## Cache dan trim

Default cache **OFF** (`cache_max_bytes=cache_max_entries=0`). Mengaktifkan cache wajib memberikan kedua cap nonzero. Cache hanya menyimpan exact-size scratch readback internal; bukan allocation caller atau cache aplikasi umum.

Scratch baru atau yang diambil dari cache diberi lease internal. Ia baru dapat kembali ke cache setelah copy dan wait selesai, host mapping sudah di-unmap, lease dilepas, serta tidak quarantined. Entry yang mapped, leased, incomplete, quarantined atau berasal dari caller tidak eligible. Public map/read/write/copy/free/graph menolak handle privat. Lease ini hanya untuk scratch sinkron; native in-flight accounting universal tidak ditambahkan.

Release scratch melakukan admission terhadap kedua cap. Jika tidak muat atau cache disabled, scratch dilepas melalui wait/unmap/free guarded yang sama. Cache hits tetap charged dan tidak mengubah retained bytes; cache misses tunduk budget bersama caller/quarantine/unknown. Allocation yang gagal budget tidak mengusir cache otomatis; aplikasi boleh trim idle cache lalu mencoba ulang berdasarkan policy existing.

`trim(target_bytes=..., target_entries=...)` menghapus entry eligible sampai kedua target remaining-cache terpenuhi. Trim tidak menyentuh caller, mapped/leased scratch, quarantine atau unresolved charge. Ia mempertahankan completion wait sebelum free. Native failure dapat menghasilkan partial progress; `NativeMemoryControlError.partial` hanya berisi counter bila native memberi `valid=1`, dan retained quarantine tetap charged. Tidak ada LRU/performance guarantee.

Mengubah limits bersifat atomik dan tidak meng-evict resource. Konfigurasi di bawah charge/cache saat ini ditolak; trim eksplisit dahulu bila ingin menurunkan cap. Setting cache OFF ketika cache masih berisi entry juga ditolak sampai trim. Tidak ada worker reclaim/background policy baru.

CPU/CUDA metadata vector growth/slot reuse tetap kandidat terpisah yang memerlukan baseline dinamis. Free registry bridge tidak diklaim mengecilkan seluruh metadata backend, heap, atau pool fisik.

## Validasi yang tersedia

- [Pure binding tests](tests/test_native_memory_control_binding.py) memuat production binding langsung dari path, menggunakan fake lib dan owner/lock, tanpa import package engine/Taichi. Tes ini mencakup ABI/width handling, unknown values, owner lifecycle/guard, runtime/library reinitialization dan partial trim errors; tidak membuktikan C++/driver.
- [Native ledger tests](tests/native_memory_ledger_test.cpp) menguji helper produksi arithmetic/reservation/uncertain accounting, overflow, dual cache caps dan eligibility guards. Source native disiapkan, belum dikompilasi/dijalankan.
- [Deferred integration source](tests/test_native_memory_boundary_deferred.py) menambahkan budget rejection, cache reuse, snapshot transitions dan trim yang mempertahankan mapped caller. Tetap opt-in dengan rebuilt matching bridge/C API; tidak dijalankan dalam sesi no-compilation.
- Header v1 mempunyai version/size checks; reserved limits fields harus nol. Static layout assertions serta ctypes layout check bukan bukti ABI binary karena build/link belum dilakukan.
