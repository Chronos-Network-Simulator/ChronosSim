from kivy.event import EventDispatcher
from kivy.properties import OptionProperty, ColorProperty
from utils import convert_hex_to_decimal
from kivy.core.text import LabelBase
from threading import Lock


class ThemeManager(EventDispatcher):
    """
    Manages the theme of the application.
    This is a singleton class
    """

    current_theme = OptionProperty("dark", options=["light", "dark"])

    bg_color = ColorProperty()
    secondary_bg_color = ColorProperty()
    text_color = ColorProperty()
    secondary_text_color = ColorProperty()
    bg_border_color = ColorProperty()
    sec_bg_border_color = ColorProperty()

    primary_color = ColorProperty()

    _instance = None
    _lock = Lock()

    def __new__(cls):
        """Creates a new instance of ThemeManager or returns the existing one."""
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
            return cls._instance

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._initialize_defaults()
        self._initialize_fonts()
        self.bind(current_theme=self.on_theme_change)

    def _initialize_fonts(self):
        """Initialize default fonts based on the current theme."""
        LabelBase.register(
            name="Inter",
            fn_regular="../src/assets/fonts/Inter-Regular.ttf",
        )
        LabelBase.register(
            name="Inter-Medium",
            fn_regular="../src/assets/fonts/Inter-Medium.ttf",
        )
        LabelBase.register(
            name="Inter-Bold",
            fn_regular="../src/assets/fonts/Inter-Bold.ttf",
        )

    def _initialize_defaults(self):
        """Initialize default colors based on the current theme."""
        self.on_theme_change()

    def on_theme_change(self, *args):
        """Update color properties when the theme changes."""
        theme_colors = {
            "dark": {
                "bg_color": "1A1B26",
                "secondary_bg_color": "1F222D",
                "text_color": "FFFFFF",
                "secondary_text_color": "868383",
                "bg_border_color": "36384F",
                "sec_bg_border_color": "30364F",
                "primary_color": "4863EC",
            },
            "light": {
                "bg_color": "FFFFFF",
                "secondary_bg_color": "F2F2F2",
                "text_color": "000000",
                "secondary_text_color": "666666",
                "border_color": "30364F",
            },
        }

        colors = theme_colors.get(self.current_theme, theme_colors["dark"])

        self.bg_color = convert_hex_to_decimal(colors["bg_color"])
        self.secondary_bg_color = convert_hex_to_decimal(colors["secondary_bg_color"])
        self.text_color = convert_hex_to_decimal(colors["text_color"])
        self.secondary_text_color = convert_hex_to_decimal(
            colors["secondary_text_color"]
        )
        self.bg_border_color = convert_hex_to_decimal(colors["bg_border_color"])
        self.sec_bg_border_color = convert_hex_to_decimal(colors["sec_bg_border_color"])
        self.primary_color = convert_hex_to_decimal(colors["primary_color"])

    def toggle_theme(self):
        """Toggle between light and dark themes."""
        self.current_theme = "dark" if self.current_theme == "light" else "light"
