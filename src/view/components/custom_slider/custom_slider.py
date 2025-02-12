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