from abc import ABC
from enum import Enum
from typing import List, TypeVar, Generic, Dict

from pubsub import pub

T = TypeVar("T")


# TODO: Implement a validate function here instead in the view


class SupportedEntity(Enum):
    """
    Represents the different types of entities that the settings sub system can support
    """

    GRID = "grid"
    NODE = "node"
    MESSAGE = "message"


class BaseModelSetting(ABC, Generic[T]):
    """
    Base class for model settings. Inherit this class to implement any settings
    class that needs to be used to expose certain settings to the view.
    """

    name: str
    """
    Name of the setting
    """

    description: str
    """
    Description of the setting
    """

    _value: T
    """
    Value of the setting. Do not access directly as this is a private variable.
    """

    default_value: T
    """
    Default value of the setting
    """

    attributes: List[str]
    """
    The list of attributes that this setting can control on the base model
    """

    entityType: SupportedEntity
    """
    The type of entity that this setting belongs to. This value is required for the pu/sub
    system to properly dispatch edit events based on the entity type.
    """

    channel: str
    """
    The generated channel that models should subscribe to listen to changes in this setting.
    """

    def __init__(
        self,
        name: str,
        description: str,
        default_value: T,
        attributes: List[str],
        entity_type: SupportedEntity,
    ):
        self.name = name
        self.description = description
        self.default_value = default_value
        self._value = default_value
        self.attributes = attributes
        self.entityType = entity_type
        self.channel = self._generate_channel_name()

    def _generate_channel_name(self) -> str:
        """
        Generates a Pub/Sub channel name for this setting at instantiation.
        :return:  The channel name
        """
        return (
            f"setting.{self.entityType.value}." + ".".join(self.attributes) + ".changed"
        )

    @property
    def value(self) -> T:
        return self._value

    @value.setter
    def value(self, new_value: T):
        old_value = self._value
        self._value = new_value
        self._publish_change_event(old_value, new_value)

    def _publish_change_event(self, old_value: T, new_value: T):
        """
        Publishes an event when the setting's value is changed.
        """
        if self.channel:
            pub.sendMessage(
                self.channel,
                attributes=self.attributes,
                new_value=new_value,
                old_value=old_value,
            )


class NumericSetting(BaseModelSetting[float]):
    """
    Setting that holds a numeric value.
    """

    min_value: float
    max_value: float

    def __init__(
        self,
        name: str,
        description: str,
        default_value: float,
        min_value: float,
        max_value: float,
        attributes: List[str],
        entity_type: SupportedEntity,
    ):
        super().__init__(name, description, default_value, attributes, entity_type)
        self.min_value = min_value
        self.max_value = max_value

    @BaseModelSetting.value.setter
    def value(self, new_value: float):
        if not (self.min_value <= new_value <= self.max_value):
            raise ValueError(
                f"Value must be between {self.min_value} and {self.max_value}"
            )
        BaseModelSetting.value.fset(self, new_value)


class StringSetting(BaseModelSetting[str]):
    """
    Setting that holds a string value.
    """

    def __init__(
        self,
        name: str,
        description: str,
        default_value: str,
        attributes: List[str],
        entity_type: SupportedEntity,
    ):
        super().__init__(name, description, default_value, attributes, entity_type)


class RangeSetting(BaseModelSetting[float]):
    """
    Setting that represents a range with a start and end value.
    """

    min_range: float
    max_range: float
    step: int

    def __init__(
        self,
        name: str,
        description: str,
        default_value: float,
        min_range: float,
        max_range: float,
        step: int,
        attributes: List[str],
        entity_type: SupportedEntity,
    ):
        super().__init__(name, description, default_value, attributes, entity_type)
        self.min_range = min_range
        self.max_range = max_range
        self.step = step


class OptionSetting(BaseModelSetting[Dict[str, str]]):
    """
    Setting that holds a selectable option from a predefined list.
    """

    options: List[Dict[str, str]]

    def __init__(
        self,
        name: str,
        description: str,
        default_value: str,
        options: List[Dict[str, str]],
        attributes: list[str],
        entity_type: SupportedEntity,
    ):
        super().__init__(name, description, default_value, attributes, entity_type)
        self.options = options
