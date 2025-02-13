from controller.base_controller import BaseController
from view.components.grid_renderer.grid_view import GridView


class GridController(BaseController):

    def __init__(self, simulation):
        super().__init__(GridView(), "grid", simulation)


    def _init_subscribers(self) -> None:
        # simulation
        # pub.subscribe(cast(GridView, self.view).draw_grid, "simulation.grid_changed")
        pass
    def on_grid_changed(self, grid_type: str) -> None:
        """
        Called when the grid type has changed in the simulation model. This method
        clears the gridview of all current nodes, and draws the new grid on top.
        :param grid_type:
        :return: The type of grid to draw.
        """