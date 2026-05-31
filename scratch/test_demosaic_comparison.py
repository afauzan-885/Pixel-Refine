import os
import sys
import time
import numpy as np
import cv2
import rawpy

# Pastikan path modul utama bisa diimpor
file_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(file_dir, "../"))
if project_root not in sys.path:
    sys.path.append(project_root)

import pixel_refine_desktop.enhance_stack.core.algorithm.taichi_aot as ta_aot
from pixel_refine_desktop.enhance_stack.core.algorithm.taichi_aot.engine import engine


def main():
    test_path = "test_algorithm/IMG_20250423_160105_B001.dng"

    if not os.path.exists(test_path):
        print(f"Error: File {test_path} tidak ditemukan!")
        return

    # Paksa bongkar modul cache lama agar memuat berkas TCM yang baru dikompilasi
    ta_aot.unload_all_modules()

    print("=" * 60)
    print("Mengekstrak RAW Bayer & Mengunggah ke GPU Buffer...")
    print("=" * 60)

    # 1. Ekstrak data RAW sekali saja di awal
    with rawpy.imread(test_path) as raw:
        bayer_cpu = raw.raw_image.astype(np.float32)
        bl = float(raw.black_level_per_channel[0])
        wl = float(raw.white_level) * 0.98
        wb_np = np.array(raw.camera_whitebalance, dtype=np.float32)
        if len(wb_np) == 4:
            if wb_np[3] <= 0.01:
                wb_np[3] = wb_np[1]
            g_gain = (wb_np[1] + wb_np[3]) / 2.0
            wb_np /= g_gain
        else:
            wb_np = np.array([1.5, 1.0, 2.0, 1.0], dtype=np.float32)
        wb_r, wb_g1, wb_b, wb_g2 = wb_np[0], wb_np[1], wb_np[2], wb_np[3]
        c00 = int(raw.raw_colors[0, 0])
        c01 = int(raw.raw_colors[0, 1])
        c10 = int(raw.raw_colors[1, 0])
        c11 = int(raw.raw_colors[1, 1])
        cmatrix = raw.color_matrix[:, :3].astype(np.float32)

    h, w = bayer_cpu.shape[:2]
    print(f"Dimensi Gambar Asli: {w}x{h} ({w*h/1e6:.1f} Megapiksel)")
    print(
        f"Dimensi Gambar Half-Res: {w//2}x{h//2} ({(w//2)*(h//2)/1e6:.1f} Megapiksel)"
    )

    # Unggah data bayer & cmatrix ke VRAM GPU sekali saja!
    bayer_gpu = ta_aot.InputArray(bayer_cpu)
    cmatrix_gpu = ta_aot.InputArray(cmatrix)

    # Alokasikan output buffer di VRAM sekali saja (Pre-allocated buffers)
    dst_1ch_gpu = engine.allocate((h, w), dtype=np.float32)
    dst_half_res_gpu = engine.allocate((h // 2, w // 2), dtype=np.float32)
    dst_rgb_half_gpu = engine.allocate((h // 2, w // 2, 3), dtype=np.float32)
    dst_3ch_gpu = engine.allocate((h, w, 3), dtype=np.float32)

    # Lakukan pemanasan (Warmup)
    print("\nWarmup / Pemanasan Modul AOT GPU...")
    try:
        ta_aot.hamilton_demosaic_1channel(
            bayer_gpu,
            wb_r,
            wb_g1,
            wb_b,
            wb_g2,
            bl,
            wl,
            c00,
            c01,
            c10,
            c11,
            return_gpu=True,
            dst=dst_1ch_gpu,
        )
        ta_aot.demosaic(
            bayer_gpu,
            wb_r=wb_r,
            wb_g1=wb_g1,
            wb_b=wb_b,
            wb_g2=wb_g2,
            black_level=bl,
            white_level=wl,
            c00=c00,
            c01=c01,
            c10=c10,
            c11=c11,
            method="half-res",
            return_gpu=True,
            dst=dst_half_res_gpu,
        )
        ta_aot.demosaic(
            bayer_gpu,
            wb_r=wb_r,
            wb_g1=wb_g1,
            wb_b=wb_b,
            wb_g2=wb_g2,
            cmatrix=cmatrix_gpu,
            black_level=bl,
            white_level=wl,
            c00=c00,
            c01=c01,
            c10=c10,
            c11=c11,
            method="rgb-half-res",
            return_gpu=True,
            dst=dst_rgb_half_gpu,
        )
        ta_aot.hamilton_demosaic(
            bayer_gpu,
            wb_r,
            wb_g1,
            wb_b,
            wb_g2,
            cmatrix_gpu,
            bl,
            wl,
            c00,
            c01,
            c10,
            c11,
            return_gpu=True,
            dst=dst_3ch_gpu,
        )
        engine.sync()
        print("Warmup GPU selesai dengan sukses.")
    except Exception as e:
        print(f"Gagal saat warmup GPU: {e}")
        import traceback

        traceback.print_exc()
        return

    # --- 10 ITERASI MURNI GPU HALF-RES (GREEN SUB-SAMPLING) ---
    print("\n[1] Menjalankan 10 Iterasi Komputasi GPU Half-Res (Green Sub-Sampling)...")
    times_half = []
    for i in range(10):
        t0 = time.perf_counter()
        ta_aot.demosaic(
            bayer_gpu,
            wb_r=wb_r,
            wb_g1=wb_g1,
            wb_b=wb_b,
            wb_g2=wb_g2,
            black_level=bl,
            white_level=wl,
            c00=c00,
            c01=c01,
            c10=c10,
            c11=c11,
            method="half-res",
            return_gpu=True,
            dst=dst_half_res_gpu,
        )
        engine.sync()
        t_elapsed = (time.perf_counter() - t0) * 1000
        times_half.append(t_elapsed)
        print(f"  Iterasi {i+1:2d}: {t_elapsed:.2f} ms")

    avg_half = np.mean(times_half)
    print(f"--> Rata-rata Murni GPU Half-Res (Green): {avg_half:.2f} ms")

    # --- 10 ITERASI MURNI GPU HALF-RES RGB (FULL RGB HALF-SIZE) ---
    print("\n[2] Menjalankan 10 Iterasi Komputasi GPU Half-Res RGB...")
    times_rgb_half = []
    for i in range(10):
        t0 = time.perf_counter()
        ta_aot.demosaic(
            bayer_gpu,
            wb_r=wb_r,
            wb_g1=wb_g1,
            wb_b=wb_b,
            wb_g2=wb_g2,
            cmatrix=cmatrix_gpu,
            black_level=bl,
            white_level=wl,
            c00=c00,
            c01=c01,
            c10=c10,
            c11=c11,
            method="rgb-half-res",
            return_gpu=True,
            dst=dst_rgb_half_gpu,
        )
        engine.sync()
        t_elapsed = (time.perf_counter() - t0) * 1000
        times_rgb_half.append(t_elapsed)
        print(f"  Iterasi {i+1:2d}: {t_elapsed:.2f} ms")

    avg_rgb_half = np.mean(times_rgb_half)
    print(f"--> Rata-rata Murni GPU Half-Res RGB: {avg_rgb_half:.2f} ms")

    # --- 10 ITERASI MURNI GPU 1-CHANNEL ---
    print("\n[3] Menjalankan 10 Iterasi Komputasi GPU 1-Channel (Grayscale full)...")
    times_1ch = []
    for i in range(10):
        t0 = time.perf_counter()
        ta_aot.hamilton_demosaic_1channel(
            bayer_gpu,
            wb_r,
            wb_g1,
            wb_b,
            wb_g2,
            bl,
            wl,
            c00,
            c01,
            c10,
            c11,
            return_gpu=True,
            dst=dst_1ch_gpu,
        )
        engine.sync()
        t_elapsed = (time.perf_counter() - t0) * 1000
        times_1ch.append(t_elapsed)
        print(f"  Iterasi {i+1:2d}: {t_elapsed:.2f} ms")

    avg_1ch = np.mean(times_1ch)
    print(f"--> Rata-rata Murni GPU 1-Channel: {avg_1ch:.2f} ms")

    # --- 10 ITERASI MURNI GPU 3-CHANNEL ---
    print("\n[4] Menjalankan 10 Iterasi Komputasi GPU 3-Channel (Full RGB)...")
    times_3ch = []
    for i in range(10):
        t0 = time.perf_counter()
        ta_aot.hamilton_demosaic(
            bayer_gpu,
            wb_r,
            wb_g1,
            wb_b,
            wb_g2,
            cmatrix_gpu,
            bl,
            wl,
            c00,
            c01,
            c10,
            c11,
            return_gpu=True,
            dst=dst_3ch_gpu,
        )
        engine.sync()
        t_elapsed = (time.perf_counter() - t0) * 1000
        times_3ch.append(t_elapsed)
        print(f"  Iterasi {i+1:2d}: {t_elapsed:.2f} ms")

    avg_3ch = np.mean(times_3ch)
    print(f"--> Rata-rata Murni GPU 3-Channel: {avg_3ch:.2f} ms")

    # --- MEMBUAT PREVIEW ---
    print("\n[5] Menyalin Hasil Akhir & Membuat Gambar Preview Gabungan...")
    try:
        res_half_cpu = dst_half_res_gpu.to_numpy()
        res_rgb_half_cpu = dst_rgb_half_gpu.to_numpy()
        res_1ch_cpu = dst_1ch_gpu.to_numpy()
        res_3ch_cpu = dst_3ch_gpu.to_numpy()

        img_half = np.clip(res_half_cpu * 255.0, 0, 255).astype(np.uint8)
        img_half_bgr = cv2.cvtColor(img_half, cv2.COLOR_GRAY2BGR)
        # Upscale half-res ke dimensi asli secara visual agar pas di-hstack
        img_half_bgr_resized = cv2.resize(
            img_half_bgr, (w, h), interpolation=cv2.INTER_NEAREST
        )

        img_rgb_half = np.clip(res_rgb_half_cpu * 255.0, 0, 255).astype(np.uint8)
        img_rgb_half_bgr = cv2.cvtColor(img_rgb_half, cv2.COLOR_RGB2BGR)
        img_rgb_half_bgr_resized = cv2.resize(
            img_rgb_half_bgr, (w, h), interpolation=cv2.INTER_NEAREST
        )

        img_1ch = np.clip(res_1ch_cpu * 255.0, 0, 255).astype(np.uint8)
        img_1ch_bgr = cv2.cvtColor(img_1ch, cv2.COLOR_GRAY2BGR)

        img_3ch = np.clip(res_3ch_cpu * 255.0, 0, 255).astype(np.uint8)
        img_3ch_bgr = cv2.cvtColor(img_3ch, cv2.COLOR_RGB2BGR)

        # Tambahkan teks label info performa murni
        font = cv2.FONT_HERSHEY_SIMPLEX
        cv2.putText(
            img_half_bgr_resized,
            f"Half-Res Green Sub-sampling",
            (50, 150),
            font,
            3,
            (0, 0, 255),
            8,
            cv2.LINE_AA,
        )
        cv2.putText(
            img_half_bgr_resized,
            f"Avg: {avg_half:.2f}ms",
            (50, 280),
            font,
            3,
            (0, 0, 255),
            8,
            cv2.LINE_AA,
        )

        cv2.putText(
            img_rgb_half_bgr_resized,
            f"Half-Res RGB",
            (50, 150),
            font,
            3,
            (255, 0, 255),
            8,
            cv2.LINE_AA,
        )
        cv2.putText(
            img_rgb_half_bgr_resized,
            f"Avg: {avg_rgb_half:.2f}ms (NEW!)",
            (50, 280),
            font,
            3,
            (255, 0, 255),
            8,
            cv2.LINE_AA,
        )

        cv2.putText(
            img_1ch_bgr,
            "Murni GPU 1-Channel (Grayscale)",
            (50, 150),
            font,
            3,
            (0, 255, 0),
            8,
            cv2.LINE_AA,
        )
        cv2.putText(
            img_1ch_bgr,
            f"Avg: {avg_1ch:.2f}ms",
            (50, 280),
            font,
            3,
            (0, 255, 0),
            8,
            cv2.LINE_AA,
        )

        cv2.putText(
            img_3ch_bgr,
            "Murni GPU 3-Channel (Full RGB)",
            (50, 150),
            font,
            3,
            (0, 255, 255),
            8,
            cv2.LINE_AA,
        )
        cv2.putText(
            img_3ch_bgr,
            f"Avg: {avg_3ch:.2f}ms",
            (50, 280),
            font,
            3,
            (0, 255, 255),
            8,
            cv2.LINE_AA,
        )

        # Jahit secara horizontal (4 Panel!)
        side_by_side = np.hstack(
            (img_half_bgr_resized, img_rgb_half_bgr_resized, img_1ch_bgr, img_3ch_bgr)
        )

        out_path = "scratch/demosaic_side_by_side.png"
        cv2.imwrite(out_path, side_by_side)
        print(f"--> Hasil komparasi 4 panel disimpan ke: {out_path}")

    except Exception as e:
        print(f"Gagal membuat gambar side-by-side: {e}")
        import traceback

        traceback.print_exc()

    # Bebaskan semua alokasi VRAM secara manual
    bayer_gpu.release()
    cmatrix_gpu.release()
    dst_1ch_gpu.release()
    dst_half_res_gpu.release()
    dst_rgb_half_gpu.release()
    dst_3ch_gpu.release()

    print("\n" + "=" * 60)
    print("ANALISIS KOMPARASI PERFORMA:")
    print(f"* 1. Half-Res Sub-sampling (Green): {avg_half:.2f} ms")
    print(f"* 2. Half-Res RGB                  : {avg_rgb_half:.2f} ms")
    print(f"* 3. Full-Res 1-Channel (Grayscale): {avg_1ch:.2f} ms")
    print(f"* 4. Full-Res 3-Channel (Full RGB) : {avg_3ch:.2f} ms")
    print("=" * 60)


if __name__ == "__main__":
    main()
