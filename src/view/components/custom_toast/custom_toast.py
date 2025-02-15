from kivy.animation import Animation
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.properties import NumericProperty, StringProperty
from kivy.uix.label import Label

Builder.load_string(
    """
<Toast>:
    size_hint: None, None
    height: self.texture_size[1] + dp(20)
    width: min(self.texture_size[0] + dp(40), dp(500))
    text_size: self.width - dp(20), None
    halign: "center"
    valign: "middle"
    opacity: 0
    canvas.before:
        Color:
            rgba: 0.2, 0.2, 0.2, 0.9
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [dp(10)]
"""
)


class Toast(Label):
    duration = NumericProperty(2.0)  # How long the toast should stay visible
    text = StringProperty("")  # The toast message

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.padding = (dp(15), dp(10))
        self.font_size = dp(15)
        self.bind(size=self.update_position)

    def update_position(self, *args):
        """Center the toast at the bottom of the screen."""
        padding = dp(20)
        self.pos = (
            (Window.width - self.width) - padding,  # Distance from right
            padding,  # Distance from bottom
        )

    def show(self):
        """Show the toast with fade-in and fade-out animations."""
        anim_in = Animation(opacity=1, duration=0.2)
        anim_wait = Animation(opacity=1, duration=self.duration)
        anim_out = Animation(opacity=0, duration=0.2)

        # Chain animations
        anim = anim_in + anim_wait + anim_out

        def on_complete(*args):
            if self.parent:
                self.parent.remove_widget(self)

        anim.bind(on_complete=on_complete)
        anim.start(self)


def toast(text, duration=2.0):
    """Show a toast message.

    Args:
        text (str): Message to display.
        duration (float): Duration in seconds.
    """
    toast = Toast(text=text, duration=duration)
    Window.add_widget(toast)

    # Wait a moment before ensuring it's centered
    Clock.schedule_once(lambda dt: toast.update_position(), 0)

    toast.show()
