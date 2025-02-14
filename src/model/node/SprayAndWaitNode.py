from collections import defaultdict
from typing import List, Optional, Literal, Dict

from model.message.BaseMessage import BaseMessage
from model.node import BaseNode
from model.setting.model_settings import SupportedEntity, OptionSetting


class SprayAndWaitNode(BaseNode):
    """
    A node that uses a spray and wait protocol to send messages.

    This version uses the improved message storage (dictionary of messages to counts).
    It also includes a `message_selection_strategy`.
    """

    name = "Spray N Wait"
    description = (
        "A node that uses a simplified spray and wait protocol to disseminate messages from its storage to all nodes within its detection range, avoiding immediate reply to recent senders. "
        "It can be configured to send the first, last, or all messages it holds."
    )
    icon = "spray-bottle"

    message_selection_strategy: Literal["First", "Last", "All"] = "First"

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
        )
    ]

    messages = {}

    def __init__(self):
        super().__init__()
        self._recent_senders = set()
        self.messages: Dict[BaseMessage, int] = defaultdict(int)

    def send_message(self, receiving_node: BaseNode) -> Optional[List[BaseMessage]]:
        if receiving_node.id in self._recent_senders:
            return None

        if not self.messages:
            return None

        messages_to_send: List[BaseMessage] = []

        if self.message_selection_strategy == "First":
            first_message = next(iter(self.messages))  # Gets the first message
            messages_to_send = [first_message] * self.messages[
                first_message
            ]  # Sends all copies
        elif self.message_selection_strategy == "Last":
            last_message = None
            for message in self.messages:
                last_message = message  # keeps updating to the last
            if last_message:
                messages_to_send = [last_message] * self.messages[
                    last_message
                ]  # Sends all copies
        elif self.message_selection_strategy == "All":
            for message, count in self.messages.items():
                messages_to_send.extend([message] * count)  # More efficient extend
        if messages_to_send:
            return messages_to_send
        else:
            return None

    def receive_message(self, messages: List[BaseMessage], sending_node: BaseNode):
        self._recent_senders.add(sending_node.id)
        print(f"{self.id} received {len(messages)} messages from {sending_node.id}")
        for message in messages:
            self.messages[message] = (
                1  # we only store one copy of each message that we get
            )

        self._recent_senders = set()

    def on_collision_complete(self):
        self._recent_senders = set()

    def on_simulation_step_end(self):
        pass

    def on_message_create(self, message: BaseMessage):
        self.messages[message] = 1  # only store one copy of each message
