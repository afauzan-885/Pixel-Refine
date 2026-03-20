from kivy.lang import Builder
import os

def load_kv_files():
    """
    Muat semua file .kv dari folder ui/kv secara dinamis 
    sebelum aplikasi utama dibangun.
    """
    # Dapatkan path absolut menuju folder ui/kv (Satu level di atas folder core/)
    base_dir = os.path.dirname(os.path.dirname(__file__))
    ui_kv_dir = os.path.join(base_dir, 'ui', 'kv')
    
    # KivyMD membutuhkan prefix path ke file desainnya
    for filename in os.listdir(ui_kv_dir):
        if filename.endswith('.kv'):
            filepath = os.path.join(ui_kv_dir, filename)
            Builder.load_file(filepath)
            
    print("[Core] All KV UI files loaded successfully.")
