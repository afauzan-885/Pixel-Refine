# Pixel Refine Mobile — Core Components Implementation Plan

## Context

The mobile app needs to be reset and rebuilt from scratch, focusing on 5 core components: **Home Page, MFDenoiser, MFResolution, HDR, and Panorama**. The goal is to create a solid foundation that mirrors the mature desktop architecture while being suitable for mobile implementation. All UI must use GenericUILibrary (Python-only composition). All backend logic must maintain strict API parity with desktop.

---

## 1. Architecture Overview

### Desktop Pattern (to replicate)
```
View → Controller → Model → Repository → SQLite DB
                ↓
        AlgorithmProcessorThread(QThread)
                ↓
        running_* functions (MFDenoiser, ORB, AKAZE, etc.)
```

### Mobile Target
```
UI Components (GenericUI) → Screen Builder → AppState Router
                ↓
        Controllers (batch, processing, import)
                ↓
        Core Logic (DB manager, algorithm processor, thumbnail manager)
                ↓
        Repositories → SQLite DB
```

---

## 2. Directory Structure

```
pixel_refine_mobile/
├── core/
│   ├── __init__.py                    # Re-export MobileApp, AppBridge
│   ├── app.py                         # [KEEP] MobileApp wrapper
│   ├── app_bridge.py                  # [EXTEND] Add page_changed signal
│   ├── app_state.py                   # [REWRITE] Screen router
│   └── config.py                      # [NEW] Mobile config (paths, DB)
│
├── models/
│   ├── __init__.py
│   ├── algorithm_config_model.py      # [NEW] Port from desktop
│   ├── batch_model.py                 # [NEW] Port from desktop
│   ├── image_model.py                 # [NEW] Port from desktop
│   └── data_access/
│       ├── __init__.py
│       ├── base_repository.py         # [NEW] Direct port
│       ├── batch_repository.py        # [NEW] Direct port
│       ├── image_repository.py        # [NEW] Direct port
│       └── thumbnail_repository.py    # [NEW] Simplified disk cache
│
├── controllers/
│   ├── __init__.py
│   ├── batch_controller.py            # [NEW] Adapted port
│   ├── processing_controller.py       # [NEW] Adapted port
│   └── import_controller.py           # [NEW] Adapted port
│
├── core_logic/
│   ├── __init__.py
│   ├── database_manager.py            # [NEW] Simplified port
│   ├── algorithm_processor.py         # [NEW] Direct port
│   ├── thumbnail_manager.py           # [NEW] 2-tier cache
│   ├── batch_parameter_manager.py     # [NEW] Direct port
│   └── process_manager.py             # [NEW] Thread lifecycle
│
├── ui/
│   ├── __init__.py
│   ├── screens/
│   │   ├── __init__.py
│   │   ├── home_page.py               # [NEW] Tool selection hub
│   │   ├── workspace_page.py          # [NEW] Shared workspace
│   │   └── settings_page.py           # [NEW] App settings
│   └── components/
│       ├── __init__.py
│       ├── batch_strip.py             # [NEW] Horizontal batch selector
│       ├── algorithm_strip.py         # [NEW] Algorithm method tabs
│       ├── image_preview_area.py      # [NEW] Image preview + dots
│       ├── thumbnail_grid.py          # [NEW] Thumbnail grid
│       ├── progress_panel.py          # [NEW] Progress bar
│       └── bottom_nav.py              # [NEW] Bottom action bar
│
└── [DELETE] Legacy Kivy screens
```

---

## 3. Component-to-Desktop Mapping

