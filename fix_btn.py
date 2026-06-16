import sys

file_path = r'e:\APP Developer\Pixel Refine\pixel_refine_desktop\enhance_stack\components\batch_page_v2\algorithm_panel.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

old_string = '''        self.process_btn = Button(
            f"▶ {language_config.BTN_START}",
            variant="primary",
        )
        self.process_btn.setFixedWidth(180)  # Make it smaller and elegant
        self.process_btn.setStyleSheet(
            self.process_btn.styleSheet()
            + \"\"\"
            QPushButton {
                padding: 6px 12px;
                font-size: 10pt;
            }
        \"\"\"
        )'''

new_string = '''        self.process_btn = Button(
            f"▶ {language_config.BTN_START}",
            variant="primary",
        )
        self.process_btn.setFixedWidth(180)  # Make it smaller and elegant
        
        from resources.GenericUILibrary.theme import get_theme, create_button_style
        theme = get_theme()
        self.process_btn.setStyleSheet(
            create_button_style(self.process_btn.variant, theme)
            + \"\"\"
            QPushButton {
                padding: 6px 12px;
                font-size: 10pt;
            }
        \"\"\"
        )'''

if old_string in content:
    content = content.replace(old_string, new_string)
    
    # Also update _update_all_buttons
    old_update = '''                if variant is not None:
                    btn.variant = variant
                    # Update objectName to match the correct QSS selector for dynamic styling
                    btn.setObjectName("deleteButton" if variant == "danger" else "processButton")
                    btn.setStyleSheet(\"\"\"
                        .QPushButton {
                            padding: 6px 12px;
                            font-size: 10pt;
                        }
                    \"\"\")'''
    
    new_update = '''                if variant is not None:
                    btn.variant = variant
                    # Update objectName to match the correct QSS selector for dynamic styling
                    btn.setObjectName("deleteButton" if variant == "danger" else "processButton")
                    from resources.GenericUILibrary.theme import get_theme, create_button_style
                    theme = get_theme()
                    btn.setStyleSheet(
                        create_button_style(btn.variant, theme)
                        + \"\"\"
                        QPushButton {
                            padding: 6px 12px;
                            font-size: 10pt;
                        }
                        \"\"\"
                    )'''
    content = content.replace(old_update, new_update)

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print('Replaced successfully')
else:
    print('String not found!')
