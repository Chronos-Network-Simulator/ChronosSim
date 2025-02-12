from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivymd.uix.behaviors import CommonElevationBehavior
from pubsub import pub

from model.grid import AVAILABLE_GRIDS, get_grid_by_name
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


class GridSettingsGroup(  # type: ignore
    BoxLayout, SettingRenderer
):
    """
    Controls the background color of the expansion panel when switching between open and closed states
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
        # Render the respective Grid's settings
        grid = None if grid_type == "None" else get_grid_by_name(grid_type)
        if grid is None:
            self.ids.grid_type_description.text = ""
            return
        self.render_settings(grid.settings)
