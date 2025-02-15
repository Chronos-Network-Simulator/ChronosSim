from kivy.properties import StringProperty, BooleanProperty
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout


class CustomButton(ButtonBehavior, BoxLayout):
    text = StringProperty("")
    icon = StringProperty("")
    hover = BooleanProperty(False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.register_event_type("on_hover")
        self.bind(pos=self.update_canvas, size=self.update_canvas)

    def on_hover(self, *args):
        pass

    def update_canvas(self, *args):
        self.canvas.ask_update()

    def on_mouse_pos(self, window, pos):
        if not self.get_root_window():
            return

        # Convert window coordinates to widget coordinates
        converted_pos = self.to_widget(*pos)
        inside = self.collide_point(*converted_pos)

        if inside != self.hover:
            self.hover = inside
            self.dispatch("on_hover")
