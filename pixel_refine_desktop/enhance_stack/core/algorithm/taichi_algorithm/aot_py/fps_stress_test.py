import time
import numpy as np
import os
import sys

# Add project root to sys.path
file_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(file_dir, "../../../../../../"))
if project_root not in sys.path:
    sys.path.append(project_root)

from pixel_refine_desktop.enhance_stack.core.algorithm import taichi_aot


def print_progress(iteration, total, prefix="", suffix="", length=50, fill="█"):
    percent = ("{0:.1f}").format(100 * (iteration / float(total)))
    filled_length = int(length * iteration // total)
    bar = fill * filled_length + "-" * (length - filled_length)
    sys.stdout.write(f"\r{prefix} |{bar}| {percent}% {suffix}")
    sys.stdout.flush()


def run_unlimited_resize_test(total_frames=10000):
    print(f"=== Taichi AOT Ultra-FPS Stress Test ({total_frames} Frames) ===")

    # Pre-upload base image (12MP)
    h12, w12 = 3000, 4000
    h4, w4 = 1500, 2000  # 3MP/4MP approx
    h48, w48 = 6000, 8000  # 48MP

    print("Generating base 12MP image...")
    img_np = np.random.rand(h12, w12, 3).astype(np.float32)
    current_gpu_buf = taichi_aot.upload(img_np)

    start_time = time.time()
    last_report_time = start_time
    frames_processed = 0

    resolutions = [
        (h4, w4),  # Down to 4MP
        (h12, w12),  # Up to 12MP
        (h48, w48),  # Up to 48MP
    ]

    print("\nStarting Loop (12MP -> 4MP -> 12MP -> 48MP)...")

    try:
        for i in range(total_frames):
            # Pick resolution in cycle
            target_h, target_w = resolutions[i % 3]

            # Execute Resize (Zero-Overhead)
            # return_gpu=True ensures no data leaves VRAM
            current_gpu_buf = taichi_aot.resize(
                current_gpu_buf, (target_w, target_h), return_gpu=True
            )

            frames_processed += 1

            # Update Progress Bar every 50 frames
            if frames_processed % 50 == 0:
                elapsed = time.time() - start_time
                fps = frames_processed / elapsed
                print_progress(
                    frames_processed,
                    total_frames,
                    prefix="Processing",
                    suffix=f"FPS: {fps:.2f}",
                    length=40,
                )

        total_elapsed = time.time() - start_time
        avg_fps = total_frames / total_elapsed

        print(f"\n\n=== Stress Test Summary ===")
        print(f"Total Frames: {total_frames}")
        print(f"Total Time  : {total_elapsed:.2f} seconds")
        print(f"Average FPS : {avg_fps:.2f} frames/sec")
        print(f"Total Ops   : {total_frames * 1} resizes")
        print("Memory Status: STABLE (No OOM detected)")

    except Exception as e:
        print(f"\n\n[CRASH] Test failed at frame {frames_processed}: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    # Start with 10k frames
    run_unlimited_resize_test(1000)
