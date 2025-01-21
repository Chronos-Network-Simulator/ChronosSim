from kivy.lang.builder import Builder
from kivymd.uix.screen import MDScreen


class SimulationScreen(MDScreen):

    def __init__(self, *args, **kwargs):
        Builder.load_file("ui/simulation_screen/SimulationScreen.kv")
        super().__init__(*args, **kwargs)
