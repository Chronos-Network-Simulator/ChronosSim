from typing import Dict, Type, TypeVar, Optional

from controller.base_controller import BaseController


T = TypeVar("T", bound=BaseController)


class ControllerRegistry:
    _controllers: Dict[str, BaseController] = {}
    """
    A dictionary that stores all registered controllers of the application
    """

    @classmethod
    def register(cls, controller: BaseController) -> None:
        """
        Regsiter a controller in the application. This allows the controller to
        be accessed anywhere in the application.

        :param controller: The controller to be registered
        :type controller: BaseController
        """
        if controller.name in cls._controllers:
            return
        cls._controllers[controller.name] = controller

    @classmethod
    def get(cls, name: str, expected_type: Type[T]) -> Optional[T]:
        """
        Get a controller from the registry by name and check if it is of the expected type.

        :param name: The name of the controller to get
        :type name: str
        :param expected_type: The expected type of the controller
        :type expected_type: Type[T]
        :raises KeyError: If the controller with the given name is not found
        :raises TypeError: If the controller is not of the expected type
        :return: The controller
        :rtype: Optional[T]
        """
        controller = cls._controllers.get(name)
        if controller is None:
            raise KeyError(f"Controller with name '{name}' not found.")

        if not isinstance(controller, expected_type):
            raise TypeError(
                f"Controller '{name}' is not of type {expected_type.__name__}."
            )

        return controller

    @classmethod
    def all(cls) -> Dict[str, BaseController]:
        return cls._controllers

    @classmethod
    def unregister(cls, name: str):
        if name in cls._controllers:
            del cls._controllers[name]

    @classmethod
    def clear(cls):
        cls._controllers.clear()
