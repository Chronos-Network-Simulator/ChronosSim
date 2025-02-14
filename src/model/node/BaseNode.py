from __future__ import annotations

import random
from abc import ABC, abstractmethod
from typing import Tuple, List, Any, Dict

from pubsub import pub
from slugify import slugify

from model.message.BaseMessage import BaseMessage
from model.setting.model_settings import (
    BaseModelSetting,
    NumericSetting,
    SupportedEntity,
)


class BaseNode(ABC):
    """
    Represents a node in the simulation network.
    Extends the base node with message processing, queues, movement capabilities and message ID tracking.
    """

    id: str
    """
    The unique identifier of this node instance
    """

    name: str
    """
    The name of this node type
    """

    slug: str
    """
    An Auto generated slug name for the Node that is used to identify
    it in pub sub events
    """

    description: str
    """
    Description of this node
    """

    icon: str
    """
    The material Design Icon to display to represent this node type
    https://pictogrammers.com/library/mdi/
    """

    settings: List[BaseModelSetting] = [
        NumericSetting(
            name="Detection Range:",
            description=" The detection Range of a node in meters. Typical smart phones have a range of 10-15 meters. Typical Wifi"
            "base stations have a range upto 30 meters",
            min_value=1,
            max_value=30,
            default_value=10,
            entity_type=SupportedEntity.NODE,
            attributes=["detection_range"],
        ),
        NumericSetting(
            name="Movement Range:",
            description="The maximum range in each direction the node can move in each step. For normal use choose values between 1-10 meters",
            min_value=1,
            max_value=10,
            default_value=5,
            entity_type=SupportedEntity.NODE,
            attributes=["movement_range"],
        ),
    ]
    """
    A list of settings that should be exposed to configure this model.
    ClassVar to indicate it's a class variable, inheritable but shared if not overridden.
    Initialize it as an empty list at the class level in BaseNode.
    """

    position: Tuple[float, float]
    """
    Position of the node in the simulation grid
    """

    detection_range: float = 10
    """
    The range in meters a node can detect another node
    """

    movement_range: float = 1.0
    """
    The maximum range in each direction the node can move in each step.
    """

    messages: Dict[BaseMessage, int] = {}
    """
    A dictionary of messages that this node is currently holding.
    The key is the ID of the node that sent the message and the value is a list
    where the first element is the message and the second element is the number of copies of
    that message that the node is holding.
    """

    def __init__(self):
        if not self.name:
            raise NotImplementedError(
                f"Node class {self.__class__.__name__} must define a name."
            )
        self.slug = slugify(self.name)
        self.id = f"{self.slug}-{random.randint(1000, 9999)}"
        self.settings = list(self.__class__.settings)
        self._register_settings()

    def _register_settings(self):
        """
        Register the settings of the node
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
        # send a pub event that the model's values have been changed
        pub.sendMessage("simulation.grid_updated", grid=self)

    @abstractmethod
    def send_message(self, receiving_node: BaseNode) -> List[BaseMessage] | None:
        """
        This function is called by a grid when it detects that this node is in collision with another node.
        The node that will be receiving this message is provided as a parameter and the function should determine
        the message to send and return it. If no message should be sent, the function should return None.
        :param receiving_node:  The node that this node is in collision with
        :return:The messages to send to the receiving node
        """

    @abstractmethod
    def receive_message(
        self, messages: List[BaseMessage], sending_node: BaseNode
    ) -> None:
        """
        The function is called by the grid when a message is received by this node. The function also receives the node
        that sent this message so it can perform processing on that message if needed. When implementing this function
        make sure to add the message to the list of messages that this node currently holds if you wish for the node to
        retain the message.
        :param sending_node: The node that sent this message
        :param messages:  The message that was sent to this node from the sending node
        :return: None
        """

    def move(self):
        """
        Moves the node randomly within its movement range.
        """
        delta_x = random.uniform(-self.movement_range, self.movement_range)
        delta_y = random.uniform(-self.movement_range, self.movement_range)
        new_x = self.position[0] + delta_x
        new_y = self.position[1] + delta_y
        self.position = (new_x, new_y)

    @abstractmethod
    def on_collision_complete(self):
        """
        Called when the grid has finished processing a collision event
        """
        pass

    @abstractmethod
    def on_simulation_step_end(self):
        """
        Called when the simulation step ends
        """
        pass
