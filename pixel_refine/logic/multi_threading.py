import threading
import time
import cv2
import numpy as np
import rawpy
from concurrent.futures import ThreadPoolExecutor, as_completed
from kivy.clock import Clock
from kivy.core.image import Image as CoreImage
from kivy.graphics.texture import Texture
from io import BytesIO

from config import SUPPORTED_FORMATS

class BaseMultiThreading:
    """
    Base class for multithreading tasks using standard threading and Kivy Clock.
    """
    def __init__(self, task_function, items, batch_size=3, delay_ms=50, 
                 on_progress=None, on_completion=None, on_result=None, on_error=None):
        self.task_function = task_function
        self.items = items
        self.batch_size = batch_size
        self.delay_ms = delay_ms
        self._is_running = False
        self._thread = None
        
        # Callbacks (must be thread-safe or scheduled on main thread)
        self.on_progress = on_progress
        self.on_completion = on_completion
        self.on_result = on_result
        self.on_error = on_error

    def start(self):
        self._is_running = True
        self._thread = threading.Thread(target=self._run_thread)
        self._thread.daemon = True
        self._thread.start()

    def _run_thread(self):
        total_items = len(self.items)
        current_batch = 0

        while current_batch * self.batch_size < total_items:
            if not self._is_running:
                break
                
            start_index = current_batch * self.batch_size
            end_index = min((current_batch + 1) * self.batch_size, total_items)
            batch = self.items[start_index:end_index]

            for i, item in enumerate(batch):
                if not self._is_running:
                    break
                try:
                    result = self.task_function(item)
                    if self.on_result:
                        Clock.schedule_once(lambda dt, r=result: self.on_result(r))
                except Exception as e:
                    if self.on_error:
                        Clock.schedule_once(lambda dt, err=str(e): self.on_error(err))
                    continue

                global_index = start_index + i + 1
                progress = int(global_index / total_items * 100)
                items_left = total_items - global_index
                
                if self.on_progress:
                    Clock.schedule_once(lambda dt, p=progress, l=items_left: self.on_progress(p, l))

            current_batch += 1
            time.sleep(self.delay_ms / 1000.0)

        if self.on_completion:
            Clock.schedule_once(lambda dt: self.on_completion(total_items))

    def stop(self):
        self._is_running = False

def _process_image_part(img_part_data):
    # ... (Same logic as original) ...
    img_part = img_part_data.copy()
    try:
        if img_part.dtype == np.uint16:
            img_part = (img_part / 256).astype(np.uint8)
        elif img_part.dtype != np.uint8:
             # raise ValueError(f"Invalid dtype: {img_part.dtype}")
             pass

        processed_part = img_part
        if len(img_part.shape) == 2:
            processed_part = cv2.cvtColor(img_part, cv2.COLOR_GRAY2RGB)
        elif img_part.shape[2] == 4:
            processed_part = cv2.cvtColor(img_part, cv2.COLOR_RGBA2RGB)

        return processed_part
    except Exception as e:
        raise RuntimeError(f"Failed to process quadrant: {e}")

class RawImageProcessingThread(BaseMultiThreading):
    def __init__(self, image_paths, batch_size=1, delay_ms=100, low_res_target_size=None, **callbacks):
        self.low_res_mode = low_res_target_size is not None
        self.target_size = low_res_target_size
        
        try:
             total_cores = 8 # os.cpu_count() or 8
             self.num_part_workers = max(1, (total_cores // 2) if total_cores else 2)
        except:
             self.num_part_workers = 2

        def process_image(image_path):
            # ... (Logic adapted from original, returning Texture instead of QPixmap) ...
            # Simplified for brevity, assuming similar OpenCV logic
            try:
                # TAHAP 1: Read
                filename = image_path # os.path.basename(image_path)
                extension = "." + image_path.split('.')[-1].lower() # Simple extension check
                img_array = None
                
                is_raw = any(extension in formats for key, formats in SUPPORTED_FORMATS.items() if key == "raw")
                
                if is_raw:
                    with rawpy.imread(image_path) as raw:
                        img_array = raw.postprocess(output_bps=8, use_camera_wb=True)
                else:
                    img_cv = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
                    if img_cv is None: raise RuntimeError("OpenCV failed")
                    if img_cv.dtype == np.uint16: img_array = (img_cv / 256).astype(np.uint8)
                    else: img_array = img_cv.astype(np.uint8)
                    if len(img_array.shape) == 3 and img_array.shape[2] == 3:
                         img_array = cv2.cvtColor(img_array, cv2.COLOR_BGR2RGB)

                # TAHAP 2: Low Res
                if self.low_res_mode:
                    # ... Resize logic ...
                    h, w = img_array.shape[:2]
                    if max(h, w) > self.target_size:
                        scale = self.target_size / max(h, w)
                        img_array = cv2.resize(img_array, (int(w*scale), int(h*scale)))
                    
                    # Convert to Texture
                    buf = img_array.tobytes()
                    texture = Texture.create(size=(img_array.shape[1], img_array.shape[0]), colorfmt='rgb')
                    texture.blit_buffer(buf, colorfmt='rgb', bufferfmt='ubyte')
                    texture.flip_vertical()
                    return (image_path, texture)

                # TAHAP 3: Full Res (Simplified, skipping parallel parts for now to reduce complexity)
                # Convert to Texture
                buf = img_array.tobytes()
                texture = Texture.create(size=(img_array.shape[1], img_array.shape[0]), colorfmt='rgb')
                texture.blit_buffer(buf, colorfmt='rgb', bufferfmt='ubyte')
                texture.flip_vertical()
                return texture

            except Exception as e:
                print(f"Error processing {image_path}: {e}")
                raise e

        super().__init__(process_image, image_paths, batch_size, delay_ms, **callbacks)

class ImageImportThreading(BaseMultiThreading):
    def __init__(self, database_manager, image_paths, batch_size, delay_ms, **callbacks):
        def import_task(image_path):
            database_manager.single_process_save_image_path(image_path)
        
        super().__init__(import_task, image_paths, batch_size, delay_ms, **callbacks)
