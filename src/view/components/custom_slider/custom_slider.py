from kivy.clock import Clock
from kivy.properties import NumericProperty
from kivy.uix.boxlayout import BoxLayout


class CustomSlider(BoxLayout):

    stored_value = NumericProperty(0.0)
    """
    The actual value that this setting holds. Do not read
    the direct text inside the input component and instead
    read this value always.
    """

    min = NumericProperty(0.0)
    """
    The minimum value that this setting can hold.
    """

    max = NumericProperty(100.0)
    """
    The maximum value that this setting can hold.
    """

    step = NumericProperty(1)
    """
    The step size that the value can be adjusted by.
    """

    callback = None
    """
    Called when the  value of the slider changes
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Clock.schedule_once(self._on_init)

    def _on_init(self, *args):
        self.ids.internal_slider.bind(value=self.on_slider_value_change)

    def on_slider_value_change(self, instance, value):
        self.stored_value = value
        if self.callback:
            self.callback(value)
