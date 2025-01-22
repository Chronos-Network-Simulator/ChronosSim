from controller.base_controller import BaseController
from controller.components.sidebar_controller import SideBarController


class MainScreenController(BaseController):

    sidebar: SideBarController
    """
    The sidebar controller for the main screen. This is a child controller and just a quick
    way to access the sidebar controller
    """

    def __init__(self, view, name, simulation):
        self.sidebar = SideBarController(simulation)
        self.child_controllers.append(self.sidebar)
        super().__init__(view, name, simulation)
        self._init_views()

    def _init_views(self) -> None:
        """
        Initializes and adds all views to the Main Screen
        """
        self.view.ids.sidebar.add_widget(self.sidebar.view)
