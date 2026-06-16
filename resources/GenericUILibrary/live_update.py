import weakref
import functools
from PySide6.QtWidgets import QWidget

# Global list of weak references to registered QWidget instances and their configuration
# Stored as tuples: (weakref_to_widget, method_name)
_registered_widgets = []

def live_update(arg=None, method_name="retranslate_ui"):
    """
    A class decorator for QWidget-based classes.
    Registers widget instances to automatically receive setting/language updates.
    
    Can be used:
    1. Without arguments (defaults to "retranslate_ui" method):
        @live_update
        class MyWidget(QWidget):
            ...
            
    2. With custom method name:
        @live_update("update_settings")
        class MyWidget(QWidget):
            ...
    """
    # Case A: Decorator used without arguments: @live_update
    if isinstance(arg, type):
        cls = arg
        orig_init = cls.__init__

        @functools.wraps(orig_init)
        def new_init(self, *args, **kwargs):
            orig_init(self, *args, **kwargs)
            ref = weakref.ref(self)
            _registered_widgets.append((ref, "retranslate_ui"))

        cls.__init__ = new_init
        return cls

    # Case B: Decorator used with arguments: @live_update("my_method")
    target_method = arg if isinstance(arg, str) else method_name

    def decorator(cls):
        orig_init = cls.__init__

        @functools.wraps(orig_init)
        def new_init(self, *args, **kwargs):
            orig_init(self, *args, **kwargs)
            ref = weakref.ref(self)
            _registered_widgets.append((ref, target_method))

        cls.__init__ = new_init
        return cls

    return decorator

def _get_widget_depth(widget):
    """
    Helper to calculate nesting depth of a QWidget in the UI tree.
    Root level widgets have depth 0.
    """
    depth = 0
    try:
        p = widget.parent()
        while p is not None:
            depth += 1
            p = p.parent()
    except RuntimeError:
        pass  # Occurs if C++ widget is deleted or wrapper invalid
    return depth

def trigger_live_update(*args, **kwargs):
    """
    Triggers the live update by:
    1. Sorting all alive registered widgets by their parent-nesting depth (shallowest/root first).
    2. Invoking the registered method (e.g. retranslate_ui or retake_setting).
    3. Cascading the call recursively down all children widgets.
    
    Prevents duplicate executions of the SAME method on the SAME widget using a tracking set
    scoped to (widget_id, method_name) tuples, allowing different methods to run independently.
    """
    global _registered_widgets
    alive_widgets = []
    
    # 1. Resolve weak references and filter out dead ones
    active_instances = []
    for ref, method_name in _registered_widgets:
        widget = ref()
        if widget is not None:
            active_instances.append((widget, ref, method_name))
            alive_widgets.append((ref, method_name))
            
    # Keep our global registry clean
    _registered_widgets = alive_widgets

    # 2. Calculate nesting depth for sorting (root/topmost widgets first)
    # Sorts ascending: depth 0 -> depth 1 -> ...
    active_instances.sort(key=lambda item: _get_widget_depth(item[0]))

    # 3. Track processed updates (widget_id, method_name) to isolate pipelines
    updated_instances = set()
    
    for widget, ref, method_name in active_instances:
        widget_id = id(widget)
        pipeline_key = (widget_id, method_name)
        
        # A. Update the parent widget itself if this specific method hasn't run yet
        if pipeline_key not in updated_instances:
            if hasattr(widget, method_name):
                try:
                    getattr(widget, method_name)()
                except RuntimeError:
                    pass  # Widget C++ part might be deleted
                except Exception as e:
                    print(f"Error during live update for root {widget}: {e}")
            updated_instances.add(pipeline_key)
        
        # B. Recursively cascade to all child widgets in the tree for this method
        try:
            for child in widget.findChildren(QWidget):
                child_id = id(child)
                child_pipeline_key = (child_id, method_name)
                
                if child_pipeline_key not in updated_instances:
                    if hasattr(child, method_name) and child != widget:
                        try:
                            getattr(child, method_name)()
                        except RuntimeError:
                            pass
                        except Exception as e:
                            print(f"Error during cascading update for child {child}: {e}")
                        finally:
                            updated_instances.add(child_pipeline_key)
        except RuntimeError:
            pass
        except Exception as e:
            print(f"Error walking children tree for {widget}: {e}")
