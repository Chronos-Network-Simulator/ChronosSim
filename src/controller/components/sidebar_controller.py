from typing import cast
from controller.base_controller import BaseController
from exception.exception import ConfigError
from model.grid import get_grid_by_name
from view.components.sidebar.sidebar import SideBarView
from pubsub import pub


class SideBarController(BaseController):

    def __init__(self, simulation):
        super().__init__(SideBarView(), "sidebar", simulation)
        self._initialize_subscribers()

    def _initialize_subscribers(self) -> None:
        """
        Initialize all subscribers for the sidebar controller for listening to any UI events.
        """
        # simulation
        pub.subscribe(
            cast(SideBarView, self.view).update_grid_type, "simulation.grid_changed"
        )
        # UI Updates
        pub.subscribe(self.grid_type_changed, "ui.grid_type_changed")

    def grid_type_changed(self, grid_type: str) -> None:
        """
        Change the grid type of the simulation to the specified grid name.

        Args:
            grid_name (str): The name of the grid to change to.
        """
        try:
            if grid_type == "None":
                self.simulation.set_grid(None)
                return
            self.simulation.set_grid(get_grid_by_name(grid_type))
        except ConfigError as e:
            pub.sendMessage("ui.error", message=str(e))
        except ValueError as e:
            pub.sendMessage("ui.error", message=str(e))
