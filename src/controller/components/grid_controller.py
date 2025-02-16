from typing import cast

from pubsub import pub

from controller.base_controller import BaseController
from controller.components.bottombar_controller import BottomBarController
from model.grid import BaseSimulationGrid
from view.components.grid_renderer.grid_view import GridView


class GridController(BaseController):
    def __init__(self, simulation):
        super().__init__(GridView(), "grid", simulation)
        self.add_child_controller(BottomBarController(simulation))
        self.view.ids.bottom_bar.add_widget(self.child_controllers[0].view)
        self.current_page = 1
        self.current_simulation_id = None

    def _init_subscribers(self) -> None:
        super()._init_subscribers()
        pub.subscribe(self.on_grid_changed, "simulation.grid_changed")
        pub.subscribe(self.on_grid_changed, "simulation.grid_type_changed")
        pub.subscribe(self.on_grid_update, "simulation.grid_updated")
        # pub.subscribe(self.on_simulation_selected, "simulation.selected")
        pub.subscribe(self.on_simulation_state_update, "simulation.state_updated")

    def on_simulation_state_update(self, simulation_id: str) -> None:
        """Handle real-time updates from the simulation"""
        self.current_simulation_id = simulation_id
        if simulation_id != self.current_simulation_id:
            return  # we don't care about computing simulations that are not visible\
        cast(GridView, self.view).draw_grid_nodes_from_live_simulation(
            self.simulation.data_handler.simulations[simulation_id][-1].node_states, 0.2
        )

    def on_grid_update(self) -> None:
        """
        This method updates the grid view to reflect the new state of the simulation.
        :return: None
        """
        cast(GridView, self.view).draw_grid_nodes(self.simulation.grid.nodes, 0.2)

    def on_grid_changed(self, grid: BaseSimulationGrid) -> None:
        """
        Called when the grid type has changed in the simulation model. This method
        clears the gridview of all current nodes, and draws the new grid on top.
        :param grid: The new grid to draw. This is ignored as the grid is already stored in the simulation model.
        :return: The type of grid to draw.
        """
        if self.simulation.grid is not None:
            cast(GridView, self.view).draw_grid_outline(
                self.simulation.grid.length,
                self.simulation.grid.width,
                self.simulation.grid.region_size,
                0.2,
            )
            cast(GridView, self.view).draw_grid_nodes(self.simulation.grid.nodes, 0.2)
        else:
            cast(GridView, self.view).clear()
