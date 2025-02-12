from typing import List

from kivy.properties import NumericProperty, StringProperty, ListProperty
from kivy.uix.boxlayout import BoxLayout

from model.setting.model_settings import BaseModelSetting, NumericSetting


class SettingRenderer:
    """
    A Mixin class that provides any other component the ability to render the
    settings that is passed to this mixin.
    The component that implements this Mixin must define a view that will contain the
    rendered settings.
    """

    settings_view: BoxLayout
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
                setting_view = NumericSettingView(
                    min_value=setting.min_value,
                    max_value=setting.max_value,
                    default_value=setting.default_value,
                    setting=setting,
                    title=setting.name,
                    description=setting.description,
                )
                self.settings_view.add_widget(setting_view)


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
        self.bind(value=self.setting.callback)




class NumericSettingView(BaseSettingView):
    """
    A Kivy widget that renders a numeric setting. Allows to set
    a maximum and minimum value and buttons that allows you to
    increment of decrement the value.
    """

    value = NumericProperty(0)

    min_value = NumericProperty(0)

    max_value = NumericProperty(100)

    def __init__(self,default_value: float, min_value: float, max_value: float, setting: NumericSetting, **kwargs):
        self.value = default_value
        self.min_value = min_value
        self.max_value = max_value
        super().__init__(setting, **kwargs)

class StringSettingView(BaseSettingView):
    """
    A Kivy widget that renders a string setting.
    """

    value = StringProperty("")

    def __init__(self,default_value: str, setting: BaseModelSetting, **kwargs):
        self.value = default_value
        super().__init__(setting, **kwargs)

class RangeSettingView(BaseSettingView):
    """
    A kivy widget that renders a range settings as a slider.
    """

    value = NumericProperty(0)

    min_value = NumericProperty(0)

    max_value = NumericProperty(100)

    step = NumericProperty(1)

    def __init__(self,default_value: float, min_value: float, max_value: float, step:int, setting: NumericSetting, **kwargs):
        self.value = default_value
        self.min_value = min_value
        self.max_value = max_value
        self.step = step
        super().__init__(setting, **kwargs)

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

    def __init__(self,default_value: str, options: List[dict], setting: BaseModelSetting, **kwargs):
        self.selected_option = default_value
        self.options = options
        super().__init__(setting, **kwargs)

    def set_value(self, value: str):
        self.value = value


