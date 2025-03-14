from typing import cast, List

from pubsub import pub

from controller.base_controller import BaseController
from controller.components.bottombar_controller import BottomBarController
from model.grid import BaseSimulationGrid
from view.components.grid_renderer.grid_view import GridView


class GridController(BaseController):
    _current_simulation_id: str | None = None

    @property
    def current_simulation_id(self) -> str | None:
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
        self._current_simulation_id = None
        self._simulation_ids_cache: List[str] = []

    def _init_subscribers(self) -> None:
        super()._init_subscribers()
        pub.subscribe(self.on_grid_changed, "simulation.grid_changed")
        pub.subscribe(self.on_grid_changed, "simulation.grid_type_changed")
        pub.subscribe(self.on_grid_update, "simulation.grid_updated")
        pub.subscribe(self.on_simulation_selected, "ui.simulation_selected")
        pub.subscribe(self.on_simulation_state_update, "simulation.state_updated")
        pub.subscribe(self.export_graphs, "ui.export_graphs")

    def _get_simulation_ids(self) -> List[str]:
        """
        Get list of simulation IDs from the data handler.
        Cache it to avoid repeated calculations.
        """
        if (
            not self._simulation_ids_cache
            and self.simulation.data_handler.current_session
        ):
            # Get simulation IDs from metadata
            self._simulation_ids_cache = list(
                self.simulation.data_handler._simulation_metadata.keys()
            )
        return self._simulation_ids_cache

    def on_simulation_selected(self, direction: str) -> None:
        """
        Called when the user presses the next or previous button to switch between simulations.
        """
        if self.current_simulation_id is None:
            return

        simulations_list = self._get_simulation_ids()
        if not simulations_list:
            return

        current_index = simulations_list.index(self.current_simulation_id)

        if direction == "next":
            next_index = (current_index + 1) % len(simulations_list)
            self.current_simulation_id = simulations_list[next_index]
        elif direction == "previous":
            previous_index = (current_index - 1) % len(simulations_list)
            self.current_simulation_id = simulations_list[previous_index]

        cast(GridView, self.view).set_pagination_values(
            current_page=simulations_list.index(self.current_simulation_id) + 1,
            total_pages=len(simulations_list),
        )
        self.on_simulation_state_update(simulation_id=self.current_simulation_id)

    def on_simulation_state_update(self, simulation_id: str) -> None:
        """Handle real-time updates from the simulation"""
        data_handler = self.simulation.data_handler

        # If no simulation is selected, try to select the first one
        if self.current_simulation_id is None:
            simulation_ids = self._get_simulation_ids()
            if simulation_ids:
                self.current_simulation_id = simulation_ids[0]
                cast(GridView, self.view).set_pagination_values(
                    current_page=1,
                    total_pages=len(simulation_ids),
                )
            else:
                return  # No simulations available

        # If the update is for a different simulation than the currently displayed one, ignore it
        if simulation_id != self.current_simulation_id:
            return

        # Get latest metadata for this simulation
        metadata = data_handler._simulation_metadata.get(simulation_id, {})
        latest_step = metadata.get("latest_step", 0)
        max_step = metadata.get("max_step", 0)

        view = cast(GridView, self.view)
        view.current_step = latest_step + 1  # UI often shows 1-indexed steps
        view.total_steps = self.simulation.step_count

        # Get the latest state to display
        latest_state = data_handler.get_latest_state(simulation_id)
        if latest_state:
            view.draw_grid_nodes_from_live_simulation(latest_state.node_states, 0.2)

    def on_grid_update(self) -> None:
        """
        This method updates the grid view to reflect the new state of the simulation.
        :return: None
        """
        if self.simulation.grid is not None:
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

    def export_graphs(self) -> None:
        """
        Export all graphs for the current simulation to the specified directory.
        :return: None
        """
        self.simulation.data_handler.graph_generator.generate_all_graphs()

    def reset_cache(self) -> None:
        """Clear the cached simulation IDs when simulations change"""
        self._simulation_ids_cache = []
