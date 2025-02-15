from __future__ import annotations

import random
import uuid
from abc import ABC, abstractmethod
from typing import Tuple, List, Dict

from model.message.BaseMessage import BaseMessage
from model.setting.model_setting_mixin import ModelSettingMixin
from model.setting.model_settings import (
    BaseModelSetting,
    NumericSetting,
    SupportedEntity,
)


class BaseNode(ModelSettingMixin, ABC):
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
            max_value=1000,
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

    movement_range: float = 5.0
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
    entity_type = SupportedEntity.NODE

    def __init__(self):
        super().__init__()
        self.id = f"{self.slug}-{uuid.uuid4().hex}"

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

    @abstractmethod
    def on_message_create(self, message: BaseMessage):
        """
        Called when a message is created. Use this function to apply any initial processing to a message
        before it is stored in the internal nodes message array. MessageSpawners will call this function
        when they create a message.
        """
        pass

    def move(self):
        """
        Moves the node randomly within its movement range.
        """
        delta_x = random.uniform(-self.movement_range, self.movement_range)
        delta_y = random.uniform(-self.movement_range, self.movement_range)
        new_x = self.position[0] + delta_x
        new_y = self.position[1] + delta_y
        self.position = (new_x, new_y)

    def __repr__(self):
        return f"{self.name} - {self.id} at {self.position}"
