from kivymd.uix.behaviors import CommonElevationBehavior
from view.components.base_component import BaseComponentView


class SideBarView(BaseComponentView, CommonElevationBehavior):

    kv_file = "view/components/sidebar/sidebar.kv"

    elevation_level = 4

    shadow_radius = [20, 20, 20, 20]

    shadow_softness = 5

    # shadow_offset = [5, 0]
