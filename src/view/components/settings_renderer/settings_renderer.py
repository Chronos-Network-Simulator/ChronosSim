from typing import List, cast

from kivy.properties import NumericProperty, StringProperty, ListProperty
from kivy.uix.boxlayout import BoxLayout

from model.setting.model_settings import (
    BaseModelSetting,
    NumericSetting,
    RangeSetting,
    OptionSetting,
    StringSetting,
)


class SettingRenderer:
    """
    A Mixin class that provides any other component the ability to render the
    settings that is passed to this mixin.
    The component that implements this Mixin must define a view that will contain the
    rendered settings.
    """

    settings_view: BoxLayout | None = None
    """
    The kivy widget that contains the settings view to which settings are to be added
    """

    def render_settings(self, settings: List[BaseModelSetting]) -> None:
        """
        Render the settings that are passed to this method.
        :param settings: A list of settings that need to be rendered
        :return: None
        """
        # clear the view of all settings
        self.settings_view.clear_widgets()
        for setting in settings:
            # Based on the base setting type render the appropriate setting view
            if isinstance(setting, NumericSetting):
                num_setting = cast(NumericSetting, setting)
                setting_view = NumericSettingView(
                    min_value=num_setting.min_value,
                    max_value=num_setting.max_value,
                    default_value=num_setting.default_value,
                    setting=num_setting,
                    title=num_setting.name,
                    description=num_setting.description,
                )
                self.settings_view.add_widget(setting_view)
            elif isinstance(setting, RangeSetting):
                range_setting = cast(RangeSetting, setting)
                setting_view = RangeSettingView(
                    min_value=range_setting.min_range,
                    max_value=range_setting.max_range,
                    step=range_setting.step,
                    default_value=range_setting.default_value,
                    setting=range_setting,
                    title=range_setting.name,
                    description=range_setting.description,
                )
                self.settings_view.add_widget(setting_view)
            elif isinstance(setting, OptionSetting):
                option_setting = cast(OptionSetting, setting)
                setting_view = OptionSettingView(
                    default_value=option_setting.default_value,
                    options=option_setting.options,
                    setting=option_setting,
                    title=option_setting.name,
                    description=option_setting.description,
                )
                self.settings_view.add_widget(setting_view)
            elif isinstance(setting, StringSetting):
                setting_view = StringSettingView(
                    default_value=setting.default_value,
                    setting=setting,
                    title=setting.name,
                    description=setting.description,
                )
                self.settings_view.add_widget(setting_view)

    def clear_settings(self) -> None:
        """
        Clear all the settings from the view
        """
        if self.settings_view is not None:
            self.settings_view.clear_widgets()


class BaseSettingView(BoxLayout):
    """
    Base class for all setting views. All setting views should inherit this class.
    """

    title = StringProperty("Title")
    """
    The title of the setting
    """

    description = StringProperty("Description")
    """
    The description or help text for the setting. Basically what this setting does.
    """

    setting: BaseModelSetting
    """
    The setting that this view is rendering
    """

    def __init__(self, setting: BaseModelSetting, **kwargs):
        super().__init__(**kwargs)
        self.setting = setting
        self.bind(value=self._on_value_changed)

    def _on_value_changed(self, instance, value):
        self.setting.value = value


class NumericSettingView(BaseSettingView):
    """
    A Kivy widget that renders a numeric setting. Allows to set
    a maximum and minimum value and buttons that allows you to
    increment of decrement the value.
    """

    value = NumericProperty(0)

    min_value = NumericProperty(0)

    max_value = NumericProperty(100)

    def __init__(
        self,
        default_value: float,
        min_value: float,
        max_value: float,
        setting: NumericSetting,
        **kwargs,
    ):
        self.value = default_value
        self.min_value = min_value
        self.max_value = max_value
        super().__init__(setting, **kwargs)

    def set_value(self, value: float):
        self.value = value


class StringSettingView(BaseSettingView):
    """
    A Kivy widget that renders a string setting.
    """

    value = StringProperty("")

    def __init__(self, default_value: str, setting: StringSetting, **kwargs):
        self.value = default_value
        super().__init__(setting, **kwargs)

    def set_value(self, value: str):
        self.value = value


class RangeSettingView(BaseSettingView):
    """
    A kivy widget that renders a range settings as a slider.
    """

    value = NumericProperty(0)

    min_value = NumericProperty(0)

    max_value = NumericProperty(100)

    step = NumericProperty(1)

    def __init__(
        self,
        default_value: float,
        min_value: float,
        max_value: float,
        step: int,
        setting: RangeSetting,
        **kwargs,
    ):
        self.value = default_value
        self.min_value = min_value
        self.max_value = max_value
        self.step = step
        super().__init__(setting, **kwargs)

    def set_value(self, value: float):
        self.value = value


class OptionSettingView(BaseSettingView):
    """
    A kivy widget that renders a setting with options in the form
    of a dropdown. Each option is represented as an
    text and icon.
    """

    value = StringProperty("default text")
    """
    Represents the option that is selected
    """

    options = ListProperty([])

    def __init__(
        self,
        default_value: str,
        options: List[dict],
        setting: OptionSetting,
        **kwargs,
    ):
        self.selected_option = default_value
        self.options = options
        super().__init__(setting, **kwargs)
        self.ids.input.on_select_callback = self.set_value

    def set_value(self, value: str):
        self.value = value
