from typing import cast

from pubsub import pub

from controller.base_controller import BaseController
from controller.components.bottombar_controller import BottomBarController
from model.grid import BaseSimulationGrid
from view.components.grid_renderer.grid_view import GridView


class GridController(BaseController):

    _current_simulation_id: str = None

    @property
    def current_simulation_id(self) -> str:
        """
        The current Simulation ID that is displayed and being processed by the grid controller.
        The controller only loads and listens to one simulation at a time due to the large number
        of data that is being processed.
        """
        return self._current_simulation_id

    @current_simulation_id.setter
    def current_simulation_id(self, value: str) -> None:
        self._current_simulation_id = value
        if value is not None:
            cast(GridView, self.view).current_simulation_id = value

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
        pub.subscribe(self.on_simulation_selected, "ui.simulation_selected")
        pub.subscribe(self.on_simulation_state_update, "simulation.state_updated")

    def on_simulation_selected(self, direction: str) -> None:
        """
        Called when the user presses the next or previous button to switch between simulations.
        """
        if self.current_simulation_id is None:
            return
        simulations_list = list(self.simulation.data_handler.simulations)
        current_index = simulations_list.index(self.current_simulation_id)

        if direction == "next":
            next_index = (current_index + 1) % len(simulations_list)
            self.current_simulation_id = simulations_list[next_index]
        elif direction == "previous":
            previous_index = (current_index - 1) % len(simulations_list)
            self.current_simulation_id = simulations_list[previous_index]

        cast(GridView, self.view).set_pagination_values(
            current_page=simulations_list.index(self.current_simulation_id),
            total_pages=len(simulations_list),
        )
        self.on_simulation_state_update(self.current_simulation_id)

    def on_simulation_state_update(self, simulation_id: str) -> None:
        """Handle real-time updates from the simulation"""
        if self.current_simulation_id is None:
            # if no simulation ID set then we get the first simulation ID from our data handler
            self.current_simulation_id = next(
                iter(self.simulation.data_handler.simulations)
            )
            cast(GridView, self.view).set_pagination_values(
                current_page=list(self.simulation.data_handler.simulations).index(
                    self.current_simulation_id
                )
                + 1,
                total_pages=len(self.simulation.data_handler.simulations),
            )
        view = cast(GridView, self.view)
        view.current_step = (
            self.simulation.data_handler.simulations[simulation_id][-1].step + 1
        )
        view.total_steps = self.simulation.step_count
        if simulation_id != self.current_simulation_id:
            return  # we don't care about computing simulations that are not visible
        view.draw_grid_nodes_from_live_simulation(
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
