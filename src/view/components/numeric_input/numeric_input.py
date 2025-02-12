from kivy.properties import NumericProperty, StringProperty, BooleanProperty
from kivy.uix.behaviors.button import  ButtonBehavior
from kivy.uix.boxlayout import BoxLayout


class NumericInput(ButtonBehavior, BoxLayout):  # type: ignore
    class ValueAdjustButton(ButtonBehavior, BoxLayout):  # type: ignore
        icon = StringProperty("plus")

    stored_value = NumericProperty(0.0)

    min_value = NumericProperty(0.0)

    max_value = NumericProperty(100.0)

    focused = BooleanProperty(False)

    def update_focus(self, focus):
        self.focused = focus

    def set_value(self, value: str):
        value = float(value)
        if self.min_value <= value <= self.max_value:
            self.stored_value = value
        else:
            self.stored_value = self.min_value if value < self.min_value else self.max_value

    def update_value(self, value: int):
        if (self.stored_value + value) <= self.max_value and (
            self.stored_value + value
        ) >= self.min_value:
            self.stored_value += value