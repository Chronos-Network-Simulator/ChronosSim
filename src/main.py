from kivy.core.window import Window

from ui.configure_screen.ConfigureScreen import ConfigureScreen
from ui.simulation_screen.SimulationScreen import SimulationScreen
from kivy.uix.screenmanager import ScreenManager
from kivymd.app import MDApp

Window.left = 0  # TODO: Remove this line
Window.top = 0  # TODO: Remove this line


class ChronosSim(MDApp):

    title = "Network Simulator"

    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "DeepOrange"
        sm = ScreenManager()
        sm.switch_to(ConfigureScreen(name="configure_screen"))
        return sm


if __name__ == "__main__":
    ChronosSim().run()
