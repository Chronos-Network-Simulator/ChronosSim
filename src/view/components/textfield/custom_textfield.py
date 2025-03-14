from kivy.properties import StringProperty, BooleanProperty
from kivy.uix.boxlayout import BoxLayout


class CustomTextField(BoxLayout):

    stored_value = StringProperty("")
    """
    The actual value that this setting holds. Do not read
    the direct text inside the input component and instead
    read this value always.
    """

    callback = None
    """
    Called when the  value of the text field changes
    """

    focused = BooleanProperty(False)

    def update_focus(self, focus):
        self.focused = focus

    def set_value(self, value: str):
        self.stored_value = value
        if self.callback:
            self.callback(value)
