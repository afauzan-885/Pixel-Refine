# Global registry untuk tracking instances
import atexit
from functools import wraps
import gc
from signal import signal
import sys
import traceback
import weakref


_lightglue_instances = weakref.WeakSet()
_cleanup_in_progress = False


# ==========================================================
# HOOK 1: MONKEY PATCH LightGlueAlgorithm.__init__
# ==========================================================
def patch_lightglue_init():
    """
    Monkey patch __init__ untuk auto-register tanpa modifikasi class
    """
    try:
        # Dinamis import untuk menghindari circular dependency
        import importlib
        import sys
        
        # Cari module yang berisi LightGlueAlgorithm
        for module_name, module in sys.modules.items():
            if hasattr(module, 'LightGlueAlgorithm'):
                LightGlueClass = module.LightGlueAlgorithm
                
                # Simpan __init__ original
                original_init = LightGlueClass.__init__
                
                @wraps(original_init)
                def patched_init(self, *args, **kwargs):
                    # Call original __init__
                    original_init(self, *args, **kwargs)
                    
                    # Register instance
                    _lightglue_instances.add(self)
                    print(f"🛡️ LightGlue instance registered for auto-cleanup (ID: {id(self)})")
                
                # Replace __init__
                LightGlueClass.__init__ = patched_init
                
                print(f"✅ Patched LightGlueAlgorithm in module: {module_name}")
                return True
        
        print("⚠️ LightGlueAlgorithm not found in loaded modules")
        return False
        
    except Exception as e:
        print(f"⚠️ Error patching LightGlueAlgorithm: {e}")
        return False


# ==========================================================
# HOOK 2: MONKEY PATCH _cleanup_gpu untuk safety
# ==========================================================
def patch_cleanup_gpu():
    """
    Enhance _cleanup_gpu dengan error handling yang lebih robust
    """
    try:
        for module_name, module in sys.modules.items():
            if hasattr(module, 'LightGlueAlgorithm'):
                LightGlueClass = module.LightGlueAlgorithm
                
                original_cleanup = LightGlueClass._cleanup_gpu
                
                @wraps(original_cleanup)
                def enhanced_cleanup(self):
                    try:
                        # Call original cleanup
                        original_cleanup(self)
                    except Exception as e:
                        # Fallback manual cleanup jika original gagal
                        print(f"⚠️ Original cleanup failed, using fallback: {e}")
                        try:
                            if hasattr(self, 'sess') and self.sess is not None:
                                del self.sess
                                self.sess = None
                            gc.collect()
                            print("✅ Fallback cleanup succeeded")
                        except Exception as e2:
                            print(f"❌ Fallback cleanup also failed: {e2}")
                
                LightGlueClass._cleanup_gpu = enhanced_cleanup
                print("✅ Enhanced _cleanup_gpu with error handling")
                return True
                
    except Exception as e:
        print(f"⚠️ Error enhancing _cleanup_gpu: {e}")
        return False


# ==========================================================
# HOOK 3: CLEANUP FUNCTIONS
# ==========================================================
def cleanup_all_instances():
    """
    Cleanup semua instance LightGlue yang ter-register
    """
    global _cleanup_in_progress
    
    if _cleanup_in_progress:
        return
    
    _cleanup_in_progress = True
    
    try:
        print("🧹 Cleaning up all LightGlue instances...")
        count = 0
        
        for instance in list(_lightglue_instances):
            try:
                # Coba berbagai method cleanup
                if hasattr(instance, '_cleanup_gpu'):
                    instance._cleanup_gpu()
                    count += 1
                elif hasattr(instance, 'stop_all'):
                    instance.stop_all()
                    count += 1
                elif hasattr(instance, 'sess'):
                    if instance.sess is not None:
                        del instance.sess
                        instance.sess = None
                    count += 1
            except Exception as e:
                print(f"⚠️ Error cleaning instance {id(instance)}: {e}")
        
        # Force garbage collection
        gc.collect()
        
        if count > 0:
            print(f"✅ Cleaned {count} LightGlue instances")
        
    except Exception as e:
        print(f"❌ Error in cleanup_all_instances: {e}")
    finally:
        _cleanup_in_progress = False


