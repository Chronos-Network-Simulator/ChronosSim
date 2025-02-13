from typing import cast

from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivymd.uix.behaviors import CommonElevationBehavior
from pubsub import pub

from model.grid import AVAILABLE_GRIDS, get_grid_by_name
from model.node import AVAILABLE_NODES, get_node_by_name
from view.components.base_component import BaseComponentView
from view.components.settings_renderer.settings_renderer import SettingRenderer


class SideBarView(BaseComponentView, CommonElevationBehavior):
    kv_file = "view/components/sidebar/sidebar.kv"

    elevation_level = 4

    shadow_radius = [20, 20, 20, 20]

    shadow_softness = 5

    def update_grid_type(self, grid_type: str) -> None:
        grid = None if grid_type == "None" else get_grid_by_name(grid_type)
        if grid is None:
            self.ids.grid_settings_group.ids.grid_type_selector.selected_option = "None"
            self.ids.grid_settings_group.ids.grid_type_description.text = ""
            return
        self.ids.grid_settings_group.ids.grid_type_selector.selected_option = grid.name
        self.ids.grid_settings_group.ids.grid_type_description.text = grid.description
        # Render the grid settings
        cast(GridSettingsGroup, self.ids.grid_settings_group).render_settings(
            grid.settings
        )

    def update_node_type(self, node_type: str) -> None:
        node = None if node_type == "None" else get_node_by_name(node_type)
        if node is None:
            self.ids.node_settings_group.ids.node_type_selector.selected_option = "None"
            self.ids.node_settings_group.ids.node_type_description.text = ""
            return
        self.ids.node_settings_group.ids.node_type_selector.selected_option = node.name
        self.ids.node_settings_group.ids.node_type_description.text = node.description
        # Render the node settings
        cast(NodeSettingsGroup, self.ids.node_settings_group).render_settings(
            node.settings
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
