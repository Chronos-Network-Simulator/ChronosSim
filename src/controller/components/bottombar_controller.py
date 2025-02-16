from pubsub import pub

from controller.base_controller import BaseController
from view.components.bottom_bar.bottom_bar import BottomBarView


class BottomBarController(BaseController):

    def __init__(self, simulation):
        super().__init__(BottomBarView(), "bottom_bar", simulation)

    def _init_subscribers(self) -> None:
        pub.subscribe(self._handle_simulation_status, "ui.simulation.status")

    def _handle_simulation_status(self, status: str) -> None:
        """
        Handles the simulation status changes requested by the UI
        :param status:
        :return:
        """
        if status == "play":
            self.simulation.create_simulations()
            self.simulation.play()
        elif status == "pause":
            self.simulation.pause()
        elif status == "stop":
            self.simulation.stop()
        elif status == "step":
            self.simulation.create_simulations()
            self.simulation.step()
        else:
            raise ValueError(f"Unknown status: {status}")