# ==========================================================
# HOOK 4: SIGNAL HANDLERS
# ==========================================================
def signal_handler(signum, frame):
    """Handler untuk SIGINT dan SIGTERM"""
    print(f"\n🛑 Signal {signum} received, cleaning up...")
    cleanup_all_instances()
    sys.exit(0)


def exception_handler(exc_type, exc_value, exc_traceback):
    """Handler untuk uncaught exceptions"""
    # Skip SystemExit
    if exc_type is SystemExit:
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    
    print(f"\n💥 Uncaught exception: {exc_type.__name__}: {exc_value}")
    traceback.print_exception(exc_type, exc_value, exc_traceback)
    
    print("🧹 Cleaning GPU before exit...")
    cleanup_all_instances()
    
    # Call original hook
    sys.__excepthook__(exc_type, exc_value, exc_traceback)


# ==========================================================
# HOOK 5: WRAPPER untuk running_light_glue
# ==========================================================
def wrap_running_light_glue(original_func):
    """
    Wrapper untuk running_light_glue tanpa mengubah signature-nya
    """
    @wraps(original_func)
    def wrapper(*args, **kwargs):
        try:
            return original_func(*args, **kwargs)
        except KeyboardInterrupt:
            print("\n⚠️ Process interrupted by user")
            cleanup_all_instances()
            raise
        except Exception as e:
            print(f"💥 Error in running_light_glue: {e}")
            cleanup_all_instances()
            raise
        finally:
            # Cleanup setelah selesai
            cleanup_all_instances()
    
    return wrapper


def patch_running_light_glue():
    """
    Monkey patch running_light_glue untuk menambahkan cleanup otomatis
    """
    try:
        for module_name, module in sys.modules.items():
            if hasattr(module, 'running_light_glue'):
                original_func = module.running_light_glue
                wrapped_func = wrap_running_light_glue(original_func)
                module.running_light_glue = wrapped_func
                print(f"✅ Wrapped running_light_glue in module: {module_name}")
                return True
        
        print("⚠️ running_light_glue not found in loaded modules")
        return False
        
    except Exception as e:
        print(f"⚠️ Error wrapping running_light_glue: {e}")
        return False


# ==========================================================
# HOOK 6: WRAPPER untuk main()
# ==========================================================
def wrap_main_function(original_main):
    """
    Wrapper untuk function main() tanpa mengubah signature
    """
    @wraps(original_main)
    def wrapper(*args, **kwargs):
        processor = None
        
        try:
            # Jalankan main original
            result = original_main(*args, **kwargs)
            return result
            
        except Exception as e:
            print(f"💥 Error in main: {e}")
            raise
            
        finally:
            # Cleanup di akhir
            cleanup_all_instances()
    
    return wrapper


def patch_main_function():
    """
    Monkey patch function main() untuk cleanup otomatis
    """
    try:
        for module_name, module in sys.modules.items():
            if hasattr(module, 'main') and callable(module.main):
                # Skip built-in modules
                if module_name.startswith('_'):
                    continue
                
                original_main = module.main
                wrapped_main = wrap_main_function(original_main)
                module.main = wrapped_main
                # print(f"✅ Wrapped main() in module: {module_name}")
                return True
        
        print("⚠️ main() not found in loaded modules")
        return False
        
    except Exception as e:
        print(f"⚠️ Error wrapping main(): {e}")
        return False


