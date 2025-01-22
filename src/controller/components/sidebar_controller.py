from controller.base_controller import BaseController
from view.components.sidebar.sidebar import SideBarView


class SideBarController(BaseController):

    def __init__(self, simulation):
        super().__init__(SideBarView(), "sidebar", simulation)
