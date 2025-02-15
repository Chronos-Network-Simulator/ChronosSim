from kivy.properties import NumericProperty, StringProperty, BooleanProperty
from kivy.uix.behaviors.button import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout


class NumericInput(ButtonBehavior, BoxLayout):  # type: ignore
    class ValueAdjustButton(ButtonBehavior, BoxLayout):  # type: ignore
        icon = StringProperty("plus")

    stored_value = NumericProperty(0.0)  # Holds the actual value
    default_value = NumericProperty(0.0)  # Allows setting an external initial value

    min_value = NumericProperty(0.0)
    max_value = NumericProperty(100.0)
    focused = BooleanProperty(False)
    callback = None

    def on_kv_post(self, base_widget):
        """Sets the initial value of stored_value once from default_value."""
        self.stored_value = self.default_value

    def update_focus(self, focus):
        self.focused = focus

    def set_value(self, value: str):
        """Updates stored_value when TextInput is validated."""
        value = float(value)
        if self.min_value <= value <= self.max_value:
            self.stored_value = value
        else:
            self.stored_value = (
                self.min_value if value < self.min_value else self.max_value
            )
        if self.callback:
            self.callback(self.stored_value)

    def update_value(self, value: int):
        """Updates stored_value when plus/minus buttons are clicked."""
        new_value = self.stored_value + value
        if self.min_value <= new_value <= self.max_value:
            self.stored_value = new_value
