from kivy.lang import Builder
from kivy.uix.screenmanager import Screen

from ui.simulation_screen.SimulationScreen import SimulationScreen


class ConfigureScreen(Screen):

    def __init__(self, *args, **kwargs):
        Builder.load_file("ui/configure_screen/ConfigureScreen.kv")
        super().__init__()

    def navigate_to_simulation_screen(self):
        """
        Applies the current simulation properties and navigates the user to the simulation screen
        """
        self.manager.switch_to(
            SimulationScreen(name="simulation_screen"), direction="left"
        )
