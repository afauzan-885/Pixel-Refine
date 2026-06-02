import os
import json
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QSlider,
    QHBoxLayout,
    QScrollArea,
    QComboBox,
    QLineEdit,
    QPushButton,
    QSizePolicy,
    QToolButton,
)
from PySide6.QtGui import QFont, QDoubleValidator, QIntValidator
from PySide6.QtCore import Qt, QLocale

from pixel_refine_desktop.ui.resources.GenericUILibrary import FormGroup
from pixel_refine_desktop.ui.resources.styles.stylesheet import (
    SCROLL_AREA,
    SLIDER_STYLE,
    DROPDOWN_BOX,
    APPLY_BUTTON,
    VALUE_EDIT_LABEL,
    TOGGLE_BUTTON,
)
from pixel_refine_desktop.ui.views.settings.General.Language import language_config
from config import CONFIG_DIR, ALGORITHM_PARAMETER_SETTINGS_FILE, GENERAL_SETTINGS_FILE


def get_default_font(size=10, weight=QFont.Weight.Normal):
    return QFont("Arial", size, weight)


def load_similarity_config():
    defaults = {
        "use_multi_core": True,
        "spatial_params": {
            "similarity_spatial_tile_size": 8,
            "similarity_spatial_motion_sensitivity": 100.0,
            "similarity_spatial_noise_mad_offset_factor": 0.12,
            "similarity_spatial_overlap_percent": 0.40,
            "similarity_spatial_num_workers": 1,
            "similarity_smart_noise_alpha": 1.0,
            "similarity_smart_noise_aware_enable": False,  # Default diset ke False (OFF)
            "similarity_smart_noise_strength": 100.0,  # [PENAMBAHAN] Strength (%)
        },
    }
    final_config = {
        "use_multi_core": defaults["use_multi_core"],
        **defaults["spatial_params"],
    }
    try:
        if os.path.exists(ALGORITHM_PARAMETER_SETTINGS_FILE):
            with open(ALGORITHM_PARAMETER_SETTINGS_FILE, "r") as f:
                all_params_file = json.load(f)
            if "Similarity" in all_params_file and isinstance(
                all_params_file.get("Similarity"), dict
            ):
                loaded_similarity_section = all_params_file["Similarity"]
                if "use_multi_core" in loaded_similarity_section:
                    final_config["use_multi_core"] = loaded_similarity_section[
                        "use_multi_core"
                    ]
                if "spatial_params" in loaded_similarity_section and isinstance(
                    loaded_similarity_section["spatial_params"], dict
                ):
                    for key, value in defaults["spatial_params"].items():
                        final_config[key] = loaded_similarity_section[
                            "spatial_params"
                        ].get(key, value)
                else:
                    for key, value in defaults["spatial_params"].items():
                        final_config[key] = loaded_similarity_section.get(key, value)
                return final_config
    except (IOError, json.JSONDecodeError) as e:
        print(f"Error loading Similarity config: {e}. Using defaults.")
    return final_config


def save_similarity_v1_config(config_to_save):
    os.makedirs(CONFIG_DIR, exist_ok=True)
    config_filename = ALGORITHM_PARAMETER_SETTINGS_FILE
    all_params_file = {}
    try:
        if os.path.exists(config_filename):
            with open(config_filename, "r") as f:
                all_params_file = json.load(f)
    except Exception:
        pass
    if "Similarity" not in all_params_file or not isinstance(
        all_params_file.get("Similarity"), dict
    ):
        all_params_file["Similarity"] = {}
    similarity_section_to_save = {
        "use_multi_core": config_to_save.get("use_multi_core", True),
        "spatial_params": {},
        "spatial_params": {},
    }
    spatial_keys = [
        "similarity_spatial_tile_size",
        "similarity_spatial_motion_sensitivity",
        "similarity_spatial_noise_mad_offset_factor",
        "similarity_spatial_overlap_percent",
        "similarity_spatial_num_workers",
        "similarity_smart_noise_alpha",
        "similarity_smart_noise_aware_enable",
        "similarity_smart_noise_strength",
    ]  # [PENAMBAHAN]

    for key in spatial_keys:
        if key in config_to_save:
            similarity_section_to_save["spatial_params"][key] = config_to_save[key]
    all_params_file["Similarity"] = similarity_section_to_save
    try:
        with open(config_filename, "w") as f:
            json.dump(all_params_file, f, indent=4)
    except Exception as e:
        print(f"Error saving Similarity config: {e}")


