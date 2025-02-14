from typing import cast

from kivy.clock import Clock
from pubsub import pub

from controller.base_controller import BaseController
from exception.exception import ConfigError
from model.grid import get_grid_by_name
from model.message_spawner import get_message_spawner_by_name
from model.node import get_node_by_name
from view.components.sidebar.sidebar import SideBarView


class SideBarController(BaseController):

    def __init__(self, simulation):
        super().__init__(SideBarView(), "sidebar", simulation)

    def _init_subscribers(self) -> None:
        # simulation
        pub.subscribe(
            cast(SideBarView, self.view).update_grid_type, "simulation.grid_changed"
        )
        pub.subscribe(
            cast(SideBarView, self.view).update_node_type, "simulation.node_changed"
        )
        pub.subscribe(
            cast(SideBarView, self.view).render_message_spawner_settings,
            "simulation.message_spawner_changed",
        )

        # UI Updates
        pub.subscribe(self.grid_type_changed, "ui.grid_type_changed")
        pub.subscribe(self.node_type_changed, "ui.node_type_changed")
        pub.subscribe(
            self.message_spawner_type_changed, "ui.message_spawner_type_changed"
        )
        pub.subscribe(self.simulation.set_node_count, "ui.update_node_count")
        pub.subscribe(self.update_step_count, "ui.update_step_count")
        Clock.schedule_once(lambda dt: self._render_static_settings(), 0)

    def _render_static_settings(self) -> None:
        # render the message settings instantly
        cast(SideBarView, self.view).render_message_template_settings(
            self.simulation.message_template
        )

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
        except ConfigError as e:
            pub.sendMessage("ui.error", message=str(e))
        except ValueError as e:
            pub.sendMessage("ui.error", message=str(e))

    def node_type_changed(self, node_type: str) -> None:
        """
        Change the node type of the simulation to the specified node name.

        Args:
            :param node_type: The name of the node to change to.
        """
        try:
            if node_type == "None":
                self.simulation.set_node(None)
                return
            self.simulation.set_node(get_node_by_name(node_type))
        except ConfigError as e:
            pub.sendMessage("ui.error", message=str(e))
        except ValueError as e:
            pub.sendMessage("ui.error", message=str(e))

    def message_spawner_type_changed(self, message_spawner_type: str) -> None:
        """
        Change the message spawner type of the simulation to the specified message spawner name.

        Args:
            :param message_spawner_type: The name of the message spawner to change to.
        """
        try:
            if message_spawner_type == "None":
                self.simulation.set_message_spawner(None)
                return
            self.simulation.set_message_spawner(
                get_message_spawner_by_name(message_spawner_type)
            )
        except ConfigError as e:
            pub.sendMessage("ui.error", message=str(e))
        except ValueError as e:
            pub.sendMessage("ui.error", message=str(e))

    def update_step_count(self, step_count: int) -> None:
        """
        Update the step count of the simulation to the specified step count.
        :param step_count:
        :return:
        """
        self.simulation.step_count = step_count
