"""
THUMBNAIL PROCESSOR - USAGE GUIDE
==================================

File ini menjelaskan cara menggunakan thumbnail_processor.py yang telah dibuat
untuk menampilkan thumbnail gambar di preview view, mirip dengan panorama page.

Lokasi File:
- Utility: pixel_refine_desktop/enhance_stack/core/logic/thumbnail_processor.py
- Usage: pixel_refine_desktop/enhance_stack/components/single_page/left_panel.py

CARA KERJA
==========

1. ThumbnailLoaderThread
   - QThread yang memproses gambar secara asinkron
   - Support untuk JPEG, PNG, TIFF, RAW formats
   - Auto-correct orientasi gambar dari EXIF data
   - Cache hasil thumbnail untuk performa

2. ThumbnailBatchProcessor
   - Wrapper class untuk manage multiple threads
   - Batasi concurrent threads dengan Semaphore (max 4)
   - Callback-based interface untuk hasil

3. Helper Functions
   - create_thumbnail_placeholder(): Buat loading indicator
   - display_thumbnail_in_layout(): Display thumbnail di layout
   - stop_thumbnail_threads(): Stop all threads safely

CONTOH PENGGUNAAN DASAR
=======================

# 1. Import
from pixel_refine_desktop.enhance_stack.core.logic.thumbnail_processor import (
    ThumbnailBatchProcessor,
    ThumbnailLoaderThread,
    create_thumbnail_placeholder
)

# 2. Create processor
processor = ThumbnailBatchProcessor(thumbnail_size=(128, 128))

# 3. Process single image dengan callback
def on_thumbnail_ready(q_image, image_path):
    if not q_image.isNull():
        pixmap = QPixmap.fromImage(q_image)
        label.setPixmap(pixmap)

processor.process_image("/path/to/image.jpg", callback=on_thumbnail_ready)

# 4. Process batch
image_paths = ["/path/img1.jpg", "/path/img2.png", "/path/img3.raw"]
processor.process_batch(image_paths, callback=on_thumbnail_ready)

# 5. Stop processing
processor.stop_all()

PENGGUNAAN DI LEFT PANEL
=========================

Di left_panel.py, telah ditambahkan:

1. __init__ method:
   - self.thumbnail_processor = ThumbnailBatchProcessor()
   - self.thumbnail_threads = []

2. load_batch method:
   - Clear previous thumbnails
   - Load images dan process thumbnail asinkron
   - Call _load_thumbnail_async() untuk setiap image

3. _load_thumbnail_async method (BARU):
   - Process thumbnail untuk image card
   - Update card dengan pixmap ketika ready

4. _display_image_preview method (BARU):
   - Load full-size preview gambar
   - Display di preview container
   - Similar dengan panorama page display

5. _on_card_double_clicked method (UPDATED):
   - Call _display_image_preview() ketika double-click

FEATURE COMPARISON DENGAN PANORAMA PAGE
========================================

┌─────────────────────────┬─────────────────┬────────────────┐
│ Feature                 │ Enhance Stack   │ Panorama Page  │
├─────────────────────────┼─────────────────┼────────────────┤
│ Async thumbnail loading │ ✅ Ya (TBaru)   │ ✅ Ya          │
│ Cache thumbnail         │ ✅ Ya           │ ✅ Ya          │
│ Format support          │ ✅ JPG/PNG/RAW  │ ✅ JPG/PNG/RAW │
│ EXIF orientation fix    │ ✅ Ya           │ ✅ Ya          │
│ Batch processing        │ ✅ Ya           │ ✅ Ya          │
│ Thread management       │ ✅ Ya           │ ✅ Ya          │
│ Preview display         │ ✅ Ya (TBaru)   │ ✅ Ya          │
└─────────────────────────┴─────────────────┴────────────────┘

INTEGRASI DENGAN PANORAMA PAGE
===============================

Kedua module sekarang menggunakan logika yang sama:

1. Batch processing thumbnail
2. Asinkron loading dengan QThread
3. Caching untuk performa
4. Semaphore untuk membatasi thread

Perbedaan:
- Enhance Stack: Grid preview + single image preview
- Panorama Page: Grid preview + processing + zoomable preview

ADVANCED USAGE
==============

# Custom thumbnail size
processor = ThumbnailBatchProcessor(thumbnail_size=(256, 256))

# Custom max concurrent threads
processor = ThumbnailBatchProcessor(max_concurrent=2)

# Manual thread control
from pixel_refine_desktop.enhance_stack.core.logic.thumbnail_processor import ThumbnailLoaderThread

thread = ThumbnailLoaderThread(image_path, thumbnail_size=(256, 256))
thread.thumbnail_ready.connect(on_thumbnail_ready)
thread.start()

# Pause/Resume thread
thread.pause()
# ... do something
thread.resume()

# Stop specific thread
thread.requestInterruption()
thread.wait()

ERROR HANDLING
==============

1. Invalid image path
   - ThumbnailLoaderThread akan emit empty QImage
   - Check dengan q_image.isNull() sebelum display

2. Unsupported format
   - Exception ditangkap di _process_image()
   - Log error message, emit empty QImage

3. Thread safety
   - Semaphore otomatis membatasi concurrent threads
   - QMutex untuk thread pause/resume
   - All operations thread-safe

4. Memory management
   - Cache dibatasi di CACHE_DIR
   - Thread cleanup di stop_all()
   - Destructor otomatis cleanup

PERFORMANCE TIPS
=================

1. Adjust semaphore limit untuk machine spec:
   - Weak machine: max_concurrent=2
   - Normal machine: max_concurrent=4 (default)
   - Powerful machine: max_concurrent=8

2. Adjust thumbnail size sesuai kebutuhan:
   - Kecil (80x80): Lebih cepat, RAM rendah
   - Medium (128x128): Default, balanced
   - Besar (256x256): Detail lebih, RAM lebih

3. Cache strategy:
   - Cache otomatis disimpan di database/cache/
   - Clearing cache: delete files di folder tersebut
   - Persistent cache antar session

DEBUGGING
=========

1. Enable logging (di thumbnail_processor.py):
   - Uncomment print statements
   - Check console untuk error messages

2. Monitor threads:
   - processor.threads list shows all active threads
   - thread.isRunning() check thread status

3. Memory usage:
   - Monitor CACHE_DIR size
   - Use task manager untuk check RAM usage

4. Performance profiling:
   - Time thumbnail loading: QTime
   - Count active threads: len(processor.threads)
   - Check semaphore state: _thumbnail_semaphore.available()

TROUBLESHOOTING
===============

Q: Thumbnail tidak muncul
A: 1. Check image path valid
   2. Check image format supported
   3. Check error messages di console
   4. Verify CACHE_DIR writable

Q: Thread tidak berhenti
A: 1. Call processor.stop_all() explicitly
   2. Disconnect signals manually
   3. Use requestInterruption() untuk force stop

Q: Memory usage tinggi
A: 1. Reduce thumbnail_size
   2. Reduce max_concurrent threads
   3. Clear cache directory
   4. Check image size (raw files besar)

Q: Performance lambat
A: 1. Increase max_concurrent threads
   2. Reduce thumbnail processing pada batch besar
   3. Optimize image processing (half_size untuk raw)
   4. Check disk I/O untuk cache access

NEXT STEPS
==========

1. Test integration dengan left_panel
2. Optimize thumbnail size untuk UI
3. Add progress tracking untuk batch processing
4. Integrate dengan panorama page untuk consistency
5. Add thumbnail caching strategy improvements
"""
