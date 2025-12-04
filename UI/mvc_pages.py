"""
Page configuration for MVC architecture.
Defines available pages without importing legacy code.
"""

class MVCPages:
    """
    Page configuration for MVC architecture.
    Format: (label, icon_path, page_class_name)
    """
    
    # Main pages
    MAIN_PAGES = [
        ("Enhance Stack", "UI/resources/icon/enhance_stack.png", "EnhanceStackView"),
    ]
    
    # Footer pages
    FOOTER_PAGES = [
        ("Settings", "UI/resources/icon/setting.png", None),  # Not yet migrated
    ]
    
    # All pages combined
    ALL_PAGES = MAIN_PAGES + FOOTER_PAGES
