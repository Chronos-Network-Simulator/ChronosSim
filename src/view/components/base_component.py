from kivy.uix.boxlayout import BoxLayout
from kivy.lang import Builder


class BaseComponentView(BoxLayout):

    kv_file: str = ""
    """
    The kv file for the component. This must be defined in the subclass.
    """

    def __init__(self):
        Builder.load_file(self.kv_file)
        super().__init__()