def create_slider_input_field_layout(
    min_val,
    max_val,
    initial_value_slider,
    initial_value_text,
    slider_multiplier,
    text_format_func,
    validator,
    c_locale,
    slider_min_val=None,
    slider_max_val=None,
    is_overlap=False,
):
    """
    Membuat QHBoxLayout yang berisi Slider, QLineEdit, dan label '%' jika is_overlap.
    Mengembalikan QHBoxLayout, slider, dan line_edit.
    """
    slider = QSlider(Qt.Orientation.Horizontal)
    actual_slider_min = slider_min_val if slider_min_val is not None else min_val
    actual_slider_max = slider_max_val if slider_max_val is not None else max_val
    slider.setMinimum(int(actual_slider_min))
    slider.setMaximum(int(actual_slider_max))
    slider.setValue(int(initial_value_slider))
    slider.setStyleSheet(SLIDER_STYLE)
    slider.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

    line_edit = QLineEdit(initial_value_text)
    line_edit.setStyleSheet(VALUE_EDIT_LABEL)
    line_edit.setFixedWidth(50 if isinstance(validator, QDoubleValidator) else 40)
    line_edit.setAlignment(Qt.AlignmentFlag.AlignRight)
    if isinstance(validator, QDoubleValidator):
        line_edit.setLocale(c_locale)
    line_edit.setValidator(validator)

    field_layout = QHBoxLayout()
    field_layout.setContentsMargins(0, 0, 0, 0)
    field_layout.setSpacing(6)
    field_layout.addWidget(slider, 1)
    field_layout.addWidget(line_edit)

    if is_overlap:
        percent_label = QLabel("%")
        percent_label.setFont(get_default_font(9))
        field_layout.addWidget(percent_label)

    return field_layout, slider, line_edit