# ==========================================================
# HOOK 7: WORKER THREAD PATCH
# ==========================================================
def patch_worker_stop():
    """
    Enhance ImageProcessingMultiThreading.stop() dengan cleanup
    """
    try:
        for module_name, module in sys.modules.items():
            if hasattr(module, 'ImageProcessingMultiThreading'):
                WorkerClass = module.ImageProcessingMultiThreading
                
                original_stop = WorkerClass.stop
                
                @wraps(original_stop)
                def enhanced_stop(self):
                    print("🛑 Worker.stop() called, cleaning GPU...")
                    
                    # Call original stop
                    try:
                        original_stop(self)
                    except Exception as e:
                        print(f"⚠️ Original stop() error: {e}")
                    
                    # Cleanup semua instances
                    cleanup_all_instances()
                
                WorkerClass.stop = enhanced_stop
                # print("✅ Enhanced ImageProcessingMultiThreading.stop()")
                return True
                
    except Exception as e:
        print(f"⚠️ Error enhancing worker.stop(): {e}")
        return False


# ==========================================================
# MAIN INSTALLATION FUNCTION
# ==========================================================
def install_safety_hooks():
    """
    Install semua safety hooks untuk GPU cleanup otomatis
    Call function ini di awal aplikasi Anda
    """
    print("=" * 60)
    print("🛡️ Installing GPU Safety Hooks...")
    print("=" * 60)
    
    # 1. Install atexit handler
    atexit.register(cleanup_all_instances)
    print("✅ Registered atexit cleanup")
    
    # 2. Install signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    print("✅ Registered signal handlers (SIGINT, SIGTERM)")
    
    # 3. Install exception handler
    sys.excepthook = exception_handler
    print("✅ Registered exception handler")
    
    # 4. Patch LightGlueAlgorithm.__init__
    if patch_lightglue_init():
        print("✅ LightGlueAlgorithm.__init__ patched")
    
    # 5. Patch _cleanup_gpu
    if patch_cleanup_gpu():
        print("✅ _cleanup_gpu enhanced")
    
    # 6. Patch running_light_glue
    # Uncomment jika sudah ada di sys.modules
    # if patch_running_light_glue():
    #     print("✅ running_light_glue wrapped")
    
    # 7. Patch main function
    # Uncomment jika sudah ada di sys.modules
    # if patch_main_function():
    #     print("✅ main() wrapped")
    
    # 8. Patch worker.stop()
    # Uncomment jika sudah ada di sys.modules
    # if patch_worker_stop():
    #     print("✅ worker.stop() enhanced")
    
    print("=" * 60)
    print("✅ All GPU Safety Hooks Installed Successfully!")
    print("=" * 60)


# ==========================================================
# DELAYED PATCHING untuk modules yang belum loaded
# ==========================================================
def install_delayed_patches():
    """
    Install patches untuk modules yang di-load setelah safety hooks
    Call ini setelah import modules yang ingin di-patch
    """
    # print("🔧 Installing delayed patches...")
    
    success_count = 0
    
    if patch_running_light_glue():
        success_count += 1
    
    if patch_main_function():
        success_count += 1
    
    if patch_worker_stop():
        success_count += 1
    
    # print(f"✅ Installed {success_count} delayed patches")


# ==========================================================
# MANUAL CLEANUP FUNCTION (untuk explicit calls)
# ==========================================================
def force_gpu_cleanup():
    """
    Force cleanup GPU secara manual
    Bisa dipanggil kapan saja dari kode Anda
    """
    print("🧹 Force GPU cleanup requested...")
    cleanup_all_instances()


# ==========================================================
# CONTEXT MANAGER untuk per-operation cleanup
# ==========================================================
class SafeLightGlueContext:
    """
    Context manager untuk guaranteed cleanup per operation
    
    Usage:
        with SafeLightGlueContext():
            processor = LightGlueAlgorithm(db_path)
            # ... use processor ...
        # Auto cleanup here
    """
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        cleanup_all_instances()
        return False  # Don't suppress exceptions
    
__all__ = [
    'install_safety_hooks',
    'install_delayed_patches',
    'force_gpu_cleanup',
    'SafeLightGlueContext',
    'cleanup_all_instances'
]
            