from kivy.utils import get_color_from_hex

# Colors from stylesheet.py
COLOR_BACKGROUND_MAIN = get_color_from_hex("#F5F8FA")
COLOR_BACKGROUND_PANEL = get_color_from_hex("#FFFFFF")
COLOR_TEXT_PRIMARY = get_color_from_hex("#333333")
COLOR_TEXT_SECONDARY = get_color_from_hex("#555555")

# Slider
COLOR_SLIDER_GROOVE_BORDER = get_color_from_hex("#bbbbbb")
COLOR_SLIDER_GROOVE_BG = get_color_from_hex("#dddddd")
COLOR_SLIDER_HANDLE = get_color_from_hex("#50A2D5")
COLOR_SLIDER_HANDLE_BORDER = get_color_from_hex("#3B89C2")
COLOR_SLIDER_HANDLE_HOVER = get_color_from_hex("#428BB8")

# Buttons
COLOR_BTN_APPLY = get_color_from_hex("#5cb85c")
COLOR_BTN_APPLY_HOVER = get_color_from_hex("#4cae4c")
COLOR_BTN_APPLY_PRESSED = get_color_from_hex("#449d44")

COLOR_BTN_DELETE = get_color_from_hex("#e74c3c")
COLOR_BTN_DELETE_HOVER = get_color_from_hex("#c0392b")

COLOR_BTN_IMPORT = get_color_from_hex("#3498db")
COLOR_BTN_IMPORT_HOVER = get_color_from_hex("#2980b9")

COLOR_BTN_PROCESS_START = get_color_from_hex("#B2F2A0")
COLOR_BTN_PROCESS_END = get_color_from_hex("#66D966")

# Lists
COLOR_LIST_BG = get_color_from_hex("#ffffff")
COLOR_LIST_ITEM_HOVER = get_color_from_hex("#F0F1F1")
COLOR_LIST_ITEM_SELECTED = get_color_from_hex("#CDE8F4")
COLOR_LIST_ITEM_SELECTED_TEXT = get_color_from_hex("#003C5A")

THEME_KV = """
#:import get_color_from_hex kivy.utils.get_color_from_hex

<FlatButton@Button>:
    background_normal: ''
    background_down: ''
    background_color: get_color_from_hex("#FFFFFF")
    color: get_color_from_hex("#333333")
    font_size: '14sp'
    size_hint_y: None
    height: '40dp'
    canvas.before:
        Color:
            rgba: get_color_from_hex("#DCDCDC")
        Line:
            width: 1
            rectangle: self.x, self.y, self.width, self.height

<PrimaryButton@FlatButton>:
    background_color: get_color_from_hex("#3498db")
    color: get_color_from_hex("#FFFFFF")
    canvas.before:
        Color:
            rgba: self.background_color
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [5,]

<DeleteButton@FlatButton>:
    background_color: get_color_from_hex("#e74c3c")
    color: get_color_from_hex("#FFFFFF")
    canvas.before:
        Color:
            rgba: self.background_color
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [5,]

<SuccessButton@FlatButton>:
    background_color: get_color_from_hex("#5cb85c")
    color: get_color_from_hex("#FFFFFF")
    canvas.before:
        Color:
            rgba: self.background_color
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [5,]

<StyledSlider@Slider>:
    cursor_size: (20, 20)
    background_width: '4dp'
    cursor_image: ''
    canvas:
        Color:
            rgba: get_color_from_hex("#dddddd")
        Rectangle:
            pos: (self.x + self.padding, self.center_y - 2)
            size: (self.width - self.padding * 2, 4)
        Color:
            rgba: get_color_from_hex("#50A2D5")
        Ellipse:
            pos: (self.value_pos[0] - 10, self.center_y - 10)
            size: (20, 20)

<Card@BoxLayout>:
    canvas.before:
        Color:
            rgba: get_color_from_hex("#FFFFFF")
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [8,]
"""
