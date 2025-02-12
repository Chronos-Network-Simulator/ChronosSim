from abc import ABC
from typing import Any, List, TypeVar, Generic, Callable, Dict

T = TypeVar("T")

# TODO: Implement a validate function here instead in the view


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

    value: T
    """
    Value of the setting
    """

    default_value: T
    """
    Default value of the setting
    """

    callback: Callable[[T, T], None]
    """
    Callback function to be called when the setting is changed.
    Use this to update any values in your base model when its corresponding
    setting is updated. Views call this function when the setting is updated.
    Will receive the object that invoked this callback and the new value.
    """


class NumericSetting(BaseModelSetting[float]):
    """
    Setting that holds a numeric value.
    """

    value: float
    min_value: float
    max_value: float

    def __init__(
        self,
        name: str,
        description: str,
        default_value: float,
        min_value: float,
        max_value: float,
        callback: Callable[[float, float], None]
    ):
        self.name = name
        self.description = description
        self.default_value = default_value
        self.min_value = min_value
        self.max_value = max_value
        self.callback = callback



class StringSetting(BaseModelSetting[str]):
    """
    Setting that holds a string value.
    """

    value: str

    def __init__(self, name: str, description: str, default_value: str):
        self.name = name
        self.description = description
        self.default_value = default_value


class RangeSetting(BaseModelSetting[float]):
    """
    Setting that represents a range with a start and end value.
    """

    value: float
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
        step: int
    ):
        self.name = name
        self.description = description
        self.default_value = default_value
        self.min_range = min_range
        self.max_range = max_range
        self.step = step


class OptionSetting(BaseModelSetting[Dict[str,str]]):
    """
    Setting that holds a selectable option from a predefined list.
    """

    value: Any
    options: List[Dict[str,str]]

    def __init__(self, name: str, description: str, default_value: Any, options: List[Dict[str,str]]):
        self.name = name
        self.description = description
        self.default_value = default_value
        self.options = options