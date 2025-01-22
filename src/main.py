import os
from typing import List, cast

from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager
from kivymd.app import MDApp

from controller.contoller_registry import ControllerRegistry
from controller.base_controller import BaseController
from controller.screens.main_screen_contoller import MainScreenController
from model.simulation import SimulationModel
from theme import ThemeManager
from view.components.base_component import BaseComponentView
from view.screens.base_screen import BaseScreenView
from view.screens.main_screen.main_screen import MainScreenView

Window.left = 0  # TODO: Remove this line
Window.top = 0  # TODO: Remove this line


def get_all_kv_files(base_directory: str) -> list:
    """
    Recursively collects all .kv files within the screens and components directories.

    :param base_directory: The root directory (e.g., 'views')
    :return: A list of .kv file paths relative to the base directory.
    """
    kv_files = []
    for subdir in ["screens", "components"]:
        target_dir = os.path.join(os.getcwd() + "/src", base_directory, subdir)
        for root, _, files in os.walk(target_dir):
            for file in files:
                if file.endswith(".kv"):
                    kv_files.append(os.path.join(root, file))
    return kv_files


class ChronosSim(MDApp):

    title: str = "Network Simulator"

    screen_manager: ScreenManager

    simulation_model: SimulationModel

    theme_manager: ThemeManager

    KV_FILES: List[str] = get_all_kv_files("view")

    def build(self, first: bool = False) -> ScreenManager:
        Window.maximize()
        self.theme_manager = ThemeManager()
        self.simulation_model = SimulationModel()
        self.screen_manager = ScreenManager()
        self.add_screen(MainScreenController, MainScreenView(), "main_screen")
        print(self.screen_manager.screen_names)
        return self.screen_manager

    def add_screen(
        self,
        controller: type[BaseController],
        view: BaseScreenView | BaseComponentView,
        name: str,
    ) -> None:
        """
        Instantiates the controller and passes it the simulation model.
        Adds the controller to the list of controllers and the view to the screen manager.
        :param controller: the controller to be added to the app
        :return: None
        """
        controller_instance = controller(view, name, self.simulation_model)
        ControllerRegistry.register(controller_instance)
        self.screen_manager.add_widget(controller_instance.view)

    # def on_keyboard_down(self, window, keyboard, keycode, text, modifiers) -> None:
    #     if "meta" in modifiers or "ctrl" in modifiers and text == "r":
    #         # clear the ControllerRegistry
    #         ControllerRegistry.clear()
    #         self.rebuild()

    def get_theme_manager(self) -> ThemeManager:
        """
        Helper method to ensure IDE auto-completion by explicitly returning the ThemeManager instance.
        """
        return cast(ThemeManager, self.theme_manager)


if __name__ == "__main__":
    ChronosSim().run()
