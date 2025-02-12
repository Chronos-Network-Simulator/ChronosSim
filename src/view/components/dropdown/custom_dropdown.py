from typing import Callable, Optional

from kivy.properties import BooleanProperty, ListProperty, StringProperty
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.dropdown import DropDown
from kivymd.uix.behaviors import CommonElevationBehavior

from view.components.base_component import BaseComponentView


class CustomDropDownItem(ButtonBehavior, BaseComponentView):  # type: ignore
    text = StringProperty("default text")
    icon = StringProperty("")
    callback: Optional[Callable[[str], None]] = None

    def __init__(
        self, text: str, callback: Optional[Callable[[str], None]] = None, **kwargs
    ):
        self.text = text
        self.callback = callback
        super().__init__(**kwargs)

    def on_release(self):
        if self.callback:
            self.callback(self.text)
        return super().on_release()


class CustomDropDown(ButtonBehavior, BoxLayout):  # type: ignore
    class CustomDropDownInternal(DropDown): ...  # type: ignore

    class CustomDropDownContainer(BoxLayout, CommonElevationBehavior):  # type: ignore
        shadow_offset = [0, 0]

        elevation_level = 2

        shadow_radius = [15, 15, 15, 15]

        selected_option = StringProperty("default text")

        open = BooleanProperty(False)

    selected_option = StringProperty("default text")

    options = ListProperty([])

    open = BooleanProperty(False)

    _dropdown: CustomDropDownInternal

    on_select_callback: Optional[Callable[[str], None]] = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._dropdown = self.CustomDropDownInternal()
        self._dropdown.bind(on_dismiss=self.on_dismiss)

        # Bind options to update the dropdown items when changed
        self.bind(options=self._update_dropdown_items)

    def on_press(self, *args):
        if self.open:
            self.open = False
            self._dropdown.dismiss()

        else:
            self.open = True
            self._dropdown.open(self)
        return super().on_press()

    def on_dismiss(self, *args):
        self.open = False

    def on_select(self, option: str) -> None:
        self._dropdown.dismiss()
        self.open = False
        if self.on_select_callback:
            self.on_select_callback(option)

    def _update_dropdown_items(self, instance, value):
        """Update dropdown items when options change."""
        if self._dropdown.container:
            self._dropdown.clear_widgets()
            for option in value:
                self._dropdown.add_widget(
                    CustomDropDownItem(
                        text=option["text"],
                        callback=self.on_select,
                        icon=option["icon"],
                    )
                )
