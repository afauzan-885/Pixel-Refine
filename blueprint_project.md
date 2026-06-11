# 🗺️ Complete Pixel Refine Codebase Blueprint & File Map

This document provides an exhaustive, directory-by-directory mapping of the entire Pixel Refine workspace. It outlines the role, class structure, and function interface of every single Python script.

---

## 📂 Directory: `Root Directory`

### 📄 [# DIRECTORY: .](file:///e:/APP%20Developer/Pixel%20Refine/# DIRECTORY: .)


--------------------


## 📂 Directory: `Root Directory`

### 📄 [build_android.py](file:///e:/APP%20Developer/Pixel%20Refine/build_android.py)

* **Function**: `run_command(command, shell)`
    *Jalankan perintah sistem dan tampilkan outputnya secara real-time.*

* **Function**: `get_wsl_path(win_path)`
    *Ubah path Windows ke format WSL (/mnt/c/...)*

* **Function**: `main()`
    *----------------------------------------*

--------------------

### 📄 [config.py](file:///e:/APP%20Developer/Pixel%20Refine/config.py)
    *----------------------------------------*

--------------------

### 📄 [inspect_model.py](file:///e:/APP%20Developer/Pixel%20Refine/inspect_model.py)

* **Function**: `describe_onnx_io(onnx_path)`
    *----------------------------------------*

--------------------

### 📄 [main_desktop.py](file:///e:/APP%20Developer/Pixel%20Refine/main_desktop.py)

* **File Overview**:
    *Pixel Refine - Main Application Entry Point*
    *============================================*
    *This module initializes and runs the Pixel Refine application.*

* **Class**: `CustomStyle`
    *Custom style to set tooltip delay to 200ms.*
  * Method: `styleHint(self, hint, option, widget, returnData)`

* **Class**: `ToolTipFilter`
    *Event filter to intercept tooltip events and wrap text using HTML*
    *to ensure adaptive width based on font size (em units).*
  * Method: `eventFilter(self, obj, event)`
    *Filter tooltip events to add HTML formatting for word wrapping.*

* **Class**: `PixelRefineMain`
    *Main application window for Pixel Refine.*
  * Method: `__init__(self)`
    *Initialize main window.*
    *Lightweight constructor that only initializes attributes.*
  * Method: `setup_ui_and_logic(self, splash)`
    *Setup UI and application logic with progress updates.*
  * Method: `_initialize_core_components(self, splash)`
    *Initialize core application components.*
  * Method: `_configure_window(self, splash)`
    *Configure window properties and settings.*
  * Method: `_load_ui_components(self, splash)`
    *Load UI components.*
  * Method: `_load_mvc_architecture(self, splash)`
    *Load MVC architecture components.*
  * Method: `_assemble_layout(self, splash)`
    *Assemble the final UI layout.*
  * Method: `closeEvent(self, event)`
    *Handle application close event.*
  * Method: `switch_page(self, index)`
    *Switch to a different page with fade animation.*
  * Method: `toggle_sidebar(self)`
    *Toggle sidebar visibility (placeholder for future implementation).*

* **Function**: `main()`
    *Main application entry point.*
    *----------------------------------------*

--------------------

### 📄 [main_mobile.py](file:///e:/APP%20Developer/Pixel%20Refine/main_mobile.py)

* **Class**: `PixelRefineApp`
  * Method: `build(self)`
    *----------------------------------------*

--------------------

### 📄 [motion_photo.py](file:///e:/APP%20Developer/Pixel%20Refine/motion_photo.py)

* **Class**: `DropListWidget`
  * Method: `__init__(self, title, file_extensions)`
  * Method: `dragEnterEvent(self, event)`
  * Method: `dragMoveEvent(self, event)`
  * Method: `dropEvent(self, event)`

* **Class**: `MotionWorker`
  * Method: `__init__(self, images, videos, compression_level)`
  * Method: `run(self)`
  * Method: `compress_video(self, input_path, output_path, level)`
  * Method: `inject_metadata(self, file_path, video_size)`

* **Class**: `MotionEmbedderApp`
  * Method: `__init__(self)`
  * Method: `initUI(self)`
  * Method: `clear_lists(self)`
  * Method: `start_processing(self)`
  * Method: `update_progress(self, val)`
  * Method: `update_status(self, msg)`
  * Method: `process_finished(self)`
    *----------------------------------------*

--------------------

### 📄 [nuitka_build.py](file:///e:/APP%20Developer/Pixel%20Refine/nuitka_build.py)

* **Function**: `build_nuitka()`
    *Membangun daftar perintah Nuitka dan menjalankannya.*
    *----------------------------------------*

--------------------

### 📄 [pyinstaller_build.py](file:///e:/APP%20Developer/Pixel%20Refine/pyinstaller_build.py)

* **Function**: `build_pyinstaller()`
    *----------------------------------------*

--------------------

### 📄 [watcher.py](file:///e:/APP%20Developer/Pixel%20Refine/watcher.py)

* **Class**: `ReloadHandler`
  * Method: `__init__(self, process)`
  * Method: `on_modified(self, event)`

* **Function**: `start_watcher()`
    *----------------------------------------*

--------------------


## 📂 Directory: `Root Directory`

### 📄 [# DIRECTORY: pixel_refine_desktop/app_core](file:///e:/APP%20Developer/Pixel%20Refine/# DIRECTORY: pixel_refine_desktop/app_core)


--------------------


## 📂 Directory: `Root Directory`

### 📄 [app_manager.py](file:///e:/APP%20Developer/Pixel%20Refine/pixel_refine_desktop/app_core/app_manager.py)

* **File Overview**:
    *Application manager module for handling core business logic.*
    *Manages database, folders, and application lifecycle.*

* **Class**: `ApplicationManager`
    *Manages core application logic including database, folders, and cleanup.*
  * Method: `__init__(self, main_window)`
    *Initialize application manager.*
    *Args:*
    *main_window: Reference to the main window instance*
  * Method: `initialize_database(self, db_path)`
    *Initialize and create database.*
    *Args:*
    *db_path: Path to the database file*
    *Returns:*
    *DatabaseManager instance*
  * Method: `setup_animator(self)`
    *Initialize animation manager.*
    *Returns:*
    *StackedWidgetAnimator instance*
  * Method: `load_algorithms(self)`
    *Load and validate available algorithms.*
    *Returns:*
    *dict: Summary of loaded algorithms count by category.*
  * Method: `initialize_folders(self)`
    *Create necessary folders if they don't exist.*
    *Raises:*
    *SystemExit: If folder creation fails*
  * Method: `cleanup_folders(self)`
    *Clean up temporary folders and cache.*
    *Called when application is closing.*
    *----------------------------------------*

--------------------

### 📄 [window_config.py](file:///e:/APP%20Developer/Pixel%20Refine/pixel_refine_desktop/app_core/window_config.py)

* **File Overview**:
    *Window configuration module for adaptive window sizing and positioning.*

* **Class**: `WindowConfig`
    *Handles window size calculation and configuration.*
    *Provides adaptive window sizing based on screen dimensions.*
  * Method: `__init__(self, app_aspect_ratio, min_screen_ratio, abs_min_width, abs_min_height)`
    *Initialize window configuration.*
    *Args:*
    *app_aspect_ratio: Desired aspect ratio for the application (width / height)*
    *min_screen_ratio: Percentage of screen that will be the minimum size*
    *abs_min_width: Absolute minimum width (fallback for very low resolution screens)*
    *abs_min_height: Absolute minimum height (fallback for very low resolution screens)*
  * Method: `calculate_adaptive_size(self)`
    *Calculate adaptive window size based on screen dimensions.*
    *Returns:*
    *Tuple of (min_width, min_height, center_x, center_y)*
  * Method: `apply_to_window(self, window)`
    *Apply calculated configuration to a QMainWindow.*
    *Args:*
    *window: The QMainWindow to configure*
    *----------------------------------------*

--------------------


## 📂 Directory: `Root Directory`

### 📄 [# DIRECTORY: pixel_refine_desktop/enhance_stack/components/batch_page](file:///e:/APP%20Developer/Pixel%20Refine/# DIRECTORY: pixel_refine_desktop/enhance_stack/components/batch_page)


--------------------


## 📂 Directory: `Root Directory`

### 📄 [batch_layout.py](file:///e:/APP%20Developer/Pixel%20Refine/pixel_refine_desktop/enhance_stack/components/batch_page/batch_layout.py)

* **Class**: `MassAlgorithmEditDialog`
  * Method: `__init__(self, panels, parent)`
  * Method: `initUI(self)`
  * Method: `apply_changes(self)`

* **Class**: `ProcessingThread`
  * Method: `__init__(self, panels_to_process, batch_page_layout, target_folder)`
  * Method: `run(self)`
  * Method: `stop(self)`

* **Class**: `BatchProcessDialog`
  * Method: `__init__(self, panels_to_process, batch_page_layout, parent)`
  * Method: `initUI(self)`
  * Method: `_set_row_color(self, row, color)`
    *Helper function untuk mengatur warna latar belakang seluruh baris.*
    *Menggunakan setStyleSheet untuk keandalan maksimum pada widget.*
  * Method: `_get_algorithm_summary(self, batch_id)`
  * Method: `populate_table(self)`
  * Method: `resizeEvent(self, event)`
  * Method: `on_batch_finished(self, row, success, result_message)`
  * Method: `open_mass_edit_dialog(self)`
    *Membuka dialog dan menghubungkan sinyalnya untuk update real-time.*
  * Method: `refresh_details_column(self)`
    *Mengupdate kolom "Details" untuk semua baris.*
    *Ini adalah fungsi yang dipanggil untuk update real-time.*
  * Method: `on_progress_update_from_thread(self, row, status, details, percent_in_batch, current_num, total_num)`
    *Update status baris yang sedang diproses dan progress bar utama.*
  * Method: `_update_details_cell(self, row, text)`
    *Helper function untuk update teks di sel Details.*
    *Sekarang juga mengatur perataan teks secara dinamis.*
  * Method: `update_row_status(self, row, status, details, percent_in_batch)`
    *Update status baris yang sedang diproses.*
  * Method: `start_processing(self)`
  * Method: `cancel_processing(self)`
    *Menampilkan dialog konfirmasi dan membatalkan proses jika dikonfirmasi.*
  * Method: `reset_dialog_state(self)`
  * Method: `adjust_column_widths(self)`
  * Method: `browse_output_folder(self)`
  * Method: `open_mass_edit_dialog(self)`
    *Membuka dialog, dan me-refresh tabel jika perubahan diterapkan.*
  * Method: `update_row_status(self, row, current_progress, status, details)`
  * Method: `on_processing_complete(self, failed_batches_summary)`
  * Method: `cancel_processing(self)`

* **Function**: `setup_main_panel(layout_instance, scroll_area_style)`
    *Membuat panel utama dengan layout yang diberikan.*

* **Function**: `load_json_state(path, default)`

* **Function**: `save_json_state(path, data)`
    *----------------------------------------*

--------------------

### 📄 [batch_page_layout.py](file:///e:/APP%20Developer/Pixel%20Refine/pixel_refine_desktop/enhance_stack/components/batch_page/batch_page_layout.py)

* **Class**: `BatchPageLayout`
  * Method: `__init__(self)`
  * Method: `update_batch_view(self)`
    *Memperbarui tampilan daftar batch secara cerdas.*
    *Hanya menambah, menghapus, atau mempertahankan widget yang ada*
    *tanpa membangun ulang seluruh UI.*
  * Method: `_reorder_visual_batch_numbers(self)`
    *Mengatur ulang label nomor urut (Batch #1, Batch #2, dst.) pada semua panel.*
  * Method: `_manage_placeholder_and_spacer(self)`
    *Menampilkan placeholder jika tidak ada batch, atau spacer jika ada batch.*
  * Method: `_create_placeholder_widget(self)`
    *Membuat widget placeholder untuk ditampilkan saat tidak ada batch.*
  * Method: `_start_fade_in_animation(self, panel_to_animate)`
  * Method: `_on_fade_in_finished(self, effect, widget)`
  * Method: `_on_parameters_file_changed(self, path)`
  * Method: `setup_combined_panel(self, batch_id)`
  * Method: `eventFilter(self, source, event)`
  * Method: `_handle_scroll_area_events(self, event)`
  * Method: `_handle_drag_enter(self, event)`
  * Method: `_handle_drag_leave(self, event)`
  * Method: `_handle_drag_move(self, event)`
  * Method: `_handle_drop(self, event)`
  * Method: `get_files_in_stack_folder(self)`
    *Mengembalikan daftar path lengkap file di folder 'database/stack'.*
  * Method: `process_all_batches(self)`
    *Mengumpulkan batch yang valid dan menampilkan dialog konfirmasi pemrosesan.*
  * Method: `_move_single_batch_result(self, source_file_path, target_folder)`
    *Memindahkan file hasil ke folder target, hanya menggunakan nama file asli.*
    *Jika file dengan nama yang sama sudah ada, tambahkan akhiran "_1", "_2", dst.*
  * Method: `handle_delete_individual_batch(self, batch_id)`
  * Method: `handle_delete_all_batches(self)`
  * Method: `_start_bulk_background_delete_process(self)`
    *Memulai proses penghapusan semua batch di background.*
  * Method: `_trigger_single_bulk_fade_out(self, panel_ref)`
    *Memulai fade out untuk satu panel dalam proses bulk delete.*
  * Method: `_check_bulk_delete_animations_finished(self)`
    *Dipanggil setiap kali satu animasi fade-out selesai saat delete all.*
  * Method: `_bulk_delete_post_single_animation(self, panel_ref)`
  * Method: `_individual_delete_post_animation(self, batch_id, panel_ref)`
    *Callback setelah animasi fade-out individual selesai.*
  * Method: `_start_background_delete_process(self, batch_id)`
    *Memulai proses penghapusan di background thread.*
  * Method: `_on_delete_thread_finished(self, thread_instance)`
    *Dipanggil saat thread delete selesai untuk menghapusnya dari list.*
  * Method: `handle_batch_import_button(self)`
    *Membuka dialog file dan memulai proses impor batch.*
  * Method: `stop_thumbnail(self)`
    *Menghentikan semua thread thumbnail yang sedang berjalan.*
  * Method: `_handle_item_imported(self)`
    *Dipanggil setiap kali satu item berhasil diimpor oleh thread manapun.*
  * Method: `_handle_thread_finished(self, thread_instance)`
    *Dipanggil saat thread impor selesai.*
  * Method: `_update_aggregated_progress_toast(self)`
    *Menghitung dan menampilkan progres impor agregat via toast.*
  * Method: `_update_import_progress_toast(self, progress_percent, items_left)`
    *Update teks toast dengan informasi progres impor.*
  * Method: `on_batch_import_error(self, item_path, error_message)`
  * Method: `_on_batch_import_complete(self, total_items_processed)`
    *Dipanggil saat thread impor batch selesai.*

* **Function**: `load_json_state(path)`

* **Function**: `is_widget_valid(widget)`
    *Cek apakah widget masih valid (belum dihapus).*

* **Function**: `safe_hide_widget(widget)`
    *Sembunyikan widget jika masih valid, tangani error jika sudah dihapus.*
    *----------------------------------------*

--------------------

### 📄 [combined_panel.py](file:///e:/APP%20Developer/Pixel%20Refine/pixel_refine_desktop/enhance_stack/components/batch_page/combined_panel.py)

* **Class**: `ClickableLabel`
  * Method: `__init__(self, parent)`
  * Method: `mousePressEvent(self, event)`

* **Class**: `CombinedPanel`
    *Kelas untuk membuat panel gabungan yang memuat:*
    *- Tombol (add & delete)*
    *- Panel parameter (combo box & checkbox)*
    *- Panel list thumbnail*
  * Method: `__init__(self, database_manager, batch_id, parent, thumbnail_threads, thumbnail_placeholders, initial_state, sequential_batch_number)`
  * Method: `update_sequential_number(self, new_number)`
    *Memperbarui nomor urut batch yang ditampilkan di UI.*
  * Method: `get_thumbnail_setting(self)`
  * Method: `init_ui(self)`
  * Method: `refresh_ui_from_broadcast(self, all_new_states)`
    *Slot yang dipanggil saat BatchPageLayout menyiarkan perubahan state.*
    *Slot ini TIDAK MEMBACA FILE. Ia hanya menerima data dan menerapkan perubahan.*
  * Method: `apply_state(self, state)`
    *Menerapkan state dari dictionary ke semua aspek panel:*
    *1. Widget UI (checkboxes, comboboxes).*
    *2. State internal (self.selected_algorithms).*
    *3. Tampilan visual (visibilitas, status enabled/disabled).*
  * Method: `_on_overlay_destroyed(self)`
  * Method: `delay_thumbnails(self)`
  * Method: `_on_thumbnail_loaded(self)`
  * Method: `_start_next_thumbnail_loaders(self)`
    *Jalankan loading thumbnail secara asynchronous hingga semua selesai.*
  * Method: `_make_loader_callback(self, animator_ref)`
    *Mengembalikan fungsi on_ready(image, image_path) yang sudah mengecek*
    *apakah overlay masih 'alive' sebelum setText(...).*
  * Method: `closeEvent(self, event)`
    *Override closeEvent agar kita bisa disconnect semua ThumbnailLoader*
    *sebelum widget ini benar-benar di-destroy.*
  * Method: `load_text_labels(self)`
  * Method: `get_current_state(self, batch_id)`
    *Mengambil state saat ini dari widget panel parameter.*
    *Sekarang menggunakan self.label_to_key_map untuk konsistensi kunci.*
  * Method: `layout_panel_parameter(self, list_layout)`
  * Method: `create_button_parameter(self, list_layout)`
    *Buat widget tombol yang berisi tombol add dan delete.*
  * Method: `process_and_preview(self)`
    *Jalankan semua algoritma batch terlebih dahulu, lalu tampilkan preview gambar.*
  * Method: `handle_preview_button(self)`
    *Menampilkan gambar terbaru setelah batch diproses.*
  * Method: `dropdown_box_control(self)`
  * Method: `execute_algorithm(self, category, selected_algo)`
    *Simpan pilihan algoritma dan update JSON secara realtime.*
  * Method: `_handle_denoising_state_changed(self, is_checked)`
    *Logika eksklusif saat state checkbox Denoising berubah.*
  * Method: `_handle_superres_state_changed(self, is_checked)`
    *Logika eksklusif saat state checkbox Super Resolution berubah.*
  * Method: `_save_state_to_json(self, batch_id)`
    *Simpan state checkbox dan combobox untuk batch_id ke dalam file JSON.*
  * Method: `_trigger_exclusive_handler(self, checkbox_key)`
    *Dipanggil oleh klik label atau toggle checkbox untuk memicu logika eksklusif.*
  * Method: `_handle_crop_keep_edge(self, is_checked, changed_cb_key, other_cb_key)`
    *Logika eksklusif untuk Crop Edge dan Keep Edge.*
  * Method: `_update_visibility_internal(self)`
    *Memperbarui visibilitas/enabled widget berdasarkan state checkbox.*
  * Method: `process_all_batch(self, progress_callback)`
    *Jalankan semua algoritma yang dipilih untuk self.batch_id.*
    *Fungsi ini sekarang menerima 'progress_callback' untuk melaporkan status*
    *sub-proses kembali ke thread pemanggil tanpa membuat UI baru.*
  * Method: `create_parameter_panel(self)`
    *Buat panel parameter yang berisi combo box dan checkbox.*
    *Diperbaiki untuk menggunakan pemetaan kunci yang stabil untuk penyimpanan state.*

* **Function**: `load_json_state(path)`

* **Function**: `save_json_state(path, state)`
    *----------------------------------------*

--------------------

### 📄 [image_batch_management.py](file:///e:/APP%20Developer/Pixel%20Refine/pixel_refine_desktop/enhance_stack/components/batch_page/image_batch_management.py)

* **Class**: `BatchDeleteProcess`
  * Method: `__init__(self, database_manager, batch_id, cache_dir, thumbnail_threads, parent)`
  * Method: `individual_batch_delete(self)`
    *Menghapus satu batch beserta cache gambarnya.*
  * Method: `delete_all_batch(self)`
    *Menghapus semua batch beserta cache gambar yang terkait.*
  * Method: `run(self)`
    *Metode run default akan menjalankan individual_batch_delete.*
    *Anda dapat memanggil delete_all_batch secara eksplisit jika ingin menghapus semua batch.*

* **Function**: `handle_add_image_to_batch(batch_page_layout, database_manager, thumbnail_threads, batch_id, list_layout)`

* **Function**: `process_and_start_batch_import(batch_page_layout, image_paths)`
    *Memproses dan memulai impor batch dengan pola streaming sejati,*
    *memperbarui UI secara bertahap saat file siap.*

* **Function**: `convert_tiff_to_uncompressed(input_paths, output_folder)`
    *Mengonversi daftar gambar input secara paralel dan MENGHASILKAN (yield) setiap hasil*
    *segera setelah selesai.*
    *Args:*
    *input_paths: Sebuah list path file yang akan dikonversi.*
    *output_folder: Folder tujuan untuk semua file yang dikonversi.*
    *Yields:*
    *Tuple (bool, str) yang berisi status keberhasilan dan path hasil atau pesan error.*
    *----------------------------------------*

--------------------

### 📄 [scrollable_error_dialog.py](file:///e:/APP%20Developer/Pixel%20Refine/pixel_refine_desktop/enhance_stack/components/batch_page/scrollable_error_dialog.py)

* **Class**: `ScrollableErrorDialog`
    *Sebuah dialog kustom untuk menampilkan pesan error yang panjang*
    *dengan area teks yang bisa di-scroll.*
  * Method: `__init__(self, title, intro_text, detailed_text, parent)`
    *----------------------------------------*

--------------------

### 📄 [thumbnail.py](file:///e:/APP%20Developer/Pixel%20Refine/pixel_refine_desktop/enhance_stack/components/batch_page/thumbnail.py)

* **Class**: `ThumbnailLoader`
    *Versi yang telah di-upgrade sepenuhnya menggunakan Pillow untuk kecepatan,*
    *keandalan, dan koreksi orientasi otomatis.*
  * Method: `__init__(self, image_path, parent)`
  * Method: `pause(self)`
  * Method: `resume(self)`
  * Method: `run(self)`

* **Function**: `thumbnail_placeholder(list_layout, image_path, placeholders, retry_count)`

* **Function**: `make_safe_callback(current_path, layout_ref)`

* **Function**: `show_thumbnail(ref_layout, image, image_path, animator, retry_count)`

* **Function**: `stop_process_thumbnails(threads)`
    *Menghentikan semua thread thumbnail dengan aman dan sinkron.*
    *Fungsi ini sekarang akan memblokir sampai semua thread benar-benar berhenti*
    *sebelum membersihkan daftar referensi.*
    *----------------------------------------*

--------------------


## 📂 Directory: `Root Directory`

### 📄 [# DIRECTORY: pixel_refine_desktop/enhance_stack/components/batch_page_v2](file:///e:/APP%20Developer/Pixel%20Refine/# DIRECTORY: pixel_refine_desktop/enhance_stack/components/batch_page_v2)


--------------------


## 📂 Directory: `Root Directory`

### 📄 [algorithm_panel.py](file:///e:/APP%20Developer/Pixel%20Refine/pixel_refine_desktop/enhance_stack/components/batch_page_v2/algorithm_panel.py)

* **File Overview**:
    *Algorithm Panel Component - Handles workflow settings and algorithms.*
    *Part of the refactored LeftPanel architecture.*
    *UI Layer only - Logic separated to core/logic/algorithm_logic.py*

* **Class**: `AlgorithmPanel`
    *Algorithm Panel untuk workflow settings dan parameter konfigurasi.*
    *Features:*
    *- Adaptive layout using QStackedWidget for parameter sections*
    *- Smooth horizontal animations (Slide)*
    *- Auto-collapse integration via visibility signals*
  * Method: `__init__(self, controller, store)`
  * Method: `_setup_ui(self)`
    *Setup UI dengan adaptive parameter stack.*
  * Method: `_create_parameter_alignment(self)`
    *Create column for alignment parameters.*
  * Method: `_create_parameter_algorithm(self)`
    *Create column for algorithm parameters.*
  * Method: `_on_process_clicked(self)`
  * Method: `_enable_cancel_button(self)`
    *Called 1s after Start to turn button into Cancel.*
  * Method: `_on_cancel_requested(self)`
    *Handle cancellation logic.*
  * Method: `_update_all_buttons(self, enabled, text, variant, bg, hover)`
    *Helper to sync all process button instances.*
  * Method: `_on_progress_update(self, percent, message)`
  * Method: `_on_processing_finished(self)`
  * Method: `set_current_batch(self, batch_id)`
  * Method: `get_settings(self)`
  * Method: `_setup_bindings(self)`
    *Setup declarative bindings for the algorithm panel.*
  * Method: `on_store_changed(self, key, value)`
    *React to store changes with fallback support.*
  * Method: `update_settings(self, settings)`
    *Receive updated settings and trigger adaptive UI with debounce.*
  * Method: `_do_update_adaptive_ui(self)`
    *Perform the actual UI update from debounced timer.*
  * Method: `update_settings_immediate(self, settings)`
    *Bypass debounce for immediate initialization.*
  * Method: `_update_adaptive_ui(self, settings)`
    *Update parameter stack with horizontal slide animation.*
  * Method: `set_settings(self, settings)`
  * Method: `show_progress(self, value)`
  * Method: `hide_progress(self)`
  * Method: `set_process_enabled(self, enabled)`
  * Method: `database_manager(self)`
    *----------------------------------------*

--------------------

### 📄 [batch_page_v2_layout.py](file:///e:/APP%20Developer/Pixel%20Refine/pixel_refine_desktop/enhance_stack/components/batch_page_v2/batch_page_v2_layout.py)

* **Class**: `BatchPageV2Layout`
    *Batch page layout v2 - Enhanced version with modular components.*
  * Method: `__init__(self, database_manager)`
  * Method: `_connect_workspace_signals(self)`
    *Gracefully attempt to connect preview signals if components are available.*
    *This method fails silently if components are not initialized.*
  * Method: `resizeEvent(self, event)`
    *Handles window resizing by calling the handler's resize method.*
  * Method: `handle_import_button(self)`
    *Membuka dialog file dan memulai proses impor.*
  * Method: `handle_dropped_images(self, image_paths)`
    *Menangani file gambar yang di-drop dan memulai proses impor.*
  * Method: `_process_and_start_import(self, image_paths)`
    *Memvalidasi, memproses (konversi TIFF), menyeleksi, dan*
    *memulai impor background untuk daftar path gambar yang diberikan.*
  * Method: `on_import_complete(self, successful_images)`
    *Dijalankan saat semua proses impor selesai.*
  * Method: `handle_delete_button(self)`
    *Function to delete images*
  * Method: `single_process_algorithm(self, batch_mode)`
    *Fungsi untuk memproses algoritma berdasarkan pilihan dropdown.*
    *Args:*
    *batch_mode: If True, skip UI dialogs and previews (for background processing)*
  * Method: `run_batch_for_id(self, batch_id)`
    *Execute processing pipeline for a specific batch ID programmatically.*
    *Used by BatchProcessingThread.*
    *IMPORTANT: This method is called from a background thread, so it must NOT*
    *perform any UI operations directly. All UI updates should be done via signals.*
    *This version uses AlgorithmProcessorThread for proper threading control.*
  * Method: `get_files_in_stack_folder(self)`
    *Get list of files in the stack folder.*
  * Method: `_move_single_batch_result(self, source_file, target_folder)`
    *Move a processed file to target folder, handling naming.*
  * Method: `save_image(self)`
    *Menyimpan gambar hasil proses ke lokasi yang dipilih pengguna.*
    *Untuk TIFF, file akan disalin/dipindahkan. Untuk format lain, akan dikonversi.*
    *Metadata asli dari gambar sumber akan coba diterapkan.*
  * Method: `update_progress_bar(self, value, images_left)`
    *Memperbarui progress bar dan menampilkan jumlah gambar yang tersisa.*
  * Method: `on_import_error(self, error_message)`
    *Handle errors during image import.*
    *----------------------------------------*

--------------------

### 📄 [batch_process_dialog.py](file:///e:/APP%20Developer/Pixel%20Refine/pixel_refine_desktop/enhance_stack/components/batch_page_v2/batch_process_dialog.py)

* **Class**: `MassAlgorithmEditDialog`
  * Method: `__init__(self, batches, parent)`
  * Method: `initUI(self)`
  * Method: `apply_changes(self)`

* **Class**: `BatchProcessDialog`
  * Method: `__init__(self, batches_to_process, batch_page_layout, parent)`
  * Method: `initUI(self)`
  * Method: `_get_algorithm_summary(self, batch_id)`
    *Get algorithm summary using extracted logic.*
  * Method: `populate_table(self)`
  * Method: `resizeEvent(self, event)`
  * Method: `on_batch_finished(self, row, success, result_message)`
  * Method: `open_mass_edit_dialog(self)`
    *Membuka dialog dan menghubungkan sinyalnya untuk update real-time.*
  * Method: `refresh_details_column(self)`
    *Mengupdate kolom 'Details' untuk semua baris.*
  * Method: `on_progress_update_from_thread(self, row, status, details, percent_in_batch, current_num, total_num)`
    *Update status baris yang sedang diproses.*
  * Method: `_update_details_cell(self, row, text)`
    *Helper function untuk update teks di sel Details.*
  * Method: `start_processing(self)`
  * Method: `cancel_processing(self)`
    *Menampilkan dialog konfirmasi dan membatalkan proses.*
  * Method: `reset_dialog_state(self)`
  * Method: `browse_output_folder(self)`
  * Method: `on_processing_complete(self, failed_batches_summary)`
  * Method: `_handle_batch_context_switch(self, batch_id)`
    *Handle batch context switching in the main thread.*
    *Called via signal from worker thread to avoid thread safety issues.*
  * Method: `_handle_algorithm_execution(self, batch_id)`
    *Execute algorithm processing in the main thread using AlgorithmProcessorThread.*
    *Called via signal from worker thread to avoid nested thread deadlock.*
    *CRITICAL: This runs in main thread, so algorithms can spawn their own*
    *worker threads (ThreadWorker, ImageProcessingMultiThreading) safely.*
    *NON-BLOCKING: Uses signal-based completion to keep UI responsive.*
    *Uses AlgorithmProcessorThread with:*
    *- batch_id: The specific batch to process*
    *- single_process=False: Use batch mode (reads images from batch_process_image table)*
  * Method: `_on_algorithm_progress_update(self, batch_id, percent, message)`
    *Handle real-time progress updates from AlgorithmProcessorThread.*
    *Updates both the table row for this batch and the overall progress bar.*
    *----------------------------------------*

--------------------

### 📄 [display_panel.py](file:///e:/APP%20Developer/Pixel%20Refine/pixel_refine_desktop/enhance_stack/components/batch_page_v2/display_panel.py)

* **Class**: `DisplayPanel`
    *Panel untuk menampilkan Grid images dan Preview.*
    *Menggunakan QStackedWidget untuk switch antara Grid View dan Preview View.*
    *Struktur: DisplayPanel (Logic) -> QStackedLayout (Overlay support)*
    *-> Layer 0: Content Widget -> Container -> Header + Stack*
    *-> Layer 1: Overlay Widget -> Floating Progress Bar*
    *-> Layer 2: Sidebar Overlay*
  * Method: `__init__(self, controller)`
  * Method: `_setup_ui(self)`
    *Setup UI dengan stacked widget untuk grid dan preview mode.*
  * Method: `_setup_sidebar(self)`
    *Initialize Floating Sidebar.*
  * Method: `_setup_settings_overlay(self)`
    *Setup independent overlay for Settings View.*
  * Method: `_handle_sidebar_navigation(self, index)`
    *Handle navigation from sidebar.*
    *Intercepts Settings (index 2) to show overlay.*
    *Forwards others (0, 1) to main window.*
  * Method: `show_settings(self)`
    *Show settings overlay with FADE animation.*
  * Method: `toggle_sidebar(self)`
    *Toggle floating sidebar visibility with animation.*
  * Method: `_create_placeholder_widget(self, html_text, button_text, on_button_click)`
    *Delegate to UIStateManager.*
  * Method: `_set_placeholder(self, widget)`
    *Delegate to UIStateManager.*
  * Method: `_on_scroll_changed(self)`
    *Triggered when scrollbar moves or range changes.*
  * Method: `_check_visible_cards(self)`
    *Delegate to DisplayLogic for lazy loading.*
  * Method: `load_batch(self, batch_id, images, batch_name)`
    *Load batch images ke grid secara progresif (pure lazy loading).*
  * Method: `clear_display(self)`
    *Clear display ketika tidak ada batch yang dipilih.*
    *Reset ke state default dengan placeholder widget dan tombol "New Batch".*
  * Method: `_reset_population_state(self)`
    *Unified method to stop all pending populating tasks and clear tracking.*
  * Method: `_show_empty_batch_state(self)`
    *Delegate to UIStateManager.*
  * Method: `_create_new_batch(self)`
    *Call _create_new_batch dari right_panel untuk create batch baru.*
    *Right panel akan handle dialog input dan emit signal.*
  * Method: `_clear_grid(self)`
    *Delegate to GridManager.*
  * Method: `_clear_selection(self)`
    *Deselect semua cards via Manager.*
  * Method: `_select_range(self, start_card_id, end_card_id)`
    *Select range via Manager.*
  * Method: `_is_widget_in_viewport(self, widget)`
    *Delegate to GridManager.*
  * Method: `_load_thumbnail_async(self, image_path, card_widget)`
    *Load thumbnail asinkron untuk image card dengan Viewport-Aware Animation.*
  * Method: `_on_thumbnail_ready(self, q_image, path, card_widget)`
    *Callback when thumbnail is ready, updates card directly (No Fade-In).*
  * Method: `_on_card_clicked(self, card_id, event, card_widget)`
    *Handle click via Manager.*
  * Method: `_on_thumbnail_progress(self, batch_id, decode_pct, save_pct)`
    *Update toast progress for thumbnail creation and saving.*
  * Method: `_on_card_double_clicked(self, card_id)`
    *Handle double-click pada image card untuk preview full resolution.*
    *Args:*
    *card_id: ID dari card yang di-click*
  * Method: `_select_all_images(self)`
    *Select all via Manager.*
  * Method: `_refresh_current_batch(self)`
    *Helper to re-load current batch settings from controller/db.*
  * Method: `keyPressEvent(self, event)`
    *Handle keyboard events (Delete key, Ctrl+A, and Arrow navigation).*
  * Method: `_handle_enter_press(self)`
    *Delegate to SelectionManager.*
  * Method: `_navigate_selection(self, key, shift_held)`
    *Navigate via Manager.*
  * Method: `contextMenuEvent(self, event)`
    *Delegate to ContextMenuHandler.*
  * Method: `_set_as_reference(self, image_path)`
    *Delegate to ContextMenuHandler.*
  * Method: `_handle_delete_action(self)`
    *Handle deletion via Manager.*
  * Method: `on_batch_import_started(self, batch_id)`
    *Delegate to ImportManager.*
  * Method: `on_batch_import_finished(self, batch_id)`
    *Delegate to ImportManager.*
  * Method: `add_single_image_to_grid(self, batch_id, batch_name, image_path)`
    *Delegate to ImportManager.*
  * Method: `_on_deletion_finished(self, count)`
    *Handle completion of image deletion.*
  * Method: `_on_deletion_error(self, error_message)`
    *Handle error during image deletion.*
  * Method: `_display_image_preview(self, image_path)`
    *Display single image preview di Zoomable view dengan full resolution.*
    *Args:*
    *image_path: Path ke image file untuk di-preview*
  * Method: `_on_preview_process_clicked(self)`
    *Handle 'Preview Process' button click from Grid.*
  * Method: `_on_result_changed(self, value)`
    *Handle dropdown selection change.*
  * Method: `display_processed_result(self, image_path, update_dropdown)`
    *Display processed result image in Compare Mode (Default).*
    *Loads Original + Processed into ComparisonGraphicsItem.*
  * Method: `check_result_availability(self)`
    *Check if results exist for current batch and update 'Preview Process' button.*
  * Method: `show_grid(self)`
    *Switch ke Grid View.*
  * Method: `show_preview(self, show_dropdown)`
    *Switch ke Preview View.*
  * Method: `remove_selected_images(self)`
    *Remove currently selected images dari grid via Logic.*
  * Method: `get_selected_image_list(self)`
    *Get list of selected image paths.*
  * Method: `set_header_title(self, text)`
    *Sets the text of the header title.*
  * Method: `_update_header_title(self, count)`
    *Delegate to UIStateManager.*
  * Method: `_on_save_clicked(self)`
    *Handle floating save button click.*
  * Method: `_setup_delete_confirmation_widget(self)`
    *Create and configure the delete confirmation widget.*
  * Method: `show_delete_confirmation(self, batch_ids, batch_names)`
    *Switch to the delete confirmation view and pass batch info.*
    *Args:*
    *batch_ids: List of batch IDs to be deleted.*
    *batch_names: List of batch names to display.*
  * Method: `_delete_confirmed_batches(self)`
    *Handle the actual deletion after confirmation.*
  * Method: `resizeEvent(self, event)`
  * Method: `dragEnterEvent(self, event)`
    *Delegate to DragDropHandler.*
  * Method: `dragLeaveEvent(self, event)`
  * Method: `dropEvent(self, event)`
    *Delegate to DragDropHandler.*
    *----------------------------------------*

--------------------

### 📄 [left_panel.py](file:///e:/APP%20Developer/Pixel%20Refine/pixel_refine_desktop/enhance_stack/components/batch_page_v2/left_panel.py)

* **Class**: `AdaptiveStackedWidget`
    *QStackedWidget that resizes to fit its current widget.*
  * Method: `minimumSizeHint(self)`
  * Method: `sizeHint(self)`

* **Class**: `LeftPanel`
  * Method: `__init__(self, controller, store)`
  * Method: `_setup_ui(self)`
    *Setup UI dengan DisplayPanel dan AlgorithmPanel menggunakan stacked widget.*
  * Method: `resizeEvent(self, event)`
    *Handle resize to switch between fixed height and flex ratio for algorithm panel.*
  * Method: `_update_layout_responsive(self)`
    *Adjust layout based on height threshold.*
    *- Height < 850px: Algorithm Panel fixed 230px (approx 30%)*
    *- Height >= 850px: Algorithm Panel flex 50%*
    *Only applies if Algo Panel is visible (not collapsed).*
  * Method: `clear_display(self)`
    *Clear display saat tidak ada batch yang dipilih.*
    *Forward ke DisplayPanel dan hide AlgorithmPanel dengan SLIDE_DOWN animation.*
  * Method: `_handle_algorithm_panel_visibility(self, visible)`
    *Handle visibility changes from AlgorithmPanel.*
    *Expand or collapse the panel with animation.*
  * Method: `load_batch(self, batch_id, images, batch_name)`
    *Load batch images dan show AlgorithmPanel dengan SLIDE_UP animation.*
    *Forward ke DisplayPanel dan expand AlgorithmPanel.*
    *Args:*
    *batch_id: ID dari batch*
    *images: List of image objects*
    *batch_name: Nama dari batch (optional)*
  * Method: `_forward_process_requested(self, settings)`
    *Forward process_requested signal dari AlgorithmPanel.*
  * Method: `_on_images_imported(self, file_paths)`
    *Handle imported images dari drag & drop.*
    *Forward ke parent untuk database processing.*
    *Args:*
    *file_paths: List of image file paths*
  * Method: `remove_selected_images(self)`
    *Remove selected images. Forward ke DisplayPanel.*
  * Method: `get_select_image_list(self)`
    *Get selected image list. Forward ke DisplayPanel.*
  * Method: `load_image_paths(self)`
    *Refresh grid. Stub untuk compatibility.*
  * Method: `_on_algorithm_completed(self, data)`
    *Handle algorithm completion to display result.*
    *Args:*
    *data: dict containing 'batch_id' and 'settings'*
    *----------------------------------------*

--------------------

### 📄 [multiple_batch_delete_widget.py](file:///e:/APP%20Developer/Pixel%20Refine/pixel_refine_desktop/enhance_stack/components/batch_page_v2/multiple_batch_delete_widget.py)

* **Class**: `MultipleBatchDeleteWidget`
    *Widget to confirm deletion of multiple batches.*
    *Emits signals for yes/no actions.*
  * Method: `__init__(self, parent)`
  * Method: `_setup_ui(self)`
    *Set up the UI components.*
  * Method: `set_batch_info(self, batch_names)`
    *Sets the information about the batches to be deleted.*
    *Args:*
    *batch_names: A list of names of the batches selected for deletion.*
    *----------------------------------------*

--------------------

### 📄 [page_layout.py](file:///e:/APP%20Developer/Pixel%20Refine/pixel_refine_desktop/enhance_stack/components/batch_page_v2/page_layout.py)

* **Class**: `BatchPageV2Layout`
    *V2 Layout Wrapper for Batch Page.*
    *Uses setup_main_layout to build the UI.*
  * Method: `__init__(self, database_manager)`

* **Function**: `setup_main_layout(layout_instance, database_manager)`
    *Membuat layout utama dengan Workspace (Kiri) dan Batch List (Kanan).*
    *Menginisialisasi Controller dan menghubungkan sinyal antar panel.*

* **Function**: `_load_batch_content(layout_instance, batch_id)`
    *Helper to load batch content into workspace panel.*

* **Function**: `_handle_images_imported(layout_instance, file_paths)`
    *Delegates image import handling to ImportManager.*

* **Function**: `setup_signals(layout_instance)`
    *Menghubungkan sinyal-sinyal tambahan jika diperlukan.*
    *----------------------------------------*

--------------------

### 📄 [parameter_pages.py](file:///e:/APP%20Developer/Pixel%20Refine/pixel_refine_desktop/enhance_stack/components/batch_page_v2/parameter_pages.py)

* **Class**: `ParameterPages`
  * Method: `__init__(self, stacked_widget)`
    *Inisialisasi dengan QStackedWidget yang akan menampung halaman-halaman parameter.*
    *Kemudian, panggil metode untuk membuat dan menambahkan halaman.*
  * Method: `create_pages(self)`
    *Buat dan tambahkan semua halaman parameter ke QStackedWidget.*
  * Method: `wrap_in_scroll_area(self, widget)`
    *Bungkus widget ke dalam QScrollArea dengan tampilan yang lebih modern dan tanpa outline.*
  * Method: `get_default_page(self)`
    *Buat halaman default yang ditampilkan bila tidak ada pilihan parameter khusus.*
  * Method: `get_setting_pages_map(self)`
    *Kembalikan dictionary mapping nama halaman ke indeks QStackedWidget.*
    *----------------------------------------*

--------------------

### 📄 [quick_batch_dialog.py](file:///e:/APP%20Developer/Pixel%20Refine/pixel_refine_desktop/enhance_stack/components/batch_page_v2/quick_batch_dialog.py)

* **Class**: `QuickBatchDialog`
    *Custom dialog for creating a new batch with a 'Quick Create' option.*
  * Method: `__init__(self, default_name, parent)`
  * Method: `get_data(self)`
    *Return (name, skip_next_time)*
    *----------------------------------------*

--------------------

### 📄 [right_panel.py](file:///e:/APP%20Developer/Pixel%20Refine/pixel_refine_desktop/enhance_stack/components/batch_page_v2/right_panel.py)

* **Class**: `RightPanel`
    *Batch List Panel for Enhance Stack.*
    *Displays a list of Batches (Projects).*
  * Method: `__init__(self, controller, left_panel, store)`
  * Method: `on_store_changed(self, key, value)`
    *React to store changes (SyncMixin handles bindings).*
  * Method: `_load_batch_settings(self, batch_id)`
    *Load settings for specific batch from store.*
    *Uses SyncMixin scope to automate updates.*
  * Method: `_save_batch_settings(self)`
    *Save current UI values to store under the current batch scope.*
  * Method: `_setup_ui(self)`
  * Method: `resizeEvent(self, event)`
    *Handle resize to adjust splitter ratio based on screen state context.*
  * Method: `_on_settings_changed(self, save_to_store)`
    *Emit current settings and optionally save to persistence.*
  * Method: `get_current_settings(self)`
    *Public accessor for settings.*
  * Method: `_load_batches(self)`
    *Load batches from controller.*
  * Method: `_create_new_batch(self)`
  * Method: `_delete_batch(self)`
  * Method: `_calculate_algo_target_h(self)`
    *Calculate dynamic target height based on content but capped at 280px.*
  * Method: `_on_selection_changed(self, selected_values)`
    *Buffer selection change to prevent UI lag during rapid clicking.*
  * Method: `set_collapsed_state(self, collapsed)`
    *Update internal collapsed state and animate height.*
  * Method: `_do_handle_selection(self)`
    *Delegate handling to logical selection_handler.*
  * Method: `_on_process_all_clicked(self)`
    *Open BatchProcessDialog for batch processing.*
  * Method: `_on_batch_renamed(self, batch_id, new_name)`
    *Handle batch rename from ListGroup.*
  * Method: `_on_batches_reordered(self, batch_ids, direction, start_idx, target_idx)`
    *Handle reordering from ListGroup (Drag & Drop).*
  * Method: `_show_batch_context_menu(self, pos)`
    *Show context menu for batch items.*
  * Method: `_toggle_move_mode(self)`
    *----------------------------------------*

--------------------


## 📂 Directory: `Root Directory`

### 📄 [# DIRECTORY: pixel_refine_desktop/enhance_stack/components/batch_page_v2/parameter_alignment](file:///e:/APP%20Developer/Pixel%20Refine/# DIRECTORY: pixel_refine_desktop/enhance_stack/components/batch_page_v2/parameter_alignment)


--------------------


## 📂 Directory: `Root Directory`

### 📄 [akaze_parameter_settings.py](file:///e:/APP%20Developer/Pixel%20Refine/pixel_refine_desktop/enhance_stack/components/batch_page_v2/parameter_alignment/akaze_parameter_settings.py)

* **Function**: `get_default_font(size, weight)`
    *Mengembalikan objek QFont dengan ukuran dan berat tertentu.*

* **Function**: `load_akaze_config()`
    *Muat konfigurasi AKAZE dari file JSON, tangani default.*

* **Function**: `_load_general_settings()`
    *Membaca semua setting relevan dari app_setting.json.*

* **Function**: `save_akaze_config(config)`
    *Menyimpan konfigurasi AKAZE ke ALGORITHM_PARAMETER_SETTINGS_FILE.*

* **Function**: `create_slider(label_text, min_val, max_val, step, initial_value, format_func, tooltip)`

* **Function**: `get_akaze_page()`
    *----------------------------------------*

--------------------

### 📄 [farneback_parameter_settings.py](file:///e:/APP%20Developer/Pixel%20Refine/pixel_refine_desktop/enhance_stack/components/batch_page_v2/parameter_alignment/farneback_parameter_settings.py)

* **Function**: `get_default_font(size, weight)`

* **Function**: `load_farneback_config()`

* **Function**: `_load_general_setting()`
    *Membaca semua setting relevan dari app_setting.json.*

* **Function**: `save_farneback_config(config)`
    *Menyimpan konfigurasi Farneback ke Parameter_Stack_Enhance.json.*

* **Function**: `create_slider(label_text, min_val, max_val, step, initial_value, format_func, tooltip)`

* **Function**: `get_farneback_optical_flow_page()`
    *----------------------------------------*

--------------------

### 📄 [light_glue_parameter_settings.py](file:///e:/APP%20Developer/Pixel%20Refine/pixel_refine_desktop/enhance_stack/components/batch_page_v2/parameter_alignment/light_glue_parameter_settings.py)

* **Function**: `get_default_font(size, weight)`

* **Function**: `load_light_glue_config(config_filename)`
    *Memuat konfigurasi LightGlue dari file JSON.*
    *Fungsi ini sekarang menjadi sumber utama untuk memuat konfigurasi.*

* **Function**: `_load_general_settings()`
    *Membaca semua setting relevan dari app_setting.json.*

* **Function**: `save_light_glue_config(config)`
    *Menyimpan konfigurasi LightGlue ke ALGORITHM_PARAMETER_SETTINGS_FILE.*

* **Function**: `create_slider(label_text, min_val, max_val, step, initial_value, format_func, tooltip)`

* **Function**: `get_light_glue_page()`
    *Fungsi utama untuk membuat halaman UI pengaturan LightGlue.*
    *----------------------------------------*

--------------------

### 📄 [orb_parameter_settings.py](file:///e:/APP%20Developer/Pixel%20Refine/pixel_refine_desktop/enhance_stack/components/batch_page_v2/parameter_alignment/orb_parameter_settings.py)

* **Function**: `get_default_font(size, weight)`

* **Function**: `load_orb_config()`

* **Function**: `_load_general_settings()`
    *Membaca semua setting relevan dari app_setting.json.*

* **Function**: `save_orb_config(config)`
    *Menyimpan konfigurasi ORB ke ALGORITHM_PARAMETER_SETTINGS_FILE.*

* **Function**: `create_slider(label_text, min_val, max_val, step, initial_value, format_func, tooltip)`

* **Function**: `get_orb_page()`
    *----------------------------------------*

--------------------


## 📂 Directory: `Root Directory`

### 📄 [# DIRECTORY: pixel_refine_desktop/enhance_stack/components/batch_page_v2/parameter_denoising](file:///e:/APP%20Developer/Pixel%20Refine/# DIRECTORY: pixel_refine_desktop/enhance_stack/components/batch_page_v2/parameter_denoising)


--------------------


## 📂 Directory: `Root Directory`

### 📄 [similarity_parameter_settings.py](file:///e:/APP%20Developer/Pixel%20Refine/pixel_refine_desktop/enhance_stack/components/batch_page_v2/parameter_denoising/similarity_parameter_settings.py)

* **Function**: `get_default_font(size, weight)`

* **Function**: `load_similarity_config()`

* **Function**: `save_similarity_v1_config(config_to_save)`

* **Function**: `create_slider_input_field_layout(min_val, max_val, initial_value_slider, initial_value_text, slider_multiplier, text_format_func, validator, c_locale, slider_min_val, slider_max_val, is_overlap)`
    *Membuat QHBoxLayout yang berisi Slider, QLineEdit, dan label '%' jika is_overlap.*
    *Mengembalikan QHBoxLayout, slider, dan line_edit.*

* **Function**: `get_similarity_settings_page()`
    *----------------------------------------*

--------------------

### 📄 [similarity_v2_parameter_settings.py](file:///e:/APP%20Developer/Pixel%20Refine/pixel_refine_desktop/enhance_stack/components/batch_page_v2/parameter_denoising/similarity_v2_parameter_settings.py)

* **Function**: `get_default_font(size, weight)`

* **Function**: `load_similarity_v2_config()`
    *Memuat konfigurasi Similarity V2 dari Parameter_Stack_Enhance.json.*

* **Function**: `save_similarity_v2_config(config)`
    *Menyimpan konfigurasi Similarity V2 ke Parameter_Stack_Enhance.json.*

* **Function**: `create_slider_with_input(label_text, min_val, max_val, initial_value_slider, initial_value_text, slider_multiplier, text_format_func, validator, tooltip, parent_layout, c_locale, slider_min_val, slider_max_val)`

* **Function**: `get_similarity_v2_settings_page()`
    *----------------------------------------*

--------------------


## 📂 Directory: `Root Directory`

### 📄 [# DIRECTORY: pixel_refine_desktop/enhance_stack/controllers](file:///e:/APP%20Developer/Pixel%20Refine/# DIRECTORY: pixel_refine_desktop/enhance_stack/controllers)


--------------------


## 📂 Directory: `Root Directory`

### 📄 [batch_page_controller.py](file:///e:/APP%20Developer/Pixel%20Refine/pixel_refine_desktop/enhance_stack/controllers/batch_page_controller.py)

* **File Overview**:
    *Batch Page Controller.*
    *Handles business logic for batch processing operations.*

* **Class**: `BatchPageController`
    *Controller for batch page operations.*
    *Coordinates between view and model for batch processing.*
  * Method: `__init__(self, db_path, parent)`
    *Initialize controller.*
    *Args:*
    *db_path: Path to database*
    *parent: Parent QObject*
  * Method: `create_batch(self, batch_name)`
    *Create a new batch.*
    *Args:*
    *batch_name: Name for the batch*
    *Returns:*
    *Batch ID if successful, None otherwise*
  * Method: `get_all_batches(self)`
    *Get all batches with their images.*
    *Returns:*
    *List of BatchModel instances*
  * Method: `get_batch(self, batch_id)`
    *Get a specific batch with its images.*
    *Args:*
    *batch_id: Batch ID*
    *Returns:*
    *BatchModel or None if not found*
  * Method: `delete_batch(self, batch_id)`
    *Delete a batch.*
    *Args:*
    *batch_id: Batch ID to delete*
    *Returns:*
    *True if successful, False otherwise*
  * Method: `reorder_batches(self, batch_ids)`
    *Reorder batches in the database.*
  * Method: `update_batch_name(self, batch_id, new_name)`
    *Update the name of a batch.*
    *Args:*
    *batch_id: The ID of the batch to update.*
    *new_name: The new name for the batch.*
    *Returns:*
    *True if successful, False otherwise.*
  * Method: `add_images_to_batch(self, batch_id, image_paths)`
    *Add images to a batch.*
    *Args:*
    *batch_id: Batch ID*
    *image_paths: List of image paths to add*
    *Returns:*
    *Number of images added*
  * Method: `remove_images_from_batch(self, batch_id, image_paths)`
    *Remove images from a batch.*
    *Args:*
    *batch_id: Batch ID*
    *image_paths: List of image paths to remove*
    *Returns:*
    *Number of images removed*
  * Method: `set_reference_image(self, batch_id, image_path)`
    *Set the reference image for a batch.*
    *Args:*
    *batch_id: Batch ID*
    *image_path: Path of image to set as reference*
    *Returns:*
    *True if successful, False otherwise*
  * Method: `get_batch_count(self)`
    *Get total number of batches.*
    *Returns:*
    *Batch count*
  * Method: `get_batch_image_count(self, batch_id)`
    *Get number of images in a batch.*
    *Args:*
    *batch_id: Batch ID*
    *Returns:*
    *Image count*
  * Method: `handle_batch_selected(self, batch_id)`
    *Notify that a batch has been selected.*
    *This signal is listened to by the RightPanel/Layout to switch context.*
    *----------------------------------------*

--------------------

### 📄 [image_processing_controller.py](file:///e:/APP%20Developer/Pixel%20Refine/pixel_refine_desktop/enhance_stack/controllers/image_processing_controller.py)

* **File Overview**:
    *Image Processing Controller.*
    *Orchestrates image processing algorithms (alignment, denoising, super resolution).*

* **Class**: `ImageProcessingController`
    *Controller for image processing operations.*
    *Coordinates algorithm execution and workflow.*
  * Method: `__init__(self, parent)`
    *Initialize controller.*
    *Args:*
    *parent: Parent QObject*
  * Method: `execute_alignment(self, algorithm_name, parameters, image_paths, single_process)`
    *Execute alignment algorithm.*
    *Args:*
    *algorithm_name: Name of alignment algorithm (ORB, AKAZE, etc.)*
    *parameters: Algorithm parameters*
    *image_paths: List of image paths to align*
    *single_process: Whether this is single or batch processing*
    *Returns:*
    *Path to result or None if failed*
  * Method: `execute_denoising(self, algorithm_name, parameters, image_paths, single_process)`
    *Execute denoising algorithm.*
    *Args:*
    *algorithm_name: Name of denoising algorithm (Average, Median, Similarity)*
    *parameters: Algorithm parameters*
    *image_paths: List of image paths*
    *single_process: Whether this is single or batch processing*
    *Returns:*
    *Path to result or None if failed*
  * Method: `execute_super_resolution(self, algorithm_name, parameters, image_path, single_process)`
    *Execute super resolution algorithm.*
    *Args:*
    *algorithm_name: Name of super resolution algorithm*
    *parameters: Algorithm parameters*
    *image_path: Path to image*
    *single_process: Whether this is single or batch processing*
    *Returns:*
    *Path to result or None if failed*
  * Method: `execute_workflow(self, alignment_config, denoising_config, super_res_config, image_paths, single_process)`
    *Execute complete processing workflow.*
    *Args:*
    *alignment_config: Alignment algorithm configuration*
    *denoising_config: Denoising algorithm configuration*
    *super_res_config: Super resolution algorithm configuration*
    *image_paths: List of image paths*
    *single_process: Whether this is single or batch processing*
    *Returns:*
    *Path to final result or None if failed*
  * Method: `_run_alignment_algorithm(self, algorithm_name, parameters, single_process)`
    *Internal method to run alignment algorithm.*
    *This will import and call the actual algorithm modules.*
  * Method: `_run_denoising_algorithm(self, algorithm_name, parameters, single_process)`
    *Internal method to run denoising algorithm.*
  * Method: `_run_super_resolution_algorithm(self, algorithm_name, parameters, single_process)`
    *Internal method to run super resolution algorithm.*
    *----------------------------------------*

--------------------

### 📄 [import_export_controller.py](file:///e:/APP%20Developer/Pixel%20Refine/pixel_refine_desktop/enhance_stack/controllers/import_export_controller.py)

* **File Overview**:
    *Import/Export Controller.*
    *Handles file import/export operations including validation and format conversion.*

* **Class**: `ImportExportController`
    *Controller for import/export operations.*
    *Handles file validation, format conversion, and threading.*
  * Method: `__init__(self, parent)`
    *Initialize controller.*
    *Args:*
    *parent: Parent QObject*
  * Method: `validate_files(self, file_paths)`
    *Validate file paths and formats.*
    *Args:*
    *file_paths: List of file paths to validate*
    *Returns:*
    *Tuple of (valid_paths, invalid_paths)*
  * Method: `check_duplicates(self, paths, existing_paths)`
    *Check for duplicate files.*
    *Args:*
    *paths: List of paths to check*
    *existing_paths: List of already existing paths*
    *Returns:*
    *Tuple of (unique_paths, duplicate_paths)*
  * Method: `group_by_format(self, file_paths)`
    *Group files by format.*
    *Args:*
    *file_paths: List of file paths*
    *Returns:*
    *Dictionary mapping format type to list of paths*
  * Method: `needs_tiff_conversion(self, tiff_path)`
    *Check if TIFF file needs conversion.*
    *Args:*
    *tiff_path: Path to TIFF file*
    *Returns:*
    *Tuple of (needs_conversion, compression_type)*
  * Method: `convert_tiff_to_uncompressed(self, tiff_paths, output_folder)`
    *Convert compressed TIFF files to uncompressed.*
    *Args:*
    *tiff_paths: List of TIFF file paths*
    *output_folder: Output folder for converted files*
    *Returns:*
    *List of tuples (success, result_path_or_error)*
  * Method: `start_import_thread(self, image_paths, database_manager, batch_size, delay_ms)`
    *Start background import thread.*
    *Args:*
    *image_paths: List of image paths to import*
    *database_manager: Database manager instance*
    *batch_size: Number of images per batch*
    *delay_ms: Delay between batches in milliseconds*
  * Method: `export_image(self, source_path, destination_path, quality, optimize)`
    *Export image with metadata preservation.*
    *Args:*
    *source_path: Source image path*
    *destination_path: Destination path*
    *quality: JPEG quality (for JPEG export)*
    *optimize: Whether to optimize (for JPEG/PNG)*
    *Returns:*
    *True if successful, False otherwise*
  * Method: `_on_import_progress(self, value, remaining)`
    *Handle import progress updates.*
  * Method: `_on_import_complete(self, successful_count)`
    *Handle import completion.*
    *----------------------------------------*

--------------------

### 📄 [single_page_controller.py](file:///e:/APP%20Developer/Pixel%20Refine/pixel_refine_desktop/enhance_stack/controllers/single_page_controller.py)

* **File Overview**:
    *Single Page Controller.*
    *Handles business logic for single page image processing operations.*

* **Class**: `SinglePageController`
    *Controller for single page operations.*
    *Coordinates between view and model for single image processing.*
  * Method: `__init__(self, db_path, parent)`
    *Initialize controller.*
    *Args:*
    *db_path: Path to database*
    *parent: Parent QObject*
  * Method: `get_all_image_paths(self)`
    *Get all image paths from database.*
    *Returns:*
    *List of image file paths*
  * Method: `validate_import_paths(self, paths)`
    *Validate import paths and check for duplicates.*
    *Args:*
    *paths: List of image paths to validate*
    *Returns:*
    *Tuple of (valid_unique_paths, duplicate_paths)*
  * Method: `delete_images(self, paths)`
    *Delete images from database.*
    *Args:*
    *paths: List of image paths to delete*
    *Returns:*
    *Number of images deleted*
  * Method: `get_image_count(self)`
    *Get total number of images.*
    *Returns:*
    *Image count*
    *----------------------------------------*

--------------------


## 📂 Directory: `Root Directory`

### 📄 [# DIRECTORY: pixel_refine_desktop/enhance_stack/core/algorithm](file:///e:/APP%20Developer/Pixel%20Refine/# DIRECTORY: pixel_refine_desktop/enhance_stack/core/algorithm)


--------------------


## 📂 Directory: `Root Directory`

### 📄 [base_worker.py](file:///e:/APP%20Developer/Pixel%20Refine/pixel_refine_desktop/enhance_stack/core/algorithm/base_worker.py)

* **Class**: `BaseAlgorithmWorker`
    *Generic background thread to execute algorithm logic.*
    *Provides standard signals and cancellation handling.*
  * Method: `__init__(self, main_func)`
    *Initialize the worker.*
    *Args:*
    *main_func: The primary function to execute (e.g., AverageAlgorithm.main)*
    **args, **kwargs: Arguments to pass to main_func*
  * Method: `run(self)`
    *Execute the function and emit signals.*
  * Method: `stop(self)`
    *Request the worker to stop.*
    *----------------------------------------*

--------------------


## 📂 Directory: `Root Directory`

### 📄 [# DIRECTORY: pixel_refine_desktop/enhance_stack/core/algorithm/alignment](file:///e:/APP%20Developer/Pixel%20Refine/# DIRECTORY: pixel_refine_desktop/enhance_stack/core/algorithm/alignment)


--------------------


## 📂 Directory: `Root Directory`

### 📄 [AKAZE.py](file:///e:/APP%20Developer/Pixel%20Refine/pixel_refine_desktop/enhance_stack/core/algorithm/alignment/AKAZE.py)

* **Class**: `AKAZEAlgorithm`
  * Method: `__init__(self, db_path, hdf5_path)`
  * Method: `load_akaze_config(config_filename)`
    *Membaca konfigurasi AKAZE dari file JSON. Jika gagal, mengembalikan nilai default.*
  * Method: `load_akaze_config_for_batch(config_filename)`
    *Membaca konfigurasi AKAZE dari file JSON. Jika gagal, mengembalikan nilai default.*
  * Method: `compute_features_block(self, akaze_instance, enhanced_gray_base, enhanced_gray_target, x, y, bw, bh, overlap_px, img_w, img_h, max_kps_per_block)`
  * Method: `calculate_global_motion(self, base_image, target_image, config_filename, num_blocks, overlap, stop_requested)`
  * Method: `compensate_motion(self, base_image, base_points, target_points, config_filename)`
    *Menerapkan kompensasi gerakan menggunakan transformasi (dengan USAC_MAGSAC)*
    *untuk menyelaraskan gambar.*

* **Function**: `main(db_path, update_progress, stop_requested, single_process, batch_id, config_filename, save_align, align_folder, command_save_to_hd5f, num_workers)`

* **Function**: `running_akaze(parent, single_process, batch_id, progress_callback, stop_callback)`
    *----------------------------------------*

--------------------

### 📄 [Farneback_optical_flow.py](file:///e:/APP%20Developer/Pixel%20Refine/pixel_refine_desktop/enhance_stack/core/algorithm/alignment/Farneback_optical_flow.py)

* **Class**: `FarnebackAlgorithm`
  * Method: `__init__(self, db_path, hdf5_path)`
  * Method: `get_all_image_paths_for_batch_process(self, batch_id)`
  * Method: `load_farneback_config(config_filename)`
    *Membaca konfigurasi Farneback Optical Flow dari file JSON.*
    *Jika gagal, mengembalikan nilai default.*
  * Method: `load_farneback_config_for_batch(config_filename)`
    *Membaca konfigurasi Farneback Optical Flow dari file JSON.*
    *Jika gagal, mengembalikan nilai default.*
  * Method: `_compute_block_cpu_internal(self, x, y, bw, bh, overlap_ratio, base_gray_8bit, target_gray_8bit, fb_config, w, h)`
  * Method: `calculate_optical_flow(self, base_image, target_image, config_filename, stop_requested)`
  * Method: `compensate_motion(self, base_image_input, flow, image_id, config_filename)`

* **Function**: `main(db_path, update_progress, stop_requested, single_process, batch_id)`

* **Function**: `running_farneback_optical_flow(parent, single_process, batch_id, progress_callback, stop_callback)`
    *----------------------------------------*

--------------------

### 📄 [Light_Glue.py](file:///e:/APP%20Developer/Pixel%20Refine/pixel_refine_desktop/enhance_stack/core/algorithm/alignment/Light_Glue.py)

* **Class**: `LightGlueAlgorithm`
    *LightGlueAlgorithm versi threaded:*
    *- Model ONNX dimuat di thread terpisah agar UI tidak hang.*
    *- Inferensi dijalankan di thread worker dengan proteksi error.*
    *- GPU memory dilepas otomatis saat crash, OOM, atau stop manual.*
  * Method: `__init__(self, db_path, hdf5_path)`
  * Method: `_initialize_model_thread(self)`
  * Method: `_download_and_prepare_model(self)`
  * Method: `_create_inference_session(self)`
  * Method: `run_inference_threaded(self, input_data, callback)`
    *Jalankan inferensi di thread terpisah dengan auto-cleanup GPU.*
    *callback: fungsi opsional yang menerima hasil output.*
  * Method: `_inference_worker(self, input_data, callback)`
  * Method: `_cleanup_gpu(self)`
  * Method: `calculate_global_motion(self, base_image, target_image, stop_requested)`
  * Method: `compensate_motion(self, base_image, base_points, target_points, config_filename)`
    *Menerapkan kompensasi gerakan menggunakan transformasi (dengan USAC_MAGSAC)*
    *untuk menyelaraskan gambar.*

* **Function**: `is_frozen_app()`
    *Memeriksa apakah aplikasi berjalan sebagai biner yang dibekukan (misalnya, Nuitka, PyInstaller).*

* **Function**: `find_cudnn_dlls()`
    *Cari semua file cuDNN (cudnn64_*.dll) + CUDA core (cublas, cufft, curand)*
    *hanya dari instalasi sistem, bukan dari venv.*

* **Function**: `add_dll_to_path()`
    *Menambahkan direktori yang berisi DLL ONNX Runtime dan CuDNN ke PATH*
    *menggunakan variabel lingkungan atau pencarian global.*

* **Function**: `main(db_path, update_progress, stop_requested, single_process, batch_id, config_filename, save_align, align_folder, command_save_to_hd5f, num_workers)`

* **Function**: `running_light_glue(parent, single_process, batch_id, progress_callback, stop_callback)`
    *----------------------------------------*

--------------------

### 📄 [ORB.py](file:///e:/APP%20Developer/Pixel%20Refine/pixel_refine_desktop/enhance_stack/core/algorithm/alignment/ORB.py)

* **Class**: `ORBAlgorithm`
  * Method: `__init__(self, db_path, hdf5_path)`
  * Method: `load_orb_config(config_filename)`
    *Membaca konfigurasi ORB dari file JSON. Jika gagal, mengembalikan nilai default.*
  * Method: `load_orb_config_for_batch(config_filename)`
    *Membaca konfigurasi ORB BATCH dari file JSON. Jika gagal, mengembalikan nilai default.*
  * Method: `compute_features_block(self, akaze_instance, enhanced_gray_base, enhanced_gray_target, x, y, bw, bh, overlap_px, img_w, img_h, max_kps_per_block)`
  * Method: `calculate_global_motion(self, base_image, target_image, config_filename, num_blocks, overlap, stop_requested)`
  * Method: `compensate_motion(self, base_image, base_points, target_points, config_filename)`
    *Menerapkan kompensasi gerakan menggunakan transformasi (dengan USAC_MAGSAC)*
    *untuk menyelaraskan gambar.*

* **Function**: `main(db_path, update_progress, stop_requested, single_process, batch_id, config_filename, save_align, align_folder, command_save_to_hd5f, num_workers)`

* **Function**: `running_orb(parent, single_process, batch_id, progress_callback, stop_callback)`
    *----------------------------------------*

--------------------


## 📂 Directory: `Root Directory`

### 📄 [# DIRECTORY: pixel_refine_desktop/enhance_stack/core/algorithm/alignment/alignment_features](file:///e:/APP%20Developer/Pixel%20Refine/# DIRECTORY: pixel_refine_desktop/enhance_stack/core/algorithm/alignment/alignment_features)


--------------------


## 📂 Directory: `Root Directory`

### 📄 [alignment_core.py](file:///e:/APP%20Developer/Pixel%20Refine/pixel_refine_desktop/enhance_stack/core/algorithm/alignment/alignment_features/alignment_core.py)

* **Class**: `ONNXSessionManager`
    *Sebuah Context Manager untuk memastikan session ONNX dan sumber daya GPU*
    *selalu dilepaskan dengan benar, bahkan jika terjadi error.*
  * Method: `__init__(self, model_path)`
  * Method: `__enter__(self)`
    *Dipanggil saat memasuki blok 'with'. Memuat model dan mengembalikan session.*
  * Method: `__exit__(self, exc_type, exc_val, exc_tb)`
    *Dipanggil saat keluar dari blok 'with'. Menjamin pelepasan sumber daya.*
  * Method: `_initialize_raft_model(self, model_path)`
    *Memuat session ONNX RAFT dengan logging minimal (hanya error fatal).*
    *Returns:*
    *ort.InferenceSession atau None jika gagal.*

* **Class**: `SimAM`
  * Method: `__init__(self, e)`
  * Method: `forward(self, x)`

* **Class**: `FeatureBlock`
  * Method: `__init__(self, in_ch, out_ch)`
  * Method: `forward(self, x)`

* **Class**: `BaseSimilarityWeightGenerator`
  * Method: `__init__(self)`
  * Method: `init_backbone(self)`
  * Method: `extract_features(self, ref_img)`
  * Method: `compute_similarity_error(self, ref_img, curr_img, features)`
  * Method: `map_to_weights(self, error_tensor, is_inference)`
  * Method: `forward(self, ref_img, curr_img, is_inference)`

* **Class**: `AdaptiveOpticalFlowHead`
  * Method: `__init__(self, feature_channels, max_search_radius)`
  * Method: `forward(self, features)`

* **Class**: `PhysicsInformedFlowGenerator`
  * Method: `init_backbone(self)`
  * Method: `extract_features(self, ref_img)`
  * Method: `compute_similarity_error(self, ref_img, curr_img, features)`
  * Method: `map_to_weights(self, error_tensor, is_inference)`

* **Class**: `Student_NanoBurstNet`
  * Method: `__init__(self)`
  * Method: `forward(self, ref_gray, curr_gray)`

* **Function**: `get_taichi_worker()`
    *Compatibility wrapper for centralized Taichi worker.*

* **Function**: `process_single_tile_resized(args, stop_requested)`
    *Worker yang memproses satu tile (sudah di-resize sesuai ukuran model).*

* **Function**: `create_blending_weights(tile_h, tile_w, overlap_h, overlap_w)`
    *Membuat peta bobot blending 2D (smooth window) agar transisi antar tile halus.*

* **Function**: `compute_flow_raft(ref_img, current_img, session, grid_rows, grid_cols, model_input_size, overlap_ratio, progress_callback, stop_requested)`
    *Menghitung optical flow dengan pembagian tile grid dinamis.*
    *Mendukung callback progres per tile untuk update progress UI secara real-time.*
    *Args:*
    *ref_img, current_img: np.uint8 [H, W, 3]*
    *session: ONNX session RAFT*
    *grid_rows, grid_cols: jumlah pembagian grid (vertikal x horizontal)*
    *model_input_size: resolusi model RAFT (H, W)*
    *overlap_ratio: proporsi overlap antar tile (0–1)*
    *progress_callback: callable(done_tiles, total_tiles) opsional*
    *Returns:*
    *final_flow: np.float32 [H, W, 2]*

* **Function**: `scale_flow_to_full_res(flow, model_h, model_w, full_h, full_w)`
    *Scale optical flow field from model resolution back to original resolution.*
    *Also scales the flow vectors accordingly.*

* **Function**: `compute_flow_with_raft(ref_img, current_img, session)`
    *Menghitung optical flow menggunakan model RAFT ONNX.*
    *Gambar input harus dalam format (H, W, C) dengan nilai [0, 255].*

* **Function**: `scale_flow(flow, work_h, work_w, full_h, full_w, ksize)`
    *Scale flow dengan interpolasi linear biasa, lalu dihaluskan dengan Median Filter.*
    *Cocok untuk menghilangkan noise 'salt-and-pepper' pada flow field.*

* **Function**: `warp_image_opencv(image, flow, interpolation, border_mode, x_coords, y_coords)`
    *Warp gambar menggunakan optical flow (CPU path).*

* **Function**: `visualize_flow(flow)`
    *Mengubah peta optical flow menjadi citra berwarna untuk visualisasi magnitude.*
    *0px pergeseran: Hijau (0, 255, 0)*
    *Pergeseran Maksimum: Merah (0, 0, 255)*

* **Function**: `save_aligned_image(aligned_img, index, backend_name, save_folder, save_prefix, harvest_mode)`
    *Menyimpan gambar RGB yang telah diselaraskan ke folder output dengan normalisasi dinamis.*
    *Jika harvest_mode aktif, sistem akan memastikan file tidak menimpa file lama.*

* **Function**: `perform_alignment_gpu(images, reference_image_float, work_res_h, work_res_w, tile_h, tile_w, ref_dtype, update_progress, stop_requested, num_alignment_workers, save_align_image, harvest_alignment, progress_start, progress_end, return_format, optical_flow_type)`
    *GPU-accelerated alignment menggunakan Taichi AOT terpandu AI adaptif.*
    *Berkomunikasi langsung dengan compute_flow (AOT) via AOTEngine dengan*
    *suntikan matriks parameter radius_map dinamis per frame dari PyTorch.*

* **Function**: `perform_image_alignment(images, reference_image_float, work_res_h, work_res_w, tile_h, tile_w, ref_dtype, update_progress, stop_requested, optical_flow_type, num_alignment_workers, visualization, save_align_image, harvest_alignment, progress_start, progress_end)`
    *----------------------------------------*

--------------------

### 📄 [automated_alignment_verification.py](file:///e:/APP%20Developer/Pixel%20Refine/pixel_refine_desktop/enhance_stack/core/algorithm/alignment/alignment_features/automated_alignment_verification.py)

* **Function**: `calculate_ssim(img1, img2)`
    *Menghitung SSIM (Structural Similarity Index) secara manual untuk kontrol yang ketat*

* **Function**: `calculate_mse(img1, img2)`
    *Menghitung Mean Squared Error (Semakin kecil semakin baik)*

* **Function**: `run_strict_verification()`
    *----------------------------------------*

--------------------

### 📄 [global_feature copy.py](file:///e:/APP%20Developer/Pixel%20Refine/pixel_refine_desktop/enhance_stack/core/algorithm/alignment/alignment_features/global_feature copy.py)

* **Function**: `get_all_image_paths_for_single_process(db_path)`
    *Mengambil semua path gambar, memvalidasi keberadaannya di disk,*
    *dan menghapus entri yang tidak valid dari database.*

* **Function**: `get_all_image_paths_for_batch_process(db_path, batch_id)`
    *Mengambil semua path gambar untuk batch ID tertentu, memvalidasi,*
    *dan menghapus entri yang tidak valid dari database.*

* **Function**: `_prepare_image_array_from_raw(original_path, linear_mode, generate_ref_proxy)`

* **Function**: `load_images_from_paths(image_paths, stop_requested, linear_mode, capture_ref_proxy)`

* **Function**: `save_to_hdf5(h5f, dataset_name, cropped, metadata)`
    *Save images (array) into HDF5 and embed metadata as attributes using multithreading.*
    *Parameters:*
    *- h5f: opened HDF5 file object*
    *- dataset_name: name of dataset to be created*
    *- cropped: array of images to be saved*
    *- metadata: dictionary containing metadata or EXIF of images*

* **Function**: `save_align_to_folder(image, index, original_path, align_folder, load_config_func)`
    *Menyimpan gambar dalam format TIFF ke folder yang ditentukan,*
    *kemudian mengembalikan metadata dari file asli ke file output menggunakan exiftool.*
    *[MODIFIED] Menggunakan logika penyimpanan yang lebih robust dengan kontrol kompresi.*

* **Function**: `save_image(image, output_path, reference_image_path)`
    *Menyimpan gambar dengan kontrol kompresi untuk file TIFF demi kompatibilitas.*
    *Menyalin metadata orientasi dari gambar referensi menggunakan exiftool.*

* **Function**: `calculate_scale_from_gt_proxy(linear_img, gt_proxy, ref_dtype)`
    *Menghitung faktor skala optimal untuk `to_gamma_proxy` dengan membandingkan*
    *Green Channel dari Linear Image (RAW Space) dengan Green Channel dari GT Proxy (sRGB).*
    *Args:*
    *linear_img: Gambar Linear (Main Image), BGR.*
    *gt_proxy: Gambar Ground Truth dari rawpy (sRGB), BGR.*
    *ref_dtype: Tipe data referensi (uint16/uint8).*
    *Returns:*
    *float: Faktor skala (scale) yang optimal.*

* **Function**: `save_linear_dng(image, output_path, reference_image_path)`
    *Menyimpan gambar sebagai Linear DNG (RGB) dengan kompresi Deflate.*

* **Function**: `save_special_jpg_and_png(img_np, dst_path, reference_image_path, quality, optimize, png_compress_level)`
    *Mengkonversi array NumPy, menerapkan rotasi, dan menyimpannya ke JPG/PNG*
    *dengan opsi kompresi yang lebih agresif dan cerdas.*

* **Function**: `extract_exif(image_path)`
    *Mengambil metadata EXIF dari file gambar menggunakan exifread.*
    *Mengembalikan dictionary dengan data EXIF dan path file.*

* **Function**: `extract_all_metadata(image_paths, metadata_file)`
    *Mengekstrak metadata dari seluruh image paths dan menyimpannya ke file JSON.*
    *Jika file metadata sudah ada, data baru akan ditambahkan (tidak overwrite).*

* **Function**: `prepare_gray(img)`

* **Function**: `prepare_image(image, grayscale, use_clahe)`
    *Fungsi Hibrida Cerdas.*
    *- Untuk Grayscale (AKAZE): Mendelegasikan tugas ke `prepare_gray_akaze` untuk hasil yang 100% identik.*
    *- Untuk Berwarna (LightGlue): Menggunakan logika internalnya sendiri yang kuat.*
    *Args:*
    *image: Gambar input.*
    *grayscale (bool): Jika True, akan memanggil pipeline khusus grayscale.*
    *use_clahe (bool): Jika True, akan menerapkan CLAHE.*
    *Returns:*
    *Gambar uint8 yang telah diproses.*

* **Function**: `resize_with_padding(img, target_size, pad_color)`

* **Function**: `resize_all_with_padding(images, method, verbose, pad_color, return_original_sizes, stop_requested, force_even)`
    *Resize + pad all images to the same size using letterbox strategy.*
    *Args:*
    *images (list): Daftar array gambar (NumPy).*
    *method (str): Strategi penentuan ukuran target. Pilihan:*
    *- "min"      : gunakan tinggi & lebar minimum dari semua gambar.*
    *- "max"      : gunakan tinggi & lebar maksimum dari semua gambar.*
    *- "median"   : gunakan median tinggi & lebar dari semua gambar.*
    *- "preserve" : gunakan ukuran gambar pertama sebagai referensi.*
    *verbose (bool): Jika True, cetak informasi proses.*
    *pad_color (tuple): Warna padding (B, G, R).*
    *return_original_sizes (bool): Jika True, juga kembalikan ukuran asli.*

* **Function**: `gaussian_window(size, sigma_scale)`
    *Menghasilkan jendela Gaussian 2D [0, 1] float32 C-contiguous.*

* **Function**: `estimate_noise_in_python(ref_image_gray_float)`

* **Function**: `apply_s_curve_float32(img, strength, pivot)`
    *S-Curve float32 dengan pivot.*
    *Input: 0..255 float32*
    *Output: float32 0..255*

* **Function**: `preprocess_in_python(ref_image_float, s_curve_contrast)`
    *Melakukan semua pra-pemrosesan gambar referensi di Python.*
    *[MODIFIED] Hanya melakukan konversi ke grayscale sesuai permintaan user.*
    *Mengembalikan gambar grayscale dan nilai noise-nya (estimasi cepat).*

* **Function**: `estimate_noise_variance(gray_image, edge_threshold_low, dilate_kernel_size, min_flat_pixels_ratio)`
    *Memperkirakan tingkat noise dalam gambar dengan menghitung varians Laplacian*
    *hanya pada area gambar yang dianggap "datar" (tidak ada tepi atau tekstur yang kuat).*
    *Args:*
    *gray_image (np.array): Gambar grayscale.*
    *edge_threshold_low (int): Ambang batas rendah untuk detektor tepi Canny.*
    *dilate_kernel_size (int): Ukuran kernel untuk operasi dilasi pada tepi.*
    *min_flat_pixels_ratio (float): Rasio minimum piksel datar yang dibutuhkan.*
    *Jika terlalu sedikit, estimasi bisa tidak andal.*
    *Returns:*
    *float: Varians noise yang diestimasi.*

* **Function**: `get_adaptive_bilateral(noise_level, min_noise, max_noise, min_d, max_d, min_sigma, max_sigma)`
    *Menghitung parameter untuk filter bilateral secara dinamis berdasarkan tingkat noise.*

* **Function**: `normalize_image(image, dtype, out)`
    *Normalisasi gambar ke range [0, 1] float32.*
    *- Jika `out` disediakan, hasil akan disalin ke buffer tersebut (otomatis disesuaikan ukuran & dimensi).*
    *- Jika `out` tidak ada, fungsi akan membuat array baru.*
    *- Menangani RGB dan grayscale secara otomatis.*
    *Args:*
    *image: np.ndarray (grayscale 2D atau RGB 3D)*
    *dtype: tipe data asli dari gambar (mis. np.uint8, np.uint16)*
    *out: buffer opsional (np.ndarray dengan dtype=float32 dan dimensi sama)*
    *Returns:*
    *np.ndarray (float32, 3 channel)*

* **Function**: `calculate_auto_scale(linear_img_float, target_mean)`
    *Menghitung scale factor agar rata-rata brightness mendekati target_mean.*
    *Digunakan untuk normalisasi brightness referensi sebelum estimasi gamma proxy.*
    *linear_img_float: HxWx3 (Linear RGB) atau HxW (Gray), range 0.0-1.0*

* **Function**: `to_gamma_proxy(linear_img, scale, gamma_pow, slope, cutoff)`
    *Konversi Linear [0,1] ke Gamma Proxy [0,1] untuk Alignment.*
    *Menggunakan parameter tuning manual: Scale, Gamma, Slope, Cutoff.*

* **Function**: `deduplicate_keypoints(mkptsL, mkptsR, scores, image_shape, distance_thresh)`
    *Menghilangkan duplikat keypoint yang mungkin muncul dari area tumpang tindih.*
    *Hanya keypoint dengan skor kepercayaan tertinggi dalam radius tertentu yang dipertahankan.*
    *Args:*
    *mkptsL, mkptsR: Array keypoint yang cocok.*
    *scores: Skor kepercayaan untuk setiap pasangan match.*
    *image_shape: Bentuk gambar penuh untuk membuat grid spasial.*
    *distance_thresh: Jarak piksel untuk dianggap sebagai duplikat.*
    *Returns:*
    *Tuple (dedup_mkptsL, dedup_mkptsR, dedup_scores)*

* **Function**: `do_warp_and_crop(image, matrix, pad, w, h, transformation_type)`
    *Menerapkan padding, warping, dan cropping untuk menjaga tepi gambar.*

* **Function**: `calculate_crop_parameters(matrix, w, h, transformation_type)`
    *Fungsi statis untuk menghitung parameter padding yang diperlukan.*
    *Args:*
    *matrix (np.ndarray): Matriks transformasi (2x3 untuk affine, 3x3 untuk homography).*
    *w (int): Lebar gambar asli.*
    *h (int): Tinggi gambar asli.*
    *transformation_type (str): Tipe transformasi ('affine', 'homography', dll.).*
    *Returns:*
    *int: Nilai padding seragam yang diperlukan, atau None jika terjadi kesalahan.*

* **Function**: `compute_transform_bounds(transform, w, h, transformation_type)`

* **Function**: `compute_global_crop(all_transforms, total_images, w, h, transformation_type)`

* **Function**: `crop_image(image, crop_bounds)`
    *Melakukan cropping pada gambar sesuai batas crop yang diberikan.*

* **Function**: `generate_balanced_batches(total_images, max_batch_size)`
    *Sebuah generator yang menghasilkan indeks (awal, akhir) untuk setiap batch.*

* **Function**: `setup_balanced_batching(total_images, language_config, max_batch_size)`
    *Menyiapkan seluruh logika batching, termasuk mencetak info ke konsol.*
    *Fungsi ini menyembunyikan semua kompleksitas dan mengembalikan rencana batching*
    *yang siap digunakan oleh perulangan di fungsi `main`.*
    *Args:*
    *total_images (int): Jumlah total gambar.*
    *language_config: Objek konfigurasi bahasa untuk pesan.*
    *max_batch_size (int): Ukuran maksimum per batch.*
    *Returns:*
    *list: Sebuah daftar tuple [(start1, end1), (start2, end2), ...]*
    *yang merupakan rencana eksekusi batch. Mengembalikan list kosong jika*
    *tidak ada gambar.*

* **Function**: `run_pipeline_non_crop(processor, image_paths, base_image, target_dims, update_progress, stop_requested, save_align, align_folder, h5_file_handle, num_workers)`
    *Pipeline sederhana dan tangguh menggunakan Thread Pool dengan progress bar real-time.*
    *Setiap thread memproses satu gambar, dan thread utama mengupdate progress saat masing-masing selesai.*

* **Function**: `run_pipeline_global_crop(processor, image_paths, base_image, target_dims, update_progress, stop_requested, transformation_type, save_align, align_folder, h5_file_handle, num_workers)`
    *Alur global crop:*
    *Stage 1 (paralel & hemat RAM) -> hitung transform*
    *Stage 2 -> hitung global crop*
    *Stage 3 -> apply & save (pakai versi yang sudah kamu miliki)*

* **Function**: `_run_transform_calculation_stage(processor, image_paths, base_image, target_dims, update_progress, stop_requested, num_workers)`
    *Tahap 1 yang disederhanakan: Menghitung transformasi secara paralel.*

* **Function**: `_run_apply_and_save_stage(processor, temp_transforms, crop_bounds, target_dims, update_progress, stop_requested, save_align, align_folder, h5_file_handle, base_image, base_image_path, num_workers)`
    *Tahap 3 yang disederhanakan: Menerapkan transformasi dan menyimpan secara paralel.*
    *----------------------------------------*

--------------------

### 📄 [global_feature.py](file:///e:/APP%20Developer/Pixel%20Refine/pixel_refine_desktop/enhance_stack/core/algorithm/alignment/alignment_features/global_feature.py)

* **Function**: `get_all_image_paths_for_single_process(db_path)`
    *Mengambil semua path gambar, memvalidasi keberadaannya di disk,*
    *dan menghapus entri yang tidak valid dari database.*

* **Function**: `get_all_image_paths_for_batch_process(db_path, batch_id)`
    *Mengambil semua path gambar untuk batch ID tertentu, memvalidasi,*
    *dan menghapus entri yang tidak valid dari database.*

* **Function**: `_prepare_image_array_from_raw_backup(original_path, linear_mode, generate_ref_proxy, alignment_mode)`
    *CPU Backup implementation using rawpy postprocessing.*

* **Function**: `_prepare_image_array_from_raw(original_path, linear_mode, generate_ref_proxy, alignment_mode)`
    *GPU-Accelerated RAW Demosaicing utilizing C++ AOT Hamilton-Adams pipeline.*

* **Function**: `load_images_from_paths(image_paths, stop_requested, linear_mode, capture_ref_proxy, alignment_mode, update_progress, progress_start, progress_end)`

* **Function**: `load_single_image(data_source, index, stop_requested, linear_mode, capture_ref_proxy)`
    *Loads a single image at the given index from HDF5 or filesystem.*

* **Function**: `save_to_hdf5(h5f, dataset_name, cropped, metadata)`
    *Save images (array) into HDF5 and embed metadata as attributes using multithreading.*
    *Parameters:*
    *- h5f: opened HDF5 file object*
    *- dataset_name: name of dataset to be created*
    *- cropped: array of images to be saved*
    *- metadata: dictionary containing metadata or EXIF of images*

* **Function**: `save_align_to_folder(image, index, original_path, align_folder, load_config_func)`
    *Menyimpan gambar dalam format TIFF ke folder yang ditentukan,*
    *kemudian mengembalikan metadata dari file asli ke file output menggunakan exiftool.*
    *[MODIFIED] Menggunakan logika penyimpanan yang lebih robust dengan kontrol kompresi.*

* **Function**: `save_image(image, output_path, reference_image_path)`
    *Menyimpan gambar dengan kontrol kompresi untuk file TIFF demi kompatibilitas.*
    *Menyalin metadata orientasi dari gambar referensi menggunakan exiftool.*

* **Function**: `calculate_scale_from_gt_proxy(linear_img, gt_proxy, ref_dtype)`
    *Menghitung faktor skala optimal untuk `to_gamma_proxy` dengan membandingkan*
    *Green Channel dari Linear Image (RAW Space) dengan Green Channel dari GT Proxy (sRGB).*
    *Args:*
    *linear_img: Gambar Linear (Main Image), BGR.*
    *gt_proxy: Gambar Ground Truth dari rawpy (sRGB), BGR.*
    *ref_dtype: Tipe data referensi (uint16/uint8).*
    *Returns:*
    *float: Faktor skala (scale) yang optimal.*

* **Function**: `save_linear_dng(image, output_path, reference_image_path)`
    *Menyimpan gambar sebagai Linear DNG (RGB) dengan kompresi Deflate.*

* **Function**: `save_special_jpg_and_png(img_np, dst_path, reference_image_path, quality, optimize, png_compress_level)`
    *Mengkonversi array NumPy, menerapkan rotasi, dan menyimpannya ke JPG/PNG*
    *dengan opsi kompresi yang lebih agresif dan cerdas.*

* **Function**: `extract_exif(image_path)`
    *Mengambil metadata EXIF dari file gambar menggunakan exifread.*
    *Mengembalikan dictionary dengan data EXIF dan path file.*

* **Function**: `extract_all_metadata(image_paths, metadata_file)`
    *Mengekstrak metadata dari seluruh image paths dan menyimpannya ke file JSON.*
    *Jika file metadata sudah ada, data baru akan ditambahkan (tidak overwrite).*

* **Function**: `prepare_gray(img)`

* **Function**: `prepare_image(image, grayscale, use_clahe)`
    *Fungsi Hibrida Cerdas.*
    *- Untuk Grayscale (AKAZE): Mendelegasikan tugas ke `prepare_gray_akaze` untuk hasil yang 100% identik.*
    *- Untuk Berwarna (LightGlue): Menggunakan logika internalnya sendiri yang kuat.*
    *Args:*
    *image: Gambar input.*
    *grayscale (bool): Jika True, akan memanggil pipeline khusus grayscale.*
    *use_clahe (bool): Jika True, akan menerapkan CLAHE.*
    *Returns:*
    *Gambar uint8 yang telah diproses.*

* **Function**: `resize_with_padding(img, target_size, pad_color)`

* **Function**: `resize_all_with_padding(images, method, verbose, pad_color, return_original_sizes, stop_requested, force_even)`
    *Resize + pad all images to the same size using letterbox strategy.*
    *Args:*
    *images (list): Daftar array gambar (NumPy).*
    *method (str): Strategi penentuan ukuran target. Pilihan:*
    *- "min"      : gunakan tinggi & lebar minimum dari semua gambar.*
    *- "max"      : gunakan tinggi & lebar maksimum dari semua gambar.*
    *- "median"   : gunakan median tinggi & lebar dari semua gambar.*
    *- "preserve" : gunakan ukuran gambar pertama sebagai referensi.*
    *verbose (bool): Jika True, cetak informasi proses.*
    *pad_color (tuple): Warna padding (B, G, R).*
    *return_original_sizes (bool): Jika True, juga kembalikan ukuran asli.*

* **Function**: `gaussian_window(size, sigma_scale)`
    *Menghasilkan jendela Gaussian 2D [0, 1] float32 C-contiguous.*

* **Function**: `estimate_noise_in_python(ref_image_gray_float)`
    *Estimasi noise sederhana menggunakan Laplacian.*
    *Menyederhanakan perhitungan dari block-based ke Laplacian MAD saja.*

* **Function**: `calibrate_sigma(est_sigma)`
    *Menerjemahkan angka kasar OpenCV menjadi skala Pure Noise [0.01 - 0.40]*

* **Function**: `apply_s_curve_float32(img, strength, pivot)`
    *S-Curve float32 dengan pivot.*
    *Input: 0..255 float32*
    *Output: float32 0..255*

* **Function**: `preprocess_in_python(ref_image_float, s_curve_contrast)`
    *Melakukan semua pra-pemrosesan gambar referensi di Python.*
    *[MODIFIED] Hanya melakukan konversi ke grayscale sesuai permintaan user.*
    *Mengembalikan gambar grayscale dan nilai noise-nya (estimasi cepat).*

* **Function**: `estimate_noise_variance(gray_image, edge_threshold_low, dilate_kernel_size, min_flat_pixels_ratio)`
    *Memperkirakan tingkat noise dalam gambar dengan menghitung varians Laplacian*
    *hanya pada area gambar yang dianggap "datar" (tidak ada tepi atau tekstur yang kuat).*
    *Args:*
    *gray_image (np.array): Gambar grayscale.*
    *edge_threshold_low (int): Ambang batas rendah untuk detektor tepi Canny.*
    *dilate_kernel_size (int): Ukuran kernel untuk operasi dilasi pada tepi.*
    *min_flat_pixels_ratio (float): Rasio minimum piksel datar yang dibutuhkan.*
    *Jika terlalu sedikit, estimasi bisa tidak andal.*
    *Returns:*
    *float: Varians noise yang diestimasi.*

* **Function**: `get_adaptive_bilateral(noise_level, min_noise, max_noise, min_d, max_d, min_sigma, max_sigma)`
    *Menghitung parameter untuk filter bilateral secara dinamis berdasarkan tingkat noise.*

* **Function**: `normalize_image(image, dtype, out)`
    *Normalisasi gambar ke range [0, 1] float32.*
    *- Jika `out` disediakan, hasil akan disalin ke buffer tersebut (otomatis disesuaikan ukuran & dimensi).*
    *- Jika `out` tidak ada, fungsi akan membuat array baru.*
    *- Menangani RGB dan grayscale secara otomatis.*
    *Args:*
    *image: np.ndarray (grayscale 2D atau RGB 3D)*
    *dtype: tipe data asli dari gambar (mis. np.uint8, np.uint16)*
    *out: buffer opsional (np.ndarray dengan dtype=float32 dan dimensi sama)*
    *Returns:*
    *np.ndarray (float32, 3 channel)*

* **Function**: `calculate_auto_scale(linear_img_float, target_mean)`
    *Menghitung scale factor agar rata-rata brightness mendekati target_mean.*
    *Digunakan untuk normalisasi brightness referensi sebelum estimasi gamma proxy.*
    *linear_img_float: HxWx3 (Linear RGB) atau HxW (Gray), range 0.0-1.0*

* **Function**: `to_gamma_proxy(linear_img, scale, gamma_pow, slope, cutoff)`
    *Konversi Linear [0,1] ke Gamma Proxy [0,1] untuk Alignment.*
    *Menggunakan parameter tuning manual: Scale, Gamma, Slope, Cutoff.*

* **Function**: `deduplicate_keypoints(mkptsL, mkptsR, scores, image_shape, distance_thresh)`
    *Menghilangkan duplikat keypoint yang mungkin muncul dari area tumpang tindih.*
    *Hanya keypoint dengan skor kepercayaan tertinggi dalam radius tertentu yang dipertahankan.*
    *Args:*
    *mkptsL, mkptsR: Array keypoint yang cocok.*
    *scores: Skor kepercayaan untuk setiap pasangan match.*
    *image_shape: Bentuk gambar penuh untuk membuat grid spasial.*
    *distance_thresh: Jarak piksel untuk dianggap sebagai duplikat.*
    *Returns:*
    *Tuple (dedup_mkptsL, dedup_mkptsR, dedup_scores)*

* **Function**: `do_warp_and_crop(image, matrix, pad, w, h, transformation_type)`
    *Menerapkan padding, warping, dan cropping untuk menjaga tepi gambar.*

* **Function**: `calculate_crop_parameters(matrix, w, h, transformation_type)`
    *Fungsi statis untuk menghitung parameter padding yang diperlukan.*
    *Args:*
    *matrix (np.ndarray): Matriks transformasi (2x3 untuk affine, 3x3 untuk homography).*
    *w (int): Lebar gambar asli.*
    *h (int): Tinggi gambar asli.*
    *transformation_type (str): Tipe transformasi ('affine', 'homography', dll.).*
    *Returns:*
    *int: Nilai padding seragam yang diperlukan, atau None jika terjadi kesalahan.*

* **Function**: `compute_transform_bounds(transform, w, h, transformation_type)`

* **Function**: `compute_global_crop(all_transforms, total_images, w, h, transformation_type)`

* **Function**: `crop_image(image, crop_bounds)`
    *Melakukan cropping pada gambar sesuai batas crop yang diberikan.*

* **Function**: `generate_balanced_batches(total_images, max_batch_size)`
    *Sebuah generator yang menghasilkan indeks (awal, akhir) untuk setiap batch.*

* **Function**: `setup_balanced_batching(total_images, language_config, max_batch_size)`
    *Menyiapkan seluruh logika batching, termasuk mencetak info ke konsol.*
    *Fungsi ini menyembunyikan semua kompleksitas dan mengembalikan rencana batching*
    *yang siap digunakan oleh perulangan di fungsi `main`.*
    *Args:*
    *total_images (int): Jumlah total gambar.*
    *language_config: Objek konfigurasi bahasa untuk pesan.*
    *max_batch_size (int): Ukuran maksimum per batch.*
    *Returns:*
    *list: Sebuah daftar tuple [(start1, end1), (start2, end2), ...]*
    *yang merupakan rencana eksekusi batch. Mengembalikan list kosong jika*
    *tidak ada gambar.*

* **Function**: `run_pipeline_non_crop(processor, image_paths, base_image, target_dims, update_progress, stop_requested, save_align, align_folder, h5_file_handle, num_workers)`
    *Pipeline sederhana dan tangguh menggunakan Thread Pool dengan progress bar real-time.*
    *Setiap thread memproses satu gambar, dan thread utama mengupdate progress saat masing-masing selesai.*

* **Function**: `run_pipeline_global_crop(processor, image_paths, base_image, target_dims, update_progress, stop_requested, transformation_type, save_align, align_folder, h5_file_handle, num_workers)`
    *Alur global crop:*
    *Stage 1 (paralel & hemat RAM) -> hitung transform*
    *Stage 2 -> hitung global crop*
    *Stage 3 -> apply & save (pakai versi yang sudah kamu miliki)*

* **Function**: `_run_transform_calculation_stage(processor, image_paths, base_image, target_dims, update_progress, stop_requested, num_workers)`
    *Tahap 1 yang disederhanakan: Menghitung transformasi secara paralel.*

* **Function**: `_run_apply_and_save_stage(processor, temp_transforms, crop_bounds, target_dims, update_progress, stop_requested, save_align, align_folder, h5_file_handle, base_image, base_image_path, num_workers)`
    *Tahap 3 yang disederhanakan: Menerapkan transformasi dan menyimpan secara paralel.*

* **Function**: `cleanup_old_hdf5_files(current_hdf5_path)`
    *Menghapus file HDF5 (.h5) lain di direktori database/align untuk menghemat ruang HDD.*
    *Hanya menyisakan file hdf5 yang sedang diproses (current_hdf5_path).*

* **Function**: `is_hdf5_cache_valid(hdf5_path, ref_image_path)`
    *Memvalidasi apakah cache HDF5 masih relevan dengan gambar referensi saat ini.*
    *HDF5 menyimpan atribut 'ref_image_path' saat dibuat. Fungsi ini*
    *membandingkan nama file (basename) dari path yang tersimpan dengan*
    *path referensi saat ini. Jika berbeda, cache dianggap tidak valid.*
    *Args:*
    *hdf5_path: Path ke file HDF5 yang akan divalidasi.*
    *ref_image_path: Path lengkap dari gambar referensi saat ini.*
    *Returns:*
    *True jika cache valid (referensi sama), False jika tidak valid.*
    *----------------------------------------*

--------------------

### 📄 [inspect_tcm.py](file:///e:/APP%20Developer/Pixel%20Refine/pixel_refine_desktop/enhance_stack/core/algorithm/alignment/alignment_features/inspect_tcm.py)

* **Function**: `inspect()`
    *----------------------------------------*

--------------------

### 📄 [smart_flow copy.py](file:///e:/APP%20Developer/Pixel%20Refine/pixel_refine_desktop/enhance_stack/core/algorithm/alignment/alignment_features/smart_flow copy.py)

* **Class**: `SmartFlowProcessor`
    *Handles memory-efficient optical flow alignment using NanoFlowNet.*
    *Uses tiling (320x320) and Overlap-Add (OLA) with warping per tile.*
  * Method: `__init__(self, model_dir)`
  * Method: `_initialize_session(self, target_device)`
    *Loads the NanoFlowNet ONNX model for 320x320 tiles.*
  * Method: `_get_gpu_vram(self)`
    *Returns dedicated VRAM in MB using PowerShell (Windows).*
  * Method: `_calculate_optimal_batch_size(self, vram_mb)`
    *Calculates batch size based on VRAM capacity.*
  * Method: `release_sessions(self)`
    *Releases the ONNX session to free memory.*
  * Method: `process_image(self, ref_img, curr_img, overlap, stop_requested)`
    *Aligns curr_img to ref_img using tiled NanoFlowNet.*
    *Warps per tile and blends using Hanning window (OLA).*
  * Method: `_estimate_global_shift(self, ref, curr)`
    *Estimates global translation using Phase Correlation on downsampled gray images.*
  * Method: `process_image(self, ref_img, curr_img, overlap, batch_size, stop_requested, return_flow)`
    *Aligns curr_img to ref_img using Hybrid Global-to-Local strategy.*
    *1. Coarse: Calculate global translation (dx, dy).*
    *2. Fine: Calculate local residual flow using Batch Inference on GPU.*
    *3. Warp: Single global remap for performance and quality.*
    *----------------------------------------*

--------------------

### 📄 [taichi_bridge.py](file:///e:/APP%20Developer/Pixel%20Refine/pixel_refine_desktop/enhance_stack/core/algorithm/alignment/alignment_features/taichi_bridge.py)

* **Function**: `normalize_image_gpu(image_gpu, dtype, out_gpu)`

* **Function**: `to_gamma_proxy_gpu(image_gpu, scale, gamma_pow, slope, cutoff, dst_gpu)`

* **Function**: `prepare_pyramid_aot(image_gpu, num_layers)`
    *Creates a multi-layer pyramid (L0, L1, ...). L0=full res, L1=1/2, L2=1/4, etc.*

* **Function**: `prepare_reference_for_alignment(reference_image_float, is_linear_mode, proxy_scale, work_res_h, work_res_w, lut_gpu, blur_work_gpu, num_layers)`
    *Prepare reference image pyramid on GPU. Returns (l0, l1, l2, ...) — caller must destroy all.*

* **Function**: `prepare_comparison_for_alignment(comp_image, ref_dtype, is_linear_mode, proxy_scale, work_res_h, work_res_w, lut_gpu, blur_work_gpu, num_layers)`
    *Prepare comparison image pyramid on GPU. Returns (l0, l1, l2, ...) — caller must destroy all.*

* **Function**: `prepare_reference_aot(reference_image_float, is_linear_mode, proxy_scale, work_res_h, work_res_w)`
    *Prepare reference image on GPU for merging. Returns (ref_work_res_pass2_gpu, ref_noise_sigma).*

* **Function**: `prepare_reference_aot(reference_image_float, is_linear_mode, proxy_scale, work_res_h, work_res_w)`
    *Prepare reference image on GPU for merging. Returns (ref_work_res_pass2_gpu, ref_noise_sigma).*

* **Function**: `prepare_frame_aot(img_orig, ref_dtype, is_linear_mode, proxy_scale, work_res_h, work_res_w, ref_image_h, ref_image_w)`
    *Prepare comparison frame on GPU for merging. Returns (curr_full_gpu, curr_work_gray_gpu).*
    *----------------------------------------*

--------------------

### 📄 [test_alignment_flow_remap.py](file:///e:/APP%20Developer/Pixel%20Refine/pixel_refine_desktop/enhance_stack/core/algorithm/alignment/alignment_features/test_alignment_flow_remap.py)

* **Function**: `test_alignment_with_flow_remap()`
    *----------------------------------------*

--------------------

### 📄 [test_full_alignment_pipeline.py](file:///e:/APP%20Developer/Pixel%20Refine/pixel_refine_desktop/enhance_stack/core/algorithm/alignment/alignment_features/test_full_alignment_pipeline.py)

* **Function**: `put_text(img, text)`

* **Function**: `test_stress_hybrid_pipeline()`
    *----------------------------------------*

--------------------

### 📄 [test_pure_aot_alignment.py](file:///e:/APP%20Developer/Pixel%20Refine/pixel_refine_desktop/enhance_stack/core/algorithm/alignment/alignment_features/test_pure_aot_alignment.py)

* **Function**: `test_pure_aot_direct()`
    *----------------------------------------*

--------------------

### 📄 [test_real_dataset_alignment.py](file:///e:/APP%20Developer/Pixel%20Refine/pixel_refine_desktop/enhance_stack/core/algorithm/alignment/alignment_features/test_real_dataset_alignment.py)

* **Function**: `load_image(path)`
    *Load DNG or common image format. Returns float32 RGB numpy array.*

* **Function**: `resize_with_aspect(img, max_size)`

* **Function**: `test_real_dataset_alignment()`
    *----------------------------------------*

--------------------


## 📂 Directory: `Root Directory`

### 📄 [# DIRECTORY: pixel_refine_desktop/enhance_stack/core/algorithm/alignment/alignment_tile](file:///e:/APP%20Developer/Pixel%20Refine/# DIRECTORY: pixel_refine_desktop/enhance_stack/core/algorithm/alignment/alignment_tile)


--------------------


## 📂 Directory: `Root Directory`

### 📄 [compute_flow.py](file:///e:/APP%20Developer/Pixel%20Refine/pixel_refine_desktop/enhance_stack/core/algorithm/alignment/alignment_tile/compute_flow.py)

* **Function**: `hanning_window_1d(idx, size)`
    *Compute Hanning window value for 1D at given index*

* **Function**: `hanning_window_2d(row, col, tile_h, tile_w)`
    *Compute 2D Hanning window: product of 1D windows*

* **Function**: `bicubic_weight(x)`

* **Function**: `compute_regularization_params(flow, y, x, tile_h, tile_w)`

* **Function**: `block_search_kernel(ref_layer, comp_layer, ai_radius_map, refined_flow, tile_h, tile_w)`

* **Function**: `search_coarse_level_kernel(ref_layer, comp_layer, flow, previous_flow, refined_flow, tile_h, tile_w, search_dist, downscale_factor)`

* **Function**: `search_fine_level_kernel(ref_layer, comp_layer, flow, previous_flow, refined_flow, tile_h, tile_w, downscale_factor)`

* **Function**: `upsample_flow_bicubic_kernel(src, dst, scale)`

* **Function**: `compile_compute_flow()`
    *----------------------------------------*

--------------------


## 📂 Directory: `Root Directory`

### 📄 [# DIRECTORY: pixel_refine_desktop/enhance_stack/core/algorithm/alignment/alignment_tile/aot](file:///e:/APP%20Developer/Pixel%20Refine/# DIRECTORY: pixel_refine_desktop/enhance_stack/core/algorithm/alignment/alignment_tile/aot)


--------------------


## 📂 Directory: `Root Directory`

### 📄 [compile_gamma_proxy_tcm.py](file:///e:/APP%20Developer/Pixel%20Refine/pixel_refine_desktop/enhance_stack/core/algorithm/alignment/alignment_tile/aot/compile_gamma_proxy_tcm.py)

* **Function**: `compile_gamma_proxy_aot(arch, save_path)`
    *----------------------------------------*

--------------------

### 📄 [compile_normalize_image_tcm.py](file:///e:/APP%20Developer/Pixel%20Refine/pixel_refine_desktop/enhance_stack/core/algorithm/alignment/alignment_tile/aot/compile_normalize_image_tcm.py)

* **Function**: `compile_normalize_image_aot(arch, save_path)`
    *----------------------------------------*

--------------------

### 📄 [compute_flow_kernels.py](file:///e:/APP%20Developer/Pixel%20Refine/pixel_refine_desktop/enhance_stack/core/algorithm/alignment/alignment_tile/aot/compute_flow_kernels.py)

* **Function**: `_compute_l1_cost(ref, comp, y_ref, x_ref, y_comp, x_comp, tile_h, tile_w)`
    *Compute Sum of Absolute Differences (SAD / L1) cost.*

* **Function**: `_downsample_2x_kernel(src, dst)`

* **Function**: `_compute_global_zncc_surface(ref, comp, zncc_surf, zncc_shift)`

* **Function**: `_reduce_min_2d_kernel(surf, res)`

* **Function**: `_block_search_init_kernel(ref, comp, global_shift, flow_out, tile_h, tile_w, search_radius)`
    *Initial layer block search using Global ZNCC shift with boundary hardening.*

* **Function**: `_block_search_refine_kernel(ref, comp, prev_flow, flow_out, tile_h, tile_w, search_radius, scale)`
    *Refinement layers with boundary hardening.*
    *----------------------------------------*

--------------------

### 📄 [cost_function.py](file:///e:/APP%20Developer/Pixel%20Refine/pixel_refine_desktop/enhance_stack/core/algorithm/alignment/alignment_tile/aot/cost_function.py)

* **Function**: `compute_zmssd_cost_func(ref, comp, y_ref, x_ref, y_comp, x_comp, tile_h, tile_w, stride)`
    *Device-side function version of ZMSSD for use inside other kernels.*
    *Mirroring C++ compute_zmssd_cost logic with stride-based subsampling.*

* **Function**: `compute_zmssd_kernel(ref, comp, h, w, y_ref, x_ref, y_comp, x_comp, tile_h, tile_w)`
    *Exposed kernel for Python-side verification.*
    *----------------------------------------*

--------------------

### 📄 [refinement.py](file:///e:/APP%20Developer/Pixel%20Refine/pixel_refine_desktop/enhance_stack/core/algorithm/alignment/alignment_tile/aot/refinement.py)

* **Function**: `parabolic_refinement(c_m1, c_0, c_p1)`
    *Sub-pixel refinement using parabolic fitting.*
    *Returns delta offset in range [-0.5, 0.5]*

* **Function**: `apply_parabolic_refinement_kernel(flow, costs, refined_flow)`
    *----------------------------------------*

--------------------


## 📂 Directory: `Root Directory`

### 📄 [# DIRECTORY: pixel_refine_desktop/enhance_stack/core/algorithm/alignment/alignment_tile/image_utils_aot](file:///e:/APP%20Developer/Pixel%20Refine/# DIRECTORY: pixel_refine_desktop/enhance_stack/core/algorithm/alignment/alignment_tile/image_utils_aot)


--------------------


## 📂 Directory: `Root Directory`

### 📄 [compile_gamma_proxy_tcm.py](file:///e:/APP%20Developer/Pixel%20Refine/pixel_refine_desktop/enhance_stack/core/algorithm/alignment/alignment_tile/image_utils_aot/compile_gamma_proxy_tcm.py)

* **Function**: `compile_gamma_proxy_aot(arch, save_path)`
    *----------------------------------------*

--------------------

### 📄 [compile_normalize_image_tcm.py](file:///e:/APP%20Developer/Pixel%20Refine/pixel_refine_desktop/enhance_stack/core/algorithm/alignment/alignment_tile/image_utils_aot/compile_normalize_image_tcm.py)

* **Function**: `compile_normalize_image_aot(arch, save_path)`
    *----------------------------------------*

--------------------

### 📄 [gamma_proxy_kernels.py](file:///e:/APP%20Developer/Pixel%20Refine/pixel_refine_desktop/enhance_stack/core/algorithm/alignment/alignment_tile/image_utils_aot/gamma_proxy_kernels.py)

* **Function**: `_gamma_proxy_core(val, scale, gamma_pow, slope, cutoff)`

* **Function**: `gamma_proxy_rgb_kernel(src, dst, cmatrix, scale, gamma_pow, slope, cutoff)`

* **Function**: `gamma_proxy_single_kernel(src, dst, scale, gamma_pow, slope, cutoff)`
    *----------------------------------------*

--------------------

### 📄 [normalize_image_kernels.py](file:///e:/APP%20Developer/Pixel%20Refine/pixel_refine_desktop/enhance_stack/core/algorithm/alignment/alignment_tile/image_utils_aot/normalize_image_kernels.py)

* **Function**: `normalize_f32_to_vec3_kernel(src, dst, inv_scale)`

* **Function**: `normalize_vec3_f32_to_vec3_f32_kernel(src, dst, inv_scale)`
    *----------------------------------------*

--------------------


## 📂 Directory: `Root Directory`

### 📄 [# DIRECTORY: pixel_refine_desktop/enhance_stack/core/algorithm/alignment/alignment_tile/tests](file:///e:/APP%20Developer/Pixel%20Refine/# DIRECTORY: pixel_refine_desktop/enhance_stack/core/algorithm/alignment/alignment_tile/tests)


--------------------


## 📂 Directory: `Root Directory`

### 📄 [test_parity.py](file:///e:/APP%20Developer/Pixel%20Refine/pixel_refine_desktop/enhance_stack/core/algorithm/alignment/alignment_tile/tests/test_parity.py)

* **Function**: `run_jit()`

* **Function**: `run_aot()`
    *----------------------------------------*

--------------------


## 📂 Directory: `Root Directory`

### 📄 [# DIRECTORY: pixel_refine_desktop/enhance_stack/core/algorithm/denoising](file:///e:/APP%20Developer/Pixel%20Refine/# DIRECTORY: pixel_refine_desktop/enhance_stack/core/algorithm/denoising)


--------------------


## 📂 Directory: `Root Directory`

### 📄 [Average.py](file:///e:/APP%20Developer/Pixel%20Refine/pixel_refine_desktop/enhance_stack/core/algorithm/denoising/Average.py)

* **Class**: `AverageAlgorithm`
  * Method: `__init__(self, db_path, hdf5_path)`
  * Method: `get_all_image_paths_for_batch_process(self, batch_id)`
  * Method: `load_images_from_hdf5(self, hdf5_path, stop_requested)`
  * Method: `average_stack(self, images, update_progress, stop_requested, total_overall_images, images_processed_so_far)`
    *Melakukan stacking gambar dengan metode rata-rata sederhana (simple average).*
    *(Docstring lainnya tetap sama)*

* **Function**: `main(db_path, update_progress, stop_requested, single_process, batch_id, progress_bar)`

* **Function**: `running_average(parent, single_process, batch_id, progress_callback, stop_callback)`
    *----------------------------------------*

--------------------

### 📄 [Median.py](file:///e:/APP%20Developer/Pixel%20Refine/pixel_refine_desktop/enhance_stack/core/algorithm/denoising/Median.py)

* **Class**: `MedianAlgorithm`
  * Method: `__init__(self, db_path, hdf5_path, max_workers)`
  * Method: `get_all_image_paths_for_batch_process(self, batch_id)`
  * Method: `load_images_from_hdf5(self, hdf5_path, stop_requested)`
  * Method: `stack_median_images(self, images, stop_requested, block_size, overlap, update_progress, total_overall_images, images_processed_so_far, use_multi_core)`
    *Menghitung stack gambar dengan metode Median berbasis blok.*
    *Mendukung kontrol penggunaan multi-core.*
  * Method: `_compute_block_median(self, block_stack)`
    *Menghitung stack blok menggunakan Median.*
    *Args:*
    *block_stack (np.ndarray): Tumpukan blok gambar (N, H, W, [C]).*
    *Returns:*
    *np.ndarray: Blok gambar hasil median (H, W, [C]), dtype float32.*
  * Method: `_compute_median_image(self, images, target_shape, block_size, dtype, overlap, update_progress, stop_requested, use_multi_core)`
    *Menghitung gambar stack menggunakan metode blok dengan Median.*
    *(Versi yang dirampingkan tanpa duplikasi kode).*

* **Function**: `main(db_path, update_progress, stop_requested, single_process, batch_id, progress_bar)`

* **Function**: `running_median(parent, single_process, batch_id, progress_callback, stop_callback)`
    *----------------------------------------*

--------------------

### 📄 [Similarity copy.py](file:///e:/APP%20Developer/Pixel%20Refine/pixel_refine_desktop/enhance_stack/core/algorithm/denoising/Similarity copy.py)

* **Class**: `DataProvider`
    *Handles data sourcing, batching, and image loading for the Similarity algorithm.*
  * Method: `__init__(self, db_path)`
  * Method: `get_all_image_paths_for_batch_process(self, batch_id)`
    *Fetches all image paths for a specific batch from the database.*
  * Method: `setup_data_source_and_paths(self, single_process, batch_id)`
    *Determines the data source (HDF5 or Raw paths) and prepares output metadata.*
  * Method: `load_images_for_batch(data_source, batch_indices, stop_requested, linear_mode, capture_ref_proxy)`
    *Loads a specific batch of images from HDF5 or filesystem.*

* **Class**: `SimilarityAlgorithm`
    *Main Orchestrator for the Similarity Merging algorithm.*
    *Coordinates between Smart Fusion (AI) and Spatial Fusion (C++/Taichi).*
  * Method: `__init__(self, db_path, hdf5_path)`
  * Method: `close(self)`
    *Cleanup resources and close AI sessions.*
  * Method: `get_all_image_paths_for_batch_process(self, batch_id)`
    *Legacy wrapper for DataProvider.*
  * Method: `similarity_mnfr(self, images, tile_size, overlap, motion_sensitivity, noise_offset_factor, update_progress, stop_requested, save_weight_map_path, num_workers, total_overall_images, images_processed_so_far, save_temporal_std_path, weight_of_each_image, ref_image_override, return_raw, is_linear_mode, proxy_scale)`
    *Entry point for the merging algorithm.*

* **Function**: `get_ram_usage()`
    *Returns the current RAM usage of the process in MiB.*

* **Function**: `main(db_path, update_progress, stop_requested, single_process, batch_id, save_final_weight_map, progress_bar)`
    *Main execution block.*

* **Function**: `running_similarity(parent, single_process, batch_id, progress_callback, stop_callback)`
    *UI Entry point.*
    *----------------------------------------*

--------------------

### 📄 [Similarity.py](file:///e:/APP%20Developer/Pixel%20Refine/pixel_refine_desktop/enhance_stack/core/algorithm/denoising/Similarity.py)

* **Class**: `DataProvider`
    *Handles data sourcing, batching, and image loading for the Similarity algorithm.*
  * Method: `__init__(self, db_path)`
  * Method: `get_all_image_paths_for_batch_process(self, batch_id)`
    *Fetches all image paths for a specific batch from the database.*
  * Method: `setup_data_source_and_paths(self, single_process, batch_id)`
    *Determines the data source (HDF5 or Raw paths) and prepares output metadata.*
  * Method: `load_images_for_batch(data_source, batch_indices, stop_requested, linear_mode, capture_ref_proxy, alignment_mode, update_progress, progress_start, progress_end)`
    *Loads a specific batch of images from HDF5 or filesystem.*

* **Class**: `SimilarityAlgorithm`
    *Main Orchestrator for the Similarity Merging algorithm.*
    *Coordinates between Smart Fusion (AI) and Spatial Fusion (C++/Taichi).*
  * Method: `__init__(self, db_path, hdf5_path)`
  * Method: `close(self)`
    *Cleanup resources and close AI sessions.*
  * Method: `get_all_image_paths_for_batch_process(self, batch_id)`
    *Legacy wrapper for DataProvider.*
  * Method: `similarity_mnfr(self, images, tile_size, overlap, motion_sensitivity, noise_offset_factor, update_progress, stop_requested, save_weight_map_path, num_workers, total_overall_images, images_processed_so_far, save_temporal_std_path, weight_of_each_image, ref_image_override, return_raw, is_linear_mode, proxy_scale)`
    *Entry point for the merging algorithm.*

* **Function**: `get_ram_usage()`
    *Returns the current RAM usage of the process in MiB.*

* **Function**: `main(db_path, update_progress, stop_requested, single_process, batch_id, save_final_weight_map, progress_bar)`
    *Main execution block.*

* **Function**: `running_similarity(parent, single_process, batch_id, progress_callback, stop_callback)`
    *UI Entry point.*
    *----------------------------------------*

--------------------


## 📂 Directory: `Root Directory`

### 📄 [# DIRECTORY: pixel_refine_desktop/enhance_stack/core/algorithm/denoising/smart_fusion](file:///e:/APP%20Developer/Pixel%20Refine/# DIRECTORY: pixel_refine_desktop/enhance_stack/core/algorithm/denoising/smart_fusion)


--------------------


## 📂 Directory: `Root Directory`

### 📄 [smart_fusion_core copy.py](file:///e:/APP%20Developer/Pixel%20Refine/pixel_refine_desktop/enhance_stack/core/algorithm/denoising/smart_fusion/smart_fusion_core copy.py)

* **Class**: `SmartFusionProcessor`
    *Handles the AI-based Smart Fusion merging logic using ONNX models.*
  * Method: `__init__(self, model_dir)`
  * Method: `_get_sessions(self, tile_size, preferred_device)`
    *Loads or returns cached ONNX inference sessions for the given tile size.*
  * Method: `release_sessions(self)`
    *Release ONNX sessions and free memory.*
  * Method: `process(self, images, reference_image_float, update_progress, stop_requested, tile_size, overlap, pass_merge_range, preferred_device, enable_alignment, work_res_h, work_res_w, ref_dtype, is_linear_mode, proxy_scale, num_workers, noise_alpha)`
    *Executes the Smart Fusion algorithm on a batch of images.*

* **Function**: `get_ram_usage()`
    *Returns the current RAM usage of the process in MiB.*
    *----------------------------------------*

--------------------

### 📄 [smart_fusion_core.py](file:///e:/APP%20Developer/Pixel%20Refine/pixel_refine_desktop/enhance_stack/core/algorithm/denoising/smart_fusion/smart_fusion_core.py)

* **Class**: `SmartFusionProcessor`
    *Handles the AI-based Smart Fusion merging logic using ONNX models.*
  * Method: `__init__(self, model_dir)`
  * Method: `_get_sessions(self, tile_size, preferred_device)`
    *Loads or returns cached ONNX inference sessions for the given tile size.*
  * Method: `release_sessions(self)`
    *Releases the ONNX sessions and clears cache.*
  * Method: `process(self, images, reference_image_float, update_progress, stop_requested, tile_size, overlap, pass_merge_range, preferred_device, enable_alignment, work_res_h, work_res_w, ref_dtype, is_linear_mode, proxy_scale, num_workers, noise_alpha)`
    *Executes the Smart Fusion algorithm on a batch of images.*

* **Function**: `get_ram_usage()`
    *Returns the current RAM usage of the process in MiB.*
    *----------------------------------------*

--------------------


## 📂 Directory: `Root Directory`

### 📄 [# DIRECTORY: pixel_refine_desktop/enhance_stack/core/algorithm/denoising/spatial_core](file:///e:/APP%20Developer/Pixel%20Refine/# DIRECTORY: pixel_refine_desktop/enhance_stack/core/algorithm/denoising/spatial_core)


--------------------


## 📂 Directory: `Root Directory`

### 📄 [spatial_fusion.py](file:///e:/APP%20Developer/Pixel%20Refine/pixel_refine_desktop/enhance_stack/core/algorithm/denoising/spatial_core/spatial_fusion.py)

* **Class**: `SpatialFusionProcessor`
    *Handles the Spatial Fusion merging logic using C++ or Taichi backends.*
  * Method: `__init__(self)`
  * Method: `process(self, images, ref_image_h, ref_image_w, ref_channels_buffer, ref_dtype, reference_image_float, tile_size, overlap, motion_sensitivity, noise_offset_factor, update_progress, stop_requested, total_overall_images, images_processed_so_far, lib_path, num_workers, weight_of_each_image, enable_alignment, scale_down_factor, return_raw, is_linear_mode, proxy_scale, process_in, merging_backend)`
    *Executes the Spatial Fusion algorithm on a batch of images.*

* **Function**: `get_ram_usage()`
    *Returns the current RAM usage of the process in MiB.*
    *----------------------------------------*

--------------------

### 📄 [spatial_pipeline.py](file:///e:/APP%20Developer/Pixel%20Refine/pixel_refine_desktop/enhance_stack/core/algorithm/denoising/spatial_core/spatial_pipeline.py)

* **Function**: `process_in_cpu(images, reference_image_float, ref_image_h, ref_image_w, ref_channels_buffer, ref_dtype, work_res_h, work_res_w, tile_h, tile_w, row_starts, col_starts, base_window, motion_sensitivity, noise_offset_factor, num_workers, update_progress, stop_requested, pass_merge_range, p_align_start, p_align_end, p_merge_start, is_linear_mode, proxy_scale, images_processed_so_far, total_overall_images, lib_path, enable_alignment)`
    *Pipeline terpadu untuk Alignment + Merging di CPU.*

* **Function**: `clear_spatial_cache()`
    *Safely destroy all cached GPU buffers for spatial merging.*

* **Function**: `process_in_gpu(images, reference_image_float, ref_image_h, ref_image_w, ref_channels_buffer, ref_dtype, work_res_h, work_res_w, tile_h, tile_w, row_starts, col_starts, base_window, motion_sensitivity, noise_offset_factor, update_progress, stop_requested, pass_merge_range, p_align_start, p_align_end, p_merge_start, is_linear_mode, proxy_scale, images_processed_so_far, total_overall_images, lib_path, alignment_tile_size, alignment_variant)`
    *Pipeline GPU Alignment + Merging (Full GPU Path).*
    *Alignment: Selalu GPU Taichi.*
    *Merging:   Selalu Taichi (full GPU).*
    *alignment_variant:*
    *'block_flow'        — HDR+ optical-flow tile matching (default)*
    *'block_correlation' — Hierarchical Phase Correlation*
    *----------------------------------------*

--------------------

### 📄 [spatial_similarity.py](file:///e:/APP%20Developer/Pixel%20Refine/pixel_refine_desktop/enhance_stack/core/algorithm/denoising/spatial_core/spatial_similarity.py)

* **Class**: `SimilaritySpatialInterface`
    *Membungkus pemanggilan fungsi C++ yang telah dioptimalkan.*
    *Sekarang HANYA menghasilkan weight_map.*
  * Method: `__init__(self, lib_path)`
  * Method: `_define_argtypes(self)`
  * Method: `call_generate_weight_map_jit(self, weight_map_sum, current_image, reference_image_processed, base_window, stability_map, row_starts, col_starts, tile_h, tile_w, h, w, channels, motion_sensitivity, noise_offset_factor, precomputed_ref_noise_sigma)`
    *----------------------------------------*

--------------------


## 📂 Directory: `Root Directory`

### 📄 [# DIRECTORY: pixel_refine_desktop/enhance_stack/core/algorithm/denoising/spatial_core/similarity_taichi](file:///e:/APP%20Developer/Pixel%20Refine/# DIRECTORY: pixel_refine_desktop/enhance_stack/core/algorithm/denoising/spatial_core/similarity_taichi)


--------------------


## 📂 Directory: `Root Directory`

### 📄 [block_matching.py](file:///e:/APP%20Developer/Pixel%20Refine/pixel_refine_desktop/enhance_stack/core/algorithm/denoising/spatial_core/similarity_taichi/block_matching.py)

* **File Overview**:
    *Block Matching - Taichi GPU*
    *===========================*
    *Mathematical functions for similarity calculation (1:1 parity with C++ block_matching.cpp).*
    *----------------------------------------*

--------------------

### 📄 [compute_spatial.py](file:///e:/APP%20Developer/Pixel%20Refine/pixel_refine_desktop/enhance_stack/core/algorithm/denoising/spatial_core/similarity_taichi/compute_spatial.py)

* **Function**: `precompute_gradients_kernel(img, grad_x, grad_y, h, w)`
    *Precomputes Sobel DX and DY gradients for the entire image to avoid redundant calculations inside windows.*

* **Function**: `equalize_brightness_kernel(src, ref, dst, h, w)`
    *Calculates global average ratio between src and ref and applies gain to dst.*

* **Function**: `phase1_coarse_analysis_kernel(current_coarse, reference_coarse, coarse_grad_x, coarse_grad_y, ref_coarse_grad_x, ref_coarse_grad_y, coarse_confidence, coarse_tile_h, coarse_tile_w, h_coarse, w_coarse, noise_sigma, motion_sensitivity, noise_offset_factor)`
    *Generates a coarse confidence map using hybrid gradient similarity.*

* **Function**: `phase2_fine_analysis_kernel(current, reference, curr_grad_x, curr_grad_y, ref_grad_x, ref_grad_y, guidance_map, stability_map, weight_map_sum, base_window, row_starts, col_starts, pass_idx, tile_h, tile_w, h, w, noise_sigma, motion_sensitivity, noise_offset_factor, use_stability, use_guidance, early_exit_threshold)`
    *Performs sliding window analysis for fine weight map accumulation on GPU.*

* **Function**: `accumulate_spatial_merging_kernel(current_image_full, weight_map_work, final_image_sum, weight_map_sum_full, h_full, w_full, h_work, w_work, num_channels)`
    *Bilinearly interpolates work resolution weights to full resolution and accumulates frames.*

* **Function**: `compile_spatial_tcm()`

* **Function**: `generate_spatial_weights_taichi(current_image, reference_image, weight_map_sum, base_window, stability_map, row_starts, col_starts, tile_h, tile_w, noise_sigma, motion_sensitivity, noise_offset_factor, equalize_brightness, buffer_provider)`
    *Calculates the weight map for a single frame relative to the reference using Taichi AOT.*

* **Function**: `accumulate_spatial_merging_taichi(current_image_full, weight_map_work, final_image_sum, weight_map_sum_full)`
    *Accumulates a frame into the global sum using its processed weight map using Taichi AOT.*
    *----------------------------------------*

--------------------


## 📂 Directory: `Root Directory`

### 📄 [# DIRECTORY: pixel_refine_desktop/enhance_stack/core/algorithm/super_resolution](file:///e:/APP%20Developer/Pixel%20Refine/# DIRECTORY: pixel_refine_desktop/enhance_stack/core/algorithm/super_resolution)


--------------------


## 📂 Directory: `Root Directory`

### 📄 [Interpolation.py](file:///e:/APP%20Developer/Pixel%20Refine/pixel_refine_desktop/enhance_stack/core/algorithm/super_resolution/Interpolation.py)

* **Class**: `ThreadWorker`
  * Method: `__init__(self, db_path, single_process, batch_id)`
  * Method: `run(self)`
  * Method: `stop(self)`

* **Class**: `InterpolationAlgorithm`
  * Method: `__init__(self, db_path, hdf5_path)`
  * Method: `get_all_image_paths_for_batch_process(self, batch_id)`
  * Method: `load_images_from_hdf5(self, hdf5_path, stop_requested)`
  * Method: `load_images_from_folder(self, folder_path)`
  * Method: `load_images_from_paths(self, image_paths, stop_requested)`
    *Loads images from a list of image paths.*
  * Method: `average_stack(self, images, update_progress, stop_requested, total_overall_images, images_processed_so_far)`
    *Melakukan stacking gambar dengan metode rata-rata sederhana (simple average).*
    *Args:*
    *images (list): List berisi NumPy array gambar yang akan di-stack.*
    *update_progress (callable, optional): Callback untuk update progress bar.*
    *Dipanggil dengan (persentase, pesan).*
    *stop_requested (callable, optional): Callback untuk mengecek apakah proses*
    *harus dihentikan. Harus return True jika berhenti.*
    *total_overall_images (int, optional): Jumlah total gambar dalam keseluruhan proses*
    *(untuk kalkulasi progress yang lebih akurat).*
    *images_processed_so_far (int, optional): Jumlah gambar yang sudah diproses*
    *sebelum batch ini (untuk progress).*
    *Returns:*
    *np.ndarray: Gambar hasil stacking (rata-rata), atau array nol jika tidak ada gambar valid.*

* **Function**: `main(db_path, update_progress, stop_requested, batch_size, single_process, batch_id, progress_bar)`

* **Function**: `running_interpolation(parent, single_process, batch_id)`
    *Menampilkan progress bar dengan gaya kustom dan memanfaatkan thread.*
    *----------------------------------------*

--------------------


## 📂 Directory: `Root Directory`

### 📄 [# DIRECTORY: pixel_refine_desktop/enhance_stack/core/logic](file:///e:/APP%20Developer/Pixel%20Refine/# DIRECTORY: pixel_refine_desktop/enhance_stack/core/logic)


--------------------


## 📂 Directory: `Root Directory`

### 📄 [algorithm_logic.py](file:///e:/APP%20Developer/Pixel%20Refine/pixel_refine_desktop/enhance_stack/core/logic/algorithm_logic.py)

* **File Overview**:
    *Algorithm Logic - Core business logic untuk AlgorithmPanel.*
    *Handles: Algorithm selection, settings management, processing.*
    *Separated dari UI untuk better maintainability dan testability.*

* **Class**: `AlgorithmLogic`
    *Core logic untuk algorithm management dan settings.*
    *Responsibilities:*
    *- Manage algorithm selections*
    *- Handle settings get/set*
    *- Validate algorithm choices*
    *- Provide algorithm info*
  * Method: `__init__(self)`
    *Initialize algorithm logic.*
  * Method: `_load_algorithm_names(self)`
    *Load available algorithm names dari backend.*
  * Method: `get_algorithm_names(self, category)`
    *Get available algorithm names untuk kategori.*
    *Args:*
    *category: 'alignment', 'super_resolution', atau 'denoising'*
    *Returns:*
    *list: List of algorithm names*
  * Method: `get_algorithm_descriptions(self, category)`
    *Get algorithm descriptions untuk kategori.*
    *Args:*
    *category: 'alignment', 'super_resolution', atau 'denoising'*
    *Returns:*
    *dict: Mapping of algorithm name -> description*
  * Method: `get_settings(self)`
    *Get current algorithm settings.*
    *Returns:*
    *dict: {'alignment': str, 'super_resolution': str, 'denoising': str}*
  * Method: `set_settings(self, settings)`
    *Set algorithm settings.*
    *Args:*
    *settings: dict dengan format:*
    *{'alignment': str, 'super_resolution': str, 'denoising': str}*
    *Returns:*
    *bool: True jika berhasil, False jika ada error*
  * Method: `set_algorithm(self, category, algorithm_name)`
    *Set single algorithm.*
    *Args:*
    *category: 'alignment', 'super_resolution', atau 'denoising'*
    *algorithm_name: Name of algorithm*
    *Returns:*
    *bool: True jika berhasil*
  * Method: `get_algorithm(self, category)`
    *Get current algorithm untuk kategori.*
    *Args:*
    *category: 'alignment', 'super_resolution', atau 'denoising'*
    *Returns:*
    *str: Current algorithm name, atau None*
  * Method: `_is_valid_algorithm(self, category, algorithm_name)`
    *Validate if algorithm is valid untuk kategori.*
  * Method: `start_processing(self)`
    *Mark processing as started.*
    *Returns:*
    *bool: True jika berhasil start*
  * Method: `stop_processing(self)`
    *Mark processing as stopped.*
  * Method: `is_processing(self)`
    *Check if currently processing.*
    *Returns:*
    *bool: True jika sedang processing*
  * Method: `set_progress(self, value)`
    *Set progress value.*
    *Args:*
    *value: Progress value (0-100)*
    *Returns:*
    *bool: True jika valid*
  * Method: `get_progress(self)`
    *Get current progress.*
    *Returns:*
    *int: Progress value (0-100)*
  * Method: `set_current_task(self, task_name)`
    *Set current task yang sedang diproses.*
    *Args:*
    *task_name: Name of current task*
  * Method: `get_current_task(self)`
    *Get current task yang sedang diproses.*
    *Returns:*
    *str: Task name, atau None*
  * Method: `get_processing_state(self)`
    *Get complete processing state.*
    *Returns:*
    *dict: Complete processing state*
  * Method: `validate_settings(self)`
    *Validate if all settings are configured.*
    *Returns:*
    *tuple: (is_valid, error_message)*
  * Method: `reset_settings(self)`
    *Reset settings ke default (None).*
  * Method: `get_settings_summary(self)`
    *Get human-readable summary dari settings.*
    *Returns:*
    *str: Settings summary*
    *----------------------------------------*

--------------------

### 📄 [algorithm_processor.py](file:///e:/APP%20Developer/Pixel%20Refine/pixel_refine_desktop/enhance_stack/core/logic/algorithm_processor.py)

* **File Overview**:
    *Algorithm Processor Thread*
    *Handles background execution of image processing algorithms with progress tracking.*

* **Class**: `AlgorithmProcessorThread`
    *Background thread to execute selected algorithms for a batch.*
    *This thread handles the execution of image processing algorithms*
    *(alignment, super resolution, denoising) with progress tracking.*
    *Supports both single process mode and batch processing mode.*
  * Method: `__init__(self, batch_id, settings, parent, single_process)`
    *Initialize the algorithm processor thread.*
    *Args:*
    *batch_id: ID of the batch to process*
    *settings: Dict with algorithm selections (alignment, super_resolution, denoising)*
    *parent: Parent QObject (usually the layout or panel)*
    *single_process: If True, run in single process mode (default).*
    *Set to False for batch processing with batch_id.*
  * Method: `stop(self)`
    *Request the thread to stop gracefully.*
  * Method: `is_cancelled(self)`
    *Check if cancellation was requested.*
  * Method: `run(self)`
    *Execute the selected algorithms.*
    *----------------------------------------*

--------------------

### 📄 [batch_parameter_manager.py](file:///e:/APP%20Developer/Pixel%20Refine/pixel_refine_desktop/enhance_stack/core/logic/batch_parameter_manager.py)

* **File Overview**:
    *Batch parameter management utilities.*
    *Handles loading and saving batch algorithm parameters from JSON.*

* **Function**: `get_json_path()`
    *Return the centralized path to batch_parameter.json.*

* **Function**: `load_json_state(path, default)`
    *Load JSON state from file.*
    *Args:*
    *path: Path to JSON file (defaults to BATCH_PARAMETER_PATH)*
    *default: Default value if file doesn't exist or is invalid*
    *Returns:*
    *Dictionary with loaded state or default*

* **Function**: `save_json_state(path, data)`
    *Save JSON state to file.*
    *Args:*
    *path: Path to JSON file (defaults to BATCH_PARAMETER_PATH)*
    *data: Dictionary to save*

* **Function**: `update_batch_settings(store, batch_id, settings)`
    *Update batch settings in the store and save to persistence.*
    *Args:*
    *store: SyncStore instance*
    *batch_id: Batch ID*
    *settings: Dictionary containing algorithm settings*

* **Function**: `get_batch_algorithm_summary(batch_id)`
    *Get algorithm summary for a batch.*
    *Args:*
    *batch_id: Batch ID*
    *Returns:*
    *Comma-separated string of active algorithms or "Not Set"*

* **Function**: `get_batch_algorithm_settings(batch_id)`
    *Get algorithm settings for a batch in the format expected by AlgorithmProcessorThread.*
    *Args:*
    *batch_id: Batch ID*
    *Returns:*
    *Dictionary with keys: alignment, super_resolution, denoising*
    *----------------------------------------*

--------------------

### 📄 [batch_processor.py](file:///e:/APP%20Developer/Pixel%20Refine/pixel_refine_desktop/enhance_stack/core/logic/batch_processor.py)

* **File Overview**:
    *Batch Processor Logic*
    *Handles background processing of image batches independently of the UI.*

* **Class**: `BatchProcessingThread`
    *Worker thread that processes a list of batches sequentially.*
  * Method: `__init__(self, panels_to_process, batch_page_layout, target_folder)`
  * Method: `stop(self)`
    *Request the thread to stop smoothly.*
  * Method: `run(self)`
    *----------------------------------------*

--------------------

### 📄 [batch_selection_handler.py](file:///e:/APP%20Developer/Pixel%20Refine/pixel_refine_desktop/enhance_stack/core/logic/batch_selection_handler.py)

* **Class**: `BatchSelectionHandler`
    *Handles the logic for batch selection in RightPanel.*
    *Coordinates between RightPanel and DisplayPanel.*
  * Method: `__init__(self, right_panel)`
  * Method: `handle_selection(self, selected_values)`
    *Main logic for handling selection changes.*
  * Method: `_finish_layout_adjustment(self)`
    *Finalize splitter sizes but ONLY if we are still in collapsed state.*
    *----------------------------------------*

--------------------

### 📄 [context_menu_handler.py](file:///e:/APP%20Developer/Pixel%20Refine/pixel_refine_desktop/enhance_stack/core/logic/context_menu_handler.py)

* **File Overview**:
    *Context Menu Handler - Handles context menu operations for image grid.*
    *Manages right-click menu creation and actions like set reference and delete.*

* **Class**: `ContextMenuHandler`
    *Handles context menu operations for image grid.*
  * Method: `__init__(self, parent_panel)`
    *Initialize ContextMenuHandler.*
    *Args:*
    *parent_panel: Reference to DisplayPanel for accessing UI components*
  * Method: `create_context_menu(self, card_under_mouse)`
    *Create context menu for grid area.*
    *Args:*
    *card_under_mouse: ImageCard widget under mouse, or None*
    *Returns:*
    *QMenu: Configured context menu*
  * Method: `set_as_reference(self, image_path)`
    *Set image as reference via controller.*
    *Args:*
    *image_path: Path to image to set as reference*
  * Method: `find_card_under_mouse(self)`
    *Find card widget under mouse cursor.*
    *Returns:*
    *ImageCard widget under mouse, or None*
    *----------------------------------------*

--------------------

### 📄 [database_manager.py](file:///e:/APP%20Developer/Pixel%20Refine/pixel_refine_desktop/enhance_stack/core/logic/database_manager.py)

* **Class**: `DatabaseManager`
    *Manages interactions with the SQLite database for storing and retrieving*
    *image paths for single and batch processing.*
  * Method: `__init__(self, db_path)`
    *Initializes the DatabaseManager.*
    *Args:*
    *db_path: The path to the database file.*
  * Method: `_get_connection(self)`
    *Establishes a database connection with High-Performance settings.*
  * Method: `_add_column_if_not_exists(self, cursor, table_name, column_name, column_def)`
  * Method: `create_database(self)`
    *Creates the necessary tables and ensures the 'is_reference' column exists*
    *in 'single_process_image' and 'is_reference_batch' in 'batch_process_image'.*
  * Method: `create_new_panorama_project(self, name)`
    *Membuat entri proyek panorama baru di database.*
    *Args:*
    *name (str): Nama untuk proyek panorama baru (misalnya, "Panorama 1").*
    *Returns:*
    *int: ID dari proyek yang baru dibuat, atau None jika gagal.*
  * Method: `get_images_for_project(self, project_id)`
    *Mengambil semua path gambar yang terkait dengan project_id tertentu,*
    *diurutkan berdasarkan image_order.*
    *Args:*
    *project_id (int): ID dari proyek panorama.*
    *Returns:*
    *list: Sebuah daftar (list) dari string path gambar.*
  * Method: `get_all_panorama_projects(self)`
    *Mengambil semua proyek panorama dari database, diurutkan berdasarkan nama.*
    *Returns:*
    *list: Daftar tuple, di mana setiap tuple berisi (id, name).*
  * Method: `delete_panorama_project(self, project_id)`
    *Menghapus proyek panorama berdasarkan ID-nya.*
    *Karena ON DELETE CASCADE, gambar terkait di panorama_project_images juga akan terhapus.*
    *Args:*
    *project_id (int): ID dari proyek yang akan dihapus.*
    *Returns:*
    *bool: True jika berhasil, False jika gagal.*
  * Method: `rename_panorama_project(self, project_id, new_name)`
    *Mengubah nama proyek panorama di database.*
    *Args:*
    *project_id (int): ID dari proyek yang akan diubah namanya.*
    *new_name (str): Nama baru untuk proyek.*
    *Returns:*
    *bool: True jika berhasil, False jika gagal.*
  * Method: `get_project_workflow_settings(self, project_id)`
    *Mengambil pengaturan workflow untuk sebuah proyek panorama tertentu.*
    *Args:*
    *project_id (int): ID dari proyek.*
    *Returns:*
    *dict: Dictionary berisi pengaturan, atau None jika proyek tidak ditemukan.*
  * Method: `save_project_workflow_setting(self, project_id, setting_key, setting_value)`
    *Menyimpan satu pengaturan workflow untuk sebuah proyek.*
    *Args:*
    *project_id (int): ID dari proyek.*
    *setting_key (str): Nama kolom di database (misal: 'align_algorithm').*
    *setting_value (str/int/float): Nilai baru untuk pengaturan.*
    *Returns:*
    *bool: True jika berhasil, False jika gagal.*
  * Method: `add_images_to_project(self, project_id, image_paths)`
    *Menambahkan daftar path gambar ke sebuah proyek panorama.*
    *Ini adalah operasi transaksional.*
    *Args:*
    *project_id (int): ID dari proyek target.*
    *image_paths (list): Daftar string path gambar.*
    *Returns:*
    *bool: True jika semua gambar berhasil ditambahkan, False jika ada error.*
  * Method: `get_images_for_project(self, project_id)`
    *Mengambil semua path gambar untuk sebuah proyek panorama tertentu.*
    *Args:*
    *project_id (int): ID dari proyek yang gambarnya ingin diambil.*
    *Returns:*
    *list: Daftar string path gambar.*
  * Method: `delete_images_from_project(self, project_id, image_paths_to_delete)`
    *Menghapus beberapa gambar dari sebuah proyek panorama tertentu.*
    *Args:*
    *project_id (int): ID dari proyek.*
    *image_paths_to_delete (list): Daftar path gambar yang akan dihapus dari proyek ini.*
    *Returns:*
    *bool: True jika berhasil, False jika ada error.*
  * Method: `_get_or_create_image_id(self, cursor, image_path)`
    *Helper function to get existing image_id or create a new one.*
    *Assumes cursor is already active within a transaction.*
  * Method: `create_new_batch(self, batch_name)`
    *Creates a new batch entry in the 'batch_process' table.*
    *If the batch name already exists, returns the ID of the existing batch.*
    *Args:*
    *batch_name: The desired unique name for the batch.*
    *Returns:*
    *The integer ID of the created or existing batch, or None on error.*
  * Method: `batch_process_save_image_path(self, batch_id, image_paths)`
    *Saves multiple image paths into a specified batch by linking them*
    *in 'batch_process_image'. Creates entries in 'images' if needed.*
    *If adding the first image to a new batch context (or batch has no ref yet),*
    *it can be set as reference.*
    *Args:*
    *batch_id: The ID of the target batch.*
    *image_paths: A list of image file paths to add.*
    *Returns:*
    *The number of images successfully added (new links created).*
  * Method: `set_batch_process_reference(self, batch_id, image_path)`
    *Sets the specified image as the reference image for a specific batch.*
    *Sets 'is_reference_batch = 0' for all other images in that batch.*
    *Args:*
    *batch_id: The ID of the batch.*
    *image_path: The path of the image to set as reference within this batch.*
    *Returns:*
    *True if successful, False otherwise (e.g., image not in batch, batch not found).*
  * Method: `batch_process_delete_image(self, batch_id, image_id)`
    *Deletes a specific image link from a given batch.*
    *If the deleted image was the reference for this batch,*
    *a new reference might need to be set if other images exist.*
    *Args:*
    *batch_id: The batch ID.*
    *image_id: The ID of the image link to remove.*
  * Method: `batch_process_delete_batch(self, batch_id)`
    *Deletes a specific batch definition from 'batch_process'.*
    *Associated image links in 'batch_process_image' should be deleted*
    *automatically due to 'ON DELETE CASCADE'.*
    *Args:*
    *batch_id: The ID of the batch to delete.*
  * Method: `batch_process_delete_selected_images(self, batch_id, image_paths_to_delete)`
    *ULTRA OPTIMIZED DELETE:*
    *1. Menggunakan 'Blind Bulk Delete' dengan sub-query untuk kecepatan maksimal.*
    *2. Memperbaiki Reference (Reference Repair) hanya SEKALI di akhir transaksi.*
    *3. Menangani limit variabel SQLite dengan chunking internal.*
  * Method: `delete_all_batches(self)`
    *Deletes ALL batch definitions from 'batch_process'.*
    *Associated links in 'batch_process_image' should be deleted via CASCADE.*
    *Does not delete images from the main 'images' table.*
  * Method: `get_all_batch_names(self)`
    *Returns a list of all batch names from the 'batch_process' table.*
  * Method: `get_all_batch_ids(self)`
    *Returns a list of all batch IDs from the 'batch_process' table.*
  * Method: `get_images_by_batch(self, batch_id)`
    *Returns a list of image paths associated with a given batch_id.*
    *The reference image for the batch is listed first.*
  * Method: `get_batch_process_reference_image(self, batch_id)`
    *Retrieves the path of the current reference image for a specific batch, if any.*
    *Args:*
    *batch_id: The ID of the batch.*
    *Returns:*
    *Path string of the reference image or None if no reference is set or batch not found.*
  * Method: `get_batch_process_image_paths(self, batch_id)`
    *Retrieves image paths currently linked in batch_process_image.*
    *If batch_id is provided, retrieves paths only for that specific batch,*
    *with the reference image listed first.*
    *Otherwise, retrieves distinct paths from ALL batches (order might be less defined).*
    *Args:*
    *batch_id (int, optional): The specific batch ID. Defaults to None (all batches).*
    *Returns:*
    *A list of image paths.*
  * Method: `single_process_save_image_path(self, image_path)`
  * Method: `set_single_process_reference(self, image_path)`
  * Method: `single_process_delete_path_images(self, image_paths)`
  * Method: `get_single_process_image_paths(self)`
  * Method: `get_single_process_reference_image(self)`
  * Method: `delete_image_path_from_all(self, image_path)`
    *----------------------------------------*

--------------------

### 📄 [deletion_manager.py](file:///e:/APP%20Developer/Pixel%20Refine/pixel_refine_desktop/enhance_stack/core/logic/deletion_manager.py)

* **Class**: `ImageDeletionWorker`
    *Worker menghapus gambar dari DB/Disk.*
    *OPTIMASI: Menggunakan Chunk Besar (50) untuk efisiensi I/O Database (HDD Friendly).*
  * Method: `__init__(self, controller, batch_id, paths_to_remove)`
  * Method: `run(self)`

* **Class**: `DeletionManager`
  * Method: `__init__(self, display_panel)`
  * Method: `_is_widget_in_viewport(self, widget)`
  * Method: `_lite_fade_out(self, widget, duration, callback)`
    *Animasi Fade Out Ringan (In-Place) untuk mencegah crash QPainter.*
  * Method: `_process_one_item(self)`
    *Mengambil 1 item dari antrean UI dan memprosesnya.*
  * Method: `request_deletion(self, selected_ids)`
    *Request deletion of selected images with confirmation.*
  * Method: `start_deletion_process(self, paths_to_remove)`
  * Method: `_on_worker_progress(self, deleted_ids)`
    *Diterima saat Worker selesai menghapus CHUNK BESAR (50 gambar).*
    *Ini akan mengisi antrean UI sekaligus.*
  * Method: `_on_worker_finished(self, count, batch_id)`
  * Method: `_on_worker_error(self, message, batch_id)`
  * Method: `resume_deletion_simulation(self, batch_id)`
  * Method: `queue_zombie_card(self, card_id, card_widget)`
    *----------------------------------------*

--------------------

### 📄 [display_logic.py](file:///e:/APP%20Developer/Pixel%20Refine/pixel_refine_desktop/enhance_stack/core/logic/display_logic.py)

* **File Overview**:
    *Display Logic - Core business logic untuk DisplayPanel.*
    *Handles: Grid management, thumbnail loading, preview display.*
    *Separated dari UI untuk better maintainability dan testability.*

* **Class**: `DisplayLogic`
    *Core logic untuk image display dan grid management.*
    *Responsibilities:*
    *- Manage batch state*
    *- Load thumbnails*
    *- Handle preview display*
    *- Manage grid items*
  * Method: `__init__(self)`
    *Initialize display logic.*
  * Method: `set_batch(self, batch_id, images)`
    *Set current batch.*
    *Args:*
    *batch_id: ID dari batch*
    *images: List of image objects dengan .id dan .path attributes*
  * Method: `get_batch_info(self)`
    *Get current batch info.*
    *Returns:*
    *dict: {'batch_id': int, 'images': list, 'count': int}*
  * Method: `is_batch_empty(self)`
    *Check if current batch is empty.*
    *Returns:*
    *bool: True jika batch kosong atau tidak ada batch*
  * Method: `load_thumbnail_async(self, image_path, callback)`
    *Load thumbnail asinkron untuk image.*
    *Args:*
    *image_path: Path ke image file*
    *callback: Callable(QImage, str) - Called ketika thumbnail ready*
  * Method: `load_thumbnails_bulk_async(self, path_callback_pairs)`
    *Load multiple thumbnails in bulk for maximum efficiency.*
    *path_callback_pairs: list of (image_path, callback)*
  * Method: `prepare_preview(self, image_path)`
    *Prepare untuk preview display.*
    *Args:*
    *image_path: Path ke image untuk di-preview*
    *Returns:*
    *bool: True jika ready, False jika error*
  * Method: `display_preview(self, zoomable_widget, image_path)`
    *Display preview di zoomable widget.*
    *Args:*
    *zoomable_widget: Zoomable widget untuk display*
    *image_path: Path ke image*
    *Returns:*
    *ImageLoaderThread: Thread yang loading image*
  * Method: `register_grid_item(self, card_id, image_info)`
    *Register card item untuk tracking.*
    *Args:*
    *card_id: ID dari card*
    *image_info: dict dengan image information*
  * Method: `unregister_grid_item(self, card_id)`
    *Unregister card item.*
    *Args:*
    *card_id: ID dari card*
  * Method: `get_grid_item_count(self)`
    *Get jumlah items di grid.*
    *Returns:*
    *int: Jumlah grid items*
  * Method: `clear_all(self)`
    *Clear semua state dan stop background tasks.*
  * Method: `get_thumbnail_processor(self)`
    *Get thumbnail processor instance.*
    *Returns:*
    *ThumbnailBatchProcessor: Current thumbnail processor*
  * Method: `validate_image_path(self, image_path)`
    *Validate image path.*
    *Args:*
    *image_path: Path ke image*
    *Returns:*
    *bool: True jika path valid*
  * Method: `get_selected_images(self)`
    *Get list of selected images.*
    *Note: Requires selection tracking in ImageCard.*
    *For now returns current batch.*
    *Returns:*
    *list: List of selected image paths*
  * Method: `detect_processed_results(self, original_path)`
    *Detect processed result files related to an original image.*
    *Assumes naming convention: [OriginalName]_[Process].tif*
    *Args:*
    *original_path: Path to original image*
    *Returns:*
    *list: List of dicts {'name': 'Process Name', 'path': str}*
  * Method: `check_visible_cards(self, all_cards, grid_container, viewport_getter)`
    *Detect cards visible in viewport and load their thumbnails lazily.*
    *Args:*
    *all_cards: Dict of card_id -> ImageCard*
    *grid_container: GridContainer widget*
    *viewport_getter: Callable that returns viewport widget*
    *Returns:*
    *List of (path, card) tuples to load*
  * Method: `load_visible_thumbnails(self, to_load_pairs)`
    *Load thumbnails for visible cards.*
    *Args:*
    *to_load_pairs: List of (path, card, callback_maker) tuples*
    *----------------------------------------*

--------------------

### 📄 [display_manager.py](file:///e:/APP%20Developer/Pixel%20Refine/pixel_refine_desktop/enhance_stack/core/logic/display_manager.py)

* **File Overview**:
    *Display Manager for Enhance Stack.*
    *Utilities untuk mengelola clear_display logic,*
    *termasuk membersihkan grid, preview, cache, dan threads.*
    *Mirrored dari panorama/working_left_panel.py untuk consistency.*

* **Class**: `DisplayThreadManager`
    *Singleton Manager for handling Display-related threads (e.g. Thumbnails).*
    *Prevents 'QThread destroyed while thread is still running' errors by*
    *holding strong references until finished() signal is emitted.*
  * Method: `instance(cls)`
  * Method: `__init__(self)`
  * Method: `register_thread(self, thread)`
    *Register a thread to safely manage its lifecycle.*
    *Pass ownership logic to this manager until the thread finishes.*
  * Method: `_cleanup_thread(self, thread)`
    *Remove thread from active set, allowing it to be GC'd.*
  * Method: `stop_all_threads(self)`
    *Request interruption for all managed threads.*
    *NON-BLOCKING: Does not wait for threads to finish, keeps UI responsive.*
    *Threads will be cleaned up automatically when they finish in background.*

* **Function**: `clear_grid_display(grid_layout, scroll_area, empty_state_widget, title, message)`
    *Clear grid view dan tampilkan empty state.*
    *Args:*
    *grid_layout: QHBoxLayout containing grid items*
    *scroll_area: QScrollArea widget*
    *empty_state_widget: EmptyState widget untuk tampilan kosong*
    *title: Title untuk empty state*
    *message: Message untuk empty state*

* **Function**: `clear_preview_display(preview_scene)`
    *Clear preview/zoom view.*
    *Args:*
    *preview_scene: QGraphicsScene untuk preview*

* **Function**: `reset_display_state(left_panel)`
    *Reset semua display state di left panel.*
    *Args:*
    *left_panel: LeftPanel instance*

* **Function**: `display_processed_result(display_panel, image_path, update_dropdown)`
    *Refactored display_processed_result logic.*
    *Display processed result image in Compare Mode (Default).*
    *Loads Original + Processed into ComparisonGraphicsItem.*
    *----------------------------------------*

--------------------

### 📄 [drag_drop_handler.py](file:///e:/APP%20Developer/Pixel%20Refine/pixel_refine_desktop/enhance_stack/core/logic/drag_drop_handler.py)

* **File Overview**:
    *Drag Drop Handler - Handles drag and drop operations for image import.*
    *Manages drag enter, drag leave, and drop events with file validation.*

* **Class**: `DragDropHandler`
    *Handles drag and drop operations for image files.*
  * Method: `__init__(self, parent_panel)`
    *Initialize DragDropHandler.*
    *Args:*
    *parent_panel: Reference to DisplayPanel for accessing UI components*
  * Method: `handle_drag_enter(self, mime_data)`
    *Handle drag enter event.*
    *Args:*
    *mime_data: MIME data from drag event*
    *Returns:*
    *Tuple of (should_accept, file_count)*
  * Method: `handle_drag_leave(self)`
    *Handle drag leave event.*
  * Method: `handle_drop(self, mime_data)`
    *Handle drop event and filter valid image files.*
    *Args:*
    *mime_data: MIME data from drop event*
    *Returns:*
    *Tuple of (should_accept, valid_files_list)*
  * Method: `filter_valid_files(self, urls)`
    *Filter valid image files from URL list.*
    *Args:*
    *urls: List of QUrl objects*
    *Returns:*
    *List of valid file paths*
    *----------------------------------------*

--------------------

### 📄 [grid_manager.py](file:///e:/APP%20Developer/Pixel%20Refine/pixel_refine_desktop/enhance_stack/core/logic/grid_manager.py)

* **File Overview**:
    *Grid Manager - Handles all grid-related operations for DisplayPanel.*
    *Manages grid population, incremental loading, and viewport detection.*
    *Windowed Lazy Loading:*
    *- Hanya WINDOW_SIZE (50) card terdekat dari viewport yang memuat gambar di RAM.*
    *- Card di luar window otomatis di-unload (card.unload_image()) untuk hemat RAM.*
    *- Saat scroll, window dihitung ulang → card baru dimuat dari disk cache (JPG), lama di-unload.*
    *- Sort berdasarkan jarak dari tengah viewport (bukan FIFO).*
    *- Recovery watchdog setiap 15 detik untuk retry card yang tertinggal.*

* **Class**: `GridManager`
    *Manages grid operations including population and viewport detection.*
  * Method: `__init__(self, parent_panel)`
    *Initialize GridManager.*
    *Args:*
    *parent_panel: Reference to DisplayPanel for accessing UI components*
  * Method: `clear_grid(self)`
    *Remove all widgets from grid container.*
  * Method: `populate_grid_incremental(self, visual_images)`
    *Start incremental population of grid with images.*
    *Args:*
    *visual_images: List of image objects to populate*
  * Method: `_process_incremental_population(self)`
    *Tambah gambar ke grid dalam chunk untuk menghindari UI freeze.*
  * Method: `on_scroll(self)`
    *Dipanggil saat scrollbar bergerak. Debounce 120ms sebelum update window.*
  * Method: `_get_viewport_center_y(self)`
    *Dapatkan posisi Y tengah viewport dalam koordinat content widget.*
  * Method: `_compute_card_distance(self, card, center_y)`
    *Hitung jarak absolut card dari pusat viewport.*
    *Digunakan untuk sort prioritas loading (terdekat = prioritas tertinggi).*
  * Method: `_update_window(self)`
    *Inti dari Windowed Lazy Loading.*
    *1. Hitung jarak semua card dari pusat viewport.*
    *2. Card dalam WINDOW_SIZE terdekat → load jika belum termuat.*
    *3. Card di luar window → unload untuk bebaskan RAM.*
  * Method: `_on_card_loaded(self, q_image, path, card, card_id)`
    *Callback setelah thumbnail selesai dimuat dari disk/decode.*
  * Method: `_start_background_sync(self)`
    *Trigger background sync setelah breathing room selesai.*
  * Method: `set_sync_paths(self, paths)`
    *Set paths untuk background sync.*
  * Method: `start_recovery_timer(self)`
    *Mulai watchdog timer untuk retry thumbnail yang tertinggal.*
  * Method: `stop_recovery_timer(self)`
    *Stop watchdog timer.*
  * Method: `_recovery_check(self)`
    *Watchdog: Dipanggil setiap 15 detik.*
    *Cek apakah card di dalam window saat ini ada yang masih belum termuat.*
    *- Jika semua dalam window sudah termuat → stop timer.*
    *- Jika ada yang tertinggal → reset _is_fetching (lepas stuck state), retry.*
  * Method: `stop_staged_timer(self)`
    *Stop semua timer (staged, scroll debounce, dan recovery).*
  * Method: `is_widget_in_viewport(self, widget)`
    *Check if widget is visible in GridContainer viewport.*
    *Used for viewport-aware animation optimization.*
    *----------------------------------------*

--------------------

### 📄 [ImagePreviewHandler.py](file:///e:/APP%20Developer/Pixel%20Refine/pixel_refine_desktop/enhance_stack/core/logic/ImagePreviewHandler.py)

* **Class**: `ImagePreviewHandler`
    *Mengelola logika tampilan pratinjau gambar dengan cache LRU adaptif*
    *berbasis RAM/item count, dengan opsi penyimpanan cache sebagai JPEG bytes atau QImage.*
  * Method: `__init__(self, preview_scene, preview_view, parent)`
  * Method: `get_total_system_ram()`
    *Ambil total RAM sistem (bytes) tanpa psutil.*
  * Method: `_get_current_process_ram_bytes(self)`
    *Mengambil penggunaan memori saat ini (RSS) dari proses Python*
    *tanpa menggunakan psutil.*
  * Method: `_store_view_state(self, level, relative_center)`
    *Menyimpan level zoom dan posisi tengah relatif terakhir.*
  * Method: `update_preview(self, selected_paths)`
    *Memulai proses pembaruan panel pratinjau. Mengecek cache QImage terlebih dahulu.*
  * Method: `preload_low_res_images(self, paths_to_preload)`
    *Memulai thread untuk membuat cache resolusi rendah menggunakan RawImageProcessingThread.*
  * Method: `_handle_preloaded_image_ready(self, result)`
    *Menyimpan hasil dari thread pra-pemuatan ke dalam cache low-res.*
  * Method: `_load_pixmap_from_cache_value(self, image_path, cached_value)`
    *Helper untuk memuat QPixmap dari nilai cache (QImage atau bytes).*
  * Method: `_trigger_full_processing(self, image_path)`
    *Menampilkan status loading & memulai timer utama.*
  * Method: `handle_resize(self)`
    *Menyesuaikan tampilan gambar saat ukuran view berubah.*
  * Method: `get_original_pixmap(self)`
    *Mengembalikan QPixmap asli yang sedang ditampilkan.*
  * Method: `clear_cache(self)`
    *Menghapus semua item dari cache preview.*
  * Method: `set_cache_mode(self, use_jpeg, quality)`
    *Mengatur mode cache dan membersihkan cache lama.*
  * Method: `_stop_current_processing(self)`
    *Menghentikan SEMUA timer dan thread pemrosesan.*
  * Method: `_initiate_processing(self)`
    *Memulai pemrosesan dari timer UTAMA.*
  * Method: `_initiate_pending_full_res_load(self)`
    *Memulai pemrosesan full-res JIKA path masih relevan.*
  * Method: `_start_raw_processing(self, path_to_process)`
    *Memulai thread untuk memproses satu gambar full-res.*
  * Method: `_handle_image_ready(self, image_result)`
    *Menangani hasil full-res, update cache, pindahkan ke low-res jika perlu.*
  * Method: `_handle_image_error(self, error_message)`
    *Menangani pesan error dari thread pemrosesan.*
  * Method: `_display_image(self, pixmap)`
    *Menampilkan QPixmap yang diberikan dan memanggil _fit_image_to_panel.*
  * Method: `_fit_image_to_panel(self)`
    *Reset view, fit item, dan terapkan state zoom/posisi persisten.*
  * Method: `_show_status_message(self, message)`
    *Menampilkan pesan status menggunakan QGraphicsTextItem dengan word wrap jika panjang teks melebihi 50px.*
    *Menambahkan kemampuan untuk menyalin teks yang ditampilkan.*
    *----------------------------------------*

--------------------

### 📄 [image_display_helper.py](file:///e:/APP%20Developer/Pixel%20Refine/pixel_refine_desktop/enhance_stack/core/logic/image_display_helper.py)

* **File Overview**:
    *Image Display Helper untuk Zoomable Preview*
    *============================================*
    *Helper module untuk menampilkan gambar full resolution di Zoomable widget*
    *dengan support untuk berbagai format dan ukuran gambar.*

* **Class**: `ComparisonCache`
    *Manager specifically for caching the 'Original' (Reference) image*
    *used in Comparison Mode.*
    *Saves converted results (e.g. from RAW) to disk to avoid re-conversion.*
  * Method: `instance(cls)`
  * Method: `__init__(self)`
  * Method: `_get_paths(self, batch_id)`
    *Helper to get cache file and metadata file for a specific batch.*
  * Method: `get_cached_path(self, batch_id, original_path)`
    *Returns the local cache path if it matches original_path for the batch, else None.*
  * Method: `save_to_cache(self, batch_id, original_path, image_array)`
    *Saves converted image_array to cache for a specific batch and updates metadata.*
  * Method: `clear_cache(self)`
    *Deletes cache files.*

* **Class**: `ImageLoaderThread`
    *Thread untuk load gambar full resolution dari disk.*
    *Support untuk JPEG, PNG, TIFF, RAW formats.*
  * Method: `__init__(self, image_path, max_width, max_height, is_reference, batch_id, parent)`
    *Initialize image loader thread.*
    *Args:*
    *image_path: Path ke file gambar*
    *max_width: Max width untuk resize (optional)*
    *max_height: Max height untuk resize (optional)*
    *is_reference: Jika True, gunakan/update comparison cache*
    *batch_id: ID batch untuk caching referensi*
    *parent: Parent widget*
  * Method: `run(self)`
    *Metode utama untuk loading gambar di background thread.*
  * Method: `_load_image(self)`
    *Load image file dan return numpy array.*
  * Method: `_array_to_pixmap(self, image_array)`
    *Convert numpy array ke QPixmap.*
  * Method: `_resize_pixmap(self, pixmap)`
    *Resize pixmap jika terlalu besar.*

* **Function**: `setup_zoomable_preview(zoomable_widget, image_path, is_reference, batch_id)`
    *Setup Zoomable widget untuk display gambar.*
    *Args:*
    *zoomable_widget: Zoomable QGraphicsView instance*
    *image_path: Path ke file gambar*
    *is_reference: Jika True, gunakan/update comparison cache*
    *batch_id: ID batch untuk caching referensi*

* **Function**: `display_image_in_zoomable(zoomable_widget, image_path, callback, is_reference, batch_id)`
    *Display gambar di Zoomable widget dengan loading indicator.*
    *Args:*
    *zoomable_widget: Zoomable QGraphicsView instance*
    *image_path: Path ke file gambar*
    *callback: Optional callback saat image loaded (pixmap, path) -> None*
    *is_reference: Jika True, gunakan/update comparison cache*
    *batch_id: ID batch untuk caching referensi*

* **Function**: `load_and_display_image(image_path, max_width, max_height, is_reference, batch_id)`
    *Load dan return QPixmap dari image path.*
    *Helper untuk synchronous image loading.*
    *Support caching untuk reference image.*
    *Args:*
    *image_path: Path ke file gambar*
    *max_width: Max width untuk resize*
    *max_height: Max height untuk resize*
    *is_reference: Jika True, gunakan/update comparison cache*
    *batch_id: ID batch untuk caching referensi*
    *----------------------------------------*

--------------------

### 📄 [image_handler.py](file:///e:/APP%20Developer/Pixel%20Refine/pixel_refine_desktop/enhance_stack/core/logic/image_handler.py)

* **Function**: `handle_import_button(self)`
    *Function to manage images import using SUPPORTED_FORMATS.*

* **Function**: `handle_delete_button(self)`
    *Function to delete images*
    *----------------------------------------*

--------------------

### 📄 [image_streamer.py](file:///e:/APP%20Developer/Pixel%20Refine/pixel_refine_desktop/enhance_stack/core/logic/image_streamer.py)

* **Class**: `ImageStreamer`
    *Kelas generik untuk Producer-Consumer Image Streaming.*
    *Membaca gambar dari HDF5 atau list path disk satu per satu*
    *di latar belakang (background thread),*
    *sehingga UI thread / Main thread hanya perlu mengiterasi `.stream()`.*
    *Penyelamat RAM untuk mencegah OOM (Out Of Memory).*
  * Method: `__init__(self, data_source, stop_requested, max_queue_size)`
  * Method: `__len__(self)`
  * Method: `__bool__(self)`
  * Method: `__getitem__(self, idx)`
  * Method: `_image_loader_worker(self)`
  * Method: `stream(self)`
    *Generator yang dapat diiterasi oleh Main Thread secara kontinyu.*
    *Yields: (index: int, image_array: np.ndarray)*
    *----------------------------------------*

--------------------

### 📄 [import_manager.py](file:///e:/APP%20Developer/Pixel%20Refine/pixel_refine_desktop/enhance_stack/core/logic/import_manager.py)

* **Class**: `ImportManager`
    *Manager untuk menangani semua logika import gambar.*
    *Mengikuti pola yang sama dengan DeletionManager.*
  * Method: `__init__(self, display_panel)`
  * Method: `_build_file_filter(self)`
    *Build file filter string untuk QFileDialog dari config.SUPPORTED_FORMATS.*
    *Returns:*
    *str: File filter string (e.g., "Images (*.jpg *.jpeg *.png ...)")*
  * Method: `import_images(self)`
    *Membuka dialog file untuk impor gambar dengan format dari config.SUPPORTED_FORMATS.*
    *Mirip dengan panorama page import_images method.*
  * Method: `add_single_image_to_grid(self, batch_id, batch_name, image_path)`
    *Menambah satu thumbnail ke grid secara real-time.*
  * Method: `on_batch_import_started(self, batch_id)`
    *Slot to mark a batch as actively importing.*
  * Method: `on_batch_import_finished(self, batch_id)`
    *Slot to mark a batch as finished importing.*
  * Method: `handle_batch_import(self, controller, database_manager, file_paths, batch_id)`
    *Handle the background import process for a batch.*
    *Extracted from page_layout.py.*
    *----------------------------------------*

--------------------

### 📄 [multi_threading.py](file:///e:/APP%20Developer/Pixel%20Refine/pixel_refine_desktop/enhance_stack/core/logic/multi_threading.py)

* **Class**: `BaseMultiThreading`
    *Base class for multithreading tasks. This class supports batch processing.*
  * Method: `__init__(self, task_function, items, batch_size, delay_ms)`
  * Method: `run(self)`
  * Method: `stop(self)`
    *Set the running flag to False to stop the thread.*

* **Class**: `RawImageProcessingThread`
    *Thread untuk memproses gambar dari path file menjadi QPixmap atau QImage.*
    *Mendukung dua mode operasi:*
    *1.  Resolusi Penuh (default):*
    *Memuat gambar dengan kualitas penuh, menerapkan pemrosesan paralel*
    *untuk format tertentu, dan menghasilkan QPixmap.*
    *2.  Resolusi Rendah (diaktifkan dengan `low_res_target_size`):*
    *Mengambil jalur cepat untuk memuat, mengubah ukuran gambar ke target*
    *yang ditentukan, dan menghasilkan tuple (path, QImage). Mode ini*
    *dirancang untuk pra-pemuatan (pre-caching) yang cepat.*
  * Method: `__init__(self, image_paths, batch_size, delay_ms, low_res_target_size)`
    *Inisialisasi thread pemrosesan.*
    *Args:*
    *image_paths (list): Daftar path gambar yang akan diproses.*
    *batch_size (int): Ukuran batch untuk pemrosesan.*
    *delay_ms (int): Jeda antar batch.*
    *low_res_target_size (int, optional): Jika diisi, mengaktifkan mode resolusi*
    *rendah. Nilai ini adalah ukuran (dalam piksel)*
    *untuk sisi terpanjang gambar thumbnail.*

* **Class**: `ImageImportThreading`
  * Method: `__init__(self, database_manager, image_paths, batch_size, delay_ms, batch_id)`

* **Class**: `BatchImageImportThreading`
  * Method: `__init__(self, database_manager, image_paths, batch_id, batch_name, batch_size, delay_ms)`

* **Class**: `ImageProcessingMultiThreading`
  * Method: `__init__(self, worker_function, db_path, single_process, batch_id, parent)`
  * Method: `run(self)`
  * Method: `stop(self)`

* **Function**: `_process_image_part(img_part_data)`
    *Memproses bagian gambar (NumPy array). Melakukan konversi warna/tipe jika perlu.*

* **Function**: `load_raw_as_8bit_rgb(image_path)`
    *Loads a RAW/DNG image and returns it as an 8-bit RGB numpy array using Hamilton Demosaic with rawpy fallback.*
    *----------------------------------------*

--------------------

### 📄 [process_manager.py](file:///e:/APP%20Developer/Pixel%20Refine/pixel_refine_desktop/enhance_stack/core/logic/process_manager.py)

* **Class**: `ProcessManager`
    *Centralized manager for background tasks, timers, and animations.*
    *Ensures that switching contexts (e.g., batches) cleans up previous tasks.*
  * Method: `instance(cls)`
  * Method: `__init__(self, parent)`
  * Method: `register_timer(self, context_id, timer)`
    *Register a timer to a specific context (e.g., 'batch_123').*
  * Method: `register_thread(self, context_id, thread)`
    *Register a thread to a specific context.*
  * Method: `cancel_context(self, context_id)`
    *Cancel all tasks associated with a context.*
  * Method: `clear_all(self)`
    *Emergency stop for everything.*

* **Function**: `is_widget_alive(widget)`
    *Safe check for PySide6 C++ objects.*
    *----------------------------------------*

--------------------

### 📄 [selection_manager.py](file:///e:/APP%20Developer/Pixel%20Refine/pixel_refine_desktop/enhance_stack/core/logic/selection_manager.py)

* **Class**: `SelectionManager`
    *Manages selection logic for DisplayPanel's grid.*
    *Handles click, multi-select (Ctrl/Shift), and keyboard navigation.*
  * Method: `__init__(self, display_panel)`
  * Method: `clear(self)`
    *Reset selection state completely.*
  * Method: `clear_selection(self)`
    *Deselect all visible cards visually.*
  * Method: `select_range(self, start_card_id, end_card_id)`
    *Select range between two cards.*
  * Method: `select_all(self)`
    *Select all images in current batch.*
  * Method: `handle_card_clicked(self, card_id, event, card_widget)`
    *Handle click event from ImageCard.*
  * Method: `navigate_selection(self, key, shift_held)`
    *Handle arrow key navigation.*
  * Method: `get_selected_ids(self)`
  * Method: `handle_enter_press(self)`
    *Handle Enter key to show preview for single selection.*
    *Returns:*
    *str or None: Image path to preview, or None if not applicable*
  * Method: `handle_delete_key(self)`
    *Handle Delete key press.*
    *Returns:*
    *list: List of selected card IDs to delete*
    *----------------------------------------*

--------------------

### 📄 [thumbnail_processor.py](file:///e:/APP%20Developer/Pixel%20Refine/pixel_refine_desktop/enhance_stack/core/logic/thumbnail_processor.py)

* **File Overview**:
    *Thumbnail Processor Utility*
    *============================*
    *Utility untuk memproses dan menampilkan thumbnail gambar dengan cara yang konsisten.*
    *Diekstrak dari batch_page/thumbnail.py untuk digunakan kembali di berbagai modul.*
    *Fitur:*
    *- Memproses thumbnail secara asinkron menggunakan QThread*
    *- Support untuk berbagai format gambar (JPEG, PNG, TIFF, RAW)*
    *- Koreksi orientasi otomatis menggunakan EXIF*
    *- Cache thumbnail untuk performa*
    *- Thread-safe dengan semaphore untuk membatasi thread aktif*

* **Class**: `ThumbnailWorkerSignals`
    *Signals for the ThumbnailWorker because QRunnable is not a QObject.*

* **Class**: `ThumbnailWorker`
    *Worker QRunnable untuk memproses thumbnail gambar guna menghindari handle leak (Window Manager objects).*
    *Menggunakan QThreadPool untuk eksekusi massal yang efisien.*
  * Method: `__init__(self, image_path, processor, batch_id, thumbnail_size)`
    *Initialize thumbnail worker.*
  * Method: `_should_abort(self)`
    *Check if this worker should stop immediately.*
  * Method: `abort(self)`
    *Request worker to stop.*
  * Method: `run(self)`
    *Main execution logic.*
  * Method: `_convert_to_qimage(self, pil_img)`
    *Helper to convert PIL Image to QImage safely.*
  * Method: `_process_image(self)`
    *Image processing logic for single worker.*

* **Class**: `ThumbnailBulkWorker`
    *Worker QRunnable untuk memproses SEKELOMPOK (Chunk) thumbnail gambar.*
    *Mengurangi overhead pembuatan objek worker dan emisi sinyal massal.*
  * Method: `__init__(self, image_paths, processor, batch_id, thumbnail_size)`
  * Method: `_should_abort(self)`
  * Method: `run(self)`
  * Method: `_safe_emit(self, q_image, path)`
    *Emisi sinyal dengan perlindungan terhadap shutdown.*

* **Class**: `ThumbnailBatchProcessor`
    *Utility class untuk memproses batch thumbnail images.*
    *Mengelola multiple thumbnail loader threads, RAM Cache, dan Deferred SQLite Save.*
  * Method: `__init__(self, thumbnail_size, max_concurrent)`
    *Initialize batch processor.*
  * Method: `add_to_stats(self, count)`
    *Tambah jumlah total gambar yang diproses secara dinamis (incremental).*
  * Method: `process_image(self, image_path, callback)`
    *Process single image thumbnail dengan sistem cache 2 level (RAM -> Disk).*
  * Method: `reset_stats(self, batch_id, total_count)`
    *Reset progress statistics for a new batch of work.*
  * Method: `process_batch(self, image_paths, callback)`
    *Process multiple images dengan Bulk Load dari RAM & Disk.*
  * Method: `_on_thumbnail_ready(self, q_image, image_path)`
    *Internal callback saat dekoding gambar selesai.*
  * Method: `_emit_progress(self)`
    *Kirim signal progress ke UI.*
  * Method: `flush_to_disk(self)`
    *Menyimpan semua thumbnail yang ada di pending queue ke disk (JPG) secara BULK.*
    *Dipanggil saat idle atau saat stop_all() untuk memastikan tidak ada yang terlewat.*
  * Method: `stop_all(self)`
    *Stop semua background tasks dan pastikan data tersimpan.*
  * Method: `__del__(self)`
    *Cleanup on deletion.*

* **Function**: `get_thumbnail_repo()`

* **Function**: `process_thumbnail_logic(image_path, thumbnail_size)`
    *Core logic to process a single thumbnail, used by both workers.*

* **Function**: `convert_pil_to_qimage(pil_img)`
    *Helper to convert PIL Image to QImage safely with data copy.*

* **Function**: `create_thumbnail_placeholder(thumbnail_size)`
    *Create a placeholder widget untuk menampilkan loading state.*
    *Args:*
    *thumbnail_size: Tuple (width, height) untuk ukuran placeholder*
    *Returns:*
    *QLabel widget dengan styling placeholder*

* **Function**: `display_thumbnail_in_layout(layout, q_image, image_path, display_size, animator)`
    *Display thumbnail image dalam layout.*
    *Args:*
    *layout: QLayout yang akan menampung thumbnail*
    *q_image: QImage object untuk ditampilkan*
    *image_path: Path ke file gambar (untuk tracking)*
    *display_size: Tuple (width, height) untuk display*
    *animator: Optional animator untuk fade effect*

* **Function**: `stop_thumbnail_threads(threads)`
    *Stop semua thumbnail threads dengan aman dan sinkron.*
    *----------------------------------------*

--------------------

### 📄 [ui_state_manager.py](file:///e:/APP%20Developer/Pixel%20Refine/pixel_refine_desktop/enhance_stack/core/logic/ui_state_manager.py)

* **File Overview**:
    *UI State Manager - Handles UI state management and placeholder widgets.*
    *Manages header titles, placeholders, and supported file extensions.*

* **Class**: `UIStateManager`
    *Manages UI state, placeholders, and header information.*
  * Method: `__init__(self, parent_panel)`
    *Initialize UIStateManager.*
    *Args:*
    *parent_panel: Reference to DisplayPanel for accessing UI components*
  * Method: `_build_supported_extensions(self)`
    *Build tuple of supported file extensions from config.*
    *Returns:*
    *Tuple of supported extensions*
  * Method: `create_placeholder_widget(self, html_text, button_text, on_button_click)`
    *Create placeholder widget to display when grid is empty.*
    *Follows pattern from panorama with flexible layout.*
    *Args:*
    *html_text: HTML text to display*
    *button_text: Text for button (optional)*
    *on_button_click: Callback for button click (optional)*
    *Returns:*
    *QWidget: Container with layout stretch + label + button (if provided)*
  * Method: `set_placeholder(self, widget)`
    *Set placeholder widget in stack.*
    *Safely removes previous placeholder if exists.*
    *Args:*
    *widget: Generic widget/container to show, or None to show grid*
  * Method: `show_empty_batch_state(self)`
    *Show empty state when batch is selected but has no images.*
    *Display informative message + button to import images directly.*
  * Method: `show_no_batch_state(self, on_create_batch)`
    *Show state when no batch is selected.*
    *Display message with "New Batch" button.*
    *Args:*
    *on_create_batch: Callback for creating new batch*
  * Method: `update_header_title(self, batch_id, batch_name, count)`
    *Update header title with batch name and image count.*
    *Args:*
    *batch_id: Current batch ID*
    *batch_name: Current batch name*
    *count: Image count to display*
  * Method: `get_supported_extensions(self)`
    *Get tuple of supported file extensions.*
    *Returns:*
    *Tuple of supported extensions*
    *----------------------------------------*

--------------------

### 📄 [workflow_process.py](file:///e:/APP%20Developer/Pixel%20Refine/pixel_refine_desktop/enhance_stack/core/logic/workflow_process.py)

* **Class**: `ImageViewer`
  * Method: `__init__(self, image_path, parent)`
  * Method: `update_zoom(self, value)`
    *Update zoom level for the image.*

* **Class**: `ZoomableGraphicsView`
  * Method: `__init__(self, image_path, parent)`
  * Method: `init_ui(self)`
    *Initialize the graphics view.*
  * Method: `wheelEvent(self, event)`
    *Handle mouse wheel event for zooming.*
  * Method: `set_zoom(self, scale_factor)`
    *Set zoom level by scaling the view.*

* **Function**: `get_last_image(path)`
    *Mengambil file gambar terakhir dari folder berdasarkan waktu modifikasi*
    *----------------------------------------*

--------------------

### 📄 [Zoomable_Handler.py](file:///e:/APP%20Developer/Pixel%20Refine/pixel_refine_desktop/enhance_stack/core/logic/Zoomable_Handler.py)

* **Class**: `Zoomable`
    *QGraphicsView dengan kemampuan zoom in/out berbasis kursor mouse.*
  * Method: `__init__(self, scene, parent)`
  * Method: `_get_relative_center(self)`
    *Menghitung posisi relatif pusat viewport terhadap item utama di scene.*
  * Method: `_emit_view_state(self)`
    *Mengambil state saat ini dan memancarkan sinyal.*
  * Method: `wheelEvent(self, event)`
    *Tangani zoom dan emit state baru.*
  * Method: `mousePressEvent(self, event)`
    *Catat jika pan dimulai.*
  * Method: `mouseReleaseEvent(self, event)`
    *Jika pan selesai, emit state baru.*
  * Method: `apply_zoom_level(self, target_level)`
    *Terapkan level zoom absolut.*
  * Method: `apply_state(self, target_level, relative_center)`
    *Menerapkan level zoom dan posisi tengah relatif.*
  * Method: `reset_zoom(self)`
    *Mengembalikan zoom ke level default (100%) dan membersihkan transform.*
  * Method: `zoom_to_fit(self, rect)`
    *Fit the given rect (or scene rect) into the view.*
  * Method: `get_view_state(self)`
    *Return current zoom level and center point.*
  * Method: `set_view_state(self, state)`
    *Restore view state.*
    *----------------------------------------*

--------------------


## 📂 Directory: `Root Directory`

### 📄 [# DIRECTORY: pixel_refine_desktop/enhance_stack/models](file:///e:/APP%20Developer/Pixel%20Refine/# DIRECTORY: pixel_refine_desktop/enhance_stack/models)


--------------------


## 📂 Directory: `Root Directory`

### 📄 [algorithm_config_model.py](file:///e:/APP%20Developer/Pixel%20Refine/pixel_refine_desktop/enhance_stack/models/algorithm_config_model.py)

* **File Overview**:
    *Algorithm configuration model.*
    *Represents algorithm settings and parameters.*

* **Class**: `AlgorithmType`
    *Algorithm types.*

* **Class**: `AlgorithmConfig`
    *Data model for algorithm configuration.*
    *Stores algorithm selection and parameters.*
  * Method: `__init__(self, algorithm_type, algorithm_name, parameters)`
    *Initialize algorithm configuration.*
    *Args:*
    *algorithm_type: Type of algorithm*
    *algorithm_name: Name of the algorithm*
    *parameters: Algorithm parameters*
  * Method: `get_parameter(self, key, default)`
    *Get a parameter value.*
    *Args:*
    *key: Parameter name*
    *default: Default value if not found*
    *Returns:*
    *Parameter value or default*
  * Method: `set_parameter(self, key, value)`
    *Set a parameter value.*
    *Args:*
    *key: Parameter name*
    *value: Parameter value*
  * Method: `validate(self)`
    *Validate configuration.*
    *Returns:*
    *Tuple of (is_valid, error_message)*
  * Method: `to_dict(self)`
    *Convert to dictionary.*
    *Returns:*
    *Dictionary representation*
  * Method: `from_dict(cls, data)`
    *Create from dictionary.*
    *Args:*
    *data: Dictionary with config data*
    *Returns:*
    *AlgorithmConfig instance*
  * Method: `__repr__(self)`
    *----------------------------------------*

--------------------

### 📄 [algorithm_list.py](file:///e:/APP%20Developer/Pixel%20Refine/pixel_refine_desktop/enhance_stack/models/algorithm_list.py)

* **Function**: `get_algorithm_names(category)`
    *Mengembalikan daftar nama algoritma untuk kategori tertentu.*

* **Function**: `get_algorithm_descriptions(category)`
    *Mengembalikan daftar deskripsi algoritma untuk kategori tertentu.*

* **Function**: `get_algorithm_options(category)`
    *Mengembalikan daftar tuple (nama, deskripsi) untuk kategori tertentu.*

* **Function**: `get_category_display_name(category)`
    *Mengembalikan nama tampilan untuk kategori tertentu.*
    *----------------------------------------*

--------------------

### 📄 [batch_model.py](file:///e:/APP%20Developer/Pixel%20Refine/pixel_refine_desktop/enhance_stack/models/batch_model.py)

* **File Overview**:
    *Batch data model.*
    *Represents a batch entity with images and validation.*

* **Class**: `BatchModel`
    *Data model for a batch.*
    *Manages batch data, images, and reference image.*
  * Method: `__init__(self, id, name, images)`
    *Initialize batch model.*
    *Args:*
    *id: Database ID (None for new batches)*
    *name: Batch name*
    *images: List of ImageModel instances*
  * Method: `reference_image(self)`
    *Get the reference image for this batch.*
  * Method: `image_count(self)`
    *Get number of images in batch.*
  * Method: `has_reference(self)`
    *Check if batch has a reference image.*
  * Method: `add_image(self, image)`
    *Add an image to the batch.*
    *Args:*
    *image: ImageModel to add*
  * Method: `remove_image(self, image)`
    *Remove an image from the batch.*
    *Args:*
    *image: ImageModel to remove*
    *Returns:*
    *True if removed, False if not found*
  * Method: `set_reference(self, image)`
    *Set an image as the reference.*
    *Args:*
    *image: ImageModel to set as reference*
    *Returns:*
    *True if successful, False if image not in batch*
  * Method: `get_image_paths(self)`
    *Get list of all image paths.*
    *Returns:*
    *List of image file paths*
  * Method: `validate(self)`
    *Validate batch data.*
    *Returns:*
    *Tuple of (is_valid, error_message)*
  * Method: `to_dict(self)`
    *Convert to dictionary.*
    *Returns:*
    *Dictionary representation*
  * Method: `from_dict(cls, data)`
    *Create from dictionary.*
    *Args:*
    *data: Dictionary with batch data*
    *Returns:*
    *BatchModel instance*
  * Method: `__repr__(self)`
  * Method: `__eq__(self, other)`
  * Method: `__hash__(self)`
    *----------------------------------------*

--------------------

### 📄 [image_model.py](file:///e:/APP%20Developer/Pixel%20Refine/pixel_refine_desktop/enhance_stack/models/image_model.py)

* **File Overview**:
    *Image data model.*
    *Represents an image entity with validation.*

* **Class**: `ImageModel`
    *Data model for an image.*
    *Provides validation and serialization.*
  * Method: `__init__(self, id, path, is_reference)`
    *Initialize image model.*
    *Args:*
    *id: Database ID (None for new images)*
    *path: File path*
    *is_reference: Whether this is a reference image*
  * Method: `exists(self)`
    *Check if image file exists on disk.*
  * Method: `filename(self)`
    *Get filename without path.*
  * Method: `extension(self)`
    *Get file extension.*
  * Method: `validate(self)`
    *Validate image data.*
    *Returns:*
    *Tuple of (is_valid, error_message)*
  * Method: `to_dict(self)`
    *Convert to dictionary.*
    *Returns:*
    *Dictionary representation*
  * Method: `from_dict(cls, data)`
    *Create from dictionary.*
    *Args:*
    *data: Dictionary with image data*
    *Returns:*
    *ImageModel instance*
  * Method: `from_db_row(cls, row)`
    *Create from database row.*
    *Args:*
    *row: Tuple from database query (id, path) or (id, path, is_reference)*
    *Returns:*
    *ImageModel instance*
  * Method: `__repr__(self)`
  * Method: `__eq__(self, other)`
  * Method: `__hash__(self)`
    *----------------------------------------*

--------------------


## 📂 Directory: `Root Directory`

### 📄 [# DIRECTORY: pixel_refine_desktop/enhance_stack/models/data_access](file:///e:/APP%20Developer/Pixel%20Refine/# DIRECTORY: pixel_refine_desktop/enhance_stack/models/data_access)


--------------------


## 📂 Directory: `Root Directory`

### 📄 [base_repository.py](file:///e:/APP%20Developer/Pixel%20Refine/pixel_refine_desktop/enhance_stack/models/data_access/base_repository.py)

* **File Overview**:
    *Base repository class for database operations.*
    *Provides common database connection and transaction management.*

* **Class**: `BaseRepository`
    *Base class for all repositories.*
    *Provides database connection management and common operations.*
  * Method: `__init__(self, db_path)`
    *Initialize repository with database path.*
    *Args:*
    *db_path: Path to SQLite database file*
  * Method: `get_connection(self)`
    *Context manager for database connections.*
    *Automatically handles connection cleanup and enables foreign keys.*
    *Yields:*
    *sqlite3.Connection: Database connection*
    *Example:*
    *with self.get_connection() as conn:*
    *cursor = conn.cursor()*
    *cursor.execute("SELECT * FROM images")*
  * Method: `get_cursor(self, commit)`
    *Context manager for database cursor with automatic commit.*
    *Args:*
    *commit: Whether to commit changes automatically (default: True)*
    *Yields:*
    *sqlite3.Cursor: Database cursor*
    *Example:*
    *with self.get_cursor() as cursor:*
    *cursor.execute("INSERT INTO images (path) VALUES (?)", (path,))*
  * Method: `execute_query(self, query, params, fetch_one)`
  * Method: `execute_query(self, query, params, fetch_one)`
  * Method: `execute_query(self, query, params, fetch_one)`
  * Method: `execute_query(self, query, params, fetch_one)`
    *Execute a SELECT query and return results.*
    *Args:*
    *query: SQL query string*
    *params: Query parameters*
    *fetch_one: If True, return only first result*
    *Returns:*
    *Single row (if fetch_one=True) or list of rows*
  * Method: `execute_update(self, query, params)`
    *Execute an INSERT, UPDATE, or DELETE query.*
    *Args:*
    *query: SQL query string*
    *params: Query parameters*
    *Returns:*
    *Number of affected rows or last inserted row ID*
  * Method: `execute_many(self, query, params_list)`
    *Execute a query multiple times with different parameters.*
    *Args:*
    *query: SQL query string*
    *params_list: List of parameter tuples*
    *Returns:*
    *Number of affected rows*
  * Method: `table_exists(self, table_name)`
    *Check if a table exists in the database.*
    *Args:*
    *table_name: Name of the table*
    *Returns:*
    *True if table exists, False otherwise*
  * Method: `column_exists(self, table_name, column_name)`
    *Check if a column exists in a table.*
    *Args:*
    *table_name: Name of the table*
    *column_name: Name of the column*
    *Returns:*
    *True if column exists, False otherwise*
  * Method: `add_column_if_not_exists(self, table_name, column_name, column_def)`
    *Add a column to a table if it doesn't exist.*
    *Args:*
    *table_name: Name of the table*
    *column_name: Name of the column to add*
    *column_def: Column definition (e.g., "INTEGER NOT NULL DEFAULT 0")*
    *Returns:*
    *True if column was added, False if it already existed*
    *----------------------------------------*

--------------------

### 📄 [batch_repository.py](file:///e:/APP%20Developer/Pixel%20Refine/pixel_refine_desktop/enhance_stack/models/data_access/batch_repository.py)

* **File Overview**:
    *Batch repository for batch-related database operations.*
    *Handles CRUD operations for batch_process and batch_process_image tables.*

* **Class**: `BatchRepository`
    *Repository for batch data access.*
    *Handles all database operations related to batches.*
  * Method: `__init__(self, db_path)`
  * Method: `create(self, batch_name)`
    *Create a new batch.*
    *Args:*
    *batch_name: Unique name for the batch*
    *Returns:*
    *Batch ID if successful, None if batch name already exists*
  * Method: `get_by_id(self, batch_id)`
    *Get batch by ID.*
    *Args:*
    *batch_id: Batch ID*
    *Returns:*
    *Tuple of (id, batch_name) or None*
  * Method: `get_id_by_name(self, batch_name)`
    *Get batch ID by name.*
    *Args:*
    *batch_name: Batch name*
    *Returns:*
    *Batch ID or None if not found*
  * Method: `get_all(self)`
    *Get all batches.*
    *Returns:*
    *List of tuples (id, batch_name)*
  * Method: `update_batch_order(self, batch_ids)`
    *Update order_index for a list of batches.*
  * Method: `delete(self, batch_id)`
    *Delete batch by ID.*
    *Associated images in batch_process_image will be deleted automatically (CASCADE).*
    *Args:*
    *batch_id: Batch ID to delete*
    *Returns:*
    *Number of rows deleted*
  * Method: `update_name(self, batch_id, new_name)`
    *Update the name of a batch.*
    *Args:*
    *batch_id: The ID of the batch to update.*
    *new_name: The new name for the batch.*
    *Returns:*
    *Number of rows updated (should be 1 on success).*
  * Method: `add_images(self, batch_id, image_paths)`
    *Add multiple images to a batch using optimized bulk operations.*
    *Args:*
    *batch_id: Batch ID*
    *image_paths: List of image file paths*
    *Returns:*
    *Number of images successfully added*
  * Method: `remove_images(self, batch_id, image_paths)`
    *Remove images from a batch using optimized bulk deletion.*
    *Args:*
    *batch_id: Batch ID*
    *image_paths: List of image file paths to remove*
    *Returns:*
    *Number of images removed*
  * Method: `get_batch_images(self, batch_id)`
    *Get all images in a batch.*
    *Args:*
    *batch_id: Batch ID*
    *Returns:*
    *List of tuples (image_id, path, is_reference)*
  * Method: `set_reference_image(self, batch_id, image_path)`
    *Set an image as the reference for a batch.*
    *Args:*
    *batch_id: Batch ID*
    *image_path: Path of image to set as reference*
    *Returns:*
    *True if successful, False otherwise*
  * Method: `get_reference_image(self, batch_id)`
    *Get the reference image for a batch.*
    *Args:*
    *batch_id: Batch ID*
    *Returns:*
    *Tuple of (image_id, path) or None if no reference set*
  * Method: `is_image_in_batch(self, batch_id, image_id)`
    *Check if an image is in a batch.*
    *Args:*
    *batch_id: Batch ID*
    *image_id: Image ID*
    *Returns:*
    *True if image is in batch, False otherwise*
  * Method: `is_reference_image(self, batch_id, image_id)`
    *Check if an image is the reference for a batch.*
    *Args:*
    *batch_id: Batch ID*
    *image_id: Image ID*
    *Returns:*
    *True if image is reference, False otherwise*
  * Method: `has_reference_image(self, batch_id)`
    *Check if a batch has a reference image set.*
    *Args:*
    *batch_id: Batch ID*
    *Returns:*
    *True if batch has reference, False otherwise*
  * Method: `_set_new_reference(self, batch_id)`
    *Set a new reference image for a batch (internal method).*
    *Called when the current reference is removed.*
    *Args:*
    *batch_id: Batch ID*
  * Method: `count(self)`
    *Get total number of batches.*
    *Returns:*
    *Number of batches in database*
  * Method: `count_images_in_batch(self, batch_id)`
    *Get number of images in a batch.*
    *Args:*
    *batch_id: Batch ID*
    *Returns:*
    *Number of images in the batch*
    *----------------------------------------*

--------------------

### 📄 [image_repository.py](file:///e:/APP%20Developer/Pixel%20Refine/pixel_refine_desktop/enhance_stack/models/data_access/image_repository.py)

* **File Overview**:
    *Image repository for image-related database operations.*
    *Handles CRUD operations for images table.*

* **Class**: `ImageRepository`
    *Repository for image data access.*
    *Handles all database operations related to images.*
  * Method: `get_or_create(self, path)`
    *Get existing image ID or create new image record.*
    *Args:*
    *path: Image file path*
    *Returns:*
    *Image ID*
  * Method: `get_by_id(self, image_id)`
    *Get image by ID.*
    *Args:*
    *image_id: Image ID*
    *Returns:*
    *Tuple of (id, path) or None if not found*
  * Method: `get_by_path(self, path)`
    *Get image by path.*
    *Args:*
    *path: Image file path*
    *Returns:*
    *Tuple of (id, path) or None if not found*
  * Method: `get_all(self)`
    *Get all images.*
    *Returns:*
    *List of tuples (id, path)*
  * Method: `delete(self, image_id)`
    *Delete image by ID.*
    *Args:*
    *image_id: Image ID to delete*
    *Returns:*
    *Number of rows deleted*
  * Method: `delete_by_path(self, path)`
    *Delete image by path.*
    *Args:*
    *path: Image file path*
    *Returns:*
    *Number of rows deleted*
  * Method: `exists(self, path)`
    *Check if image exists in database.*
    *Args:*
    *path: Image file path*
    *Returns:*
    *True if exists, False otherwise*
  * Method: `count(self)`
    *Get total number of images.*
    *Returns:*
    *Number of images in database*
    *----------------------------------------*

--------------------

### 📄 [panorama_repository.py](file:///e:/APP%20Developer/Pixel%20Refine/pixel_refine_desktop/enhance_stack/models/data_access/panorama_repository.py)

* **File Overview**:
    *Panorama repository for panorama project database operations.*
    *Handles CRUD operations for panorama_projects and panorama_project_images tables.*

* **Class**: `PanoramaRepository`
    *Repository for panorama project data access.*
    *Handles all database operations related to panorama projects.*
  * Method: `__init__(self, db_path)`
  * Method: `create_project(self, name)`
    *Create a new panorama project.*
    *Args:*
    *name: Project name*
    *Returns:*
    *Project ID if successful, None if name already exists*
  * Method: `get_project(self, project_id)`
    *Get panorama project by ID.*
    *Args:*
    *project_id: Project ID*
    *Returns:*
    *Tuple of (id, name, created_at) or None*
  * Method: `get_all_projects(self)`
    *Get all panorama projects.*
    *Returns:*
    *List of tuples (id, name, created_at)*
  * Method: `delete_project(self, project_id)`
    *Delete panorama project.*
    *Associated images will be unlinked automatically (CASCADE).*
    *Args:*
    *project_id: Project ID*
    *Returns:*
    *True if successful, False otherwise*
  * Method: `rename_project(self, project_id, new_name)`
    *Rename a panorama project.*
    *Args:*
    *project_id: Project ID*
    *new_name: New project name*
    *Returns:*
    *True if successful, False otherwise*
  * Method: `add_images(self, project_id, image_paths)`
    *Add images to a panorama project.*
    *Args:*
    *project_id: Project ID*
    *image_paths: List of image file paths*
    *Returns:*
    *True if successful, False otherwise*
  * Method: `remove_images(self, project_id, image_paths)`
    *Remove images from a panorama project.*
    *Args:*
    *project_id: Project ID*
    *image_paths: List of image file paths to remove*
    *Returns:*
    *True if successful, False otherwise*
  * Method: `get_project_images(self, project_id)`
    *Get all image paths for a project.*
    *Args:*
    *project_id: Project ID*
    *Returns:*
    *List of image file paths*
  * Method: `get_workflow_settings(self, project_id)`
    *Get workflow settings for a project.*
    *Args:*
    *project_id: Project ID*
    *Returns:*
    *Dictionary of settings or None if project not found*
  * Method: `save_workflow_setting(self, project_id, setting_key, setting_value)`
    *Save a single workflow setting for a project.*
    *Args:*
    *project_id: Project ID*
    *setting_key: Setting name (must be in allowed list)*
    *setting_value: Setting value*
    *Returns:*
    *True if successful, False otherwise*
    *----------------------------------------*

--------------------

### 📄 [thumbnail_repository.py](file:///e:/APP%20Developer/Pixel%20Refine/pixel_refine_desktop/enhance_stack/models/data_access/thumbnail_repository.py)

* **Class**: `ThumbnailRepository`
    *Repository for storing and retrieving thumbnails as physical files.*
    *Uses SHA-1 hashing of the image path for unique, file-system safe names.*
  * Method: `__init__(self, cache_dir)`
  * Method: `_get_hash_path(self, image_path)`
    *Konversi path gambar menjadi path cache unik via SHA-1.*
  * Method: `get_thumbnail(self, image_path)`
    *Load thumbnail dari file sistem.*
  * Method: `get_thumbnails_bulk(self, image_paths)`
    *Muat banyak thumbnail sekaligus dari disk.*
    *Returns a dict of {path: QImage}*
  * Method: `save_thumbnail(self, image_path, q_image)`
    *Simpan satu thumbnail ke disk sebagai JPG.*
  * Method: `save_thumbnails_bulk(self, thumbnail_data)`
    *Simpan banyak thumbnail sekaligus.*
    *thumbnail_data: list of (image_path, q_image)*
  * Method: `delete_thumbnails(self, image_paths)`
    *Hapus file cache untuk gambar yang dihapus.*
  * Method: `execute_query(self)`
  * Method: `execute_update(self)`
  * Method: `execute_many(self)`
    *----------------------------------------*

--------------------


## 📂 Directory: `Root Directory`

### 📄 [# DIRECTORY: pixel_refine_desktop/enhance_stack/views](file:///e:/APP%20Developer/Pixel%20Refine/# DIRECTORY: pixel_refine_desktop/enhance_stack/views)


--------------------


## 📂 Directory: `Root Directory`

### 📄 [batch_page_view.py](file:///e:/APP%20Developer/Pixel%20Refine/pixel_refine_desktop/enhance_stack/views/batch_page_view.py)

* **File Overview**:
    *Batch Page View (MVC Hybrid).*
    *Wraps legacy BatchPageLayout while connecting to MVC controllers.*

* **Class**: `BatchPageView`
    *Batch page view with MVC architecture.*
    *Wraps legacy BatchPageLayout but connects to controllers for business logic.*
  * Method: `__init__(self, db_path, parent)`
  * Method: `setup_ui(self)`
    *Setup UI using V2 Layout.*
  * Method: `connect_controller_signals(self)`
    *Connect controller signals to view updates.*
  * Method: `handle_batch_import_button(self)`
    *Handle batch import button.*
  * Method: `handle_delete_all_batches(self)`
    *Handle delete all batches.*
  * Method: `process_all_batches(self)`
    *Handle process all batches.*
  * Method: `_on_batch_created(self, batch_id, batch_name)`
    *Handle batch creation.*
  * Method: `_on_batch_updated(self, batch_id)`
    *Handle batch update.*
  * Method: `_on_batch_deleted(self, batch_id)`
    *Handle batch deletion.*
  * Method: `_on_batch_error(self, error)`
    *Handle batch error.*
  * Method: `_on_workflow_completed(self, result_path)`
    *Handle workflow completion.*
  * Method: `_on_workflow_error(self, error)`
    *Handle workflow error.*
  * Method: `_on_data_changed(self)`
    *Handle data changed from legacy layout.*
    *----------------------------------------*

--------------------

### 📄 [enhance_stack_view.py](file:///e:/APP%20Developer/Pixel%20Refine/pixel_refine_desktop/enhance_stack/views/enhance_stack_view.py)

* **File Overview**:
    *Enhanced Stack Page View (MVC Refactored).*
    *Main container for single and batch page views with controller integration.*

* **Class**: `EnhanceStackView`
    *Main view for enhance stack feature (MVC Architecture).*
    *Manages single and batch page views with controllers.*
  * Method: `__init__(self, db_path, parent)`
  * Method: `setup_ui(self)`
    *Setup the UI layout.*
  * Method: `connect_signals(self)`
    *Connect top bar signals and toast notifications.*
  * Method: `_handle_switch_request(self)`
    *Handle switch between single and batch pages.*
    *----------------------------------------*

--------------------

### 📄 [single_page_view.py](file:///e:/APP%20Developer/Pixel%20Refine/pixel_refine_desktop/enhance_stack/views/single_page_view.py)

* **File Overview**:
    *Single Page View (MVC Hybrid).*
    *Reuses legacy UI components while connecting to MVC controllers.*

* **Class**: `SinglePageView`
    *Single page view with MVC architecture.*
    *Inherits from BatchPageV2Layout to reuse all UI and functionality.*
    *This is a pragmatic hybrid approach for complex refactoring.*
  * Method: `__init__(self, db_path, parent)`
  * Method: `connect_controller_signals(self)`
    *Connect MVC controller signals to view updates.*
    *----------------------------------------*

--------------------

### 📄 [top_bar.py](file:///e:/APP%20Developer/Pixel%20Refine/pixel_refine_desktop/enhance_stack/views/top_bar.py)

* **Class**: `TopBar`
    *Top bar dengan QGridLayout untuk menjaga tombol switch tetap di tengah.*
  * Method: `__init__(self)`
  * Method: `switch_stacks_to_index(self, index)`
    *Memberi tahu EnhanceStackPage untuk memulai transisi pada stack ini.*
    *----------------------------------------*

--------------------


## 📂 Directory: `Root Directory`

### 📄 [# DIRECTORY: pixel_refine_desktop/ui](file:///e:/APP%20Developer/Pixel%20Refine/# DIRECTORY: pixel_refine_desktop/ui)


--------------------


## 📂 Directory: `Root Directory`

### 📄 [PanoramaGenericPage.py](file:///e:/APP%20Developer/Pixel%20Refine/pixel_refine_desktop/ui/PanoramaGenericPage.py)

* **Class**: `PanoramaGenericPage`
  * Method: `__init__(self, database_manager, parent)`
  * Method: `_setup_controller_logic(self)`
  * Method: `_on_item_selected(self, item_id, label)`
  * Method: `_on_selection_cleared(self)`
  * Method: `_on_process(self, data)`
  * Method: `_populate_dummy_data(self)`
    *----------------------------------------*

--------------------


## 📂 Directory: `Root Directory`

### 📄 [# DIRECTORY: pixel_refine_desktop/ui/components/common](file:///e:/APP%20Developer/Pixel%20Refine/# DIRECTORY: pixel_refine_desktop/ui/components/common)


--------------------


## 📂 Directory: `Root Directory`

### 📄 [progress_panel.py](file:///e:/APP%20Developer/Pixel%20Refine/pixel_refine_desktop/ui/components/common/progress_panel.py)

* **File Overview**:
    *Progress Panel - Reusable progress bar widget.*
    *Can be used across different pages for showing operation progress.*

* **Class**: `ProgressPanel`
    *Reusable progress panel with progress bar, status label, and optional cancel button.*
  * Method: `__init__(self, parent)`
  * Method: `setup_ui(self)`
    *Setup the UI components.*
  * Method: `update_progress(self, value, message, remaining)`
    *Update progress display.*
    *Args:*
    *value: Progress value (0-100)*
    *message: Status message*
    *remaining: Number of items remaining (-1 to hide)*
  * Method: `reset(self)`
    *Reset progress to initial state.*
  * Method: `set_cancelable(self, cancelable)`
    *Enable or disable cancel button.*
    *Args:*
    *cancelable: Whether operation can be canceled*
    *----------------------------------------*

--------------------

### 📄 [sidebar.py](file:///e:/APP%20Developer/Pixel%20Refine/pixel_refine_desktop/ui/components/common/sidebar.py)

* **File Overview**:
    *Reusable Sidebar Component (MVC).*
    *100% identical to legacy UI/sidebar.py with all features, animations, and styling.*

* **Class**: `Sidebar`
    *Reusable sidebar component with expand/collapse animation.*
    *Identical to legacy sidebar but accepts dynamic pages configuration.*
  * Method: `__init__(self, pages, parent)`
    *Initialize sidebar.*
    *Args:*
    *pages: List of tuples (name, icon_path) for all pages*
    *Settings will automatically be placed at bottom*
    *parent: Parent widget*
  * Method: `_create_ui(self)`
    *Create sidebar UI elements.*
  * Method: `create_nav_button(self, text, icon_path, index)`
    *Create a navigation button with icon only and tooltip.*
  * Method: `_handle_nav_click(self, index)`
    *Handle navigation button click.*
    *Updates button states and emits page_changed signal.*
  * Method: `toggle_sidebar(self)`
    *Toggle sidebar expand/collapse with animation.*
    *Note: Since sidebar is now icon-only, this mainly handles the toggle signal.*
  * Method: `set_current_page(self, index)`
    *Set the current active page.*
    *Updates button checked states.*
    *----------------------------------------*

--------------------

### 📄 [splash_screen.py](file:///e:/APP%20Developer/Pixel%20Refine/pixel_refine_desktop/ui/components/common/splash_screen.py)

* **File Overview**:
    *Custom splash screen component with progress indicator.*

* **Class**: `SplashScreen`
    *Custom splash screen that displays an image, circular progress indicator,*
    *and status label.*
  * Method: `__init__(self, pixmap, version_string, flags)`
    *Initialize splash screen.*
    *Args:*
    *pixmap: Image to display on splash screen*
    *version_string: Version text to display*
    *flags: Window flags*
  * Method: `update_status(self, message, value)`
    *Update progress indicator and status message.*
    *Args:*
    *message: Status message to display*
    *value: Progress value (0-100)*
    *----------------------------------------*

--------------------


## 📂 Directory: `Root Directory`

### 📄 [# DIRECTORY: pixel_refine_desktop/ui/resources/animations](file:///e:/APP%20Developer/Pixel%20Refine/# DIRECTORY: pixel_refine_desktop/ui/resources/animations)


--------------------


## 📂 Directory: `Root Directory`

### 📄 [animation_manager.py](file:///e:/APP%20Developer/Pixel%20Refine/pixel_refine_desktop/ui/resources/animations/animation_manager.py)

* **Class**: `AnimationType`

* **Class**: `SlideDirection`

* **Class**: `StackedWidgetAnimator`
    *Animator yang TAHAN BANTING dan SELF-HEALING untuk QStackedWidget.*
    *Dirancang untuk menangani penghapusan widget di tengah animasi dengan aman.*
    *PLUS: Anti-QPainter Error dengan throttling dan safe grab.*
  * Method: `__init__(self, parent)`
  * Method: `_on_animator_destroyed(self)`
    *Final cleanup of all ghosts when animator is destroyed.*
  * Method: `stop_for_widget(self, widget)`
    *Public method to stop animations for a specific widget and delete its ghost.*
  * Method: `_safe_grab(self, widget, max_retries)`
    *Safely grab widget pixmap dengan retry mechanism.*
    *Returns (pixmap, geometry) tuple atau (None, None) jika gagal.*
  * Method: `_direct_fade_out(self, widget, duration, curve, on_finished_callback)`
    *Fallback animasi fade-out TANPA grab (direct opacity).*
    *Digunakan ketika grab() gagal atau untuk mencegah QPainter error.*
  * Method: `_can_start_animation(self)`
    *Check apakah masih bisa start animasi baru (throttle check).*
  * Method: `_process_animation_queue(self)`
    *Process queued animations jika ada slot tersedia.*
  * Method: `transition_out(self, widget, duration, curve, on_finished_callback)`
    *Animator fade-out mandiri yang aman dengan throttling dan queue.*
  * Method: `_execute_transition_out(self, widget, duration, curve, on_finished_callback)`
    *Internal executor untuk transition_out dengan safe grab dan fallback.*
  * Method: `transition_in(self, stack_widget, target, animation_type, duration_out, duration_in, curve_out, curve_in, on_mid_transition)`
  * Method: `_is_animating(self, stack_widget)`
    *Periksa apakah ada animasi yang sedang berlangsung di QStackedWidget.*
  * Method: `_clear_animation_state(self, stack_widget)`
    *Hapus state animasi untuk QStackedWidget tertentu (melepas kunci).*
  * Method: `stop_all(self)`
    *Hentikan semua animasi transisi di semua stacked widget.*
  * Method: `_reset_widget_state(self, widget, visible)`
    *Atur ulang properti visual widget dengan aman.*
  * Method: `_validate_target(self, stack_widget, target)`
  * Method: `_create_outgoing_geometry_animation(self, widget, anim_type, duration, curve)`
  * Method: `_create_incoming_geometry_animation(self, widget, anim_type, duration, curve)`
  * Method: `_on_animation_out_finished(self, stack_widget_ref)`
  * Method: `_start_incoming_animation(self, stack_widget, new_widget, data)`
  * Method: `_on_animation_in_finished(self, stack_widget_ref)`
  * Method: `_interrupt_transition(self, stack_widget)`
  * Method: `show_widget(self, widget, animation_type, duration, curve, offset)`
  * Method: `_setup_opacity_effect(self, widget, initial_opacity)`
  * Method: `_calculate_offset_pos(self, base_pos, anim_type, offset)`
  * Method: `_safe_remove_effect(self, widget)`
    *Safely remove graphics effect on the next event loop cycle.*
  * Method: `animate_list_reorder(self, list_widget, start_idx, target_idx, duration, start_delay, overlay_to_remove)`
    *Animate a cascading reorder in a QListWidget.*
    *Shows ghosts immediately to cover the UI 'jump', then animates movement.*

* **Class**: `WidgetLifecycleAnimator`
    *Animator khusus untuk siklus hidup widget (Delete/Remove).*
    *Memisahkan logika 'penghancuran' dari logika navigasi StackedWidget.*
  * Method: `__init__(self, parent)`
  * Method: `_safe_grab(self, widget, max_retries)`
    *Safely grab widget pixmap.*
  * Method: `animate_delete(self, widget, duration, use_drop_effect, drop_distance, on_finished_callback)`
  * Method: `stop_all(self)`
    *Hentikan paksa semua animasi yang sedang berjalan.*

* **Class**: `WidthAnimator`
  * Method: `__init__(self, parent)`
  * Method: `animate_width(self, target, end_width, duration, curve)`

* **Class**: `HeightAnimator`
  * Method: `__init__(self, parent)`
  * Method: `animate_height(self, target, end_height, duration, curve)`
  * Method: `_set_flex_height(self, widget, height)`
    *----------------------------------------*

--------------------

### 📄 [delete.py](file:///e:/APP%20Developer/Pixel%20Refine/pixel_refine_desktop/ui/resources/animations/delete.py)

* **Function**: `delete(widget, animator, duration, drop_distance, on_finished_callback)`
    *Menghapus widget dengan efek 'Runtuh/Jatuh'.*
    *Logic didelegasikan sepenuhnya ke animation_manager.WidgetLifecycleAnimator.*
    *Args:*
    *widget: Widget target.*
    *animator: Instance WidgetLifecycleAnimator (opsional).*
    *duration: Durasi total animasi (ms).*
    *drop_distance: Seberapa jauh widget 'jatuh' ke bawah (px).*
    *on_finished_callback: Fungsi yang dipanggil sebelum widget dimusnahkan.*
    *----------------------------------------*

--------------------

### 📄 [fade.py](file:///e:/APP%20Developer/Pixel%20Refine/pixel_refine_desktop/ui/resources/animations/fade.py)

* **Function**: `fade_in(animator, target_widget, stack_widget, duration, skip_animation_if_not_visible)`
    *Melakukan transisi FADE.*
    *- Jika 'stack_widget' diisi: Melakukan transisi halaman stack.*
    *- Jika 'stack_widget' None: Melakukan fade-in pada 'target_widget' biasa.*
    *OPTIMIZED: Fast-path untuk durasi sangat pendek (< 10ms).*
    *SMART: Skip animation jika skip_animation_if_not_visible=True (untuk viewport optimization).*

* **Function**: `fade_out(animator, widget, duration, curve, on_finished_callback, hide_on_finish)`
    *Memulai animasi fade-out.*
    *Args:*
    *hide_on_finish (bool): Jika True, widget akan di-hide() setelah animasi selesai.*
    *Sangat penting untuk widget biasa agar tidak memblokir mouse.*
    *OPTIMIZED: Fast-path untuk durasi sangat pendek (< 10ms).*
    *----------------------------------------*

--------------------

### 📄 [slide.py](file:///e:/APP%20Developer/Pixel%20Refine/pixel_refine_desktop/ui/resources/animations/slide.py)

* **Function**: `slide(animator, stack_widget, target, direction, duration, curve, on_mid_transition)`
    *Melakukan transisi SLIDE + FADE.*
    *----------------------------------------*

--------------------

### 📄 [zoom.py](file:///e:/APP%20Developer/Pixel%20Refine/pixel_refine_desktop/ui/resources/animations/zoom.py)

* **Function**: `zoom(animator, stack_widget, target, duration)`
    *Melakukan transisi ZOOM + FADE.*
    *----------------------------------------*

--------------------


## 📂 Directory: `Root Directory`

### 📄 [# DIRECTORY: pixel_refine_desktop/ui/resources/animations/loading](file:///e:/APP%20Developer/Pixel%20Refine/# DIRECTORY: pixel_refine_desktop/ui/resources/animations/loading)


--------------------


## 📂 Directory: `Root Directory`

### 📄 [circular_progress.py](file:///e:/APP%20Developer/Pixel%20Refine/pixel_refine_desktop/ui/resources/animations/loading/circular_progress.py)

* **Class**: `CircularProgress`
    *Widget kustom untuk menampilkan progress bar berbentuk lingkaran.*
  * Method: `__init__(self, parent)`
  * Method: `setValue(self, value)`
  * Method: `value(self)`
  * Method: `paintEvent(self, event)`
    *----------------------------------------*

--------------------

### 📄 [modern_progress_bar.py](file:///e:/APP%20Developer/Pixel%20Refine/pixel_refine_desktop/ui/resources/animations/loading/modern_progress_bar.py)

* **Class**: `ModernProgressBar`
    *Widget progress bar kustom yang disederhanakan menjadi HANYA satu baris.*
  * Method: `__init__(self, parent)`
  * Method: `setBarColor(self, color)`
    *Mengatur warna untuk bar foreground (progress).*
  * Method: `setValue(self, value)`
    *Mengatur nilai progres utama (0-100).*
  * Method: `value(self)`
  * Method: `paintEvent(self, event)`
    *----------------------------------------*

--------------------


## 📂 Directory: `Root Directory`

### 📄 [# DIRECTORY: pixel_refine_desktop/ui/resources/animations/toast](file:///e:/APP%20Developer/Pixel%20Refine/# DIRECTORY: pixel_refine_desktop/ui/resources/animations/toast)


--------------------


## 📂 Directory: `Root Directory`

### 📄 [toast_manager.py](file:///e:/APP%20Developer/Pixel%20Refine/pixel_refine_desktop/ui/resources/animations/toast/toast_manager.py)

* **Class**: `ToastPosition`

* **Class**: `ToastAnimation`

* **Class**: `ToastPriority`

* **Class**: `ToastWidget`
  * Method: `__init__(self, message, priority, category, parent)`
  * Method: `text(self)`
  * Method: `setText(self, text)`
  * Method: `set_blinking(self, active)`

* **Class**: `ToastManager`
  * Method: `__init__(self, parent)`
  * Method: `parent_widget(self)`
  * Method: `show_message(self, message, duration, position, animation, priority, category, single_mode)`
    *Menampilkan pesan toast baru.*
    *Allowed priorities: "URGENT", "HIGH", "NORMAL", "LOW"*
    *Args:*
    *category: ID unik (string) untuk identifikasi toast ini agar bisa di-update (reusable).*
    *Jika None, dianggap toast transient (sekali lewat).*
  * Method: `show_progress(self, message, category, position, animation, priority, single_mode, bypass_throttle)`
  * Method: `hide(self)`
    *Hide all or specific? Default implementation hides all for compatibility.*
  * Method: `hide_specific(self, message_substring)`
    *Hide toast containing specific text.*
  * Method: `hide_category(self, category)`
    *Hide all toasts with specific category.*
  * Method: `_add_toast(self, message, duration, position, animation, priority, category, single_mode)`
  * Method: `_remove_toast(self, toast)`
  * Method: `_reposition_toasts(self)`
    *Mengatur ulang posisi semua toast berdasarkan urutan di list.*
    *----------------------------------------*

--------------------


## 📂 Directory: `Root Directory`

### 📄 [# DIRECTORY: pixel_refine_desktop/ui/resources/GenericUILibrary](file:///e:/APP%20Developer/Pixel%20Refine/# DIRECTORY: pixel_refine_desktop/ui/resources/GenericUILibrary)


--------------------


## 📂 Directory: `Root Directory`

### 📄 [buttons.py](file:///e:/APP%20Developer/Pixel%20Refine/pixel_refine_desktop/ui/resources/GenericUILibrary/buttons.py)

* **File Overview**:
    *Bootstrap-like Button Components for PySide6*
    *Provides reusable button components with variants and customization*

* **Class**: `Button`
    *Bootstrap-like button with variant support*
    *Variants:*
    *- primary: Main action button (green)*
    *- secondary: Secondary action (gray)*
    *- danger: Destructive action (red)*
    *- success: Success action (green)*
    *- warning: Warning action (yellow/orange)*
    *- info: Information action (blue)*
    *- light: Light background*
    *- dark: Dark background*
    *Usage:*
    *btn = Button("Click Me", variant="primary")*
    *btn.clicked.connect(on_click)*
  * Method: `__init__(self, text, variant, object_name, bg_color, text_color, hover_color, parent)`
  * Method: `_apply_custom_colors(self, bg_color, text_color, hover_color)`
    *Apply custom colors via inline stylesheet*
  * Method: `set_variant(self, variant)`
    *Change button variant dynamically*

* **Class**: `IconButton`
    *Button with icon support*
    *Usage:*
    *btn = IconButton(icon_path="path/to/icon.png", text="Save")*
    *btn = IconButton(icon=QIcon(...), text="Save")*
  * Method: `__init__(self, text, icon, icon_path, variant, text_tooltip, square_size, parent)`

* **Class**: `ButtonGroup`
    *Group of buttons arranged horizontally or vertically*
    *Usage:*
    *group = ButtonGroup(orientation="horizontal")*
    *group.add_button("Option 1")*
    *group.add_button("Option 2")*
    *group.button_clicked.connect(on_button_click)*
  * Method: `__init__(self, orientation, parent)`
  * Method: `add_button(self, text, variant, checkable)`
    *Add a button to the group*
  * Method: `get_button(self, index)`
    *Get button by index*
  * Method: `set_active(self, index)`
    *Set active button (for checkable buttons)*

* **Class**: `ToggleButton`
    *Toggle button with on/off states*
    *Usage:*
    *toggle = ToggleButton("Enable Feature")*
    *toggle.toggled.connect(on_toggle)*
  * Method: `__init__(self, text, checked, parent)`
  * Method: `_update_appearance(self, checked)`
    *Update button appearance based on state*
    *----------------------------------------*

--------------------

### 📄 [cards.py](file:///e:/APP%20Developer/Pixel%20Refine/pixel_refine_desktop/ui/resources/GenericUILibrary/cards.py)

* **File Overview**:
    *Bootstrap-like Card Components for PySide6*
    *Provides reusable card containers*

* **Class**: `Card`
    *Bootstrap-like card component with header, body, and footer*
    *Usage:*
    *card = Card(title="User Profile")*
    *card.set_body_content("Content goes here")*
    *card.add_footer_widget(save_button)*
  * Method: `__init__(self, title, bg_color, border_color, parent)`
  * Method: `set_title(self, title)`
    *Set card title*
  * Method: `add_header_widget(self, widget)`
    *Add widget to header (e.g., buttons)*
  * Method: `set_body_content(self, content)`
    *Set body content (text or widget)*
  * Method: `add_body_widget(self, widget, stretch)`
    *Add widget to body*
  * Method: `add_footer_widget(self, widget)`
    *Add widget to footer*
  * Method: `clear_body(self)`
    *Clear body content*
  * Method: `_apply_custom_colors(self, bg_color, border_color)`
    *Apply custom colors via inline stylesheet*

* **Class**: `CardHeader`
    *Card header component*
    *Usage:*
    *header = CardHeader(title="Settings")*
    *header.add_action(close_button)*
  * Method: `__init__(self, title, parent)`
  * Method: `set_title(self, title)`
    *Set header title*
  * Method: `add_action(self, widget)`
    *Add action widget (button, etc.)*

* **Class**: `CardBody`
    *Card body component*
    *Usage:*
    *body = CardBody()*
    *body.add_widget(content_widget)*
  * Method: `__init__(self, parent)`
  * Method: `add_widget(self, widget, stretch)`
    *Add widget to body*
  * Method: `set_content(self, content)`
    *Set content (text or widget)*

* **Class**: `CardFooter`
    *Card footer component*
    *Usage:*
    *footer = CardFooter()*
    *footer.add_action(save_button)*
    *footer.add_action(cancel_button)*
  * Method: `__init__(self, align, parent)`
  * Method: `add_action(self, widget)`
    *Add action widget*

* **Class**: `CardGroup`
    *Group of cards in a row*
    *Usage:*
    *group = CardGroup()*
    *group.add_card(card1)*
    *group.add_card(card2)*
  * Method: `__init__(self, spacing, parent)`
  * Method: `add_card(self, card, stretch)`
    *Add card to group*
    *----------------------------------------*

--------------------

### 📄 [collapse.py](file:///e:/APP%20Developer/Pixel%20Refine/pixel_refine_desktop/ui/resources/GenericUILibrary/collapse.py)

* **File Overview**:
    *Bootstrap-like Collapse and Accordion Components for PySide6*
    *Provides collapsible panels and accordion widgets*

* **Class**: `Collapse`
    *Collapsible panel with animation*
    *Usage:*
    *collapse = Collapse(title="Advanced Settings")*
    *collapse.set_content(settings_widget)*
    *collapse.toggled.connect(on_toggle)*
  * Method: `__init__(self, title, expanded, parent)`
  * Method: `set_title(self, title)`
    *Set collapse title*
  * Method: `set_content(self, widget)`
    *Set content widget*
  * Method: `add_widget(self, widget)`
    *Add widget to content*
  * Method: `toggle(self)`
    *Toggle collapse state*
  * Method: `expand(self)`
    *Expand panel*
  * Method: `collapse_panel(self)`
    *Collapse panel*

* **Class**: `Accordion`
    *Accordion with multiple collapsible items (only one open at a time)*
    *Usage:*
    *accordion = Accordion()*
    *accordion.add_item("Section 1", widget1)*
    *accordion.add_item("Section 2", widget2)*
    *accordion.item_expanded.connect(on_expand)*
  * Method: `__init__(self, parent)`
  * Method: `add_item(self, title, widget)`
    *Add accordion item*
  * Method: `expand_item(self, index)`
    *Expand specific item*
  * Method: `collapse_all(self)`
    *Collapse all items*
  * Method: `_on_item_toggled(self, index, expanded)`
    *Handle item toggle*

* **Class**: `AccordionItem`
    *Individual accordion item*
    *Usage:*
    *item = AccordionItem("Title", content_widget)*
    *item.toggled.connect(on_toggle)*
  * Method: `__init__(self, title, widget, parent)`
  * Method: `get_title(self)`
    *Get item title*
  * Method: `set_content(self, widget)`
    *Set content widget*
  * Method: `toggle(self)`
    *Toggle item*
  * Method: `expand(self)`
    *Expand item*
  * Method: `collapse_panel(self)`
    *Collapse item*
    *----------------------------------------*

--------------------

### 📄 [color_customization_example.py](file:///e:/APP%20Developer/Pixel%20Refine/pixel_refine_desktop/ui/resources/GenericUILibrary/color_customization_example.py)

* **File Overview**:
    *GenericUILibrary - Color Customization Example*
    *Demonstrates how to use components with:*
    *1. Default stylesheet_global_page() styling*
    *2. Optional color customization per component*

* **Class**: `ColorCustomizationExample`
    *Example showing default and customized component styling*
  * Method: `__init__(self)`
  * Method: `_create_default_example(self, container)`
    *Example 1: Components using default stylesheet*
  * Method: `_create_custom_example(self, container)`
    *Example 2: Components with custom colors*
  * Method: `_create_mixed_example(self, container)`
    *Example 3: Mix of default and custom styling*

* **Function**: `main()`
    *Run the color customization example*
    *----------------------------------------*

--------------------

### 📄 [comparison.py](file:///e:/APP%20Developer/Pixel%20Refine/pixel_refine_desktop/ui/resources/GenericUILibrary/comparison.py)

* **Class**: `ImageCompareItem`
    *Graphics Item untuk membandingkan dua gambar dengan slider.*
    *Dapat dimasukkan ke dalam QGraphicsScene sehingga mendukung Zoomable View.*
  * Method: `__init__(self, left_pixmap, right_pixmap, left_label, right_label, parent)`
  * Method: `boundingRect(self)`
  * Method: `paint(self, painter, option, widget)`
  * Method: `mousePressEvent(self, event)`
  * Method: `mouseMoveEvent(self, event)`
  * Method: `mouseReleaseEvent(self, event)`

* **Class**: `ImageCompareWidget`
    *Widget mandiri (stand-alone) untuk membandingkan dua gambar dengan slider.*
    *Gunakan ini jika Anda ingin meletakkannya langsung di layout (bukan di QGraphicsView).*
  * Method: `__init__(self, left_pixmap, right_pixmap, left_label, right_label, parent)`
  * Method: `set_images(self, left_pixmap, right_pixmap)`
    *Update gambar secara dinamis.*
  * Method: `paintEvent(self, event)`
  * Method: `mousePressEvent(self, event)`
  * Method: `mouseMoveEvent(self, event)`
  * Method: `mouseReleaseEvent(self, event)`
  * Method: `_update_slider(self, mouse_x)`
    *----------------------------------------*

--------------------

### 📄 [config_panel.py](file:///e:/APP%20Developer/Pixel%20Refine/pixel_refine_desktop/ui/resources/GenericUILibrary/config_panel.py)

* **Class**: `ConfigPanel`
  * Method: `__init__(self, parent)`
  * Method: `_on_apply(self)`
    *----------------------------------------*

--------------------

### 📄 [containers.py](file:///e:/APP%20Developer/Pixel%20Refine/pixel_refine_desktop/ui/resources/GenericUILibrary/containers.py)

* **File Overview**:
    *Bootstrap-like Container and Layout Components for PySide6*
    *Provides reusable layout containers*

* **Class**: `Container`
    *Main container with padding (like Bootstrap container)*
    *Usage:*
    *container = Container(padding=15)*
    *container.add_widget(my_widget)*
  * Method: `__init__(self, padding, fluid, parent)`
  * Method: `add_widget(self, widget, stretch)`
    *Add widget to container*
  * Method: `add_layout(self, layout, stretch)`
    *Add layout to container*
  * Method: `add_stretch(self, stretch)`
    *Add stretch space*

* **Class**: `Row`
    *Horizontal row layout (like Bootstrap row)*
    *Usage:*
    *row = Row(spacing=10)*
    *row.add_column(widget1, stretch=1)*
    *row.add_column(widget2, stretch=2)*
  * Method: `__init__(self, spacing, parent)`
  * Method: `add_column(self, widget, stretch)`
    *Add a column (widget) to the row*
  * Method: `add_stretch(self, stretch)`
    *Add stretch space*

* **Class**: `Col`
    *Column widget (like Bootstrap col)*
    *Usage:*
    *col = Col(span=6)  # Half width (out of 12)*
    *col.add_widget(my_widget)*
  * Method: `__init__(self, span, parent)`
  * Method: `add_widget(self, widget, stretch)`
    *Add widget to column*
  * Method: `add_stretch(self, stretch)`
    *Add stretch space*

* **Class**: `Stack`
    *Vertical or horizontal stack layout*
    *Usage:*
    *stack = Stack(orientation="vertical", spacing=5)*
    *stack.add_item(widget1)*
    *stack.add_item(widget2)*
  * Method: `__init__(self, orientation, spacing, parent)`
  * Method: `add_item(self, widget, stretch)`
    *Add item to stack*
  * Method: `add_stretch(self, stretch)`
    *Add stretch space*
  * Method: `insert_item(self, index, widget)`
    *Insert item at specific position*
  * Method: `remove_item(self, widget)`
    *Remove item from stack*
  * Method: `clear(self)`
    *Remove all items*

* **Class**: `ScrollContainer`
    *Scrollable container*
    *Usage:*
    *scroll = ScrollContainer()*
    *scroll.set_widget(my_large_widget)*
  * Method: `__init__(self, parent)`
  * Method: `set_widget(self, widget)`
    *Set the scrollable widget*
  * Method: `add_widget(self, widget, stretch)`
    *Add widget to scrollable area*

* **Class**: `GridLayout`
    *Grid layout container*
    *Usage:*
    *grid = GridLayout(columns=3, spacing=10)*
    *grid.add_item(widget1)*
    *grid.add_item(widget2)*
  * Method: `__init__(self, columns, spacing, parent)`
  * Method: `add_item(self, widget)`
    *Add item to grid*
  * Method: `add_item_at(self, widget, row, col, row_span, col_span)`
    *Add item at specific position*
  * Method: `clear(self)`
    *Clear all items*

* **Class**: `Spacer`
    *Spacer widget for adding space between elements*
    *Usage:*
    *spacer = Spacer(height=20)*
    *spacer = Spacer(width=20)*
  * Method: `__init__(self, width, height, parent)`
    *----------------------------------------*

--------------------

### 📄 [empty_state.py](file:///e:/APP%20Developer/Pixel%20Refine/pixel_refine_desktop/ui/resources/GenericUILibrary/empty_state.py)

* **Class**: `EmptyState`
    *A friendly component to display when there is no content to show.*
    *Supports optional title, description message, and an optional action button.*
    *Usage:*
    *# With title*
    *empty = EmptyState(*
    *title="No Projects",*
    *message="Create a new project to get started.",*
    *button_text="Create Project",*
    *on_click=self.handle_create*
    *)*
    *# Without title (message only)*
    *empty = EmptyState(*
    *message="Drag and drop images here.",*
    *button_text="Browse",*
    *button_variant="secondary",*
    *on_click=self.handle_browse*
    *)*
  * Method: `__init__(self, title, message, button_text, button_variant, on_click, parent)`
  * Method: `set_text(self, title, message)`
    *Update the text content.*
    *----------------------------------------*

--------------------

### 📄 [examples.py](file:///e:/APP%20Developer/Pixel%20Refine/pixel_refine_desktop/ui/resources/GenericUILibrary/examples.py)

* **File Overview**:
    *GenericUILibrary - Usage Examples*
    *This file demonstrates how to use the Bootstrap-like UI components.*

* **Class**: `ExampleApp`
    *Example application demonstrating GenericUILibrary components*
  * Method: `__init__(self)`
  * Method: `_create_button_example(self, container)`
    *Example: Different button variants*
  * Method: `_create_card_example(self, container)`
    *Example: Card with header and footer*
  * Method: `_create_form_example(self, container)`
    *Example: Form with inputs*
  * Method: `_create_list_example(self, container)`
    *Example: List group with selection*
  * Method: `_create_tab_example(self, container)`
    *Example: Tabs*
  * Method: `_on_form_submit(self, name_field, email_field, role_field)`
    *Handle form submission*
  * Method: `_delete_selected_items(self, list_group)`
    *Delete selected items from list*

* **Function**: `main()`
    *Run the example application*
    *----------------------------------------*

--------------------

### 📄 [forms.py](file:///e:/APP%20Developer/Pixel%20Refine/pixel_refine_desktop/ui/resources/GenericUILibrary/forms.py)

* **File Overview**:
    *Bootstrap-like Form Components for PySide6*
    *Provides reusable form input components*

* **Class**: `FormGroup`
    *Form group with label and input field.*
    *Supports real-time data binding via RealtimeMixin.*
    *Usage:*
    *form = FormGroup(label="Username", input_type="text")*
    *form.bind_store(store, "username")*
  * Method: `__init__(self, label, input_type, placeholder, auto_sync, parent)`
  * Method: `get_value(self)`
    *Get current value*
  * Method: `set_value(self, value)`
    *Set value*
  * Method: `add_options(self, options)`
    *Add options to select input*
  * Method: `on_store_changed(self, key, value)`
    *Update UI value from Store.*
  * Method: `_handle_internal_value_change(self, value)`
    *Handle value change from UI side.*

* **Class**: `Input`
    *Enhanced text input with validation states*
    *Usage:*
    *input = Input(placeholder="Enter email")*
    *input.set_state("valid")  # or "invalid", "warning"*
  * Method: `__init__(self, placeholder, parent)`
  * Method: `set_state(self, state)`
    *Set validation state: 'valid', 'invalid', 'warning', 'normal'*

* **Class**: `Select`
    *Enhanced dropdown/select component*
    *Usage:*
    *select = Select(options=["Option 1", "Option 2"])*
    *select.value_changed.connect(on_change)*
  * Method: `__init__(self, options, placeholder, parent)`
  * Method: `set_options(self, options)`
    *Replace all options*

* **Class**: `Checkbox`
    *Checkbox with label. Supports DataStore binding.*
    *Usage:*
    *cb = Checkbox("Option 1")*
    *cb.bind_store(store, "option_1_enabled")*
  * Method: `__init__(self, text, checked, auto_sync, parent)`
  * Method: `is_checked(self)`
  * Method: `set_checked(self, checked)`
  * Method: `on_store_changed(self, key, value)`
  * Method: `_on_internal_toggle(self, checked)`

* **Class**: `Radio`
    *Radio button with label*
    *Usage:*
    *radio = Radio("Option 1")*
    *radio.toggled.connect(on_toggle)*
  * Method: `__init__(self, text, checked, parent)`
  * Method: `is_checked(self)`
  * Method: `set_checked(self, checked)`

* **Class**: `RadioGroup`
    *Group of radio buttons. Supports DataStore binding (index or text).*
    *Usage:*
    *group = RadioGroup(options=["A", "B"])*
    *group.bind_store(store, "selected_mode")*
  * Method: `__init__(self, options, orientation, auto_sync, parent)`
  * Method: `add_option(self, text, checked)`
    *Add a radio option*
  * Method: `get_selected_index(self)`
    *Get index of selected option*
  * Method: `get_selected_text(self)`
    *Get text of selected option*
  * Method: `set_selected(self, index)`
    *Set selected option by index*
  * Method: `on_store_changed(self, key, value)`
  * Method: `_block_radios(self, block)`
  * Method: `_on_internal_selection_change(self, index, text)`

* **Class**: `FormRow`
    *Horizontal form layout with label and input side by side*
    *Usage:*
    *form = FormRow()*
    *form.add_field("Name:", QLineEdit())*
    *form.add_field("Age:", QSpinBox())*
  * Method: `__init__(self, parent)`
  * Method: `add_field(self, label, widget)`
    *Add a field to the form*
  * Method: `add_row(self, widget)`
    *Add a full-width row*
    *----------------------------------------*

--------------------

### 📄 [grids.py](file:///e:/APP%20Developer/Pixel%20Refine/pixel_refine_desktop/ui/resources/GenericUILibrary/grids.py)

* **File Overview**:
    *Bootstrap-like Grid and Gallery Components for PySide6*
    *Provides grid layouts for displaying items (images, cards, etc.)*

* **Class**: `GridContainer`
    *Scrollable grid container for displaying items with wrap and responsive column support*
    *Modes:*
    *- 'vertical': Items wrap to next row (vertical scroll)*
    *- 'horizontal': Items wrap to next column (horizontal scroll)*
    *Column Modes:*
    *- 'fixed': Use specified columns parameter (default)*
    *- 'responsive': Auto-calculate columns based on container width and item size*
    *Usage - Fixed Columns:*
    *grid = GridContainer(columns=4, wrap_mode='vertical')*
    *grid.add_item(GridItem("Item 1"))*
    *Usage - Responsive Columns:*
    *grid = GridContainer(item_width=120, spacing=10, column_mode='responsive')*
    *grid.add_item(GridItem("Item 1"))*
    *# Columns auto-adjust based on available width*
  * Method: `__init__(self, columns, spacing, wrap_mode, column_mode, item_width, parent)`
  * Method: `add_item(self, widget)`
    *Add item to grid based on wrap mode and column mode*
  * Method: `_calculate_responsive_columns(self)`
    *Calculate number of columns based on available width and item size.*
  * Method: `_is_widget_alive(self, widget)`
    *Reinforced check for PySide6 C++ objects.*
  * Method: `remove_item(self, widget, rebuild)`
    *Safe removal of tracking widget.*
  * Method: `clear_items(self)`
    *Clear all items and reset state safely.*
  * Method: `set_batch_update(self, active)`
    *Enable or disable batch update mode to optimize bulk additions.*
  * Method: `on_store_changed(self, key, value)`
    *Handle real-time updates from DataStore.*
  * Method: `sync_items(self, new_data_list)`
    *Smart-update grid items based on ID.*
    *new_data_list: list of dicts with 'id' key.*
  * Method: `get_item_count(self)`
    *Get number of items*
  * Method: `set_wrap_mode(self, mode)`
    *Change wrap mode dynamically.*
    *Args:*
    *mode: 'vertical' or 'horizontal'*
  * Method: `set_column_mode(self, mode, item_width)`
    *Change column mode dynamically.*
    *Args:*
    *mode: 'fixed' or 'responsive'*
    *item_width: Item width for responsive calculation (if changing to responsive)*
  * Method: `_rebuild_grid(self)`
    *Rebuild grid layout with current settings (Full Width Reinforced)*
  * Method: `_add_to_layout_grid(self, widget)`
    *Helper internal untuk addWidget dengan penghitungan row/col (Heavy-Duty).*
  * Method: `resizeEvent(self, event)`
    *Handle resize event to recalculate responsive columns*

* **Class**: `GridItem`
    *Individual grid item with selection support*
    *Usage:*
    *item = GridItem("item_1", "Image 1")*
    *item.clicked.connect(on_click)*
  * Method: `__init__(self, item_id, label, size, parent)`
  * Method: `set_selected(self, selected)`
    *Set selection state*
  * Method: `is_selected(self)`
    *Check if selected*
  * Method: `set_content(self, widget)`
    *Replace visual box with custom widget*
  * Method: `set_label(self, label)`
    *Set label text*
  * Method: `paintEvent(self, event)`
    *Draw selection border*
  * Method: `mousePressEvent(self, event)`
    *Handle click*
  * Method: `mouseDoubleClickEvent(self, event)`
    *Handle double click*

* **Class**: `Gallery`
    *Gallery component with header and grid*
    *Usage:*
    *gallery = Gallery(title="Images", columns=5)*
    *gallery.add_item("img1", "Photo 1")*
    *gallery.item_clicked.connect(on_click)*
  * Method: `__init__(self, title, columns, show_header, parent)`
  * Method: `set_title(self, title)`
    *Set gallery title*
  * Method: `add_item(self, item_id, label)`
    *Add item to gallery*
  * Method: `remove_item(self, item_id)`
    *Remove item from gallery*
  * Method: `clear_items(self)`
    *Clear all items*
  * Method: `get_item(self, item_id)`
    *Get item by ID*
  * Method: `set_item_selected(self, item_id, selected)`
    *Set item selection state*

* **Class**: `ThumbnailGrid`
    *Grid specifically for thumbnails/images with wrap support*
    *Usage:*
    *grid = ThumbnailGrid(columns=6, wrap_mode='vertical')*
    *grid.add_thumbnail("thumb1", "Image 1.jpg")*
  * Method: `__init__(self, columns, thumbnail_size, wrap_mode, parent)`
  * Method: `add_thumbnail(self, item_id, label)`
    *Add thumbnail*
  * Method: `get_thumbnail(self, item_id)`
    *Get thumbnail by ID*
  * Method: `clear_thumbnails(self)`
    *Clear all thumbnails*
    *----------------------------------------*

--------------------

### 📄 [image_grid.py](file:///e:/APP%20Developer/Pixel%20Refine/pixel_refine_desktop/ui/resources/GenericUILibrary/image_grid.py)

* **Class**: `ImageCard`
    *A friendly card component for displaying images or thumbnails.*
    *Supports selection, loading state, and click interactions.*
    *Usage:*
    *card = ImageCard("unique_id_or_path")*
    *card.set_image(pixmap)*
    *card.clicked.connect(handle_click)*
  * Method: `__init__(self, card_id, size, parent)`
  * Method: `set_image(self, q_image, scale_to_fit)`
    *Display an image on the card (Pixel-Perfect Image Drawing).*
  * Method: `set_loading(self, loading)`
    *Show or hide the loading state.*
  * Method: `unload_image(self)`
    *Unload image to free memory (Reinforced).*
  * Method: `has_image(self)`
    *Check if card currently holds image data.*
  * Method: `get_opacity(self)`
  * Method: `set_opacity(self, value)`
  * Method: `select(self)`
    *Select this card.*
  * Method: `deselect(self)`
    *Deselect this card.*
  * Method: `toggle_selection(self)`
    *Toggle selection state.*
  * Method: `is_selected(self)`
  * Method: `paintEvent(self, event)`
    *Render the card and its content manually for ultimate stability.*
  * Method: `mousePressEvent(self, event)`
  * Method: `mouseDoubleClickEvent(self, event)`
    *----------------------------------------*

--------------------

### 📄 [list_group.py](file:///e:/APP%20Developer/Pixel%20Refine/pixel_refine_desktop/ui/resources/GenericUILibrary/list_group.py)

* **Class**: `ListGroup`
    *A friendly list component for displaying and managing lists of items.*
    *Wraps QListWidget with a simpler API and modern styling.*
    *Supports real-time updates via RealtimeMixin.*
    *Usage:*
    *list_group = ListGroup()*
    *list_group.add_item("Item 1", value=1)*
    *list_group.selection_changed.connect(my_handler)*
    *# Real-time binding*
    *list_group.bind_store(my_store, "project_list")*
  * Method: `__init__(self, parent, reordering)`
  * Method: `_apply_styles(self)`
    *Apply modern styling to the list.*
  * Method: `on_store_changed(self, key, value)`
    *Handle real-time updates from DataStore.*
  * Method: `sync_items(self, new_data_list)`
    *Smart-update list items without clearing everything.*
    *Preserves selection for items that still exist.*
  * Method: `add_item(self, text, value)`
    *Add an item to the list.*
    *Args:*
    *text: The display text for the item.*
    *value: Hidden data associated with the item (defaults to text).*
  * Method: `clear(self)`
    *Remove all items.*
  * Method: `clear_selection(self)`
    *Clear all selected items.*
  * Method: `get_selected_values(self)`
    *Return a list of values (data) of currently selected items.*
  * Method: `reordering_animation(self)`
    *Toggle cascading reorder animation.*
  * Method: `reordering_animation(self, enabled)`
  * Method: `get_selected_labels(self)`
    *Return a list of text labels of currently selected items.*
  * Method: `remove_selected_items(self)`
    *Remove currently selected items from the list.*
  * Method: `select_first(self)`
    *Select the first item if available.*
  * Method: `select_item_by_value(self, value)`
    *Select an item by its data value.*
    *Clears any existing selection first.*
    *Args:*
    *value: The data value (UserRole) to search for.*
    *Returns:*
    *True if item was found and selected, False otherwise.*
  * Method: `set_move_mode(self, enabled)`
    *Enable or disable keyboard move mode.*
  * Method: `_move_item_keyboard(self, key)`
    *Handle internal keyboard move for multiple selected items.*
    *Moves items as a group if possible.*
  * Method: `_on_selection_change(self)`
  * Method: `_on_item_double_clicked(self, item)`
    *Enter edit mode on double click.*
  * Method: `_on_item_changed(self, item)`
    *Emit a signal when an item's text has been changed.*
  * Method: `_on_rows_about_to_be_moved(self, parent, start, end, destination, row)`
    *Capture a snapshot of the list BEFORE the move happens.*
  * Method: `_on_rows_moved(self, parent, start, end, destination, row)`
    *Handle internal move of items (Drag & Drop).*
  * Method: `get_all_values(self)`
    *Helper to get all item values in current order.*
  * Method: `_emit_reordered(self)`
    *Emit notification after a small delay to ensure model consistency.*
  * Method: `eventFilter(self, source, event)`
  * Method: `count(self)`
  * Method: `widget(self)`
    *----------------------------------------*

--------------------

### 📄 [main_window.py](file:///e:/APP%20Developer/Pixel%20Refine/pixel_refine_desktop/ui/resources/GenericUILibrary/main_window.py)

* **Class**: `MainAppWindow`
  * Method: `__init__(self)`
  * Method: `_connect_logic(self)`
    *Menghubungkan signal UI ke logika (Di sini logika simpel saja).*
  * Method: `_on_item_selected(self, item_id, label)`
  * Method: `_on_selection_cleared(self)`
  * Method: `_on_process_run(self, data)`
    *----------------------------------------*

--------------------

### 📄 [mixins.py](file:///e:/APP%20Developer/Pixel%20Refine/pixel_refine_desktop/ui/resources/GenericUILibrary/mixins.py)

* **Class**: `RealtimeMixin`
    *Mixin class to provide real-time data binding capabilities to UI components.*
  * Method: `bind_store(self, store, key)`
  * Method: `_handle_store_change(self, key, value)`
  * Method: `on_store_changed(self, key, value)`
  * Method: `get_data(self, key)`
  * Method: `set_data(self, value, key, notify)`
  * Method: `signal_blocker(self)`
    *Context manager to block store signals temporarily.*

* **Class**: `SyncMixin`
    *Advanced mixin for declarative data binding.*
    *Allows linking Store keys directly to widget properties.*
  * Method: `bind_store(self, store, key)`
    *Override to initialize bindings dictionary.*
  * Method: `set_scope(self, prefix)`
    *Set a prefix for all subsequent bindings (e.g., 'batch.625').*
  * Method: `add_binding(self, key, widget, property_name, fallback)`
    *Bind a relative store key to a widget property with optional fallback.*
    *Example: add_binding("alignment_algo", self.align_form, fallback="No Alignment")*
  * Method: `on_store_changed(self, key, value)`
    *Handle automatic binding updates with scope resolution and fallbacks.*
  * Method: `_apply_binding_value(self, widget, property_name, value)`
    *Helper to call setter on widget (e.g., set_value).*
    *----------------------------------------*

--------------------

### 📄 [modals.py](file:///e:/APP%20Developer/Pixel%20Refine/pixel_refine_desktop/ui/resources/GenericUILibrary/modals.py)

* **File Overview**:
    *Bootstrap-like Modal and Overlay Components for PySide6*
    *Provides dialog, modal, and overlay components*

* **Class**: `Modal`
    *Bootstrap-like modal dialog*
    *Usage:*
    *modal = Modal(title="Confirm Action", parent=self)*
    *modal.set_body("Are you sure?")*
    *modal.add_footer_button("Cancel", variant="secondary")*
    *modal.add_footer_button("Confirm", variant="primary")*
    *modal.exec()*
  * Method: `__init__(self, title, size, parent)`
  * Method: `set_title(self, title)`
    *Set modal title*
  * Method: `set_body(self, content)`
    *Set body content (text or widget)*
  * Method: `add_body_widget(self, widget)`
    *Add widget to body*
  * Method: `add_footer_button(self, text, variant, callback)`
    *Add button to footer*

* **Class**: `ModalHeader`
    *Modal header component*
  * Method: `__init__(self, title, parent)`
  * Method: `set_title(self, title)`
    *Set title*

* **Class**: `ModalBody`
    *Modal body component*
  * Method: `__init__(self, parent)`
  * Method: `set_content(self, content)`
    *Set content (text or widget)*
  * Method: `add_widget(self, widget, stretch)`
    *Add widget to body*

* **Class**: `ModalFooter`
    *Modal footer component*
  * Method: `__init__(self, parent)`
  * Method: `add_action(self, widget)`
    *Add action widget*

* **Class**: `Overlay`
    *Loading overlay component*
    *Usage:*
    *overlay = Overlay(parent=self)*
    *overlay.show_message("Processing...")*
    *overlay.hide()*
  * Method: `__init__(self, parent)`
  * Method: `show_message(self, message)`
    *Show overlay with message*
  * Method: `hide_overlay(self)`
    *Hide overlay*

* **Class**: `Toast`
    *Toast notification component*
    *Usage:*
    *toast = Toast("Success!", variant="success", parent=self)*
    *toast.show_toast(duration=3000)*
  * Method: `__init__(self, message, variant, parent)`
  * Method: `_get_color(self, variant)`
    *Get color based on variant*
  * Method: `show_toast(self, duration)`
    *Show toast for specified duration (ms)*
  * Method: `_hide_toast(self)`
    *Hide toast with fade out*

* **Class**: `LoadingSpinner`
    *Simple loading indicator*
    *Usage:*
    *spinner = LoadingSpinner(message="Loading...")*
  * Method: `__init__(self, message, parent)`
  * Method: `set_message(self, message)`
    *Update loading message*
    *----------------------------------------*

--------------------

### 📄 [navbar.py](file:///e:/APP%20Developer/Pixel%20Refine/pixel_refine_desktop/ui/resources/GenericUILibrary/navbar.py)

* **File Overview**:
    *Bootstrap-like Navbar Components for PySide6*
    *Provides navigation bar components*

* **Class**: `Navbar`
    *Bootstrap-like navigation bar*
    *Usage:*
    *navbar = Navbar(brand="My App")*
    *navbar.add_nav_item("Home", callback=on_home)*
    *navbar.add_nav_item("Settings", callback=on_settings)*
  * Method: `__init__(self, brand, height, parent)`
  * Method: `set_brand(self, brand)`
    *Set brand text*
  * Method: `add_nav_item(self, text, callback)`
    *Add navigation item*
  * Method: `add_action(self, widget)`
    *Add action widget to right side*
  * Method: `set_active_item(self, index)`
    *Set active navigation item*

* **Class**: `NavItem`
    *Navigation item button*
    *Usage:*
    *item = NavItem("Home")*
    *item.clicked.connect(on_click)*
  * Method: `__init__(self, text, parent)`
  * Method: `set_active(self, active)`
    *Set active state*

* **Class**: `Sidebar`
    *Vertical sidebar navigation*
    *Usage:*
    *sidebar = Sidebar(width=200)*
    *sidebar.add_item("Dashboard", icon_path="...")*
    *sidebar.add_item("Settings")*
    *sidebar.item_clicked.connect(on_item_click)*
  * Method: `__init__(self, width, parent)`
  * Method: `add_item(self, text, icon_path)`
    *Add sidebar item*
  * Method: `add_separator(self)`
    *Add separator line*
  * Method: `add_stretch(self)`
    *Add stretch to push items to top*
  * Method: `set_active_item(self, index)`
    *Set active item*
  * Method: `_on_item_clicked(self, index, text)`
    *Handle item click*

* **Class**: `SidebarItem`
    *Sidebar navigation item*
    *Usage:*
    *item = SidebarItem("Dashboard", icon_path="...")*
    *item.clicked.connect(on_click)*
  * Method: `__init__(self, text, icon_path, parent)`
  * Method: `set_active(self, active)`
    *Set active state*
    *----------------------------------------*

--------------------

### 📄 [overlays.py](file:///e:/APP%20Developer/Pixel%20Refine/pixel_refine_desktop/ui/resources/GenericUILibrary/overlays.py)

* **File Overview**:
    *Overlay Components for GenericUILibrary.*
    *Improved Version: True Gaussian Blur & Ghosting Fix.*

* **Class**: `OverlayPosition`
    *Enum definitions for overlay positioning.*

* **Class**: `OverlayContainer`
  * Method: `__init__(self, parent, position, margin, smart_positioning, close_on_click_outside, dim_background, dim_opacity, blur_background, blur_radius, shadow_enabled, shadow_blur_radius, shadow_color, shadow_offset)`
  * Method: `set_content(self, widget)`
  * Method: `setParent(self, parent, mode)`
  * Method: `setVisible(self, visible)`
    *Zero-flicker capture: Grab background BEFORE becoming visible.*
  * Method: `showEvent(self, event)`
  * Method: `_capture_blur(self)`
    *Triggered primarily by parent resize events.*
  * Method: `_create_blurred_snapshot(self)`
    *Sequence: Snapshot -> Downscale -> Gaussian Blur (Smoothing)*
  * Method: `_apply_gaussian_blur(self, pixmap, radius)`
    *Applies a high-quality Gaussian blur with padding to avoid edge artifacts.*
  * Method: `hideEvent(self, event)`
  * Method: `paintEvent(self, event)`
  * Method: `mousePressEvent(self, event)`
  * Method: `eventFilter(self, obj, event)`
  * Method: `_update_position(self)`
  * Method: `_calculate_coordinates(self, position_enum, p_rect, w, h)`
  * Method: `_adjust_position_smartly(self, natural_pos, w, h, p_rect)`
    *----------------------------------------*

--------------------

### 📄 [progress_bars.py](file:///e:/APP%20Developer/Pixel%20Refine/pixel_refine_desktop/ui/resources/GenericUILibrary/progress_bars.py)

* **File Overview**:
    *Bootstrap-like Progress Bar Components for PySide6*
    *Provides various progress bar styles with animations*

* **Class**: `ProgressBar`
    *Modern progress bar with multiple styles.*
    *Supports real-time binding via RealtimeMixin.*
    *Styles:*
    *- linear: Standard horizontal bar*
    *- striped: Striped pattern*
    *- animated: Animated stripes*
    *- gradient: Gradient color*
    *- circular: Circular progress*
    *Usage:*
    *progress = ProgressBar(style="animated", variant="primary")*
    *progress.bind_store(store, "main_progress")*
  * Method: `__init__(self, style, variant, show_label, minimalist, parent)`
  * Method: `_setup_ui(self)`
    *Setup UI based on style*
  * Method: `_setup_animation(self)`
    *Setup animation for animated stripes*
  * Method: `_get_variant_color(self)`
    *Get color based on variant*
  * Method: `_apply_stylesheet(self)`
    *Apply stylesheet to standard QProgressBar*
  * Method: `_update_display_value(self, value)`
    *Internal slot to update the display from animation*
  * Method: `set_value(self, value, smooth)`
    *Set progress value (0-100)*
    *Args:*
    *value: Target value*
    *smooth: If True, animate the change. If False, jump instantly.*
  * Method: `get_value(self)`
    *Get current value*
  * Method: `set_max_value(self, max_value)`
    *Set maximum value*
  * Method: `setValue(self, value)`
    *Alias for set_value for QProgressBar compatibility.*
  * Method: `setRange(self, min_val, max_val)`
    *Alias for set_max_value for QProgressBar compatibility.*
  * Method: `setVisible(self, visible)`
    *Ensure setVisible works on the main widget.*
  * Method: `animate_to(self, target_value, duration)`
    *Legacy animate method - redirected to new smooth logic but with custom duration*
  * Method: `on_store_changed(self, key, value)`
    *Update progress from DataStore.*

* **Class**: `CustomProgressBar`
    *Custom painted progress bar with stripes and gradients*
  * Method: `__init__(self, style, variant, parent)`
  * Method: `setValue(self, value)`
    *Set value*
  * Method: `value(self)`
    *Get value*
  * Method: `start_animation(self)`
    *Start stripe animation*
  * Method: `_animate_stripes(self)`
    *Animate stripe offset*
  * Method: `_get_variant_color(self)`
    *Get color based on variant*
  * Method: `paintEvent(self, event)`
    *Custom paint*

* **Class**: `CircularProgressFallback`
    *Fallback circular progress if custom not available*
  * Method: `__init__(self, parent)`
  * Method: `setValue(self, value)`
    *Set value*
  * Method: `value(self)`
    *Get value*
  * Method: `paintEvent(self, event)`
    *Paint circular progress*

* **Class**: `IndeterminateProgress`
    *Indeterminate progress indicator (loading animation)*
    *Usage:*
    *progress = IndeterminateProgress(style="spinner")*
    *progress.start()*
    *progress.stop()*
  * Method: `__init__(self, style, size, parent)`
  * Method: `start(self)`
    *Start animation*
  * Method: `stop(self)`
    *Stop animation*
  * Method: `_update_animation(self)`
    *Update animation*
  * Method: `paintEvent(self, event)`
    *Paint spinner*

* **Class**: `ProgressGroup`
    *Group of stacked progress bars. Supports multi-key binding from Store.*
    *Usage:*
    *group = ProgressGroup()*
    *group.add_progress("Task 1", label="task1")*
    *group.bind_store(store) # Will react to any change in store*
  * Method: `__init__(self, parent)`
  * Method: `add_progress(self, label, value, variant, style)`
    *Add a progress bar to the group*
  * Method: `on_store_changed(self, key, value)`
    *Handle multi-key updates.*
    *If value is a dict, try updating multiple bars.*
    *Otherwise, try to find a bar matching the key.*
  * Method: `update_progress(self, index, value)`
    *Update progress bar value by index*
  * Method: `clear(self)`
    *Clear all progress bars*
    *----------------------------------------*

--------------------

### 📄 [selector_panel.py](file:///e:/APP%20Developer/Pixel%20Refine/pixel_refine_desktop/ui/resources/GenericUILibrary/selector_panel.py)

* **Class**: `SelectorPanel`
  * Method: `__init__(self, title, action_btn_text, parent)`
  * Method: `add_item(self, item_id, label)`
  * Method: `remove_item(self, item_id)`
  * Method: `_handle_add(self)`
  * Method: `_handle_delete(self)`
  * Method: `_handle_selection(self)`
    *----------------------------------------*

--------------------

### 📄 [store.py](file:///e:/APP%20Developer/Pixel%20Refine/pixel_refine_desktop/ui/resources/GenericUILibrary/store.py)

* **Class**: `DataStore`
    *Centralized data store for GenericUILibrary.*
    *Emits signals when data changes, allowing UI components to react.*
  * Method: `__init__(self, parent)`
  * Method: `set(self, key, value, notify)`
    *Set a value in the store and emit changed signal.*
    *Supports nested keys using dot notation.*
  * Method: `silent_set(self, key, value)`
    *Set value without emitting signals or saving to file.*
  * Method: `get(self, key, default)`
    *Get a value from the store.*
    *Supports nested keys using dot notation.*
  * Method: `update_bulk(self, data_dict, deep, save)`
    *Update multiple keys at once.*
    *Supports dotted keys (e.g., {"625.algo": "X"}) by expanding them into nested dicts.*
    *If deep=True, merges dictionaries instead of replacing.*
  * Method: `transaction(self)`
    *Context manager for batching multiple updates into a single notification.*
  * Method: `_deep_merge(self, base, source)`
    *Internal helper for recursive dict merging.*
  * Method: `bind_to_file(self, file_path)`
    *Bind this store to a JSON file.*
    *It will load data initially and watch for external changes.*
  * Method: `load_from_file(self)`
    *Load data from the bound JSON file. Replaces current data.*
  * Method: `save_to_file(self)`
    *Save current data to the bound JSON file.*
  * Method: `_on_file_changed(self, path)`
    *Handle external file changes with robust path re-registration.*

* **Function**: `get_store()`
    *----------------------------------------*

--------------------

### 📄 [tables.py](file:///e:/APP%20Developer/Pixel%20Refine/pixel_refine_desktop/ui/resources/GenericUILibrary/tables.py)

* **File Overview**:
    *Bootstrap-like Table Component for PySide6*
    *Provides a standardized data table with styling and utility methods.*

* **Class**: `DataTable`
    *Standardized Table Widget with convenient APIs for batch processing lists.*
    *Usage:*
    *table = DataTable(columns=["Name", "Status", "Details"])*
    *table.add_row(["Item 1", "Pending", "Simple job"])*
  * Method: `__init__(self, columns, parent)`
  * Method: `setup_columns(self, headers)`
    *Set headers and initialize column count.*
  * Method: `clear_rows(self)`
    *Clear all rows but keep headers.*
  * Method: `add_row_items(self, items)`
    *Add a row with a list of QTableWidgetItem or widgets.*
    *Returns the index of the new row.*
  * Method: `set_row_color(self, row, color)`
    *Set background color for an entire row.*
  * Method: `get_cell_widget(self, row, col)`
    *Safe wrapper to get cell widget.*
  * Method: `resize_columns_to_content(self, target_cols)`
    *Resize specific columns to content.*
    *----------------------------------------*

--------------------

### 📄 [tabs.py](file:///e:/APP%20Developer/Pixel%20Refine/pixel_refine_desktop/ui/resources/GenericUILibrary/tabs.py)

* **File Overview**:
    *Bootstrap-like Tab Components for PySide6*
    *Provides tabbed navigation components with animations*

* **Class**: `AnimatedTabContainer`
    *Tab container with fade and slide animations*
    *Features:*
    *- Fade animation for tab bar*
    *- Slide animation for tab content*
    *Usage:*
    *tabs = AnimatedTabContainer()*
    *tabs.add_tab("Settings", settings_widget)*
    *tabs.add_tab("Profile", profile_widget)*
    *tabs.tab_changed.connect(on_tab_change)*
  * Method: `__init__(self, enable_animations, parent)`
  * Method: `_setup_animated_stack(self)`
    *Setup animated stacked widget for tab content*
  * Method: `add_tab(self, title, widget)`
    *Add a tab with animation support*
  * Method: `remove_tab(self, index)`
    *Remove tab by index*
  * Method: `get_current_tab(self)`
    *Get current tab index and title*
  * Method: `set_current_tab(self, index)`
    *Set current tab by index with animation*
  * Method: `_on_tab_changed(self, index)`
    *Handle tab change with animations*
  * Method: `_animate_tab_bar(self, index)`
    *Animate tab bar with fade effect*

* **Class**: `TabPane`
    *Individual tab pane content*
    *Usage:*
    *pane = TabPane()*
    *pane.add_widget(content_widget)*
  * Method: `__init__(self, parent)`
  * Method: `add_widget(self, widget, stretch)`
    *Add widget to pane*
  * Method: `set_content(self, widget)`
    *Set pane content (replaces existing)*

* **Class**: `SimpleTabs`
    *Simple tab implementation with custom styling*
    *Usage:*
    *tabs = SimpleTabs()*
    *tabs.add_tab("Tab 1", widget1)*
    *tabs.add_tab("Tab 2", widget2)*
  * Method: `__init__(self, parent)`
  * Method: `add_tab(self, title, widget)`
    *Add tab*
  * Method: `get_tab_widget(self, index)`
    *Get tab widget by index*
    *----------------------------------------*

--------------------

### 📄 [theme.py](file:///e:/APP%20Developer/Pixel%20Refine/pixel_refine_desktop/ui/resources/GenericUILibrary/theme.py)

* **File Overview**:
    *Theme and Color System for GenericUILibrary*
    *Provides default colors and styling that can be customized*

* **Class**: `Theme`
    *Default theme colors (Bootstrap-inspired)*
    *Can be customized by creating a new Theme instance*
  * Method: `__init__(self)`
  * Method: `get_variant_color(self, variant)`
    *Get color for a variant*
  * Method: `get_variant_hover_color(self, variant)`
    *Get hover color for a variant (slightly darker)*

* **Function**: `get_theme()`
    *Get the current default theme*

* **Function**: `set_theme(theme)`
    *Set a custom theme globally*

* **Function**: `create_button_style(variant, theme)`
    *Create button stylesheet for a given variant*
    *Usage:*
    *btn.setStyleSheet(create_button_style("primary"))*

* **Function**: `create_card_style(theme)`
    *Create card stylesheet*

* **Function**: `create_input_style(theme)`
    *Create input field stylesheet*

* **Function**: `create_select_style(theme)`
    *Create select/combobox stylesheet*

* **Function**: `create_list_style(theme)`
    *Create list widget stylesheet*

* **Function**: `create_scrollbar_style(theme)`
    *Create scrollbar stylesheet*

* **Function**: `create_checkbox_style(theme)`
    *Create a premium checkbox stylesheet (Smaller, Blue, Circular)*
    *----------------------------------------*

--------------------

### 📄 [ui_component.py](file:///e:/APP%20Developer/Pixel%20Refine/pixel_refine_desktop/ui/resources/GenericUILibrary/ui_component.py)

* **Class**: `GridItemWidget`
    *Widget kotak sederhana untuk grid.*
    *Bisa merepresentasikan Gambar, File, Dokumen, dll.*
  * Method: `__init__(self, item_id, label_text, parent)`
  * Method: `set_selected(self, selected)`
  * Method: `paintEvent(self, event)`
    *Menggambar border biru saat dipilih.*
  * Method: `mousePressEvent(self, event)`
  * Method: `mouseDoubleClickEvent(self, event)`

* **Class**: `LoadingOverlay`
    *Tampilan Loading Generik.*
  * Method: `__init__(self, parent)`
  * Method: `set_status(self, text, percentage)`
    *----------------------------------------*

--------------------

### 📄 [viewer_panel.py](file:///e:/APP%20Developer/Pixel%20Refine/pixel_refine_desktop/ui/resources/GenericUILibrary/viewer_panel.py)

* **Class**: `ViewerPanel`
  * Method: `__init__(self, parent)`
  * Method: `set_view_title(self, title)`
  * Method: `show_empty_state(self)`
  * Method: `show_grid(self)`
  * Method: `show_loading(self, message)`
  * Method: `add_grid_item(self, item_id, label)`
  * Method: `_clear_grid(self)`
    *----------------------------------------*

--------------------

### 📄 [workspace_layout.py](file:///e:/APP%20Developer/Pixel%20Refine/pixel_refine_desktop/ui/resources/GenericUILibrary/workspace_layout.py)

* **Class**: `WorkspaceLayout`
  * Method: `__init__(self, parent)`
  * Method: `toggle_config_panel(self, show)`
    *----------------------------------------*

--------------------


## 📂 Directory: `Root Directory`

### 📄 [# DIRECTORY: pixel_refine_desktop/ui/resources/styles](file:///e:/APP%20Developer/Pixel%20Refine/# DIRECTORY: pixel_refine_desktop/ui/resources/styles)


--------------------


## 📂 Directory: `Root Directory`

### 📄 [stylesheet.py](file:///e:/APP%20Developer/Pixel%20Refine/pixel_refine_desktop/ui/resources/styles/stylesheet.py)

* **Function**: `stylesheet_global_page()`
    *Mengembalikan QSS untuk styling aplikasi*
    *----------------------------------------*

--------------------


## 📂 Directory: `Root Directory`

### 📄 [# DIRECTORY: pixel_refine_desktop/ui/views/panorama](file:///e:/APP%20Developer/Pixel%20Refine/# DIRECTORY: pixel_refine_desktop/ui/views/panorama)


--------------------


## 📂 Directory: `Root Directory`

### 📄 [PanoramaPage.py](file:///e:/APP%20Developer/Pixel%20Refine/pixel_refine_desktop/ui/views/panorama/PanoramaPage.py)

* **Class**: `PanoramaPage`
  * Method: `__init__(self)`
    *----------------------------------------*

--------------------

### 📄 [working_left_panel.py](file:///e:/APP%20Developer/Pixel%20Refine/pixel_refine_desktop/ui/views/panorama/working_left_panel.py)

* **Class**: `WorkingLeftPanel`
    *Panel Kiri: Pengontrol utama Layout (Display di atas, Workflow di bawah).*
    *Murni menangani transisi UI dan Layout.*
  * Method: `__init__(self, parent)`
  * Method: `_connect_signals(self)`
  * Method: `update_display_for_project(self, project_id, project_name)`
    *Dipanggil saat user memilih item di panel kanan.*
  * Method: `clear_display(self)`
    *Dipanggil saat seleksi kosong.*
  * Method: `_on_back_to_grid(self)`
  * Method: `_on_preview_simulation(self, stage_name)`
    *Hanya simulasi visual saat tombol preview ditekan.*
    *----------------------------------------*

--------------------

### 📄 [working_right_panel.py](file:///e:/APP%20Developer/Pixel%20Refine/pixel_refine_desktop/ui/views/panorama/working_right_panel.py)

* **Class**: `WorkingRightPanel`
    *Panel Kanan: Daftar item.*
    *Menggunakan Mock Data (ListWidget) menggantikan Database.*
  * Method: `__init__(self, parent)`
  * Method: `_create_list_panel(self)`
  * Method: `_load_dummy_data(self)`
    *Mengisi list dengan data dummy untuk preview UI.*
  * Method: `_add_item_ui(self)`
  * Method: `_delete_item_ui(self)`
  * Method: `_on_selection_change(self)`
  * Method: `_show_batch_dialog(self)`
    *----------------------------------------*

--------------------


## 📂 Directory: `Root Directory`

### 📄 [# DIRECTORY: pixel_refine_desktop/ui/views/panorama/display_area](file:///e:/APP%20Developer/Pixel%20Refine/# DIRECTORY: pixel_refine_desktop/ui/views/panorama/display_area)


--------------------


## 📂 Directory: `Root Directory`

### 📄 [display_panel.py](file:///e:/APP%20Developer/Pixel%20Refine/pixel_refine_desktop/ui/views/panorama/display_area/display_panel.py)

* **File Overview**:
    *Display Panel Component - Rewritten dengan pola Panorama.*
    *Handles image grid dan full resolution preview dengan proper drag & drop support.*
    *Adapted from: pixel_refine_desktop/ui/views/panorama/display_area/display_panel.py*

* **Class**: `DisplayPanel`
    *Panel untuk menampilkan Grid images dan Preview.*
    *Menggunakan QStackedWidget untuk switch antara Grid View dan Preview View.*
    *Struktur: DisplayPanel (Logic) -> QStackedLayout (Overlay support)*
    *-> Layer 0: Content Widget -> Container -> Header + Stack*
    *-> Layer 1: Overlay Widget -> Floating Progress Bar*
    *-> Layer 2: Sidebar Overlay*
  * Method: `__init__(self, controller)`
  * Method: `_setup_ui(self)`
    *Setup UI dengan stacked widget untuk grid dan preview mode.*
  * Method: `_setup_sidebar(self)`
    *Initialize Floating Sidebar.*
  * Method: `_setup_settings_overlay(self)`
    *Setup independent overlay for Settings View.*
  * Method: `_handle_sidebar_navigation(self, index)`
    *Handle navigation from sidebar.*
    *Intercepts Settings (index 2) to show overlay.*
    *Forwards others (0, 1) to main window.*
  * Method: `show_settings(self)`
    *Show settings overlay with FADE animation.*
  * Method: `toggle_sidebar(self)`
    *Toggle floating sidebar visibility with animation.*
  * Method: `_build_supported_extensions(self)`
  * Method: `_build_file_filter(self)`
    *Build file filter string untuk QFileDialog dari config.SUPPORTED_FORMATS.*
    *Returns:*
    *str: File filter string (e.g., "Images (*.jpg *.jpeg *.png ...)")*
  * Method: `_create_placeholder_widget(self, html_text, button_text, on_button_click)`
    *Membuat widget placeholder untuk ditampilkan saat grid kosong.*
    *Mengikuti pattern dari panorama dengan flexible layout.*
    *Args:*
    *html_text: Text HTML untuk ditampilkan*
    *button_text: Text untuk tombol (optional)*
    *on_button_click: Callback untuk button click (optional)*
    *Returns:*
    *QWidget: Container dengan layout stretch + label + button (jika ada)*
  * Method: `_set_placeholder(self, widget)`
    *Set placeholder widget in stack.*
    *Safely removes previous placeholder if exists.*
    *Args:*
    *widget: Generic widget/container to show*
  * Method: `load_batch(self, batch_id, images)`
    *Load batch images ke grid.*
    *Args:*
    *batch_id: ID dari batch*
    *images: List of image objects dengan .id dan .path attributes*
  * Method: `clear_display(self)`
    *Clear display ketika tidak ada batch yang dipilih.*
    *Reset ke state default dengan placeholder widget dan tombol "New Batch".*
  * Method: `_show_empty_batch_state(self)`
    *Show empty state ketika batch dipilih tapi belum ada images.*
    *Display pesan informatif + tombol untuk import images langsung.*
  * Method: `_create_new_batch(self)`
    *Call _create_new_batch dari right_panel untuk create batch baru.*
    *Right panel akan handle dialog input dan emit signal.*
  * Method: `set_project_view(self, project_name)`
    *Called when a project is selected to display its contents.*
  * Method: `show_empty_state(self)`
    *Called when no project is selected.*
  * Method: `show_grid_view(self)`
    *Alias for show_grid for generic UI compatibility.*
  * Method: `show_processing_view(self, message)`
    *Show a temporary processing message (UI simulation).*
  * Method: `show_preview_result(self)`
    *Show the preview result after processing (UI simulation).*
  * Method: `_clear_grid(self)`
    *Remove all widgets from grid container.*
  * Method: `_clear_selection(self)`
    *Deselect semua cards.*
  * Method: `_select_range(self, start_card_id, end_card_id)`
    *Select range antara dua cards.*
    *Args:*
    *start_card_id: ID card awal range*
    *end_card_id: ID card akhir range*
  * Method: `_load_thumbnail_async(self, image_path, card_widget)`
    *Load thumbnail asinkron untuk image card.*
    *Args:*
    *image_path: Path ke image file*
    *card_widget: ImageCard widget untuk display thumbnail*
  * Method: `_on_card_clicked(self, card_id, event, card_widget)`
    *Handle click pada image card untuk selection dengan multi-select support.*
    *- Single Click: Toggle selection single item*
    *- Ctrl + Click: Add/remove individual item (multi-select)*
    *- Shift + Click: Select range dari last selected ke current*
    *Args:*
    *card_id: ID dari card*
    *event: QMouseEvent dari click*
    *card_widget: Card widget reference*
  * Method: `_on_card_double_clicked(self, card_id)`
    *Handle double-click pada image card untuk preview full resolution.*
    *Args:*
    *card_id: ID dari card yang di-click*
  * Method: `_display_image_preview(self, image_path)`
    *Display single image preview di Zoomable view dengan full resolution.*
    *Args:*
    *image_path: Path ke image file untuk di-preview*
  * Method: `_on_preview_process_clicked(self)`
    *Handle 'Preview Process' button click from Grid.*
  * Method: `_on_result_changed(self, value)`
    *Handle dropdown selection change.*
  * Method: `display_processed_result(self, image_path, update_dropdown)`
    *Display processed result image in Compare Mode (Default).*
    *Loads Original + Processed into ComparisonGraphicsItem.*
  * Method: `check_result_availability(self)`
    *Check if results exist for current batch and update 'Preview Process' button.*
  * Method: `show_grid(self)`
    *Switch ke Grid View.*
  * Method: `show_preview(self)`
    *Switch ke Preview View.*
  * Method: `remove_selected_images(self)`
    *Remove currently selected images dari grid.*
  * Method: `get_selected_image_list(self)`
    *Get list of selected image paths.*
  * Method: `set_header_title(self, text)`
    *Sets the text of the header title.*
  * Method: `_setup_delete_confirmation_widget(self)`
    *Create and configure the delete confirmation widget.*
  * Method: `show_delete_confirmation(self, batch_ids, batch_names)`
    *Switch to the delete confirmation view and pass batch info.*
    *Args:*
    *batch_ids: List of batch IDs to be deleted.*
    *batch_names: List of batch names to display.*
  * Method: `_delete_confirmed_batches(self)`
    *Handle the actual deletion after confirmation.*
  * Method: `dragEnterEvent(self, event)`
    *Accept drag enter event jika ada image files dalam supported formats.*
  * Method: `dragLeaveEvent(self, event)`
    *Reset style saat drag leave.*
  * Method: `dropEvent(self, event)`
    *Handle drop event untuk image import.*
    *Emit signal dengan file paths untuk parent widget.*
  * Method: `import_images(self)`
    *Membuka dialog file untuk impor gambar dengan format dari config.SUPPORTED_FORMATS.*
    *Mirip dengan panorama page import_images method.*
    *----------------------------------------*

--------------------

### 📄 [display_thumbnail.py](file:///e:/APP%20Developer/Pixel%20Refine/pixel_refine_desktop/ui/views/panorama/display_area/display_thumbnail.py)

* **Class**: `ThumbnailWidget`
    *Widget kustom untuk setiap thumbnail, menggunakan paintEvent untuk seleksi.*
  * Method: `__init__(self, image_path, parent)`
  * Method: `set_pixmap(self, pixmap)`
  * Method: `is_selected(self)`
    *Getter: Mengembalikan status terpilih.*
  * Method: `set_selected(self, selected)`
    *Setter: Mengatur status terpilih dan memicu penggambaran ulang.*
  * Method: `paintEvent(self, event)`
    *Menggambar widget. Dipanggil secara otomatis oleh Qt saat 'update()' dipanggil.*
  * Method: `mousePressEvent(self, event)`
  * Method: `mouseDoubleClickEvent(self, event)`
    *----------------------------------------*

--------------------

### 📄 [thumbnail_preview.py](file:///e:/APP%20Developer/Pixel%20Refine/pixel_refine_desktop/ui/views/panorama/display_area/thumbnail_preview.py)

* **Class**: `ImagePreviewDialog`
    *Dialog yang menampilkan gambar dengan orientasi dan ukuran awal yang benar.*
  * Method: `__init__(self, image_path, parent)`
  * Method: `set_adaptive_initial_size(self, width_ratio, height_ratio)`
    *Mengatur ukuran dan posisi awal dialog agar relatif terhadap ukuran layar.*
  * Method: `load_pixmap_with_correct_orientation(self, image_path)`
    *Membuka file gambar menggunakan Pillow, menerapkan orientasi EXIF,*
    *dan mengonversinya menjadi QPixmap.*
  * Method: `showEvent(self, event)`
    *Dipanggil secara otomatis oleh Qt setelah dialog ditampilkan.*
    *Ini adalah tempat yang tepat untuk melakukan 'fitInView'.*
  * Method: `resizeEvent(self, event)`
    *Opsional, tapi sangat disarankan: Lakukan fitInView lagi saat jendela di-resize.*
    *----------------------------------------*

--------------------


## 📂 Directory: `Root Directory`

### 📄 [# DIRECTORY: pixel_refine_desktop/ui/views/panorama/logic](file:///e:/APP%20Developer/Pixel%20Refine/# DIRECTORY: pixel_refine_desktop/ui/views/panorama/logic)


--------------------


## 📂 Directory: `Root Directory`

### 📄 [BatchProcessPano.py](file:///e:/APP%20Developer/Pixel%20Refine/pixel_refine_desktop/ui/views/panorama/logic/BatchProcessPano.py)

* **Class**: `BatchProcessDialog`
    *Dialog Batch: Murni visual. Tidak ada logika thread di baliknya.*
  * Method: `__init__(self, projects_list, parent)`
  * Method: `_setup_ui(self)`
  * Method: `_populate_table(self)`
  * Method: `_simulate_process(self)`
    *Ubah status tabel secara visual saja.*
    *----------------------------------------*

--------------------

### 📄 [DynamicPanel.py](file:///e:/APP%20Developer/Pixel%20Refine/pixel_refine_desktop/ui/views/panorama/logic/DynamicPanel.py)

* **Class**: `DynamicFlowPanel`
    *Sebuah panel yang secara dinamis mengubah layout anaknya dari*
    *horizontal menjadi vertikal jika tidak ada cukup ruang.*
  * Method: `__init__(self, horizontal_threshold, parent)`
  * Method: `addWidget(self, widget)`
    *Menambahkan widget ke dalam manajemen panel ini.*
  * Method: `_reapply_layout(self, new_layout)`
    *Menghapus layout lama dan menerapkan yang baru.*
  * Method: `resizeEvent(self, event)`
    *Dipanggil setiap kali ukuran widget berubah.*

* **Class**: `FlowLayout`
    *Layout kustom Qt yang membungkus (wraps) item dari atas ke bawah,*
    *lalu memulai kolom baru jika ruang vertikal habis.*
  * Method: `__init__(self, parent, margin, spacing)`
  * Method: `__del__(self)`
  * Method: `addItem(self, item)`
  * Method: `count(self)`
  * Method: `itemAt(self, index)`
  * Method: `takeAt(self, index)`
  * Method: `expandingDirections(self)`
  * Method: `hasHeightForWidth(self)`
  * Method: `heightForWidth(self, width)`
  * Method: `setGeometry(self, rect)`
  * Method: `sizeHint(self)`
  * Method: `minimumSize(self)`
  * Method: `doLayout(self, rect, testOnly)`
    *Inti dari layout: mengatur posisi semua item.*
    *----------------------------------------*

--------------------

### 📄 [panorama_algorithms.py](file:///e:/APP%20Developer/Pixel%20Refine/pixel_refine_desktop/ui/views/panorama/logic/panorama_algorithms.py)

* **Function**: `run_projection(aligned_data, settings, progress_callback)`

* **Function**: `run_blending(projected_data, settings, progress_callback)`
    *----------------------------------------*

--------------------

### 📄 [processing_view.py](file:///e:/APP%20Developer/Pixel%20Refine/pixel_refine_desktop/ui/views/panorama/logic/processing_view.py)

* **Class**: `ProcessingView`
    *Widget kontainer adaptif yang menskalakan kontennya (judul, progress bar)*
    *berdasarkan ukurannya sendiri.*
  * Method: `__init__(self, parent)`
  * Method: `update_progress(self, title, value)`
    *Memperbarui judul, persentase, dan bar progress.*
  * Method: `_update_adaptive_styles(self)`
    *Menghitung ulang dan menerapkan semua ukuran adaptif (font, tinggi bar, margin).*
  * Method: `showEvent(self, event)`
    *Panggil pembaruan gaya saat widget pertama kali ditampilkan.*
  * Method: `resizeEvent(self, event)`
    *Panggil pembaruan gaya setiap kali ukuran widget berubah.*
    *----------------------------------------*

--------------------


## 📂 Directory: `Root Directory`

### 📄 [# DIRECTORY: pixel_refine_desktop/ui/views/panorama/workflow_area](file:///e:/APP%20Developer/Pixel%20Refine/# DIRECTORY: pixel_refine_desktop/ui/views/panorama/workflow_area)


--------------------


## 📂 Directory: `Root Directory`

### 📄 [workflow_panel.py](file:///e:/APP%20Developer/Pixel%20Refine/pixel_refine_desktop/ui/views/panorama/workflow_area/workflow_panel.py)

* **Class**: `WorkflowPanel`
    *Panel Bawah: Form Pengaturan.*
    *Murni Layout Widget. Semua Tab diaktifkan untuk demo UI.*
  * Method: `__init__(self, parent)`
  * Method: `_setup_ui(self)`
  * Method: `_create_align_ui(self)`
  * Method: `_create_proj_ui(self)`
  * Method: `_create_blend_ui(self)`
  * Method: `update_workflow_stage(self, stage, has_images)`
    *Memperbarui state UI berdasarkan progres.*
  * Method: `_update_tab_states(self)`
    *Mengaktifkan/menonaktifkan tab berdasarkan progres workflow.*
  * Method: `_update_preview_button_state(self)`
    *Memperbarui teks dan state preview button berdasarkan tab yang aktif.*
  * Method: `_on_preview_clicked(self)`
    *----------------------------------------*

--------------------


## 📂 Directory: `Root Directory`

### 📄 [# DIRECTORY: pixel_refine_desktop/ui/views/settings](file:///e:/APP%20Developer/Pixel%20Refine/# DIRECTORY: pixel_refine_desktop/ui/views/settings)


--------------------


## 📂 Directory: `Root Directory`

### 📄 [SettingPage.py](file:///e:/APP%20Developer/Pixel%20Refine/pixel_refine_desktop/ui/views/settings/SettingPage.py)

* **Class**: `SettingPage`
  * Method: `__init__(self, database_manager)`
    *----------------------------------------*

--------------------


## 📂 Directory: `Root Directory`

### 📄 [# DIRECTORY: pixel_refine_desktop/ui/views/settings/Advance](file:///e:/APP%20Developer/Pixel%20Refine/# DIRECTORY: pixel_refine_desktop/ui/views/settings/Advance)


--------------------


## 📂 Directory: `Root Directory`

### 📄 [AdvancePage.py](file:///e:/APP%20Developer/Pixel%20Refine/pixel_refine_desktop/ui/views/settings/Advance/AdvancePage.py)

* **Function**: `advance_page()`
    *----------------------------------------*

--------------------


## 📂 Directory: `Root Directory`

### 📄 [# DIRECTORY: pixel_refine_desktop/ui/views/settings/General](file:///e:/APP%20Developer/Pixel%20Refine/# DIRECTORY: pixel_refine_desktop/ui/views/settings/General)


--------------------


## 📂 Directory: `Root Directory`

### 📄 [GeneralSetting.py](file:///e:/APP%20Developer/Pixel%20Refine/pixel_refine_desktop/ui/views/settings/General/GeneralSetting.py)

* **Class**: `GeneralSettingsPage`
    *General settings page refactored using GenericUILibrary.*
    *Supports real-time auto-sync for most parameters.*
  * Method: `__init__(self, parent)`
  * Method: `_setup_ui(self)`
  * Method: `_on_apply_clicked(self)`
    *Final apply logic:*
    *1. Save language from FormGroup to store.*
    *2. Trigger restart only if language has changed.*
  * Method: `_prompt_restart(self)`

* **Function**: `general_page()`
    *Entry point for SettingPage.py*

* **Function**: `load_general_settings()`
    *Backward compatibility wrapper.*
    *Returns the current general settings from the store.*
    *----------------------------------------*

--------------------

### 📄 [general_store.py](file:///e:/APP%20Developer/Pixel%20Refine/pixel_refine_desktop/ui/views/settings/General/general_store.py)

* **Function**: `get_general_store()`
    *Returns a DataStore instance initialized with general settings.*
    *Binds it to the file path defined in config.*
    *----------------------------------------*

--------------------

### 📄 [helpers.py](file:///e:/APP%20Developer/Pixel%20Refine/pixel_refine_desktop/ui/views/settings/General/helpers.py)

* **Function**: `restart_application()`
    *Fungsi untuk merestart aplikasi baik saat dev maupun saat dibungkus Nuitka.*

* **Function**: `_show_restart_error(program, args, wd)`

* **Function**: `_show_generic_error(e)`

* **Function**: `sync_algorithm_settings(gpu_setting, multicore_setting)`
    *Sync values to Algorithm Parameter Settings File.*
    *----------------------------------------*

--------------------


## 📂 Directory: `Root Directory`

### 📄 [# DIRECTORY: pixel_refine_desktop/ui/views/settings/General/Language](file:///e:/APP%20Developer/Pixel%20Refine/# DIRECTORY: pixel_refine_desktop/ui/views/settings/General/Language)


--------------------


## 📂 Directory: `Root Directory`

### 📄 [language_config.py](file:///e:/APP%20Developer/Pixel%20Refine/pixel_refine_desktop/ui/views/settings/General/Language/language_config.py)

* **Function**: `load_language_setting()`
    *----------------------------------------*

--------------------

### 📄 [lang_english.py](file:///e:/APP%20Developer/Pixel%20Refine/pixel_refine_desktop/ui/views/settings/General/Language/lang_english.py)
    *----------------------------------------*

--------------------

### 📄 [lang_indonesian.py](file:///e:/APP%20Developer/Pixel%20Refine/pixel_refine_desktop/ui/views/settings/General/Language/lang_indonesian.py)
    *----------------------------------------*

--------------------

### 📄 [lang_melayu.py](file:///e:/APP%20Developer/Pixel%20Refine/pixel_refine_desktop/ui/views/settings/General/Language/lang_melayu.py)
    *----------------------------------------*

--------------------

### 📄 [lang_simplified_china.py](file:///e:/APP%20Developer/Pixel%20Refine/pixel_refine_desktop/ui/views/settings/General/Language/lang_simplified_china.py)
    *----------------------------------------*

--------------------


## 📂 Directory: `Root Directory`

### 📄 [# DIRECTORY: pixel_refine_desktop/ui/views/settings/Perfomance](file:///e:/APP%20Developer/Pixel%20Refine/# DIRECTORY: pixel_refine_desktop/ui/views/settings/Perfomance)


--------------------


## 📂 Directory: `Root Directory`

### 📄 [PerformancePage.py](file:///e:/APP%20Developer/Pixel%20Refine/pixel_refine_desktop/ui/views/settings/Perfomance/PerformancePage.py)

* **Function**: `performance_page()`
    *----------------------------------------*

--------------------


## 📂 Directory: `Root Directory`

### 📄 [# DIRECTORY: pixel_refine_desktop/ui/views/settings/views](file:///e:/APP%20Developer/Pixel%20Refine/# DIRECTORY: pixel_refine_desktop/ui/views/settings/views)


--------------------


## 📂 Directory: `Root Directory`

### 📄 [settings_view.py](file:///e:/APP%20Developer/Pixel%20Refine/pixel_refine_desktop/ui/views/settings/views/settings_view.py)

* **File Overview**:
    *Settings View (MVC).*
    *Inherits from legacy SettingPage to maintain all functionality.*

* **Class**: `SettingsView`
    *Settings view with MVC architecture.*
    *Inherits from legacy SettingPage - simple wrapper for consistency.*
  * Method: `__init__(self, db_path, parent)`
    *----------------------------------------*

--------------------


## 📂 Directory: `Root Directory`

### 📄 [# DIRECTORY: pixel_refine_mobile/core](file:///e:/APP%20Developer/Pixel%20Refine/# DIRECTORY: pixel_refine_mobile/core)


--------------------


## 📂 Directory: `Root Directory`

### 📄 [app_state.py](file:///e:/APP%20Developer/Pixel%20Refine/pixel_refine_mobile/core/app_state.py)

* **Class**: `AppState`
    *Core state manager setara dengan 'app_manager' di Desktop.*
    *Mengelola ScreenManager dan transisi antar halaman.*
  * Method: `__init__(self)`
  * Method: `_init_screens(self)`
  * Method: `get_root_widget(self)`
    *----------------------------------------*

--------------------

### 📄 [theme_config.py](file:///e:/APP%20Developer/Pixel%20Refine/pixel_refine_mobile/core/theme_config.py)

* **Function**: `load_kv_files()`
    *Muat semua file .kv dari folder ui/kv secara dinamis*
    *sebelum aplikasi utama dibangun.*
    *----------------------------------------*

--------------------


## 📂 Directory: `Root Directory`

### 📄 [# DIRECTORY: pixel_refine_mobile/ui/screens](file:///e:/APP%20Developer/Pixel%20Refine/# DIRECTORY: pixel_refine_mobile/ui/screens)


--------------------


## 📂 Directory: `Root Directory`

### 📄 [denoising_screen.py](file:///e:/APP%20Developer/Pixel%20Refine/pixel_refine_mobile/ui/screens/denoising_screen.py)

* **Class**: `DenoisingScreen`
    *Denoising Workspace Screen.*
    *Handles the 60-15-25 layout for main editing.*
  * Method: `import_images(self)`
  * Method: `run_algorithm(self)`
  * Method: `_simulate_progress(self, dt)`
  * Method: `go_back(self)`
    *----------------------------------------*

--------------------

### 📄 [home_screen.py](file:///e:/APP%20Developer/Pixel%20Refine/pixel_refine_mobile/ui/screens/home_screen.py)

* **Class**: `HomeScreen`
    *View logic for the Home Screen.*
    *Handles user interaction with the Denoising, HDR, and Panorama cards.*
  * Method: `open_tool_projects(self, tool_name)`
    *----------------------------------------*

--------------------

### 📄 [project_screen.py](file:///e:/APP%20Developer/Pixel%20Refine/pixel_refine_mobile/ui/screens/project_screen.py)

* **Class**: `ProjectScreen`
    *Generic Project Screen that acts as an explorer for Recent and Other projects.*
    *It adapts to the tool chosen from the Home Screen (Denoising, HDR Stack, or Panorama).*
  * Method: `on_enter(self)`
  * Method: `refresh_project_list(self)`
  * Method: `go_back(self)`
  * Method: `create_new_project(self)`
    *----------------------------------------*

--------------------

### 📄 [welcome_screen.py](file:///e:/APP%20Developer/Pixel%20Refine/pixel_refine_mobile/ui/screens/welcome_screen.py)

* **Class**: `WelcomeScreen`
    *View logic for the Welcome Screen.*
    *Handles the initial loading animation and transition to the Home Screen.*
  * Method: `on_enter(self)`
  * Method: `start_loading(self, dt)`
  * Method: `update_progress(self, dt)`
    *----------------------------------------*

--------------------

### 📄 [workspace_screen.py](file:///e:/APP%20Developer/Pixel%20Refine/pixel_refine_mobile/ui/screens/workspace_screen.py)

* **Class**: `WorkspaceScreen`
  * Method: `on_enter(self)`
  * Method: `run_algorithm(self)`
  * Method: `go_back(self)`
    *----------------------------------------*

--------------------


## 📂 Directory: `Root Directory`

### 📄 [# DIRECTORY: taichi_library](file:///e:/APP%20Developer/Pixel%20Refine/# DIRECTORY: taichi_library)


--------------------


## 📂 Directory: `Root Directory`

### 📄 [setup.py](file:///e:/APP%20Developer/Pixel%20Refine/taichi_library/setup.py)
    *----------------------------------------*

--------------------


## 📂 Directory: `Root Directory`

### 📄 [# DIRECTORY: taichi_library/taichi_algorithm](file:///e:/APP%20Developer/Pixel%20Refine/# DIRECTORY: taichi_library/taichi_algorithm)


--------------------


## 📂 Directory: `Root Directory`

### 📄 [area_interpolation.py](file:///e:/APP%20Developer/Pixel%20Refine/taichi_library/taichi_algorithm/area_interpolation.py)

* **File Overview**:
    *Area Interpolation (INTER_AREA) - Taichi AOT Implementation*
    *===========================================================*
    *High-quality downscaling using pixel area relation.*
    *Prevents aliasing by integrating contribution of source pixels.*
    *----------------------------------------*

--------------------

### 📄 [bicubic_interpolation.py](file:///e:/APP%20Developer/Pixel%20Refine/taichi_library/taichi_algorithm/bicubic_interpolation.py)

* **Function**: `bicubic_resize(src, target_h, target_w, dst, buffer_provider, g, src_arg, dst_arg, h_src_arg, w_src_arg, h_dst_arg, w_dst_arg, is_rgb_aot)`
    *Smart bicubic resize API that auto-detects input type and returns appropriate output.*
    ***Full GPU Pipeline Support:***
    *- If input is Taichi field → stays on GPU, returns Taichi field*
    *- If input is NumPy array → uploads to GPU, processes, downloads to NumPy*
    *All Taichi operations are synchronized via @ti_thread.*
    *Args:*
    *src: Input image (NumPy array or Taichi field)*
    *target_h: Target height*
    *target_w: Target width*
    *dst: Optional pre-allocated output buffer*
    *buffer_provider: Pool provider for GPU allocations*
    *Returns:*
    *Resized image (same type as input unless dst is provided)*

* **Function**: `sample_at_bicubic(img, x, y, channel)`
    *Sample image at fractional coordinates using bicubic interpolation.*
    *High-level API for point-wise bicubic sampling - perfect for:*
    *- Warping with optical flow*
    *- Subpixel refinement in alignment*
    *- Custom geometric transformations*
    *Args:*
    *img: Input image (H, W) for grayscale or (H, W, C) for color*
    *x: X coordinate (can be fractional, e.g., 10.5)*
    *y: Y coordinate (can be fractional, e.g., 20.3)*
    *channel: Optional channel index for multi-channel images (0, 1, 2, etc.)*
    *If None and image is multi-channel, returns all channels as array*
    *Returns:*
    *Interpolated pixel value(s) at (x, y)*
    *Note:*
    *For faster (but lower quality) sampling, use ta.sample_at_bilinear()*
    *Example:*
    *>>> # Single point sampling for warping*
    *>>> value = ta.sample_at_bicubic(image, 10.5, 20.3)*
    *>>>*
    *>>> # Sample specific channel (e.g., green channel)*
    *>>> green_val = ta.sample_at_bicubic(rgb_image, 10.5, 20.3, channel=1)*

* **Function**: `sample_at(img, x, y, channel)`
    *Alias for sample_at_bicubic() for backward compatibility.*
    *Note: Use sample_at_bicubic() for explicit algorithm specification.*

* **Function**: `bicubic_resize_gpu(src_gpu, target_h, target_w, dst_gpu)`
    *----------------------------------------*

--------------------

### 📄 [bilateral_grid.py](file:///e:/APP%20Developer/Pixel%20Refine/taichi_library/taichi_algorithm/bilateral_grid.py)

* **File Overview**:
    *Bilateral Grid - Taichi AOT Implementation*
    *==========================================*
    *Fast, edge-preserving smoothing using a bilateral grid.*
    *Refactored for AOT compatibility with split kernels.*

* **Function**: `bilateral_grid_filter(img, dst, s_s, s_r, sigma_s, sigma_r)`
    *----------------------------------------*

--------------------

### 📄 [bilinear_interpolation.py](file:///e:/APP%20Developer/Pixel%20Refine/taichi_library/taichi_algorithm/bilinear_interpolation.py)

* **Function**: `bilinear_resize(src, target_h, target_w, dst, buffer_provider)`
    *Smart bilinear resize API that auto-detects input type and returns appropriate output.*
    ***Full GPU Pipeline Support:***
    *- If input is Taichi field → stays on GPU, returns Taichi field*
    *- If input is NumPy array → uploads to GPU, processes, downloads to NumPy*
    *All Taichi operations are synchronized via @ti_thread.*
    *Args:*
    *src: Input image - can be NumPy array OR Taichi ndarray*
    *target_h: Target height*
    *target_w: Target width*
    *dst: Optional pre-allocated output buffer (must match input type)*
    *Returns:*
    *Resized image in the same format as input (NumPy or Taichi)*

* **Function**: `bilinear_resize_gpu(src_gpu, target_h, target_w, dst_gpu)`
    *DEPRECATED: Use bilinear_resize() instead.*

* **Function**: `bilinear_upsample_2x(src)`

* **Function**: `bilinear_downsample_2x(src)`

* **Function**: `sample_at_bilinear(img, x, y, channel)`
    *Sample image at fractional coordinates using bilinear interpolation.*
    *----------------------------------------*

--------------------

### 📄 [box_filter.py](file:///e:/APP%20Developer/Pixel%20Refine/taichi_library/taichi_algorithm/box_filter.py)

* **File Overview**:
    *Box Filter - Taichi GPU (Final Legendary Restoration: Fused 3x3 + Separable Generic)*

* **Function**: `box_filter(src, dst, kernel_size, buffer_provider, enable_tiling)`

* **Function**: `box_filter_2d(src, dst, kernel_size)`
    *----------------------------------------*

--------------------

### 📄 [common.py](file:///e:/APP%20Developer/Pixel%20Refine/taichi_library/taichi_algorithm/common.py)

* **File Overview**:
    *Common Utilities for Taichi Algorithms*
    *======================================*
    *Shared functions for buffer management, type checking, and common operations.*

* **Class**: `BufferCache`
    *Simple pool for re-using Taichi fields to avoid allocation overhead and OOM.*
    *Keyed by (shape, dtype).*
  * Method: `__init__(self)`
  * Method: `get_buffer(self, shape, dtype)`
  * Method: `release_buffer(self, buf)`
  * Method: `clear(self)`
    *Release all held buffers and reset pool.*

* **Function**: `_get_aot()`

* **Function**: `get_temp_buffer(shape, dtype, buffer_provider)`
    *Get a temporary Taichi field/ndarray, optionally from a buffer provider.*
    *Args:*
    *shape: Tuple of dimensions.*
    *dtype: Taichi data type (e.g., ti.f32).*
    *buffer_provider: Optional callable that returns a buffer.*
    *Returns:*
    *ti.ndarray or similar field.*

* **Function**: `release_temp_buffer(buf)`
    *Return buffer to pool if applicable.*

* **Function**: `cleanup_cache()`
    *Clear the global buffer cache to free GPU memory.*

* **Function**: `ensure_taichi_field(arr, dtype, shape, buffer_provider)`
    *Ensure the input is a Taichi field/ndarray.*
    *If numpy, uploads to a new GPU buffer (using provider if specified).*
    *Args:*
    *arr: Input array (numpy or taichi).*
    *dtype: Desired Taichi data type (if creating new).*
    *shape: Desired shape (if creating new).*
    *buffer_provider: 'pool' or callable.*
    *Returns:*
    *(field, is_created_temporarily)*

* **Function**: `to_numpy_if_needed(field, was_numpy, out)`
    *Convert back to numpy if the original input was numpy, or if explicitly requested.*
    *Args:*
    *field: Taichi field.*
    *was_numpy: Boolean, true if we should return numpy.*
    *out: Optional numpy array to write into.*
    *Returns:*
    *Numpy array or Taichi field.*

* **Function**: `_copy_field_lowlevel(src, dst)`
    *Low-level copy (requires pre-allocated dst).*

* **Function**: `copy_field(src, dst)`
    *Copy Taichi field from src to dst (in-place).*
    *Args:*
    *src: Source Taichi field*
    *dst: Destination Taichi field (must be pre-allocated with same shape)*

* **Function**: `_extract_channel_lowlevel(src, dst, channel)`
    *Low-level extract (requires pre-allocated dst).*

* **Function**: `_insert_channel_lowlevel(src, dst, channel)`
    *Low-level insert (requires pre-allocated dst).*

* **Function**: `split(img)`
    *Split multi-channel image into tuple of single-channel images.*
    *AOT-Aware: Dispatches to AOT module if AOT_MODE=1*

* **Function**: `merge(channels)`
    *Merge separate channels into multi-channel image.*
    *AOT-Aware: Dispatches to AOT module if AOT_MODE=1*

* **Function**: `extract_channel(img, ch)`
    *Extract single channel from multi-channel image.*
    *AOT-Aware: Dispatches to AOT module if AOT_MODE=1*

* **Function**: `insert_channel(src, dst, ch)`
    *Insert single channel into multi-channel image (in-place).*
    *OpenCV-compatible: Same as cv2.insertChannel()*
    ***Full GPU Pipeline Support:***
    *- Works with both NumPy and Taichi field inputs*
    *- Modifies dst in-place*
    *Args:*
    *src: Single-channel image (H, W) - NumPy or Taichi field*
    *dst: Multi-channel image (H, W, C) - modified in-place*
    *ch: Channel index (0, 1, 2, ...)*
    *Example:*
    *>>> # NumPy workflow*
    *>>> ta.insert_channel(green_modified, rgb, ch=1)*
    *>>> # Same as: cv2.insertChannel(green_modified, rgb, 1)*
    *>>> # GPU workflow (in-place on GPU!)*
    *>>> ta.insert_channel(green_gpu, rgb_gpu, ch=1)*

* **Function**: `copy(img)`
    *Copy image (auto-allocates output).*
    *AOT-Aware: Dispatches to AOT module if AOT_MODE=1*

* **Function**: `cvtColor(src, code, dst)`
    *Convert image color space.*
    *AOT-Aware: Dispatches to AOT module if AOT_MODE=1*

* **Function**: `absdiff(src1, src2, dst)`
    *Calculate absolute difference between two images.*
    *OpenCV-compatible: Same as cv2.absdiff()*

* **Function**: `generate_hanning_window_2d(shape, exclude_boundary, dtype)`
    *Generate 2D Hanning window directly on GPU.*
    *exclude_boundary: If True, behaves like np.hanning(M + 2)[1:-1]*

* **Function**: `mean_division(sum_img, sum_weight, ref_img, dst)`
    *Perform final mean division and fallback on GPU.*
    *----------------------------------------*

--------------------

### 📄 [enhance_image.py](file:///e:/APP%20Developer/Pixel%20Refine/taichi_library/taichi_algorithm/enhance_image.py)

* **File Overview**:
    *Grayscale Image Enhancement (1D LUT & Micro-Contrast) - Taichi GPU*

* **Function**: `enhance_grayscale(src, blur, lut, micro_contrast, clarity, noise_coring, dst, buffer_provider)`
    *GPU-accelerated Grayscale Image Enhancement (1D LUT & Micro-Contrast & Clarity).*
    *Applies detail-boosting (micro-contrast) via difference from blurred image,*
    *clarity via midtone-targeted local contrast,*
    *and shapes global contrast via a 1D Look-Up Table (LUT) - all in a single GPU pass.*
    *All Taichi operations are synchronized via @ti_thread.*
    *Args:*
    *src:             Input luma image - NumPy array OR Taichi ndarray. (H, W)*
    *blur:            Blurred luma image - NumPy array OR Taichi ndarray. (H, W)*
    *lut:             1D Look-Up Table (256 elements) - NumPy array OR Taichi ndarray.*
    *micro_contrast:  Scale factor to boost high-frequency details. Calibrated default: 2.93.*
    *clarity:         Local contrast clarity factor.*
    *noise_coring:    Threshold to suppress low-amplitude noise boosting.*
    *dst:             Optional pre-allocated output buffer (H, W).*
    *buffer_provider: Optional buffer pool provider ("pool" or None).*
    *Returns:*
    *Enhanced grayscale image in the same format as input (NumPy or Taichi).*
    *----------------------------------------*

--------------------

### 📄 [fft.py](file:///e:/APP%20Developer/Pixel%20Refine/taichi_library/taichi_algorithm/fft.py)

* **File Overview**:
    *Efficient 2D FFT Implementation in Taichi*
    *=========================================*

* **Function**: `_is_power_of_two(n)`

* **Function**: `_next_power_of_two(n)`

* **Function**: `fft_1d_gpu(data_gpu, is_inverse, is_col)`

* **Function**: `fft2(src)`

* **Function**: `ifft2(complex_gpu, target_shape)`
    *----------------------------------------*

--------------------

### 📄 [gaussian.py](file:///e:/APP%20Developer/Pixel%20Refine/taichi_library/taichi_algorithm/gaussian.py)

* **File Overview**:
    *Gaussian Blur - Taichi GPU (High-Performance Static Unrolled)*

* **Function**: `compute_gaussian_weights(sigma, radius)`

* **Function**: `gaussian_blur(src, dst, sigma, kernel_size, buffer_provider)`
    *----------------------------------------*

--------------------

### 📄 [gaussian_window.py](file:///e:/APP%20Developer/Pixel%20Refine/taichi_library/taichi_algorithm/gaussian_window.py)

* **File Overview**:
    *Gaussian Window - Taichi GPU*

* **Function**: `create_gaussian_window(height, width, sigma)`
    *Supports both NumPy and Taichi ndarrays.*
    *----------------------------------------*

--------------------

### 📄 [gradients.py](file:///e:/APP%20Developer/Pixel%20Refine/taichi_library/taichi_algorithm/gradients.py)

* **File Overview**:
    *Gradients - Taichi GPU*
    *======================*
    *Sobel and Laplacian edge detection.*

* **Function**: `sobel(src, dst_dx, dst_dy, buffer_provider, enable_tiling)`
    *Compute Sobel gradients.*
    *Returns (dx, dy).*
    *Caller responsible for releasing if pool used.*

* **Function**: `laplacian(src, dst, buffer_provider, enable_tiling)`
    *Compute Laplacian.*
    *----------------------------------------*

--------------------

### 📄 [Hamilton_demosaice.py](file:///e:/APP%20Developer/Pixel%20Refine/taichi_library/taichi_algorithm/Hamilton_demosaice.py)

* **File Overview**:
    *Hamilton-Adams GPU-Accelerated RAW Demosaicing (Strict C++ AOT-Only Module)*

* **Function**: `hamilton_demosaic(bayer, wb_r, wb_g1, wb_b, wb_g2, cmatrix, black_level, white_level, c00, c01, c10, c11, dst, buffer_provider)`
    *GPU-Accelerated 3-Pass Hamilton-Adams Demosaicing (RAW to sRGB via strict C++ AOT).*
    *Args:*
    *bayer:           Input RAW Bayer sensor image - NumPy array OR Taichi ndarray. (H, W)*
    *wb_r, wb_g1,*
    *wb_b, wb_g2:     Normalized White Balance gains for R, G1, B, G2.*
    *cmatrix:         3x3 Camera-to-sRGB conversion matrix.*
    *black_level:     Sensor black level (float).*
    *white_level:     Sensor white saturation level (float).*
    *c00, c01,*
    *c10, c11:        Bayer pattern 2x2 grid values (0=R, 1=G, 2=B, 3=G).*
    *dst:             Optional pre-allocated destination buffer (H, W, 3).*
    *buffer_provider: Unused, kept for API compatibility.*
    *Returns:*
    *Demosaiced RGB image in the same format as input (NumPy or Taichi).*
    *----------------------------------------*

--------------------

### 📄 [joint_bilateral_guidance.py](file:///e:/APP%20Developer/Pixel%20Refine/taichi_library/taichi_algorithm/joint_bilateral_guidance.py)

* **File Overview**:
    *Joint Bilateral Filter & JBLU - Taichi GPU Implementation*
    *==========================================================*
    *General-purpose edge-preserving filter + guided upsampler.*
    *Modes:*
    *1. joint_bilateral_filter()   - Post-processor for any image/flow/scalar*
    *2. joint_bilateral_upsample() - JBLU for upscaling low-res maps with hi-res guide*

* **Function**: `_get_sigma_args(preset)`

* **Function**: `joint_bilateral_filter(src, guide, preset, radius, buffer_provider)`
    *General-purpose Joint Bilateral Filter.*

* **Function**: `joint_bilateral_upsample(src_low, guide_hi, preset, buffer_provider)`
    *Joint Bilateral Upsampling (JBLU).*
    *----------------------------------------*

--------------------

### 📄 [median_filter.py](file:///e:/APP%20Developer/Pixel%20Refine/taichi_library/taichi_algorithm/median_filter.py)

* **File Overview**:
    *Median Filter - Taichi GPU*

* **Function**: `median_filter(src, dst, kernel_size, buffer_provider, enable_tiling)`
    *Supports both NumPy and Taichi ndarrays.*

* **Function**: `median_filter_flow(src, dst, kernel_size, buffer_provider, enable_tiling)`
    *Supports both NumPy and Taichi ndarrays.*

* **Function**: `confidence_weighted_median_filter_flow(src, confidence, dst, buffer_provider)`
    *Apply confidence-weighted regularization to the flow field.*
    *----------------------------------------*

--------------------

### 📄 [ncc.py](file:///e:/APP%20Developer/Pixel%20Refine/taichi_library/taichi_algorithm/ncc.py)

* **Function**: `zncc(image, template)`
    *Entry point for ZNCC alignment.*

* **Function**: `match_template(image, template, method)`
    *Compatibility wrapper for OpenCV-style template matching.*

* **Function**: `global_translate_zncc(image, template)`
    *Compatibility wrapper for global translation.*
    *----------------------------------------*

--------------------

### 📄 [nearest_interpolation.py](file:///e:/APP%20Developer/Pixel%20Refine/taichi_library/taichi_algorithm/nearest_interpolation.py)

* **Function**: `nearest_resize(src, target_h, target_w, dst)`
    *Smart nearest resize API that auto-detects input type and returns appropriate output.*
    *All Taichi operations are synchronized via @ti_thread.*

* **Function**: `nearest_resize_gpu(src_gpu, target_h, target_w, dst_gpu)`
    *----------------------------------------*

--------------------

### 📄 [ofb.py](file:///e:/APP%20Developer/Pixel%20Refine/taichi_library/taichi_algorithm/ofb.py)

* **Function**: `get_circle_offset(i)`
    *Mendapatkan offset koordinat untuk 16 piksel lingkaran FAST.*

* **Function**: `compute_dynamic_fast_score(src, y, x)`

* **Function**: `compute_score_map(src, score_map, h, w, margin)`
    *Pass 1: Membangun peta skor FAST dinamis dengan margin sensor.*

* **Function**: `extract_grid_keypoints(score_map, keypoints, counter, h, w, grid_size, threshold)`
    *Pass 2: Adaptive Non-Maximal Suppression (ANMS) Berbasis Grid dengan filter threshold.*

* **Function**: `compute_centroid_angle(src, cy, cx, h, w)`
    *Menghitung sudut orientasi centroid intensitas untuk kebal rotasi.*

* **Function**: `get_pixel_nearest(src, y, x, h, w)`
    *Mendapatkan nilai piksel terdekat dengan validasi batas gambar.*

* **Function**: `_compute_descriptors_kernel(src, kps, pattern, desc, h, w, num_kps)`
    *Mengekstrak deskriptor Oriented BRIEF 256-bit di GPU.*

* **Function**: `popcount32(x)`
    *Algoritma paralel O(1) Popcount untuk menghitung jumlah bit 1.*

* **Function**: `_hamming_matcher_kernel(desc1, desc2, matches, num_kps1, num_kps2, ratio_threshold)`
    *Pencocokan Hamming Matcher dengan Lowe's Ratio Test di GPU.*
    *----------------------------------------*

--------------------

### 📄 [oom_guard.py](file:///e:/APP%20Developer/Pixel%20Refine/taichi_library/taichi_algorithm/oom_guard.py)

* **File Overview**:
    *OOM Guard*
    *=========*
    *Provides safe execution of Taichi algorithms on arbitrary resolution images*
    *by using Tiled Processing (Chunking) with overlap support.*
    *Ensures seamless results identical to full-frame processing.*

* **Function**: `get_available_vram_mb()`
    *Get available VRAM in MB.*
    *Tries nvidia-smi, then assumes a conservative default if failed.*

* **Function**: `should_tile(image, channels, dtype_size, safety_factor, fixed_threshold)`
    *Determine if tiling is necessary based on available VRAM.*
    *Args:*
    *image: Numpy array or Tuple (H, W, ...).*
    *channels: Channels if image is shape tuple or verification needed.*
    *dtype_size: Bytes per pixel per channel (float32 = 4).*
    *safety_factor: Fraction of free VRAM we are allowed to use.*
    *fixed_threshold: Fallback threshold in pixels (default 30MP).*

* **Function**: `get_safe_tile_size(channels, safety_factor)`
    *Calculate maximum safe tile size based on available VRAM.*
    *Returns size (width/height) as int.*

* **Function**: `execute_tiled(func, src, overlap, tile_size, progress_callback)`
    *Execute a Taichi function on a large image using tiling.*
    *Args:*
    *func: The GPU function to call (e.g. gaussian_blur).*
    *src: Input NumPy array (H, W, C).*
    *overlap: Pixels of overlap to ensure seamless edges (kernel radius).*
    *tile_size: Base size of tiles. If None, calc dynamically.*
    ***kwargs: Arguments passed to func.*
    *Returns:*
    *np.ndarray: The processed image (same shape as src).*
    *----------------------------------------*

--------------------

### 📄 [phase_correlation.py](file:///e:/APP%20Developer/Pixel%20Refine/taichi_library/taichi_algorithm/phase_correlation.py)

* **File Overview**:
    *Global Motion Estimation (Phase Correlation) - Taichi GPU Implementation*
    *========================================================================*
    *Provides an extremely fast global shift estimator using frequency-domain*
    *Phase Correlation. Acts as a high-performance replacement for*
    *OpenCV's CPU phaseCorrelate.*

* **Function**: `phase_correlation(ref_layer, comp_layer, max_shift)`
    *Estimates the dominant global translation (dx, dy) between two 2D images*
    *using frequency-domain Phase Correlation.*
    *Returns:*
    *(dx, dy, response)*
    *where response is the correlation peak value [0.0, 1.0].*
    *----------------------------------------*

--------------------

### 📄 [pyramid.py](file:///e:/APP%20Developer/Pixel%20Refine/taichi_library/taichi_algorithm/pyramid.py)

* **File Overview**:
    *Image Pyramid - Taichi GPU*

* **Function**: `build_image_pyramid(image, n_levels, min_size)`
    *CPU interface: Build image pyramid and return list of NumPy arrays.*

* **Function**: `build_image_pyramid_gpu(image_gpu, n_levels, min_size, downscale_factor, buffer_provider)`
    *GPU native interface: Build image pyramid with dynamic downsampling.*
    *Args:*
    *image_gpu: Source image ti.ndarray.*
    *n_levels: Total number of levels (including full res).*
    *min_size: Minimum width or height to stop downsampling.*
    *downscale_factor: Scale factor between levels (e.g., 2, 4, 1.5).*
    *- Powers of 2: Uses high-quality cascaded 5x5 Gaussian downsampling.*
    *- Others: Uses Bilinear interpolation.*
    *buffer_provider: "pool" or "new".*

* **Function**: `build_image_pyramid_gpu_4x(image_gpu, n_levels, min_size, buffer_provider)`
    *Backward compatibility wrapper for 4x downsampling pyramid.*

* **Function**: `upsample_flow(flow, target_h, target_w, scale, buffer_provider)`
    *CPU interface: Upsample flow using NumPy input/output.*

* **Function**: `upsample_flow_gpu(src_gpu, dst_gpu, scale)`
    *GPU native interface: Upsample flow from one ti.ndarray to another.*
    *----------------------------------------*

--------------------

### 📄 [ransac.py](file:///e:/APP%20Developer/Pixel%20Refine/taichi_library/taichi_algorithm/ransac.py)

* **File Overview**:
    *RANSAC - Taichi GPU Implementation*
    *==================================*
    *GPU-accelerated RANSAC for optical flow outlier removal.*
    *Simple translation/affine model fitting with parallel inlier counting.*

* **Function**: `ransac_flow_cleanup(flow, threshold, n_iterations, buffer_provider)`
    *RANSAC-based outlier removal for optical flow.*
    *Supports both NumPy and Taichi ndarrays natively.*

* **Function**: `ransac_flow_cleanup_motion_aware(flow, threshold, motion_threshold, n_iterations, buffer_provider)`
    *Motion-aware RANSAC: Preserves local motion while cleaning global outliers.*
    *Args:*
    *flow: Input flow field*
    *threshold: RANSAC inlier threshold for global motion*
    *motion_threshold: Deviation threshold to classify local vs global motion*
    *n_iterations: Number of RANSAC iterations*
    *buffer_provider: Buffer allocation strategy*
    *Returns:*
    *Cleaned flow with local motion preserved*

* **Function**: `ransac_flow_cleanup_local(flow, block_size, threshold, n_iterations, buffer_provider)`
    *Local RANSAC - GPU Accelerated.*
    *----------------------------------------*

--------------------

### 📄 [remap.py](file:///e:/APP%20Developer/Pixel%20Refine/taichi_library/taichi_algorithm/remap.py)

* **File Overview**:
    *Remap (Image Warping) - Taichi GPU*

* **Function**: `remap(src, map_x, map_y, dst, buffer_provider)`
    *GPU-accelerated Remap (Warping) API.*
    *Interpolates input src using coordinate maps map_x and map_y.*
    *All Taichi operations are synchronized via @ti_thread.*
    *Args:*
    *src: Input image - can be NumPy array OR Taichi ndarray. (H, W) or (H, W, C)*
    *map_x: Coordinate map for X coordinates - NumPy array OR Taichi ndarray. (H_dst, W_dst)*
    *map_y: Coordinate map for Y coordinates - NumPy array OR Taichi ndarray. (H_dst, W_dst)*
    *dst: Optional pre-allocated output buffer.*
    *buffer_provider: Optional buffer pool provider ("pool" or None).*
    *Returns:*
    *Warped image in the same format as input (NumPy or Taichi).*

* **Function**: `remap_with_flow(src, flow, full_h, full_w, dst, buffer_provider)`
    *Fused GPU-accelerated Remap with Flow API.*
    *Interpolates input src using 2-channel flow field, on-the-fly interpolating flow.*
    *All Taichi operations are synchronized via @ti_thread.*
    *----------------------------------------*

--------------------

### 📄 [taichi_worker.py](file:///e:/APP%20Developer/Pixel%20Refine/taichi_library/taichi_algorithm/taichi_worker.py)

* **File Overview**:
    *Taichi Automated Thread Management (ti_thread)*
    *==============================================*
    *Fully automated persistent thread for Taichi operations.*
    *Solves CUDA context issues and minimizes overhead.*

* **Class**: `_TaichiWorker`
    *Hidden persistent thread for Taichi execution.*
  * Method: `__init__(self)`
  * Method: `_set_low_priority(self)`
    *Reduces thread priority on Windows to keep UI responsive.*
  * Method: `run(self)`
  * Method: `submit(self, func)`
    *Submit a job and wait for results (Thread-safe, non-blocking for UI).*
  * Method: `submit_and_wait(self, func)`
    *Alias for submit() for backward compatibility.*
  * Method: `submit_async(self, func)`
    *Submit a job and return a Future (Thread-safe, non-blocking).*

* **Function**: `_get_project_cache_path()`
    *Determine the project root and return the absolute path for the cache.*

* **Function**: `_get_common_module()`
    *Lazily import and cache the common module.*

* **Function**: `_get_worker()`

* **Function**: `get_taichi_worker()`
    *Public API to get the persistent worker.*

* **Function**: `ti_thread(func)`
    *Decorator: Automatically routes function execution to the persistent Taichi thread.*
    *Prevents CUDA_ERROR_INVALID_CONTEXT and minimizes startup overhead.*
    *SPECIAL CASE: If 'g' (GraphBuilder) is passed in kwargs, we bypass the worker thread*
    *to ensure graph recording happens correctly in the caller's thread/arch.*

* **Function**: `cleanup_taichi(mode)`
    *Declarative API for Taichi cleanup operations.*
    *Args:*
    *mode (str): Cleanup mode*
    *- "cache": Clear buffer cache only (fast, keeps context alive)*
    *- "memory": Clear cache + force GC (moderate)*
    *- "full": Full reset including Taichi context (slow, use sparingly)*
    *Returns:*
    *bool: True if cleanup succeeded*

* **Function**: `clear_vram()`
    *Submit a cache cleanup task to the worker thread (legacy API).*

* **Function**: `create_taichi_ndarray(arr, dtype, use_pool)`
    *Helper to create a ti.ndarray from numpy in the worker thread.*
    *Optionally uses the global buffer pool.*

* **Function**: `download_taichi_ndarray(field, out)`
    *Helper to download a ti.ndarray to numpy in the worker thread.*

* **Function**: `release_taichi_ndarray(field)`
    *Release a Taichi ndarray back to the pool.*
    *This should be called for buffers created with use_pool=True.*
    *----------------------------------------*

--------------------


## 📂 Directory: `Root Directory`

### 📄 [# DIRECTORY: taichi_library/taichi_algorithm/aot_py](file:///e:/APP%20Developer/Pixel%20Refine/# DIRECTORY: taichi_library/taichi_algorithm/aot_py)


--------------------


## 📂 Directory: `Root Directory`

### 📄 [compile_area_tcm.py](file:///e:/APP%20Developer/Pixel%20Refine/taichi_library/taichi_algorithm/aot_py/compile_area_tcm.py)

* **Function**: `compile_area_aot(arch, save_path)`
    *----------------------------------------*

--------------------

### 📄 [compile_bicubic_tcm.py](file:///e:/APP%20Developer/Pixel%20Refine/taichi_library/taichi_algorithm/aot_py/compile_bicubic_tcm.py)

* **Function**: `compile_bicubic_aot(arch, save_path)`
    *----------------------------------------*

--------------------

### 📄 [compile_bilateral_grid_tcm.py](file:///e:/APP%20Developer/Pixel%20Refine/taichi_library/taichi_algorithm/aot_py/compile_bilateral_grid_tcm.py)

* **Function**: `compile_bg_aot(arch, save_path)`
    *----------------------------------------*

--------------------

### 📄 [compile_bilinear_tcm.py](file:///e:/APP%20Developer/Pixel%20Refine/taichi_library/taichi_algorithm/aot_py/compile_bilinear_tcm.py)

* **Function**: `compile_bilinear_tcm(arch, save_path)`
    *----------------------------------------*

--------------------

### 📄 [compile_block_correlation_tcm.py](file:///e:/APP%20Developer/Pixel%20Refine/taichi_library/taichi_algorithm/aot_py/compile_block_correlation_tcm.py)

* **Function**: `compile_block_correlation_aot(arch, save_path)`
    *----------------------------------------*

--------------------

### 📄 [compile_box_filter_tcm.py](file:///e:/APP%20Developer/Pixel%20Refine/taichi_library/taichi_algorithm/aot_py/compile_box_filter_tcm.py)

* **Function**: `compile_box_filter_aot(arch, save_path)`
    *----------------------------------------*

--------------------

### 📄 [compile_cast_tcm.py](file:///e:/APP%20Developer/Pixel%20Refine/taichi_library/taichi_algorithm/aot_py/compile_cast_tcm.py)

* **Function**: `compile_cast_tcm()`
    *----------------------------------------*

--------------------

### 📄 [compile_common_tcm.py](file:///e:/APP%20Developer/Pixel%20Refine/taichi_library/taichi_algorithm/aot_py/compile_common_tcm.py)

* **Function**: `compile_common_aot(arch, save_path)`
    *----------------------------------------*

--------------------

### 📄 [compile_fft_tcm.py](file:///e:/APP%20Developer/Pixel%20Refine/taichi_library/taichi_algorithm/aot_py/compile_fft_tcm.py)

* **Function**: `compile_fft_aot(arch, save_path)`
    *----------------------------------------*

--------------------

### 📄 [compile_gaussian_tcm.py](file:///e:/APP%20Developer/Pixel%20Refine/taichi_library/taichi_algorithm/aot_py/compile_gaussian_tcm.py)

* **Function**: `compile_gaussian_tcm()`
    *----------------------------------------*

--------------------

### 📄 [compile_gradients_tcm.py](file:///e:/APP%20Developer/Pixel%20Refine/taichi_library/taichi_algorithm/aot_py/compile_gradients_tcm.py)

* **Function**: `compile_gradients_aot(arch, save_path)`
    *----------------------------------------*

--------------------

### 📄 [compile_hamilton_tcm.py](file:///e:/APP%20Developer/Pixel%20Refine/taichi_library/taichi_algorithm/aot_py/compile_hamilton_tcm.py)

* **Function**: `_preprocess_bayer_kernel(bayer, wb_bayer, wb_r, wb_g1, wb_b, wb_g2, black, white, h, w, c00, c01, c10, c11)`
    *Pass 0: Fused Pre-Processing Kernel.*
    *Performs clamping, normalization, and white balance gain scaling in a single pass.*

* **Function**: `_ha_green_interpolation_kernel_opt(wb_bayer, green, h, w, c00, c01, c10, c11)`
    *Pass 1: Hamilton-Adams Edge-Directed Green Channel Reconstruction.*
    *Optimized: standard Hamilton-Adams 1-row/col gradient estimation (no redundant loops) for 3x memory bandwidth savings.*

* **Function**: `_ha_red_blue_interpolation_kernel_opt(wb_bayer, green, cmatrix, dst, wb_r, wb_g1, wb_b, wb_g2, h, w, c00, c01, c10, c11)`
    *Pass 2: Red and Blue Reconstruction using Directional Color Difference Interpolation.*
    *Uses cached preprocessed wb_bayer for maximum performance.*

* **Function**: `_get_green_gain(nr, nc, c00, c01, c10, c11, wb_g1, wb_g2)`

* **Function**: `_ha_green_to_grayscale_1channel_fused_kernel(bayer, dst, wb_r, wb_g1, wb_b, wb_g2, black, white, h, w, c00, c01, c10, c11)`
    *FUSED 1-Channel (Grayscale Full-Res): Fuses preprocessing, normalization, white balance*
    *and fast green demosaicing into a single fast GPU pass. Eliminates temporary memory footprint entirely.*
    *Optimized: static neighborhood fetching and fast WB mapping using hardware-friendly select branches.*

* **Function**: `_ha_green_half_res_fused_kernel(bayer, dst, wb_r, wb_g1, wb_b, wb_g2, black, white, h, w, c00, c01, c10, c11)`
    *FUSED Bypass Demosaicing: Extract Green Sub-Sampling directly from RAW to 1/2 size grayscale.*
    *Executes in a single pass without intermediate VRAM buffers (saving VRAM and bandwidth).*

* **Function**: `_ha_rgb_half_res_fused_kernel(bayer, cmatrix, dst, wb_r, wb_g1, wb_b, wb_g2, black, white, h, w, c00, c01, c10, c11)`
    *FUSED Bypass Demosaicing: Extract RGB Directly from Bayer 2x2 blocks to 1/2 size RGB.*
    *Executes in a single pass without intermediate VRAM buffers.*

* **Function**: `_ha_to_grayscale_3channel_kernel(wb_bayer, green, cmatrix, dst, wb_r, wb_g1, wb_b, wb_g2, h, w, c00, c01, c10, c11)`
    *Full sRGB-Luma Demosaic to Grayscale 1-channel with Fringe and Maze Reduction.*

* **Function**: `_rgb_to_bgr_i32_kernel(src, dst, h, w)`

* **Function**: `compile_hamilton_tcm(arch, save_path)`
    *----------------------------------------*

--------------------

### 📄 [compile_hamilton_tcm_backup.py](file:///e:/APP%20Developer/Pixel%20Refine/taichi_library/taichi_algorithm/aot_py/compile_hamilton_tcm_backup.py)

* **Function**: `_preprocess_bayer_kernel(bayer, wb_bayer, wb_r, wb_g1, wb_b, wb_g2, black, white, h, w, c00, c01, c10, c11)`
    *Pass 0: Fused Pre-Processing Kernel.*
    *Performs clamping, normalization, and white balance gain scaling in a single pass.*

* **Function**: `_ha_green_interpolation_kernel_opt(wb_bayer, green, h, w, c00, c01, c10, c11)`
    *Pass 1: Hamilton-Adams Edge-Directed Green Channel Reconstruction.*
    *Optimized: standard Hamilton-Adams 1-row/col gradient estimation (no redundant loops) for 3x memory bandwidth savings.*

* **Function**: `_ha_red_blue_interpolation_kernel_opt(wb_bayer, green, cmatrix, dst, wb_r, wb_g1, wb_b, wb_g2, h, w, c00, c01, c10, c11)`
    *Pass 2: Red and Blue Reconstruction using Directional Color Difference Interpolation.*
    *Uses cached preprocessed wb_bayer for maximum performance.*

* **Function**: `_get_green_gain(nr, nc, c00, c01, c10, c11, wb_g1, wb_g2)`

* **Function**: `_ha_green_to_grayscale_1channel_fused_kernel(bayer, dst, wb_r, wb_g1, wb_b, wb_g2, black, white, h, w, c00, c01, c10, c11)`
    *FUSED 1-Channel (Grayscale Full-Res): Fuses preprocessing, normalization, white balance*
    *and fast green demosaicing into a single fast GPU pass. Eliminates temporary memory footprint entirely.*
    *Optimized: static neighborhood fetching and fast WB mapping using hardware-friendly select branches.*

* **Function**: `_ha_green_half_res_fused_kernel(bayer, dst, wb_r, wb_g1, wb_b, wb_g2, black, white, h, w, c00, c01, c10, c11)`
    *FUSED Bypass Demosaicing: Extract Green Sub-Sampling directly from RAW to 1/2 size grayscale.*
    *Executes in a single pass without intermediate VRAM buffers (saving VRAM and bandwidth).*

* **Function**: `_ha_rgb_half_res_fused_kernel(bayer, cmatrix, dst, wb_r, wb_g1, wb_b, wb_g2, black, white, h, w, c00, c01, c10, c11)`
    *FUSED Bypass Demosaicing: Extract RGB Directly from Bayer 2x2 blocks to 1/2 size RGB.*
    *Executes in a single pass without intermediate VRAM buffers.*

* **Function**: `_ha_to_grayscale_3channel_kernel(wb_bayer, green, cmatrix, dst, wb_r, wb_g1, wb_b, wb_g2, h, w, c00, c01, c10, c11)`
    *Full sRGB-Luma Demosaic to Grayscale 1-channel with Fringe and Maze Reduction.*

* **Function**: `_rgb_to_bgr_i32_kernel(src, dst, h, w)`

* **Function**: `compile_hamilton_tcm(arch, save_path)`
    *----------------------------------------*

--------------------

### 📄 [compile_jbf_tcm.py](file:///e:/APP%20Developer/Pixel%20Refine/taichi_library/taichi_algorithm/aot_py/compile_jbf_tcm.py)

* **Function**: `compile_jbf_aot(arch, save_path)`
    *----------------------------------------*

--------------------

### 📄 [compile_median_tcm.py](file:///e:/APP%20Developer/Pixel%20Refine/taichi_library/taichi_algorithm/aot_py/compile_median_tcm.py)

* **Function**: `compile_median_aot(arch, save_path)`
    *----------------------------------------*

--------------------

### 📄 [compile_ncc_tcm.py](file:///e:/APP%20Developer/Pixel%20Refine/taichi_library/taichi_algorithm/aot_py/compile_ncc_tcm.py)

* **Function**: `compile_ncc_aot(arch, save_path)`
    *----------------------------------------*

--------------------

### 📄 [compile_ofb_tcm.py](file:///e:/APP%20Developer/Pixel%20Refine/taichi_library/taichi_algorithm/aot_py/compile_ofb_tcm.py)

* **Function**: `compile_ofb_tcm(arch, save_path)`
    *----------------------------------------*

--------------------

### 📄 [compile_pyramid_tcm.py](file:///e:/APP%20Developer/Pixel%20Refine/taichi_library/taichi_algorithm/aot_py/compile_pyramid_tcm.py)

* **Function**: `compile_pyramid_aot(arch, save_path)`
    *----------------------------------------*

--------------------

### 📄 [compile_ransac_tcm.py](file:///e:/APP%20Developer/Pixel%20Refine/taichi_library/taichi_algorithm/aot_py/compile_ransac_tcm.py)

* **Function**: `compile_ransac_aot(arch, save_path)`
    *----------------------------------------*

--------------------

### 📄 [compile_remap_tcm.py](file:///e:/APP%20Developer/Pixel%20Refine/taichi_library/taichi_algorithm/aot_py/compile_remap_tcm.py)

* **Function**: `compile_remap_tcm(arch, save_path)`
    *----------------------------------------*

--------------------

### 📄 [extreme_stress_test.py](file:///e:/APP%20Developer/Pixel%20Refine/taichi_library/taichi_algorithm/aot_py/extreme_stress_test.py)

* **Function**: `extreme_stress_test()`
    *----------------------------------------*

--------------------

### 📄 [test_comprehensif.py](file:///e:/APP%20Developer/Pixel%20Refine/taichi_library/taichi_algorithm/aot_py/test_comprehensif.py)

* **Function**: `print_header(text)`

* **Function**: `print_result(name, mae, threshold)`

* **Function**: `run_comprehensive_test()`

* **Function**: `run_pipeline_stress_test(engine, img_full)`
    *----------------------------------------*

--------------------

### 📄 [test_gamma_proxy_aot.py](file:///e:/APP%20Developer/Pixel%20Refine/taichi_library/taichi_algorithm/aot_py/test_gamma_proxy_aot.py)

* **Function**: `to_gamma_proxy_python(linear_img, scale, gamma_pow, slope, cutoff)`

* **Function**: `verify_aot_parity()`
    *----------------------------------------*

--------------------

### 📄 [test_gamma_proxy_jit.py](file:///e:/APP%20Developer/Pixel%20Refine/taichi_library/taichi_algorithm/aot_py/test_gamma_proxy_jit.py)

* **Function**: `to_gamma_proxy_python(linear_img, scale, gamma_pow, slope, cutoff)`

* **Function**: `test_parity()`
    *----------------------------------------*

--------------------

### 📄 [test_normalize_aot.py](file:///e:/APP%20Developer/Pixel%20Refine/taichi_library/taichi_algorithm/aot_py/test_normalize_aot.py)

* **Function**: `normalize_image_ref(image, dtype)`

* **Function**: `verify_normalize_aot()`
    *----------------------------------------*

--------------------

### 📄 [test_normalize_jit.py](file:///e:/APP%20Developer/Pixel%20Refine/taichi_library/taichi_algorithm/aot_py/test_normalize_jit.py)

* **Function**: `normalize_image_ref(image, dtype)`

* **Function**: `test_normalize_jit()`
    *----------------------------------------*

--------------------

### 📄 [test_normalize_parity.py](file:///e:/APP%20Developer/Pixel%20Refine/taichi_library/taichi_algorithm/aot_py/test_normalize_parity.py)

* **Function**: `normalize_image_ref(image, dtype, out)`

* **Function**: `test_normalize_parity()`
    *----------------------------------------*

--------------------

### 📄 [test_remap_memory.py](file:///e:/APP%20Developer/Pixel%20Refine/taichi_library/taichi_algorithm/aot_py/test_remap_memory.py)

* **Function**: `get_cpu_memory()`
    *Mengembalikan RAM yang digunakan proses saat ini dalam MB.*

* **Function**: `run_opencv_benchmark(src_np, flow_np, h_dst, w_dst)`

* **Function**: `run_optimized_benchmark(src_np, flow_np, h_dst, w_dst)`
    *----------------------------------------*

--------------------

### 📄 [test_remap_with_flow.py](file:///e:/APP%20Developer/Pixel%20Refine/taichi_library/taichi_algorithm/aot_py/test_remap_with_flow.py)

* **Function**: `test_remap_with_flow_f32_2d()`

* **Function**: `test_remap_with_flow_f32_3d()`

* **Function**: `test_remap_with_flow_u16_3d()`
    *----------------------------------------*

--------------------

### 📄 [verify_interop_safety.py](file:///e:/APP%20Developer/Pixel%20Refine/taichi_library/taichi_algorithm/aot_py/verify_interop_safety.py)

* **Class**: `MockGPUDeviceMemory`
    *Simulates an external GPU object (like ONNX/PyTorch) using NumPy.*
  * Method: `__init__(self, arr)`

* **Function**: `verify_interop_safety()`
    *----------------------------------------*

--------------------


## 📂 Directory: `Root Directory`

### 📄 [# DIRECTORY: taichi_library/taichi_aot](file:///e:/APP%20Developer/Pixel%20Refine/# DIRECTORY: taichi_library/taichi_aot)


--------------------


## 📂 Directory: `Root Directory`

### 📄 [engine.py](file:///e:/APP%20Developer/Pixel%20Refine/taichi_library/taichi_aot/engine.py)

* **Class**: `DynamicArg`

* **Class**: `BufferPool`
    *Lightweight pool: tracks handles for potential reuse by exact size match.*
  * Method: `__init__(self)`
  * Method: `acquire(self, size)`
  * Method: `store(self, size, handle)`
    *Store a handle for reuse (caller decides if reuse or free).*
  * Method: `clear(self)`
    *Force-free all pooled handles from VRAM.*

* **Class**: `TaichiGPUBuffer`
  * Method: `__init__(self, size_bytes, handle, shape, dtype, is_vector, engine, is_owner, host_accessible, vector_dim)`
  * Method: `release(self)`
    *Release the buffer back to the engine's buffer pool for reuse.*
  * Method: `destroy(self)`
    *Immediately release GPU VRAM. Does NOT use buffer pool reuse.*
  * Method: `_force_destroy(self)`
    *Force release GPU VRAM regardless of pipeline intermediate status.*
  * Method: `__del__(self)`
  * Method: `ndim(self)`
  * Method: `nbytes(self)`
  * Method: `to_numpy(self)`
    *Read GPU data. Automatically handles staging for VRAM-only buffers.*
  * Method: `map(self)`
  * Method: `unmap(self)`
  * Method: `cast(self, target_dtype, host_accessible)`
  * Method: `view_as_vector(self, is_vector, vector_dim)`

* **Class**: `TaichiPlaceholder`
  * Method: `__init__(self, placeholder_id, shape, dtype, is_vector, vector_dim)`

* **Class**: `AOTModuleWrapper`
  * Method: `__init__(self, module_ptr)`
  * Method: `__del__(self)`
  * Method: `run(self, graph_name)`
    *Menjalankan grafik Taichi AOT dengan validasi argumen yang informatif.*
  * Method: `_dummy_run(self)`

* **Class**: `AOTEngine`
  * Method: `__new__(cls)`
  * Method: `placeholder(self, shape, dtype, is_vector, vector_dim)`
  * Method: `rec_pipeline(self, name)`
  * Method: `use_pipeline(self, name, overrides)`
  * Method: `allocate(self, shape, dtype, is_vector, host_accessible, vector_dim)`
  * Method: `clear_pipeline_by_name(self, name)`
    *Safely erases a pipeline from C++ and forces destruction of its intermediate buffers.*
  * Method: `clear_pipelines(self)`
    *Clear all registered pipelines and destroy their intermediate buffers.*
  * Method: `get_staging_buffer(self, shape, dtype)`
  * Method: `_is_external_gpu_obj(self, data)`
  * Method: `_upload_fast_interop(self, data, is_vector, vector_dim)`
    *Universal Fast-Copy bridge using Pinned Memory DMA.*
  * Method: `upload(self, data, is_vector, vector_dim)`
  * Method: `load(self, path)`
  * Method: `imread(self, path)`
  * Method: `imwrite(self, path, buf)`
  * Method: `sync(self)`
  * Method: `reinit(self, device_id)`

* **Function**: `_populate_dynamic_arg(arg, name_bytes, value, context_name)`
    *Internal helper to fill DynamicArg metadata consistently.*

* **Function**: `_init_aot_bridge()`

* **Function**: `configure_taichi_backend(prefer, device_memory_GB)`
    *Helper to initialize Taichi runtime consistently across the project.*
    *- prefer: 'vulkan', 'cuda', 'gpu', or 'cpu'. If None, reads*
    *PIXEL_REFINE_TAICHI_ARCH env var, otherwise auto-selects.*
    *- device_memory_GB: optional device memory hint forwarded to `ti.init`.*
    *This function imports Taichi lazily and calls `ti.init(...)`.*
    *Use this from scripts before invoking any Taichi kernels.*

* **Function**: `InputArray(data, is_vector, vector_dim)`
    *OpenCV-style Data Input Unification.*
    *Automatically handles NumPy arrays, PyTorch tensors, OpenCV UMats,*
    *native Python lists, or existing TaichiGPUBuffer instances.*

* **Function**: `OutputArray(shape, dtype, is_vector, vector_dim)`
    *OpenCV-style Data Output Allocation.*
    *Creates an empty GPU VRAM buffer ready for writing.*
    *----------------------------------------*

--------------------
