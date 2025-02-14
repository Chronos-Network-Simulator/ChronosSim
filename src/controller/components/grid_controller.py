from typing import cast

from pubsub import pub

from controller.base_controller import BaseController
from model.grid import BaseSimulationGrid
from view.components.grid_renderer.grid_view import GridView


class GridController(BaseController):

    def __init__(self, simulation):
        super().__init__(GridView(), "grid", simulation)

    def _init_subscribers(self) -> None:
        # simulation
        pub.subscribe(self.on_grid_changed, "simulation.grid_changed")
        pub.subscribe(self.on_grid_changed, "simulation.grid_updated")
        pub.subscribe(self.on_step_complete, "simulation.step_complete")
        pass

    def on_step_complete(self) -> None:
        """
        Called when the simulation has completed a step. This method updates the grid view to reflect the new state
        of the simulation.
        :return: None
        """
        cast(GridView, self.view).update_grid(self.simulation.grid.nodes, 0.2)

    def on_grid_changed(self, grid: BaseSimulationGrid) -> None:
        """
        Called when the grid type has changed in the simulation model. This method
        clears the gridview of all current nodes, and draws the new grid on top.
        :param grid: The new grid to draw. This is ignored as the grid is already stored in the simulation model.
        :return: The type of grid to draw.
        """
        if self.simulation.grid is not None:
            cast(GridView, self.view).draw_grid(
                self.simulation.grid.length,
                self.simulation.grid.width,
                self.simulation.grid.region_size,
                0.2,
            )
