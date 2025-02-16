from typing import cast

from kivy.clock import Clock
from pubsub import pub

from controller.base_controller import BaseController
from model.grid import get_grid_by_name
from model.message_spawner import get_message_spawner_by_name
from model.node import get_node_by_name
from view.components.sidebar.sidebar import SideBarView


class SideBarController(BaseController):
    def __init__(self, simulation):
        super().__init__(SideBarView(), "sidebar", simulation)
        Clock.schedule_once(lambda dt: self._render_static_settings(), 0)

    def _init_subscribers(self) -> None:
        view = cast(SideBarView, self.view)

        # Simulation updates
        pub.subscribe(view.update_grid_type, "simulation.grid_type_changed")
        pub.subscribe(view.update_node_type, "simulation.node_changed")
        pub.subscribe(
            view.render_message_spawner_settings, "simulation.message_spawner_changed"
        )

        # UI updates
        pub.subscribe(self.grid_type_changed, "ui.grid_type_changed")
        pub.subscribe(self.node_type_changed, "ui.node_type_changed")
        pub.subscribe(
            self.message_spawner_type_changed, "ui.message_spawner_type_changed"
        )
        pub.subscribe(self.update_node_count, "ui.update_node_count")
        pub.subscribe(self.update_step_count, "ui.update_step_count")
        pub.subscribe(self.update_simulation_count, "ui.update_simulation_count")
        pub.subscribe(self.update_simulation_delay, "ui.update_simulation_delay")

    def _render_static_settings(self) -> None:
        cast(SideBarView, self.view).render_message_template_settings(
            self.simulation.message_template
        )

    def grid_type_changed(self, grid_type: str) -> None:
        """Change the grid type of the simulation."""
        if grid_type == "None":
            self.simulation.set_grid(None)
            return
        self.simulation.set_grid(get_grid_by_name(grid_type))

    def node_type_changed(self, node_type: str) -> None:
        """Change the node type of the simulation."""
        if node_type == "None":
            self.simulation.set_node(None)
            return
        self.simulation.set_node(get_node_by_name(node_type))

    def message_spawner_type_changed(self, message_spawner_type: str) -> None:
        """Change the message spawner type of the simulation."""
        if message_spawner_type == "None":
            self.simulation.set_message_spawner(None)
            return
        self.simulation.set_message_spawner(
            get_message_spawner_by_name(message_spawner_type)
        )

    def update_node_count(self, node_count: int) -> None:
        """Update the node count of the simulation."""
        self.simulation.node_count = node_count

    def update_step_count(self, step_count: int) -> None:
        """Update the step count of the simulation."""
        self.simulation.step_count = step_count

    def update_simulation_count(self, simulation_count: int) -> None:
        """Update the simulation count."""
        self.simulation.num_simulations = simulation_count

    def update_simulation_delay(self, simulation_delay: int) -> None:
        """Update the simulation delay."""
        self.simulation.step_delay = simulation_delay
