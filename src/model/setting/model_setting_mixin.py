from typing import List, Any

from pubsub import pub
from slugify import slugify

from model.setting.model_settings import BaseModelSetting, SupportedEntity


class ModelSettingMixin:
    """
    This mixin provides the ability for a model to support the setting system
    """

    name: str
    """
    The name of the model
    """

    slug: str
    """
    The slug for the model. Used to identify the model in the pub/sub system
    """

    settings: List[BaseModelSetting]
    """
    A list of settings that should be exposed to configure this model.
    """

    entity_type: SupportedEntity
    """
    The entity type this obejct is. Based on this, the settings pub and sub channels are set
    for settings updates.
    """

    def __init__(self):
        if self.name:
            self.slug = slugify(self.name)
            self._register_settings()

    def _register_settings(self) -> None:
        """
        Registers this model to receive setting chane events from the settings
        that it defines.
        :return: None
        """
        for setting in self.settings:
            pub.subscribe(self._handle_setting_change_event, setting.channel)

    def _handle_setting_change_event(
        self, attributes: [str], new_value: Any, old_value: Any
    ):
        """
        Handles setting change events and updates the grid model's properties. Receives the exact attribute name
        that was changed in string format
        """
        for attribute in attributes:
            if hasattr(self, attribute):
                setattr(self, attribute, new_value)
            else:
                raise ValueError(f"Attribute {attribute} not found in {self}")
        if self.entity_type == SupportedEntity.GRID:
            pub.sendMessage(topicName="simulation.grid_changed", grid=self)
