from kivy.lang import Builder
from kivy.uix.screenmanager import Screen


class BaseScreenView(Screen):

    kv_file: str = ""
    """
    All screens must define a basekv file. In development mode these KV files
    are auto hot reloaded
    """

    def __init__(self):
        Builder.load_file(self.kv_file)
        super().__init__()
