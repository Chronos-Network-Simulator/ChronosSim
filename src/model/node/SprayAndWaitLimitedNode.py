from collections import defaultdict
from typing import List, Optional, Literal, Dict

from model.message.BaseMessage import BaseMessage
from model.node.BaseNode import BaseNode
from model.setting.model_settings import SupportedEntity, OptionSetting, NumericSetting


class SprayAndWaitLimitedNode(BaseNode):
    """
    A node that uses a spray and wait protocol to send messages, however it only has a limited amount of storage
    and will represent itself as full if it cannot take on any more messages.
    """

    name = "Spray N Wait Limited"

    description = (
        "A node that uses a simplified spray and wait protocol to disseminate messages from its storage to all nodes within its detection range, avoiding immediate reply to recent senders. "
        "If the node reaches its storage limit, it will not accept any more messages until it has dropped some of its messages."
        "Messages are dropped when their local TTL reaches 0. All nodes receive a starting TTL when they arrive at the node and not when they are created."
    )
    icon = "spray-bottle"

    message_selection_strategy: Literal["First", "Last", "All"] = "First"
    """
    Strategy to select messages for sending.
    """

    max_ttl: int = 10
    """
    The Local TTL that is assigned to all messages when they arrive at the node.
    """

    min_ttl: int = 0
    """
    The Local TTL at which messages are dropped from local storage
    """

    settings = BaseNode.settings + [
        OptionSetting(
            name="Msg Selection Strategy",
            description="Strategy to select messages for sending.",
            entity_type=SupportedEntity.NODE,
            attributes=["message_selection_strategy"],
            options=[
                {"text": "First", "icon": "arrow-left"},
                {"text": "Last", "icon": "arrow-right"},
                {"text": "All", "icon": "arrow-up"},
            ],
            default_value="First",
        ),
        NumericSetting(
            name="Max TTL",
            description="The Local TTL that is assigned to all messages when they arrive at the node.",
            min_value=1,
            max_value=100,
            default_value=10,
            entity_type=SupportedEntity.NODE,
            attributes=["max_ttl"],
        ),
        NumericSetting(
            name="Min TTL",
            description="The Local TTL at which messages are dropped from local storage.",
            min_value=0,
            max_value=100,
            default_value=0,
            entity_type=SupportedEntity.NODE,
            attributes=["min_ttl"],
        ),
    ]

    messages = {}

    def __init__(self):
        super().__init__()
        self._recent_senders = set()
        # Change the default value to be an integer
        self.messages: Dict[BaseMessage, int] = defaultdict(int)
        self.is_full = False

    def send_message(self, receiving_node: BaseNode) -> Optional[List[BaseMessage]]:
        if receiving_node.id in self._recent_senders:
            return None

        if not self.messages:
            return None

        messages_to_send: List[BaseMessage] = []

        if self.message_selection_strategy == "First":
            first_message = next(iter(self.messages))
            # Always use count of 1 when sending
            messages_to_send = [first_message]
        elif self.message_selection_strategy == "Last":
            last_message = None
            for message in self.messages:
                last_message = message
            if last_message:
                # Always use count of 1 when sending
                messages_to_send = [last_message]
        elif self.message_selection_strategy == "All":
            # Send one copy of each message
            messages_to_send = list(self.messages.keys())

        if messages_to_send:
            return messages_to_send
        else:
            return None

    def receive_message(self, messages: List[BaseMessage], sending_node: BaseNode):
        self._recent_senders.add(sending_node.id)
        for message in messages:
            if not self.is_full:
                message.props["ttl"] = self.max_ttl
                # Store with count of 1
                self.messages[message] = 1
        self._recent_senders = set()

    def on_message_create(self, message: BaseMessage):
        if not self.is_full:
            # Store message with count of 1, TTL is handled in message.props
            self.messages[message] = 1
            message.props["ttl"] = self.max_ttl
            if len(self.messages) >= self.max_ttl:
                self.is_full = True

    def on_collision_complete(self):
        self._recent_senders = set()

    def on_simulation_step_end(self):
        # decrement TTL of all messages
        for message in self.messages.keys():
            message.props["ttl"] -= 1
        # Drop messages with TTL of 0
        for message in list(self.messages.keys()):
            if message.props["ttl"] <= self.min_ttl:
                del self.messages[message]
        if len(self.messages) < self.max_ttl:
            self.is_full = False

    def on_target_received(self, messages: List[BaseMessage], sending_node: BaseNode):
        return None

    def on_target_send(self, receiving_node: BaseNode) -> Optional[BaseMessage]:
        return None