def get_similarity_settings_page():
    sim_v1_config = load_similarity_config()
    original_v1_ui_defaults = {
        "similarity_spatial_tile_size": 20,
        "similarity_spatial_motion_sensitivity": 120.5,
        "similarity_spatial_noise_mad_offset_factor": 0.25,
        "similarity_spatial_overlap_percent": 0.38,
        "similarity_spatial_num_workers": 2,
        "similarity_smart_noise_alpha": 1.8,
        "similarity_smart_noise_aware_enable": True,
        "similarity_smart_noise_strength": 100.0,
    }

    page_widget = QWidget()
    main_page_layout = QVBoxLayout(page_widget)
    main_page_layout.setSpacing(0)
    main_page_layout.setContentsMargins(10, 10, 10, 10)

    title_label = QLabel(
        getattr(language_config, "SIMILARITY_V1_GROUP_TITLE", "Similarity Parameters")
    )
    title_label.setFont(get_default_font(11, QFont.Weight.Bold))
    title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    title_label.setStyleSheet("margin-bottom: 10px;")
    main_page_layout.addWidget(title_label)

    widgets = {}
    c_locale = QLocale(QLocale.Language.C, QLocale.Country.AnyCountry)

    # widgets["merging_type_button"] = merging_type_button # No longer needed

    # --- Kontainer Utama untuk Parameter SPASIAL ---
    spatial_params_outer_container = QWidget()
    spatial_container_main_layout = QVBoxLayout(spatial_params_outer_container)
    spatial_container_main_layout.setContentsMargins(0, 0, 0, 0)
    spatial_container_main_layout.setSpacing(20)  # Jarak vertikal antar grup parameter

    # --- Grup 1: Tile Size (Spatial) - Using FormGroup ---
    tile_size_sp_form = FormGroup(
        label=getattr(language_config, "TILE_SIZE_LABEL", "Tile Size:"),
        input_type="select",
    )
    tile_options_int = [8, 10, 12, 16, 20, 24, 32, 48, 64, 128, 256]
    tile_size_sp_form.add_options([str(s) for s in tile_options_int])
    tile_size_sp_form.set_value(
        str(sim_v1_config.get("similarity_spatial_tile_size", 24))
    )
    tile_size_sp_form.label.setToolTip(
        getattr(language_config, "TILE_SIZE_DESCRIPTION", "...")
    )
    tile_size_sp_form.input.setMaximumWidth(150)
    widgets["tile_combo_spatial"] = tile_size_sp_form.input
    spatial_container_main_layout.addWidget(tile_size_sp_form)

    # [PENAMBAHAN] --- Grup Baru: Processing Cores - Using FormGroup ---
    num_workers_form = FormGroup(label="Processing Cores:", input_type="select")
    # Dapatkan jumlah core CPU secara dinamis
    max_cores = os.cpu_count() or 4
    worker_options = ["Auto"] + [str(i) for i in range(1, max_cores + 1)]
    num_workers_form.add_options(worker_options)

    # Atur nilai awal dari config
    current_worker_val = sim_v1_config.get("similarity_spatial_num_workers", -1)
    if current_worker_val == -1:
        num_workers_form.set_value("Auto")
    else:
        num_workers_form.set_value(str(current_worker_val))

    num_workers_form.label.setToolTip(
        "Jumlah inti CPU yang digunakan untuk pemrosesan paralel.\n'Auto' akan memilih jumlah optimal.\nNilai lebih tinggi bisa lebih cepat tetapi menggunakan lebih banyak CPU dan RAM."
    )
    num_workers_form.input.setMaximumWidth(150)
    widgets["num_workers_combo_spatial"] = num_workers_form.input
    spatial_container_main_layout.addWidget(num_workers_form)

    # --- Grup 2: Overlap (Spatial) ---
    overlap_sp_group_widget = QWidget()
    overlap_sp_layout = QVBoxLayout(overlap_sp_group_widget)
    overlap_sp_layout.setContentsMargins(0, 0, 0, 0)
    overlap_sp_layout.setSpacing(5)

    overlap_label_text_sp_obj = QLabel(
        getattr(language_config, "OVERLAP_LABEL", "Overlap % (Spatial):")
    )
    overlap_label_text_sp_obj.setFont(get_default_font(10, QFont.Weight.Bold))
    overlap_label_text_sp_obj.setToolTip(
        getattr(language_config, "OVERLAP_DESCRIPTION", "...")
    )
    overlap_sp_layout.addWidget(overlap_label_text_sp_obj)

    initial_overlap_percent_sp = int(
        round(sim_v1_config.get("similarity_spatial_overlap_percent", 0.35) * 100)
    )
    overlap_validator_sp = QIntValidator(0, 90)
    overlap_sp_field_layout, slider_ov_sp, input_ov_sp = (
        create_slider_input_field_layout(
            0,
            90,
            initial_overlap_percent_sp,
            str(initial_overlap_percent_sp),
            1.0,
            lambda v, m=1, loc=c_locale: str(int(v)),
            overlap_validator_sp,
            c_locale,
            is_overlap=True,
        )
    )
    overlap_sp_layout.addLayout(overlap_sp_field_layout)  # Tambah layout field
    widgets["overlap_slider_spatial"] = slider_ov_sp
    widgets["overlap_input_spatial"] = input_ov_sp
    spatial_container_main_layout.addWidget(overlap_sp_group_widget)

    # --- Grup 3: Motion Sensitivity (Spatial) ---
    motion_sens_group_widget = QWidget()
    motion_sens_layout = QVBoxLayout(motion_sens_group_widget)
    motion_sens_layout.setContentsMargins(0, 0, 0, 0)
    motion_sens_layout.setSpacing(5)

    motion_sens_label_obj = QLabel(
        getattr(language_config, "MOTION_THRESHOLD_LABEL", "Motion Sensitivity:")
    )
    motion_sens_label_obj.setFont(get_default_font(10, QFont.Weight.Bold))
    motion_sens_label_obj.setToolTip(
        getattr(language_config, "MOTION_SENSIVITY_DESCRIPTION", "...")
    )
    motion_sens_layout.addWidget(motion_sens_label_obj)

    initial_motion_sens_v1 = sim_v1_config.get(
        "similarity_spatial_motion_sensitivity", 110.0
    )
    motion_sens_multiplier_v1 = 10.0
    motion_sens_slider_min_v1, motion_sens_slider_max_v1 = 10, 2000
    motion_sens_validator_v1 = QDoubleValidator(0.1, 200.0, 1)
    motion_sens_validator_v1.setNotation(QDoubleValidator.Notation.StandardNotation)
    motion_sens_field_layout, slider_ms, input_ms = create_slider_input_field_layout(
        0,
        0,
        int(round(initial_motion_sens_v1 * motion_sens_multiplier_v1)),
        c_locale.toString(initial_motion_sens_v1, "f", 1),
        motion_sens_multiplier_v1,
        lambda v, m=motion_sens_multiplier_v1, loc=c_locale: loc.toString(
            v / m, "f", 1
        ),
        motion_sens_validator_v1,
        c_locale,
        slider_min_val=motion_sens_slider_min_v1,
        slider_max_val=motion_sens_slider_max_v1,
    )
    motion_sens_layout.addLayout(motion_sens_field_layout)
    widgets["motion_sensitivity_slider"] = slider_ms
    widgets["motion_sensitivity_input"] = input_ms
    spatial_container_main_layout.addWidget(motion_sens_group_widget)

    # --- Grup 4: Noise Offset (Spatial) ---
    noise_offset_group_widget = QWidget()
    noise_offset_layout = QVBoxLayout(noise_offset_group_widget)
    noise_offset_layout.setContentsMargins(0, 0, 0, 0)
    noise_offset_layout.setSpacing(5)

    noise_mad_label_obj = QLabel(
        getattr(language_config, "NOISE_OFFSET_LABEL", "Noise Offset Factor:")
    )
    noise_mad_label_obj.setFont(get_default_font(10, QFont.Weight.Bold))
    noise_mad_label_obj.setToolTip(
        getattr(language_config, "NOISE_OFFSET_DESCRIPTION", "...")
    )
    noise_offset_layout.addWidget(noise_mad_label_obj)

    initial_noise_mad_v1 = sim_v1_config.get(
        "similarity_spatial_noise_mad_offset_factor", 0.3
    )
    noise_mad_multiplier_v1 = 100.0
    noise_mad_slider_min_v1, noise_mad_slider_max_v1 = 0, 100
    noise_mad_validator_v1 = QDoubleValidator(0.0, 5.0, 2)
    noise_mad_validator_v1.setNotation(QDoubleValidator.Notation.StandardNotation)
    noise_offset_field_layout, slider_nm, input_nm = create_slider_input_field_layout(
        0,
        0,
        int(round(initial_noise_mad_v1 * noise_mad_multiplier_v1)),
        c_locale.toString(initial_noise_mad_v1, "f", 2),
        noise_mad_multiplier_v1,
        lambda v, m=noise_mad_multiplier_v1, loc=c_locale: loc.toString(v / m, "f", 2),
        noise_mad_validator_v1,
        c_locale,
        slider_min_val=noise_mad_slider_min_v1,
        slider_max_val=noise_mad_slider_max_v1,
    )
    noise_offset_layout.addLayout(noise_offset_field_layout)
    widgets["noise_mad_offset_slider"] = slider_nm
    widgets["noise_mad_offset_input"] = input_nm

    spatial_container_main_layout.addWidget(noise_offset_group_widget)

    # --- [PENAMBAHAN] Grup 5: Smart Noise Alpha ---
    smart_alpha_group_widget = QWidget()
    smart_alpha_layout = QVBoxLayout(smart_alpha_group_widget)
    smart_alpha_layout.setContentsMargins(0, 0, 0, 0)
    smart_alpha_layout.setSpacing(5)

    smart_alpha_label_obj = QLabel("Smart Noise Alpha (AI):")
    smart_alpha_label_obj.setFont(get_default_font(10, QFont.Weight.Bold))
    smart_alpha_label_obj.setToolTip(
        "Mengatur seberapa toleran model AI terhadap noise.\nNilai rendah (misal 1.5) = Lebih sensitif gerak (kurangi ghosting).\nNilai tinggi (misal 2.5) = Lebih bersih noise (risiko ghosting)."
    )
    smart_alpha_layout.addWidget(smart_alpha_label_obj)

    initial_smart_alpha = sim_v1_config.get("similarity_smart_noise_alpha", 1.8)
    smart_alpha_multiplier = 10.0
    smart_alpha_slider_min, smart_alpha_slider_max = 5, 50  # 0.5 ke 5.0
    smart_alpha_validator = QDoubleValidator(0.5, 5.0, 1)
    smart_alpha_validator.setNotation(QDoubleValidator.Notation.StandardNotation)
    smart_alpha_field_layout, slider_sa, input_sa = create_slider_input_field_layout(
        0,
        0,
        int(round(initial_smart_alpha * smart_alpha_multiplier)),
        c_locale.toString(initial_smart_alpha, "f", 1),
        smart_alpha_multiplier,
        lambda v, m=smart_alpha_multiplier, loc=c_locale: loc.toString(v / m, "f", 1),
        smart_alpha_validator,
        c_locale,
        slider_min_val=smart_alpha_slider_min,
        slider_max_val=smart_alpha_slider_max,
    )
    smart_alpha_layout.addLayout(smart_alpha_field_layout)
    widgets["smart_noise_alpha_slider"] = slider_sa
    widgets["smart_noise_alpha_input"] = input_sa
    spatial_container_main_layout.addWidget(smart_alpha_group_widget)

    # --- [PENAMBAHAN] Grup 6: Smart Noise Aware Enable & Strength ---
    noise_ctrl_group_widget = QWidget()
    noise_ctrl_layout = QVBoxLayout(noise_ctrl_group_widget)
    noise_ctrl_layout.setContentsMargins(0, 0, 0, 0)
    noise_ctrl_layout.setSpacing(10)

    # Toggle Row
    toggle_row_layout = QHBoxLayout()
    noise_aware_label = QLabel("Smart Noise Aware (AI):")
    noise_aware_label.setFont(get_default_font(10, QFont.Weight.Bold))
    noise_aware_label.setToolTip(
        "Aktifkan atau nonaktifkan kontribusi estimasi noise ke model AI.\nJika mati, model AI akan bekerja murni berdasarkan fitur gambar."
    )

    toggle_btn = QPushButton()
    toggle_btn.setCheckable(True)
    toggle_btn.setFixedSize(40, 20)
    toggle_btn.setStyleSheet(TOGGLE_BUTTON)
    toggle_btn.setChecked(
        sim_v1_config.get("similarity_smart_noise_aware_enable", True)
    )

    toggle_row_layout.addWidget(noise_aware_label)
    toggle_row_layout.addStretch()
    toggle_row_layout.addWidget(toggle_btn)
    noise_ctrl_layout.addLayout(toggle_row_layout)

    # Strength Slider
    strength_label = QLabel("Noise Contribution Strength (%):")
    strength_label.setFont(get_default_font(9, QFont.Weight.Bold))
    strength_label.setToolTip(
        "Mengatur seberapa kuat pengaruh estimasi noise (0% = Mati, 100% = Penuh)."
    )
    noise_ctrl_layout.addWidget(strength_label)

    initial_strength = sim_v1_config.get("similarity_smart_noise_strength", 100.0)
    strength_validator = QIntValidator(0, 100)
    strength_field_layout, slider_str, input_str = create_slider_input_field_layout(
        0,
        100,
        int(initial_strength),
        str(int(initial_strength)),
        1.0,
        lambda v, m=1: str(int(v)),
        strength_validator,
        c_locale,
        is_overlap=True,  # reuse '%' label
    )
    noise_ctrl_layout.addLayout(strength_field_layout)

    widgets["smart_noise_aware_toggle"] = toggle_btn
    widgets["smart_noise_strength_slider"] = slider_str
    widgets["smart_noise_strength_input"] = input_str
    spatial_container_main_layout.addWidget(noise_ctrl_group_widget)

    reset_spatial_button = QPushButton(
        getattr(language_config, "RESET_SPATIAL_DEFAULTS_BUTTON", "Reset Defaults")
    )
    reset_spatial_button.setStyleSheet(APPLY_BUTTON)
    reset_spatial_button.setMinimumHeight(28)

    reset_spatial_row_layout = QHBoxLayout()
    reset_spatial_row_layout.setContentsMargins(0, 0, 0, 0)

    reset_spatial_row_layout.addWidget(
        reset_spatial_button, 0, Qt.AlignmentFlag.AlignRight
    )

    spatial_container_main_layout.addSpacing(0)
    spatial_container_main_layout.addLayout(reset_spatial_row_layout)

    widgets["reset_spatial_button"] = reset_spatial_button

    spatial_container_main_layout.addStretch(1)

    main_page_layout.addWidget(spatial_params_outer_container)

    def save_current_settings_v1():
        settings_to_save_flat = {}
        try:
            settings_to_save_flat["similarity_spatial_tile_size"] = int(
                widgets["tile_combo_spatial"].currentText()
            )
            worker_text = widgets["num_workers_combo_spatial"].currentText()
            if worker_text == "Auto":
                settings_to_save_flat["similarity_spatial_num_workers"] = -1
            else:
                settings_to_save_flat["similarity_spatial_num_workers"] = int(
                    worker_text
                )

            ms_val, _ = c_locale.toDouble(widgets["motion_sensitivity_input"].text())
            settings_to_save_flat["similarity_spatial_motion_sensitivity"] = ms_val
            nm_val, _ = c_locale.toDouble(widgets["noise_mad_offset_input"].text())
            settings_to_save_flat["similarity_spatial_noise_mad_offset_factor"] = nm_val
            ov_sp_percent = int(widgets["overlap_input_spatial"].text())
            settings_to_save_flat["similarity_spatial_overlap_percent"] = (
                ov_sp_percent / 100.0
            )
            sa_val, _ = c_locale.toDouble(widgets["smart_noise_alpha_input"].text())
            settings_to_save_flat["similarity_smart_noise_alpha"] = sa_val
            settings_to_save_flat["similarity_smart_noise_aware_enable"] = widgets[
                "smart_noise_aware_toggle"
            ].isChecked()
            settings_to_save_flat["similarity_smart_noise_strength"] = float(
                widgets["smart_noise_strength_input"].text()
            )
        except ValueError as e:
            print(f"Error parsing settings: {e}")
            return
        except Exception as e:
            print(f"Unexpected error parsing: {e}")
            return
        general_settings_for_algo = {}
        try:
            if os.path.exists(GENERAL_SETTINGS_FILE):
                with open(GENERAL_SETTINGS_FILE, "r") as f:
                    general_settings_for_algo = json.load(f)
        except:
            pass
        settings_to_save_flat["use_multi_core"] = general_settings_for_algo.get(
            "multi_core_cpu", True
        )
        save_similarity_v1_config(settings_to_save_flat)

    spatial_params_outer_container.setVisible(True)
    save_current_settings_v1()

    def setup_slider_input_connections(
        slider,
        line_edit,
        multiplier,
        min_actual,
        max_actual,
        locale_obj,
        format_digits,
        is_float=True,
        slider_min_val_raw=None,
        slider_max_val_raw=None,
    ):
        slider.valueChanged.connect(
            lambda value, inp=line_edit, m=multiplier, loc=locale_obj, d=format_digits, f=is_float: inp.setText(
                loc.toString(value / m, "f", d) if f else str(int(round(value / m)))
            )
        )

        def update_slider_from_input():
            current_locale = line_edit.locale() if is_float else None
            try:
                if is_float:
                    value_actual, ok = current_locale.toDouble(line_edit.text())
                    assert ok
                else:
                    value_actual = int(line_edit.text())
                value_actual_clamped = max(min_actual, min(value_actual, max_actual))
                slider_value_target = int(round(value_actual_clamped * multiplier))
                s_min_raw_actual = (
                    slider_min_val_raw
                    if slider_min_val_raw is not None
                    else int(round(min_actual * multiplier))
                )
                s_max_raw_actual = (
                    slider_max_val_raw
                    if slider_max_val_raw is not None
                    else int(round(max_actual * multiplier))
                )
                slider_value_clamped_for_slider = max(
                    s_min_raw_actual, min(slider_value_target, s_max_raw_actual)
                )
                slider.blockSignals(True)
                slider.setValue(slider_value_clamped_for_slider)
                slider.blockSignals(False)
                line_edit.setText(
                    current_locale.toString(value_actual_clamped, "f", format_digits)
                    if is_float
                    else str(int(value_actual_clamped))
                )
            except (ValueError, AssertionError):
                current_slider_val = slider.value()
                line_edit.setText(
                    current_locale.toString(
                        current_slider_val / multiplier, "f", format_digits
                    )
                    if is_float
                    else str(int(round(current_slider_val / multiplier)))
                )

        line_edit.editingFinished.connect(update_slider_from_input)

    setup_slider_input_connections(
        slider_ms,
        input_ms,
        motion_sens_multiplier_v1,
        0.1,
        200.0,
        c_locale,
        1,
        True,
        motion_sens_slider_min_v1,
        motion_sens_slider_max_v1,
    )
    setup_slider_input_connections(
        slider_nm,
        input_nm,
        noise_mad_multiplier_v1,
        0.0,
        5.0,
        c_locale,
        2,
        True,
        noise_mad_slider_min_v1,
        noise_mad_slider_max_v1,
    )
    setup_slider_input_connections(
        slider_ov_sp, input_ov_sp, 1.0, 0, 90, c_locale, 0, False
    )
    setup_slider_input_connections(
        slider_str, input_str, 1.0, 0, 100, c_locale, 0, False
    )
    setup_slider_input_connections(
        slider_sa,
        input_sa,
        smart_alpha_multiplier,
        0.5,
        5.0,
        c_locale,
        1,
        True,
        smart_alpha_slider_min,
        smart_alpha_slider_max,
    )

    def reset_spatial_defaults():
        defaults = original_v1_ui_defaults
        widgets["tile_combo_spatial"].setCurrentText(
            str(defaults.get("similarity_spatial_tile_size"))
        )
        worker_default = defaults.get("similarity_spatial_num_workers", -1)
        if worker_default == -1:
            widgets["num_workers_combo_spatial"].setCurrentText("Auto")
        else:
            widgets["num_workers_combo_spatial"].setCurrentText(str(worker_default))

        widgets["motion_sensitivity_slider"].setValue(
            int(
                round(
                    defaults.get("similarity_spatial_motion_sensitivity", 100.0)
                    * motion_sens_multiplier_v1
                )
            )
        )
        widgets["noise_mad_offset_slider"].setValue(
            int(
                round(
                    defaults.get("similarity_spatial_noise_mad_offset_factor", 1.0)
                    * noise_mad_multiplier_v1
                )
            )
        )
        widgets["overlap_slider_spatial"].setValue(
            int(round(defaults.get("similarity_spatial_overlap_percent", 0.35) * 100))
        )
        widgets["smart_noise_alpha_slider"].setValue(
            int(
                round(
                    defaults.get("similarity_smart_noise_alpha", 1.8)
                    * smart_alpha_multiplier
                )
            )
        )
        widgets["smart_noise_aware_toggle"].setChecked(
            defaults.get("similarity_smart_noise_aware_enable", True)
        )
        widgets["smart_noise_strength_slider"].setValue(
            int(defaults.get("similarity_smart_noise_strength", 100.0))
        )
        save_current_settings_v1()

    widgets["reset_spatial_button"].clicked.connect(reset_spatial_defaults)
    widgets["num_workers_combo_spatial"].currentIndexChanged.connect(
        save_current_settings_v1
    )
    widgets["tile_combo_spatial"].currentIndexChanged.connect(save_current_settings_v1)
    widgets["motion_sensitivity_slider"].sliderReleased.connect(
        save_current_settings_v1
    )
    widgets["motion_sensitivity_input"].editingFinished.connect(
        save_current_settings_v1
    )
    widgets["noise_mad_offset_slider"].sliderReleased.connect(save_current_settings_v1)
    widgets["noise_mad_offset_input"].editingFinished.connect(save_current_settings_v1)
    widgets["overlap_slider_spatial"].sliderReleased.connect(save_current_settings_v1)
    widgets["overlap_input_spatial"].editingFinished.connect(save_current_settings_v1)
    widgets["smart_noise_alpha_slider"].sliderReleased.connect(save_current_settings_v1)
    widgets["smart_noise_alpha_input"].editingFinished.connect(save_current_settings_v1)
    widgets["smart_noise_aware_toggle"].clicked.connect(save_current_settings_v1)
    widgets["smart_noise_strength_slider"].sliderReleased.connect(
        save_current_settings_v1
    )
    widgets["smart_noise_strength_input"].editingFinished.connect(
        save_current_settings_v1
    )

    main_page_layout.addStretch(1)
    scroll = QScrollArea()
    scroll.setWidgetResizable(True)
    scroll.setWidget(page_widget)
    scroll.setStyleSheet(SCROLL_AREA)
    return scroll