| Mobile Component | Desktop Equivalent | Notes |
|---|---|---|
| `core/app_state.py` | `enhance_stack_view.py` + `app_manager.py` | Screen router |
| `controllers/batch_controller.py` | `batch_page_controller.py` | Same signal API |
| `controllers/processing_controller.py` | `image_processing_controller.py` | Same settings dict |
| `controllers/import_controller.py` | `import_export_controller.py` | Platform file picker |
| `models/data_access/base_repository.py` | `models/data_access/base_repository.py` | Direct port |
| `models/data_access/batch_repository.py` | `models/data_access/batch_repository.py` | Direct port |
| `models/data_access/image_repository.py` | `models/data_access/image_repository.py` | Direct port |
| `core_logic/database_manager.py` | `core/logic/database_manager.py` | Simplified |
| `core_logic/algorithm_processor.py` | `core/logic/algorithm_processor.py` | Direct port |
| `core_logic/thumbnail_manager.py` | `core/logic/thumbnail_processor.py` | 2-tier cache |
| `ui/components/batch_strip.py` | `right_panel.py` (batch list) | HorizontalScrollRow |
| `ui/components/algorithm_strip.py` | `algorithm_panel.py` (method selector) | ButtonGroup |
| `ui/components/image_preview_area.py` | `display_panel.py` (preview) | DotIndicator |
| `ui/components/thumbnail_grid.py` | `display_panel.py` (grid) | GridContainer |
| `ui/components/progress_panel.py` | `algorithm_panel.py` (progress) | ProgressBar |
| `ui/components/bottom_nav.py` | (mobile-specific) | BottomActionBar |

---

## 4. Placeholder Implementations

### 4.1 AppState (Screen Router)
```python
class AppState:
    def __init__(self, bridge):
        self._bridge = bridge
        self._pages = {}  # tool_name -> builder_func
        self._current_tool = None

    def register_page(self, tool_name, builder_func):
        self._pages[tool_name] = builder_func

    def navigate_to(self, tool_name):
        if tool_name not in self._pages:
            return
        self._current_tool = tool_name
        self._bridge.page_changed.emit(tool_name)
```

### 4.2 BatchController
```python
class BatchController(QObject):
    batch_created = Signal(int, str)
    batch_deleted = Signal(int)
    batch_selected = Signal(int)
    images_added = Signal(int, int)

    def __init__(self, db_path, parent=None): ...
    def create_batch(self, name): ...        # Placeholder
    def delete_batch(self, batch_id): ...    # Placeholder
    def get_all_batches(self): ...           # Placeholder
    def add_images_to_batch(self, bid, paths): ... # Placeholder
```

### 4.3 ProcessingController
```python
class ProcessingController(QObject):
    processing_started = Signal(int)
    processing_progress = Signal(int, int, str)
    processing_completed = Signal(int, str)
    processing_error = Signal(int, str)

    def __init__(self, db_path, parent=None): ...
    def start_processing(self, batch_id, settings): ... # Placeholder
    def cancel_processing(self): ...                     # Placeholder
```

### 4.4 AlgorithmProcessorThread
```python
class AlgorithmProcessorThread(QThread):
    progress_update = Signal(int, str)
    finished_processing = Signal()
    error_occurred = Signal(str)

    def __init__(self, batch_id, settings, parent=None): ...
    def run(self):
        for category, algo_name in self.settings.items():
            if algo_name in ["No Alignment", "No Super Resolution", "No Denoising"]:
                continue
            self.progress_update.emit(50, f"Running {algo_name}...")
        self.finished_processing.emit()
    def stop(self): ...
```

### 4.5 ThumbnailManager
```python
class ThumbnailManager:
    def __init__(self, cache_dir, max_ram=200): ...
    def get_thumbnail(self, path, size=(96,96)):
        # L1: RAM -> L2: Disk -> Generate
        ...
    def process_batch(self, paths, callback, batch_id): ...
```

### 4.6 UI Components (all use GenericUI)
```python
# batch_strip.py
def build_batch_strip(bridge, batches): ...  # HorizontalScrollRow + BatchCards

# algorithm_strip.py
def build_algorithm_strip(bridge, tool_type): ...  # ButtonGroup

# image_preview_area.py
def build_image_preview(bridge): ...  # Card + DotIndicator

# thumbnail_grid.py
def build_thumbnail_grid(bridge): ...  # GridContainer

# progress_panel.py
def build_progress_panel(bridge): ...  # ProgressBar

# bottom_nav.py
def build_bottom_nav(bridge, tool_type): ...  # BottomActionBar
```

---

## 5. Thumbnail Management Design

```
Mobile Thumbnail Flow (2-tier):
  Request(path) → L1 RAM Cache → L2 Disk Cache → Generate
                                                    ↓
                                              Save to L2 → Return to UI
```

| Aspect | Desktop | Mobile |
|---|---|---|
| Tiers | 3 (Global RAM, Session RAM, Disk) | 2 (RAM dict, Disk JPG) |
| RAM limit | 500 entries | 200 entries |
| Thumbnail size | 128x128 | 96x96 |
| Workers | 4-12 threads | 1-2 threads |
| RAW decode | Taichi GPU | CPU fallback placeholder |

