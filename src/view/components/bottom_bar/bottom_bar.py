from kivy.uix.boxlayout import BoxLayout
from pubsub import pub


class BottomBarView(BoxLayout):
    """
    Represents the bottom bar that is used controlling the status of the simulation such as
    running, paused or reset
    """

    def handle_button_clicks(self, event: str) -> None:
        """
        Handles all event clicks from the buttons in the bottom ba
        :param event:
        :return:
        """
        if event == "play":
            pub.sendMessage("ui.simulation.status", status="play")
        elif event == "pause":
            pub.sendMessage("ui.simulation.status", status="pause")
        elif event == "stop":
            pub.sendMessage("ui.simulation.status", status="stop")
        elif event == "step":
            pub.sendMessage("ui.simulation.status", status="step")
