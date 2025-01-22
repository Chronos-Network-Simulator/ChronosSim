from kivy.event import EventDispatcher
from kivy.properties import OptionProperty, ColorProperty
from utils import convert_hex_to_decimal


class ThemeManager(EventDispatcher):

    current_theme = OptionProperty("dark", options=["light", "dark"])

    bg_color = ColorProperty()
    secondary_bg_color = ColorProperty()
    text_color = ColorProperty()
    secondary_text_color = ColorProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._initialize_defaults()
        self.bind(current_theme=self.on_theme_change)

    def _initialize_defaults(self):
        """Initialize default colors based on the current theme."""
        self.on_theme_change()

    def on_theme_change(self, *args):
        """Update color properties when the theme changes."""
        theme_colors = {
            "dark": {
                "bg_color": "1A1B26",
                "secondary_bg_color": "24283B",
                "text_color": "FFFFFF",
                "secondary_text_color": "AAAAAA",
            },
            "light": {
                "bg_color": "FFFFFF",
                "secondary_bg_color": "F2F2F2",
                "text_color": "000000",
                "secondary_text_color": "666666",
            },
        }

        colors = theme_colors.get(self.current_theme, theme_colors["dark"])

        self.bg_color = convert_hex_to_decimal(colors["bg_color"])
        self.secondary_bg_color = convert_hex_to_decimal(colors["secondary_bg_color"])
        self.text_color = convert_hex_to_decimal(colors["text_color"])
        self.secondary_text_color = convert_hex_to_decimal(
            colors["secondary_text_color"]
        )

    def toggle_theme(self):
        """Toggle between light and dark themes."""
        self.current_theme = "dark" if self.current_theme == "light" else "light"