---

## 6. Screen Navigation Flow

```
Launch → Home Page (5 tool cards)
              ↓ openTool()
         AppState.navigate_to()
              ↓
         Workspace Page (shared layout)
         ├── batch_strip (top)
         ├── algorithm_strip (tabs)
         ├── image_preview_area (center)
         ├── thumbnail_grid (grid mode)
         ├── progress_panel (bottom)
         └── bottom_nav (fixed bottom)
```

### Tool-Specific Defaults

| Tool | Alignment | Super Resolution | Denoising |
|---|---|---|---|
| MFDenoiser | No Alignment | No Super Resolution | Similarity |
| MFResolution | AKAZE | WSR | No Denoising |
| HDR | No Alignment | No Super Resolution | Average |
| Panorama | AKAZE | No Super Resolution | No Denoising |

---

## 7. Implementation Phases

### Phase 1: Core Infrastructure (blocking)
1. `core/config.py` — Mobile config
2. `models/data_access/base_repository.py` — Direct port
3. `models/data_access/batch_repository.py` — Direct port
4. `models/data_access/image_repository.py` — Direct port
5. `models/algorithm_config_model.py` — Direct port
6. `models/batch_model.py` — Direct port
7. `models/image_model.py` — Direct port
8. `core_logic/database_manager.py` — Simplified port
9. `core/app_state.py` — Rewrite (router)

### Phase 2: Controllers + Logic (functional)
10. `controllers/batch_controller.py` — Adapted port
11. `controllers/processing_controller.py` — Adapted port
12. `controllers/import_controller.py` — Adapted port
13. `core_logic/algorithm_processor.py` — Direct port
14. `core_logic/thumbnail_manager.py` — Simplified
15. `core_logic/batch_parameter_manager.py` — Direct port
16. `core_logic/process_manager.py` — Simplified

### Phase 3: UI Components (visual)
17. `ui/components/batch_strip.py`
18. `ui/components/algorithm_strip.py`
19. `ui/components/image_preview_area.py`
20. `ui/components/thumbnail_grid.py`
21. `ui/components/progress_panel.py`
22. `ui/components/bottom_nav.py`

### Phase 4: Pages (assembly)
23. `ui/screens/home_page.py`
24. `ui/screens/workspace_page.py`
25. `ui/screens/settings_page.py`

### Phase 5: Cleanup + Integration
26. Delete legacy Kivy screens
27. Update `main_mobile.py`
28. Test full flow

---

## 8. Files to Delete

- `pixel_refine_mobile/ui/screens/home_screen_mobile.py`
- `pixel_refine_mobile/ui/screens/project_screen_mobile.py`
- `pixel_refine_mobile/ui/screens/workspace_screen_mobile.py`
- `pixel_refine_mobile/ui/screens/settings_screen_mobile.py`
- `pixel_refine_mobile/ui/screens/project_page.py`
- `pixel_refine_mobile/core/app_state.py` (old Kivy version)
- `pixel_refine_mobile/core/theme_config.py` (old Kivy version)

---

## 9. Verification

1. **Import test**: All new modules import without error
2. **DB test**: DatabaseManager creates tables correctly
3. **Repository test**: CRUD operations work for batches and images
4. **AlgorithmProcessorThread**: Placeholder runs and emits progress signals
5. **UI test**: `main_mobile.py` launches and shows Home Page with 5 tool cards
6. **Navigation test**: Tapping a tool card navigates to Workspace Page
7. **Workspace test**: Workspace shows batch_strip, algorithm_strip, preview, progress, bottom_nav
8. **API parity test**: Controller signal names and parameter formats match desktop exactly

---

## 10. Risks

1. **Algorithm portability**: Desktop algorithms depend on `taichi_library`, `cv2`, `rawpy`. Mobile builds may not support all. Placeholder structure is ready.
2. **Database path**: Mobile needs platform-appropriate paths (app data directory). `core/config.py` handles this.
3. **File picker**: Mobile needs platform intent/picker instead of QFileDialog. `import_controller` abstracts this.
4. **Back navigation**: Current MobileApp uses flat ScrollView. May need StackView upgrade later.
5. **Thread safety**: Mobile needs fewer threads (1-2 vs 4-12) to avoid OOM on low-end devices.
