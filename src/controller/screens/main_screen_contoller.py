from kivy.clock import Clock

from controller.base_controller import BaseController
from controller.components.bottombar_controller import BottomBarController
from controller.components.grid_controller import GridController
from controller.components.sidebar_controller import SideBarController


class MainScreenController(BaseController):

    sidebar: SideBarController
    """
    The sidebar controller for the main screen. This is a child controller and just a quick
    way to access the sidebar controller
    """

    grid: GridController
    """
    The grid controller for the main screen. This is a child controller and just a quick
    way to access the grid controller
    """

    def __init__(self, view, name, simulation):
        self.sidebar = SideBarController(simulation)
        self.grid = GridController(simulation)
        self.bottom_bar = BottomBarController(simulation)
        self.add_child_controller(self.sidebar)
        self.add_child_controller(self.grid)
        super().__init__(view, name, simulation)
        Clock.schedule_once(lambda dt: self._init_views(), 0)

    def _init_views(self) -> None:
        """
        Initializes and adds all views to the Main Screen
        """
        self.view.ids.sidebar.add_widget(self.sidebar.view)
        self.view.ids.grid.add_widget(self.grid.view)
