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

    target: bool = False
    """
    Whether this node is a target node or not. If they are a targte node then the simulation invokes the 
    on_target_received and on_target_send that allows target nodes to send data back into the network.
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
        NumericSetting(
            name="Max Memory:",
            description="The maximum amount of messages that this node can store in bytes. Beyond this point it is upto the node"
            "to decide how to handle the message.",
            min_value=1,
            max_value=1000,
            default_value=400,
            entity_type=SupportedEntity.NODE,
            attributes=["max_memory"],
        ),
    ]
    """
    A list of settings that should be exposed to configure this model.
    ClassVar to indicate it's a class variable, inheritable but shared if not overridden.
    Initialize it as an empty list at the class level in BaseNode.
    """

    position: Tuple[float, float] = (0, 0)
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

    max_memory: int = 400
    """
    Tge maximum amount of messages that this node can store in bytes. Beyond this point it is upto the node
    to decide how to handle the message. The base node class simply provides this value to the node. It is upto
    your purview tot decide to handle this in the message receive or not.
    """

    node_full: bool = False
    """
    During any collision with a nearby node, the simulation will check if the node is full or not. If it is full then no transmission
    of messages will be allowed. This is a flag that is set by the node when it reaches the max_memory limit. It is upto the node to decide
    how to handle this flag. The base node class simply provides this value to the node.
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
    def send_requested_messages(
        self, request: dict, receiving_node: BaseNode
    ) -> List[BaseMessage] | None:
        """
        Send only the messages requested by the other node based on the pre-collision metadata exchange.

        :param request: The request information from the other node
        :param receiving_node: The node requesting the messages
        :return: The requested messages to send
        """
        pass

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
    def pre_collision(self, potential_node: BaseNode) -> dict | None:
        """
        Called before actual message exchange to allow nodes to exchange metadata.
        This enables protocols to exchange summaries or other control information.

        :param potential_node: The node that this node is about to exchange messages with
        :return: A dictionary containing protocol-specific metadata (e.g., message IDs)
        """
        pass

    @abstractmethod
    def process_pre_collision(
        self, metadata: dict, sending_node: BaseNode
    ) -> dict | None:
        """
        Process the metadata received during pre_collision and determine what to request.

        :param metadata: The metadata sent by the other node during pre_collision
        :param sending_node: The node that sent the metadata
        :return: A dictionary containing request information (e.g., which message IDs to request)
        """
        pass

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

    @abstractmethod
    def on_send_to_target(self, target_node: BaseNode) -> List[BaseMessage] | None:
        """
        Called when a node needs to send a message to a target node.
        """
        pass

    @abstractmethod
    def on_receive_from_target(
        self, receiving_node: BaseNode, messages: List[BaseMessage]
    ) -> None:
        """
        Called when a node receives a message from a target node
        """
        pass

    @abstractmethod
    def on_send_as_target(self, target_node: BaseNode) -> List[BaseMessage] | None:
        """
        Called when a target node needs to send a message to a node.
        """
        pass

    @abstractmethod
    def on_receive_as_target(
        self,
        messages: List[BaseMessage],
        sending_node: BaseNode,
    ) -> None:
        """
        Called when a target node receives a message from a node
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

    @abstractmethod
    def serialize(self, new_id: bool) -> dict:
        """
        Serialize the node to be able to be passed to parallel workers in the simulation.
        All nodes must implement this method
        """
        ...

    @classmethod
    def deserialize(cls, data: dict) -> BaseNode:
        """
        Deserialize the node to be able to be passed to parallel workers in the simulation.
        All nodes must implement this method
        """
        ...
