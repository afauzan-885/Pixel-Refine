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

def reload_language():
    global LANGUAGE
    LANGUAGE = load_language_setting()
    
    import sys
    current_module = sys.modules[__name__]
    
    if LANGUAGE == "indonesian":
        from . import lang_indonesian as lang
    elif LANGUAGE == "melayu":
        from . import lang_melayu as lang
    elif LANGUAGE == "china traditional":
        from . import lang_simplified_china as lang
    else:
        from . import lang_english as lang
        
    for key, val in lang.__dict__.items():
        if key.isupper():
            setattr(current_module, key, val)

# Initial load
reload_language()

