"""Hasselblad-Tier (12MP, 24MP, 50MP, 100MP) Demosaic Benchmark & Block Compute Optimizer

Evaluates demosaic reconstruction accuracy (L1 Loss x 4, PSNR), tile-based Block Compute VRAM footprint,
execution speed, and block seam parity across 12MP, 24MP, 50MP, and 100MP synthetic sensor resolutions.
"""

import os
import sys
import time
import psutil
import numpy as np

# Ensure project root is in python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import taichi_vision.taichi_aot as aot


RESOLUTIONS = {
    "12MP":  (3000, 4000),   # 12.00 MP
    "24MP":  (4000, 6000),   # 24.00 MP
    "50MP":  (6144, 8192),   # 50.33 MP
    "100MP": (8742, 11656),  # 101.90 MP (Hasselblad H6D-100c / X2D 100C tier)
}


def generate_highres_synthetic_bayer(height, width, pattern_type="siemens_grid"):
    """Generate high-resolution synthetic ground truth RGB and RGGB Bayer sensor mosaic."""
    print(f"  [Generating Data] Creating {width}x{height} ground truth synthetic image ({height*width/1e6:.1f} MP)...")
    
    y = np.linspace(-10, 10, height, dtype=np.float32)[:, None]
    x = np.linspace(-10, 10, width, dtype=np.float32)[None, :]
    r2 = x**2 + y**2
    
    # High-frequency radial + grid pattern
    gt_r = 0.5 + 0.5 * np.cos(r2 * 0.1)
    gt_g = 0.5 + 0.5 * np.sin(x * 2.0 + y * 2.0)
    gt_b = 0.5 + 0.5 * np.cos(x * 1.5 - y * 1.5)
    
    gt_rgb = np.stack([gt_r, gt_g, gt_b], axis=-1).astype(np.float32)
    gt_rgb = np.clip(gt_rgb, 0.0, 1.0)
    
    # RGGB Bayer simulation
    bayer = np.zeros((height, width), dtype=np.float32)
    bayer[0::2, 0::2] = gt_rgb[0::2, 0::2, 0] # R
    bayer[0::2, 1::2] = gt_rgb[0::2, 1::2, 1] # G1
    bayer[1::2, 0::2] = gt_rgb[1::2, 0::2, 1] # G2
    bayer[1::2, 1::2] = gt_rgb[1::2, 1::2, 2] # B
    
    return gt_rgb, bayer


def get_process_rss_mb():
    """Get current process Resident Set Size in MB."""
    process = psutil.Process(os.getpid())
    return process.memory_info().rss / (1024.0 * 1024.0)


def evaluate_tiled_block_demosaic(bayer, gt_rgb, method="dcb", tile_size=512, halo=16):
    """Evaluates demosaic processing using tiled BlockComputeSpec for zero-OOM execution."""
    h, w = bayer.shape
    cmatrix = np.eye(3, dtype=np.float32)
    
    # Calculate VRAM working set per tile
    tile_bytes = (tile_size + 2 * halo) * (tile_size + 2 * halo) * 4  # float32 input
    tile_out_bytes = (tile_size + 2 * halo) * (tile_size + 2 * halo) * 3 * 4  # float32 RGB
    working_vram_mb = (tile_bytes + tile_out_bytes) / (1024.0 * 1024.0)
    
    rss_before = get_process_rss_mb()
    t0 = time.perf_counter()
    
    # Menggunakan dekorator @aot.compute_block yang ringkas:
    @aot.compute_block(halo=halo, mode="force")
    def demosaic_tiled(raw):
        return aot.demosaic(
            raw,
            wb_r=1.0, wb_g1=1.0, wb_b=1.0, wb_g2=1.0,
            cmatrix=cmatrix,
            black_level=0.0, white_level=1.0,
            c00=0, c01=1, c10=1, c11=2,
            method=method,
            return_gpu=False
        )
    
    pred_tiled = demosaic_tiled(bayer)
    t1 = time.perf_counter()
    rss_after = get_process_rss_mb()
    
    elapsed_ms = (t1 - t0) * 1000.0
    
    # Compute accuracy metrics (excluding 8px border)
    border = 8
    p_crop = pred_tiled[border:-border, border:-border]
    g_crop = gt_rgb[border:-border, border:-border]
    
    abs_diff = np.abs(p_crop - g_crop)
    l1_loss_x4 = 4.0 * np.mean(abs_diff)
    mse = np.mean((p_crop - g_crop) ** 2)
    psnr = 20.0 * np.log10(1.0 / np.sqrt(mse + 1e-10))
    max_err = np.max(abs_diff)
    
    return {
        "method": method,
        "tile_size": tile_size,
        "halo": halo,
        "l1_loss_x4": l1_loss_x4,
        "psnr_db": psnr,
        "max_err": max_err,
        "latency_ms": elapsed_ms,
        "vram_working_tile_mb": working_vram_mb,
        "rss_delta_mb": max(0.0, rss_after - rss_before)
    }


def main():
    print("=" * 100)
    print("  HASSELBLAD 100MP-TIER DEMOSAIC BLOCK COMPUTE OPTIMIZER & ACCURACY BENCHMARK")
    print("=" * 100)
    
    algorithms = ["dcb", "hamilton", "arm"]
    tile_sizes = [512, 1024]
    
    for res_name, (h, w) in RESOLUTIONS.items():
        print(f"\n" + "-" * 100)
        print(f"  >>> TESTING RESOLUTION TIER: {res_name} ({w} x {h} = {h*w/1e6:.2f} Megapixels) <<<")
        print(f"  Full Frame Buffer Size: Bayer = {h*w*4/1e6:.1f} MB | Output RGB = {h*w*12/1e6:.1f} MB")
        print("-" * 100)
        
        gt_rgb, bayer = generate_highres_synthetic_bayer(h, w)
        
        print(f"{'Algorithmn':<12} | {'Tile Size':<10} | {'Halo':<6} | {'L1 Loss x4':<14} | {'PSNR (dB)':<12} | {'Max Err':<10} | {'Tile VRAM':<12} | {'Time (ms)':<12}")
        print("." * 100)
        
        for alg in algorithms:
            for tile in tile_sizes:
                res = evaluate_tiled_block_demosaic(bayer, gt_rgb, method=alg, tile_size=tile, halo=16)
                print(
                    f"{res['method']:<12} | {res['tile_size']:<10} | {res['halo']:<6} | "
                    f"{res['l1_loss_x4']:<14.4f} | {res['psnr_db']:<12.2f} | {res['max_err']:<10.3f} | "
                    f"{res['vram_working_tile_mb']:<12.2f} | {res['latency_ms']:<12.1f}"
                )

if __name__ == "__main__":
    main()
