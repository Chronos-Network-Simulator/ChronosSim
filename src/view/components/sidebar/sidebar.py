from typing import cast

from kivy.clock import Clock
from kivy.properties import NumericProperty
from kivy.uix.boxlayout import BoxLayout
from kivymd.uix.behaviors import CommonElevationBehavior
from pubsub import pub

from model.grid import AVAILABLE_GRIDS, BaseSimulationGrid
from model.message.BaseMessage import BaseMessage
from model.message_spawner import AVAILABLE_MESSAGE_SPAWNERS, BaseMessageSpawner
from model.node import AVAILABLE_NODES, BaseNode
from view.components.base_component import BaseComponentView
from view.components.settings_renderer.settings_renderer import SettingRenderer


class SideBarView(BaseComponentView, CommonElevationBehavior):
    kv_file = "view/components/sidebar/sidebar.kv"

    elevation_level = 4

    shadow_radius = [20, 20, 20, 20]

    shadow_softness = 5

    def update_grid_type(self, grid: BaseSimulationGrid) -> None:
        if grid is None:
            self.ids.grid_settings_group.ids.grid_type_selector.selected_option = "None"
            self.ids.grid_settings_group.ids.grid_type_description.text = ""
            cast(GridSettingsGroup, self.ids.grid_settings_group).clear_settings()
            return
        self.ids.grid_settings_group.ids.grid_type_selector.selected_option = grid.name
        self.ids.grid_settings_group.ids.grid_type_description.text = grid.description
        # Render the grid settings
        cast(GridSettingsGroup, self.ids.grid_settings_group).render_settings(
            grid.settings
        )

    def update_node_type(self, node: BaseNode) -> None:
        if node is None:
            self.ids.node_settings_group.ids.node_type_selector.selected_option = "None"
            self.ids.node_settings_group.ids.node_type_description.text = ""
            cast(NodeSettingsGroup, self.ids.node_settings_group).clear_settings()
            return
        self.ids.node_settings_group.ids.node_type_selector.selected_option = node.name
        self.ids.node_settings_group.ids.node_type_description.text = node.description
        # Render the node settings
        cast(NodeSettingsGroup, self.ids.node_settings_group).render_settings(
            node.settings
        )

    def render_message_template_settings(self, message_template: BaseMessage) -> None:
        cast(MessageSettingsGroup, self.ids.message_settings_group).render_settings(
            message_template.settings
        )

    def render_message_spawner_settings(
        self, message_spawner: BaseMessageSpawner
    ) -> None:
        if message_spawner is None:
            self.ids.message_spawner_settings_group.ids.message_spawner_type_selector.selected_option = (
                "None"
            )
            self.ids.message_spawner_settings_group.ids.message_spawner_type_description.text = (
                ""
            )
            cast(
                MessageSpawnerSettingsGroup, self.ids.message_spawner_settings_group
            ).clear_settings()
            return
        self.ids.message_spawner_settings_group.ids.message_spawner_type_selector.selected_option = (
            message_spawner.name
        )
        self.ids.message_spawner_settings_group.ids.message_spawner_type_description.text = (
            message_spawner.description
        )
        # Render the message spawner settings
        cast(
            MessageSpawnerSettingsGroup, self.ids.message_spawner_settings_group
        ).render_settings(message_spawner.settings)


class SimulationSettingsGroup(BoxLayout):
    node_count = NumericProperty(1)
    step_count = NumericProperty(1)
    simulation_count = NumericProperty(1)
    simulation_delay = NumericProperty(1)

    """
    Note: All these events are one way as they are directly lined with the simulation handler
    rather than a controller and thus does not need to wait for the simulation handler to 
    respond with the updated value.
    """

    def _update_property(self, prop_name: str, value: float, event_name: str) -> None:
        setattr(self, prop_name, value)
        pub.sendMessage(event_name, **{prop_name: int(value)})

    def update_node_count(self, node_count: float) -> None:
        self._update_property("node_count", node_count, "ui.update_node_count")

    def update_step_count(self, step_count: float) -> None:
        self._update_property("step_count", step_count, "ui.update_step_count")

    def update_simulation_count(self, simulation_count: float) -> None:
        self._update_property(
            "simulation_count", simulation_count, "ui.update_simulation_count"
        )

    def update_simulation_delay(self, simulation_delay: float) -> None:
        self._update_property(
            "simulation_delay", simulation_delay, "ui.update_simulation_delay"
        )


class GridSettingsGroup(BoxLayout, SettingRenderer):  # type: ignore
    """
    Settings related to the grid.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # define the grid type options
        Clock.schedule_once(self.init_options)

    def init_options(self, *args):
        self.ids.grid_type_selector.options = [{"text": "None", "icon": "error"}] + [
            {"text": grid.name, "icon": grid.icon} for grid in AVAILABLE_GRIDS
        ]
        self.ids.grid_type_selector.on_select_callback = self.on_grid_type_selected
        # define the settings_render view
        self.settings_view = self.ids.settings_view

    def on_grid_type_selected(self, grid_type: str) -> None:
        pub.sendMessage(topicName="ui.grid_type_changed", grid_type=grid_type)


class NodeSettingsGroup(BoxLayout, SettingRenderer):
    """
    Settings related to the Nodes that are spawned inside the grid.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Clock.schedule_once(self.init_options)

    def init_options(self, *args):
        """
        Loads the available node types
        :param args:
        :return:
        """
        self.ids.node_type_selector.options = [{"text": "None", "icon": "error"}] + [
            {"text": node.name, "icon": node.icon} for node in AVAILABLE_NODES
        ]
        self.ids.node_type_selector.on_select_callback = self.on_node_type_selected
        self.settings_view = self.ids.settings_view

    def on_node_type_selected(self, node_type: str) -> None:
        pub.sendMessage(topicName="ui.node_type_changed", node_type=node_type)


class MessageSettingsGroup(BoxLayout, SettingRenderer):
    """
    Settings related to the messages that are sent between the nodes.
    Only controls settings related to individual messages and not message
    spawn rates and message transfer rates.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Clock.schedule_once(self.init_options)

    def init_options(self, *args):
        self.settings_view = self.ids.settings_view


class MessageSpawnerSettingsGroup(BoxLayout, SettingRenderer):
    """
    Settings related to how often messages are spawned in the simulation.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Clock.schedule_once(self.init_options)

    def init_options(self, *args):
        self.ids.message_spawner_type_selector.options = [
            {"text": "None", "icon": "error"},
        ] + [
            {"text": message_spawner.name, "icon": message_spawner.icon}
            for message_spawner in AVAILABLE_MESSAGE_SPAWNERS
        ]
        self.settings_view = self.ids.settings_view
        self.ids.message_spawner_type_selector.on_select_callback = (
            self.on_message_spawner_type_selected
        )

    def on_message_spawner_type_selected(self, message_spawner_type: str) -> None:
        pub.sendMessage(
            topicName="ui.message_spawner_type_changed",
            message_spawner_type=message_spawner_type,
        )
