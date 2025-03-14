from collections import defaultdict
from typing import List, Optional, Set, Dict
from model.message.BaseMessage import BaseMessage
from model.node import BaseNode
from model.setting.model_settings import SupportedEntity, OptionSetting


class EpidemicRoutingNode(BaseNode):
    """
    A node that implements the Epidemic Routing protocol.
    Messages are flooded through the network by exchanging message summaries
    and transferring any messages that neighboring nodes haven't seen yet.
    """

    name = "Epidemic Router"
    description = (
        "Implements epidemic routing protocol where nodes exchange summaries of their "
        "messages and transfer any messages that their neighbors haven't seen. "
        "Includes anti-entropy mechanism to ensure message propagation."
    )
    icon = "virus"

    buffer_size: int = 100  # Maximum number of messages to store

    settings = BaseNode.settings + [
        OptionSetting(
            name="Buffer Size",
            description="Maximum number of messages to store",
            entity_type=SupportedEntity.NODE,
            attributes=["buffer_size"],
            options=[
                {"text": "50", "icon": "database"},
                {"text": "100", "icon": "database"},
                {"text": "200", "icon": "database"},
            ],
            default_value="100",
        )
    ]

    def __init__(self):
        super().__init__()
        self._recent_senders = set()
        self.messages: Dict[BaseMessage, int] = defaultdict(int)
        self.message_seen_times: Dict[str, float] = defaultdict(
            float
        )  # Track when messages were first seen
        self.current_time = 0.0

    def get_message_summary(self) -> Set[str]:
        """
        Generate a summary of message IDs currently held by this node.
        """
        return {str(msg.id) for msg in self.messages.keys()}

    def manage_buffer(self):
        """
        Manage the message buffer when it exceeds the size limit.
        Removes oldest messages first based on when they were first seen.
        """
        while len(self.messages) > self.buffer_size:
            # Find and remove oldest message
            oldest_message = min(
                self.messages.keys(),
                key=lambda msg: self.message_seen_times[str(msg.id)],
            )
            del self.messages[oldest_message]
            del self.message_seen_times[str(oldest_message.id)]

    def send_message(self, receiving_node: BaseNode) -> Optional[List[BaseMessage]]:
        if receiving_node.id in self._recent_senders:
            return None

        if not self.messages:
            return None

        # In real implementation, would first exchange summaries
        # Here we simulate this by sending all messages
        messages_to_send = []

        for message in self.messages:
            messages_to_send.append(message)

        return messages_to_send if messages_to_send else None

    def receive_message(self, messages: List[BaseMessage], sending_node: BaseNode):
        self._recent_senders.add(sending_node.id)

        for message in messages:
            # Only store messages we haven't seen before
            if message not in self.messages:
                self.messages[message] = 1
                self.message_seen_times[str(message.id)] = self.current_time

        # Manage buffer if it exceeds size limit
        self.manage_buffer()

    def on_collision_complete(self):
        self._recent_senders = set()

    def on_simulation_step_end(self):
        self.current_time += 1.0

    def on_message_create(self, message: BaseMessage):
        self.messages[message] = 1
        self.message_seen_times[str(message.id)] = self.current_time
        self.manage_buffer()

    def on_send_to_target(self, messages: List[BaseMessage], sending_node: BaseNode):
        return None

    def on_receive_from_target(
        self, receiving_node: BaseNode
    ) -> Optional[List[BaseMessage]]:
        return None

    def __repr__(self):
        return (
            f"EpidemicRoutingNode(id={self.id}, "
            f"num_messages={len(self.messages)}, "
            f"buffer_usage={len(self.messages)}/{self.buffer_size})"
        )
