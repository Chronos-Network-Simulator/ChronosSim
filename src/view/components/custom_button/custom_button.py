from kivy.properties import StringProperty
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout


class CustomButton(ButtonBehavior, BoxLayout):
    text = StringProperty("")
    icon = StringProperty("")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(pos=self.update_canvas, size=self.update_canvas)

    def on_hover(self, *args):
        pass

    def update_canvas(self, *args):
        self.canvas.ask_update()
