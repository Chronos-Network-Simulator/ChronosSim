from __future__ import annotations
from abc import ABC
from typing import List


from model.simulation import SimulationModel
from view.components.base_component import BaseComponentView
from view.screens.base_screen import BaseScreenView


class BaseController(ABC):

    name: str
    """
    The name of the controller. This is used to identify the controller in the controller registry.
    """

    view: BaseScreenView | BaseComponentView
    """
    Stores a reference to the view that the controller is controlling.
    """

    simulation: SimulationModel
    """
    Stores a reference to the simulation model as most controllers will need to
    access the simulation model.
    """

    child_controllers: List[BaseController] = []
    """
    List of any child controllers that this controller may have. These are 
    auto registered when the controller is instanced
    """

    def __init__(
        self,
        view: BaseScreenView | BaseComponentView,
        name: str,
        simulation: SimulationModel,
    ):
        self.view = view
        self.name = name
        self.simulation = simulation
        self._auto_add_child_controllers()

    def _auto_add_child_controllers(self) -> None:
        from controller.contoller_registry import ControllerRegistry

        """
        Automatically registers any child controllers that the controller may have.
        """
        for controller in self.child_controllers:
            ControllerRegistry.register(controller)

    def add_child_controller(self, controller: BaseController) -> None:
        from controller.contoller_registry import ControllerRegistry

        """
        Adds a child controller to the controller.
        """
        self.child_controllers.append(controller)
        ControllerRegistry.register(controller)
