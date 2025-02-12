from kivy.properties import NumericProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import Screen, ScreenManager
from kivymd.app import MDApp

from theme import ThemeManager


class MainScreen(Screen):
    def __init__(self, **kwargs):
        super(MainScreen, self).__init__(**kwargs)

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

    def __init__(self, value,**kwargs):
        self.stored_value = value
        super(CustomSlider, self).__init__(**kwargs)



class TestApp(MDApp):
    theme_manager: ThemeManager

    sm = ScreenManager()

    def build(self, first: bool = False):
        self.theme_manager = ThemeManager()
        screen = MainScreen(name="main_screen")
        self.sm.add_widget(screen)
        screen.add_widget(CustomSlider(value=5, min = 0, max = 10, step = 1))
        return self.sm


if __name__ == "__main__":
    TestApp().run()
