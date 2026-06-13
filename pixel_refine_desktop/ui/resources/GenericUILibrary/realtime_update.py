import weakref
import functools

# Global list of weak references to registered QWidget instances
_registered_widgets = []

def realtime_update(cls):
    """
    A class decorator for QWidget-based classes.
    Automatically registers new instances of the class using weak references
    so that they can be updated in real-time when trigger_realtime_update() is called.
    
    Usage:
        @realtime_update
        class MyWidget(QWidget):
            def retranslate_ui(self):
                # Update text labels here
                pass
    """
    orig_init = cls.__init__

    @functools.wraps(orig_init)
    def new_init(self, *args, **kwargs):
        orig_init(self, *args, **kwargs)
        # Register this instance using weakref
        ref = weakref.ref(self)
        _registered_widgets.append(ref)

    cls.__init__ = new_init
    return cls

def trigger_realtime_update():
    """
    Triggers the real-time update by iterating through all alive registered widget instances
    and calling their retranslate_ui() method.
    Cleans up dead references automatically.
    """
    global _registered_widgets
    alive_widgets = []
    
    for ref in _registered_widgets:
        widget = ref()
        if widget is not None:
            alive_widgets.append(ref)
            # Check if the widget has retranslate_ui and is not wrapped in deleteLater
            if hasattr(widget, "retranslate_ui"):
                try:
                    # Check if widget is not deleted by Qt (QObject.parent or similar checks)
                    # For safety in PySide, wraps with try-except
                    widget.retranslate_ui()
                except RuntimeError:
                    # Occurs if Qt C++ object has been deleted
                    pass
                except Exception as e:
                    print(f"Error during realtime update for {widget}: {e}")
                    
    # Maintain only alive references
    _registered_widgets = alive_widgets
