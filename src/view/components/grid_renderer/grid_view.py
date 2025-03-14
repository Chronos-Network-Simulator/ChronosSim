from typing import List

from kivy.graphics import Ellipse, Color
from kivy.properties import NumericProperty, StringProperty
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scatterlayout import ScatterLayout
from kivy.uix.widget import Widget
from pubsub import pub

from model.monitoring.DataTypes import NodeState
from model.node import BaseNode


class GridCell(ButtonBehavior, Widget):
    """
    A grid cell widget that can be clicked and used to select a cell in the grid.
    """

    def __init__(self, cell_id, **kwargs):
        super().__init__(**kwargs)
        self.cell_id = cell_id
        self.size_hint = (None, None)
        self.touch_moved = False
        self.touch_start_pos = None

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self.touch_start_pos = touch.pos
            self.touch_moved = False
            return False
        return super().on_touch_down(touch)

    def on_touch_move(self, touch):
        if self.touch_start_pos:
            dx = touch.pos[0] - self.touch_start_pos[0]
            dy = touch.pos[1] - self.touch_start_pos[1]
            if (dx * dx + dy * dy) > 49:  # 5 pixels squared
                self.touch_moved = True
        return super().on_touch_move(touch)

    def on_touch_up(self, touch):
        if self.collide_point(*touch.pos) and not self.touch_moved:
            self.on_press()
            return True
        self.touch_start_pos = None
        self.touch_moved = False
        return super().on_touch_up(touch)


class CustomScatterLayout(ScatterLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.touch_mode = None
        self.last_touch_pos = None

    def _is_touch_in_sidebar(self, touch_pos):
        try:
            sidebar = self.parent.parent.ids.sidebar
            return sidebar.collide_point(*touch_pos)
        except AttributeError:
            return False

    def on_touch_down(self, touch):
        if self._is_touch_in_sidebar(touch.pos):
            return False
        if not self.collide_point(*touch.pos):
            return False
        if touch.is_mouse_scrolling:
            current_scale = self.scale
            if touch.button == "scrolldown":
                if current_scale < 10:
                    new_scale = current_scale * 1.1
                else:
                    return True
            elif touch.button == "scrollup":
                if current_scale > 0.5:
                    new_scale = current_scale * 0.9
                else:
                    return True
            else:
                return super().on_touch_down(touch)

            touch_pos = self.to_widget(*touch.pos)
            cx = self.center_x
            cy = self.center_y
            tx = touch_pos[0] - cx
            ty = touch_pos[1] - cy
            self.scale = new_scale
            scale_delta = new_scale - current_scale
            self.pos = (
                self.pos[0] - (tx * scale_delta),
                self.pos[1] - (ty * scale_delta),
            )
            return True

        self.touch_mode = "pan"
        self.last_touch_pos = touch.pos
        return False

    def on_touch_move(self, touch):
        if self._is_touch_in_sidebar(touch.pos):
            return False
        if self.touch_mode == "pan" and self.last_touch_pos:
            dx = touch.pos[0] - self.last_touch_pos[0]
            dy = touch.pos[1] - self.last_touch_pos[1]
            self.pos = (self.pos[0] + dx, self.pos[1] + dy)
            self.last_touch_pos = touch.pos
            return True
        return super().on_touch_move(touch)

    def on_touch_up(self, touch):
        if self._is_touch_in_sidebar(touch.pos):
            return False
        if self.touch_mode == "pan":
            self.touch_mode = None
            self.last_touch_pos = None
            return True
        return super().on_touch_up(touch)


class GridView(FloatLayout):
    grid_layout: GridLayout | None = None
    current_simulation_id = StringProperty()
    current_page = NumericProperty(1)
    total_pages = NumericProperty(1)
    current_step = NumericProperty(0)
    total_steps = NumericProperty(0)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.grid_layout = self.ids.grid

    def draw_grid_outline(
        self,
        length_km: float,
        width_km: float,
        region_size_km: float,
        scale_factor: float,
    ):
        self.clear()
        length = int(length_km * scale_factor)
        width = int(width_km * scale_factor)
        region_size = int(region_size_km * scale_factor)
        if not self.grid_layout:
            return
        self.grid_layout.cols = width // region_size
        self.grid_layout.width = width
        self.grid_layout.height = length
        for row in range(length // region_size):
            for col in range(width // region_size):
                cell_id = f"{row},{col}"
                cell = GridCell(cell_id, size=(region_size, region_size))
                self.grid_layout.add_widget(cell)

    def draw_grid_nodes(self, nodes: List[BaseNode], scale_factor: float):
        if not self.grid_layout:
            return
        self.grid_layout.canvas.after.clear()
        if nodes:
            for node in nodes:
                x = node.position[0] * scale_factor + self.grid_layout.x
                y = node.position[1] * scale_factor + self.grid_layout.y
                size = 4
                circle = Ellipse(pos=(x - size / 2, y - size / 2), size=(size, size))
                color = (
                    Color(0, 1, 0) if getattr(node, "target", True) else Color(1, 0, 0)
                )
                self.grid_layout.canvas.after.add(color)
                self.grid_layout.canvas.after.add(circle)
        self.grid_layout.canvas.ask_update()

    def draw_grid_nodes_from_live_simulation(
        self, nodes: List[NodeState], scale_factor: float
    ):
        if not self.grid_layout:
            return
        self.grid_layout.canvas.after.clear()
        if not nodes:
            return

        # Find min and max message counts
        message_counts = [node.message_count for node in nodes]
        min_messages = min(message_counts)
        max_messages = max(message_counts)

        # Avoid division by zero if all nodes have same message count
        message_range = max_messages - min_messages
        if message_range == 0:
            message_range = 1

        def get_color_for_message_count(count):
            # Calculate percentage between min and max (0 to 1)
            if message_range == 0:
                percentage = 1
            else:
                percentage = (count - min_messages) / message_range

            # Red color (1, 0, 0)
            # Dark grey color (0.2, 0.2, 0.2)
            r = 0.2 + (percentage * 0.8)  # From 0.2 to 1.0
            g = 0.2 - (percentage * 0.2)  # From 0.2 to 0.0
            b = 0.2 - (percentage * 0.2)  # From 0.2 to 0.0

            return r, g, b

        for node in nodes:
            x = node.position[0] * scale_factor + self.grid_layout.x
            y = node.position[1] * scale_factor + self.grid_layout.y
            size = 4
            circle = Ellipse(pos=(x - size / 2, y - size / 2), size=(size, size))

            # Get color based on message count
            r, g, b = get_color_for_message_count(node.message_count)
            if node.target:
                r, g, b = 0, 1, 0  # Green color for target nodes
            color = Color(r, g, b)

            self.grid_layout.canvas.after.add(color)
            self.grid_layout.canvas.after.add(circle)

        self.grid_layout.canvas.ask_update()

    def clear(self):
        if not self.grid_layout:
            return
        self.grid_layout.clear_widgets()
        self.grid_layout.canvas.after.clear()

    def set_pagination_values(self, current_page: int, total_pages: int):
        self.current_page = current_page
        self.total_pages = total_pages

    def navigate_page(self, direction: str):
        pub.sendMessage("ui.simulation_selected", direction=direction)

    def export_graphs(self):
        pub.sendMessage("ui.export_graphs")
