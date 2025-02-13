from typing import cast

from pubsub import pub

from controller.base_controller import BaseController
from exception.exception import ConfigError
from model.grid import get_grid_by_name
from view.components.sidebar.sidebar import SideBarView


class SideBarController(BaseController):

    def __init__(self, simulation):
        super().__init__(SideBarView(), "sidebar", simulation)

    def _init_subscribers(self) -> None:
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
            :param grid_type: The name of the grid to change to.
        """
        try:
            if grid_type == "None":
                self.simulation.set_grid(None)
                return
            self.simulation.set_grid(get_grid_by_name(grid_type))
            print(self.simulation.grid)
        except ConfigError as e:
            pub.sendMessage("ui.error", message=str(e))
        except ValueError as e:
            pub.sendMessage("ui.error", message=str(e))
