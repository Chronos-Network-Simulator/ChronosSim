from typing import List

from kivy.graphics import Ellipse, Color
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scatterlayout import ScatterLayout
from kivy.uix.widget import Widget

from model.node import BaseNode


class GridCell(ButtonBehavior, Widget):
    """
    A single grid cell with a blue border that acts as a clickable button.
    """

    def __init__(self, cell_id, **kwargs):
        super().__init__(**kwargs)
        self.cell_id = cell_id
        self.size_hint = (None, None)
        self.touch_moved = False
        self.touch_start_pos = None

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            # Store initial touch position
            self.touch_start_pos = touch.pos
            self.touch_moved = False
            return False
        return super().on_touch_down(touch)

    def on_touch_move(self, touch):
        if self.touch_start_pos:
            dx = touch.pos[0] - self.touch_start_pos[0]
            dy = touch.pos[1] - self.touch_start_pos[1]
            # If moved more than 5 pixels, consider it a drag
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
        # Get reference to sidebar through widget tree
        # parent is GridView (BoxLayout), parent.parent is MainScreenView
        try:
            sidebar = self.parent.parent.ids.sidebar
            return sidebar.collide_point(*touch_pos)
        except AttributeError:
            return False

    def on_touch_down(self, touch):
        # First check if touch is in sidebar
        if self._is_touch_in_sidebar(touch.pos):
            return False

        # If touch is outside scatter bounds, ignore it completely
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

            # Get touch pos relative to scatter
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

        # For regular touches, always allow panning
        self.touch_mode = "pan"
        self.last_touch_pos = touch.pos
        return False

    def on_touch_move(self, touch):
        # Check if touch is in sidebar
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
        # Check if touch is in sidebar
        if self._is_touch_in_sidebar(touch.pos):
            return False

        if self.touch_mode == "pan":
            self.touch_mode = None
            self.last_touch_pos = None
            return True
        return super().on_touch_up(touch)


class GridView(BoxLayout):
    """
    A scatter view containing a grid layout. Each grid cell represents a region.
    """

    grid_layout: GridLayout | None = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.grid_layout = self.ids.grid
        self.node_circles = {}

    def draw_grid(
        self,
        length_km: float,
        width_km: float,
        region_size_km: float,
        scale_factor: float,
    ):
        """
        Draws the grid based on simulation parameters.
        :param length_km: Length of the grid in km.
        :param width_km: Width of the grid in km.
        :param region_size_km: Size of each region in km.
        :param scale_factor: Pixels per km for real-world rendering.
        """
        self.grid_layout.clear_widgets()

        length = int(length_km * scale_factor)
        width = int(width_km * scale_factor)
        region_size = int(region_size_km * scale_factor)

        self.grid_layout.cols = width // region_size
        self.grid_layout.width = width
        self.grid_layout.height = length

        for row in range(length // region_size):
            for col in range(width // region_size):
                cell_id = f"{row},{col}"
                cell = GridCell(cell_id, size=(region_size, region_size))
                self.grid_layout.add_widget(cell)

    def update_grid(self, nodes: List[BaseNode], scale_factor: float):
        """
        Updates the grid by drawing nodes as circles.
        """
        # Clear previous node drawings
        for circle in self.node_circles.values():
            self.grid_layout.canvas.remove(circle)  # Remove from canvas
        self.node_circles.clear()

        if nodes:
            for node in nodes:
                x = node.position[0] * scale_factor + self.grid_layout.x
                y = node.position[1] * scale_factor + self.grid_layout.y
                size = 10  # Adjust node size as needed (in pixels)
                circle = Ellipse(pos=(x - size / 2, y - size / 2), size=(size, size))
                color = Color(1, 0, 0)
                self.grid_layout.canvas.add(color)
                self.grid_layout.canvas.add(circle)
                self.node_circles[node.id] = circle

        self.grid_layout.canvas.ask_update()
