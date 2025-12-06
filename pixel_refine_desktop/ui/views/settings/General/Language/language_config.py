import os
import json

# Path ke file setting
SETTINGS_DIR = os.path.join("database", "setting")
SETTINGS_FILE = os.path.join(SETTINGS_DIR, "app_setting.json")

def load_language_setting():
    try:
        with open(SETTINGS_FILE, "r") as f:
            settings = json.load(f)
        # Ambil nilai bahasa, default ke 'English' jika tidak ada
        language = settings.get("language", "English").lower()
    except Exception as e:
        print(f"Error loading settings: {e}")
        language = "english"
    return language

LANGUAGE = load_language_setting()

# Import modul bahasa sesuai nilai dari app_setting.json
if LANGUAGE in ["indonesian"]:
    from .lang_indonesian import *
elif LANGUAGE in ["english"]:
    from .lang_english import *
elif LANGUAGE in ["melayu"]:
    from .lang_melayu import *
elif LANGUAGE in ["china traditional"]:
    from .lang_simplified_china import *
else:
    # Jika tidak sesuai, default ke bahasa Inggris
    from .lang_english import *
