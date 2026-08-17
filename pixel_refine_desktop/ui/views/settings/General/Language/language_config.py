import os
import json

# Path ke file setting
SETTINGS_DIR = os.path.join("database", "setting")
SETTINGS_FILE = os.path.join(SETTINGS_DIR, "app_setting.json")


def load_language_setting():
    try:
        with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
            settings = json.load(f)
        # Ambil nilai bahasa, default ke 'English' jika tidak ada
        language = settings.get("language", "English").lower()
    except Exception as e:
        print(f"Error loading settings: {e}")
        language = "english"
    return language


LANGUAGE = load_language_setting()


def reload_language(lang_str=None):
    global LANGUAGE
    if lang_str:
        LANGUAGE = lang_str.lower()
    else:
        LANGUAGE = load_language_setting()

    import sys
    import importlib

    current_module = sys.modules[__name__]

    # Tentukan nama module yang akan digunakan
    if LANGUAGE == "indonesian":
        from . import lang_indonesian as lang
    elif LANGUAGE == "melayu":
        from . import lang_melayu as lang
    elif LANGUAGE == "china traditional":
        from . import lang_simplified_china as lang
    else:
        from . import lang_english as lang

    # KUNCI: Paksa Python baca ulang file module dari disk.
    # Ini mencegah bug "stuck language" akibat Python module cache —
    # dimana lang.__dict__ ter-overwrite oleh bahasa terakhir yang di-import.
    importlib.reload(lang)

    # Salin semua konstanta huruf besar ke module language_config
    translations = {}
    for key, val in lang.__dict__.items():
        if key.isupper():
            translations[key] = val
            setattr(current_module, key, val)

    # Suntikkan terjemahan ke semua modul aplikasi yang sudah mengimpor konstanta bahasa
    for name, module in list(sys.modules.items()):
        if module and (
            name.startswith("pixel_refine_desktop") or name == "main_desktop"
        ):
            for key, val in translations.items():
                if hasattr(module, key):
                    setattr(module, key, val)
                # Update referensi language_config di modul lain


reload_language()
