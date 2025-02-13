from typing import List, Optional, Literal

from model.message.BaseMessage import BaseMessage
from model.node import BaseNode
from model.setting.model_settings import SupportedEntity, OptionSetting


class SprayAndWaitNode(BaseNode):
    """
    A node that uses a spray and wait protocol to send messages. The waiting is not implemented due to the
    nature of the simulation. The node will send messages to all nodes in its detection range. This node type
    ensures that it does not send a message to a node it just received a message from.

    This version of SprayAndWaitNode sends messages from its internal message storage (self.messages).
    It does not create new messages when sending; instead, it disseminates existing messages it holds.

    It now includes a `message_selection_strategy` to control which messages are sent.
    """

    name = "Spray N Wait"

    description = (
        "A node that uses a simplified spray and wait protocol to disseminate messages from its storage to all nodes within its detection range, avoiding immediate reply to recent senders. "
        "It can be configured to send the first, last, or all messages it holds."
    )

    icon = "spray-bottle"

    message_selection_strategy: Literal["first", "last", "all"] = "first"
    """
    Strategy to select messages for sending:
    - "first": Send only the first message in storage.
    - "last": Send only the last message in storage.
    - "all": Send all messages in storage.
    """

    settings = BaseNode.settings + [
        OptionSetting(
            name="Message Selection Strategy",
            description="Strategy to select messages for sending. "
            "First: Send only the first message in storage. "
            "Last: Send only the last message in storage. "
            "All: Send all messages in storage.",
            entity_type=SupportedEntity.NODE,
            attributes=["message_selection_strategy"],
            options=[
                {
                    "text": "First",
                    "icon": "arrow-left",
                },
                {
                    "text": "Last",
                    "icon": "arrow-right",
                },
                {
                    "text": "All",
                    "icon": "arrow-up",
                },
            ],
            default_value="first",
        )
    ]

    def __init__(self):
        super().__init__()
        self._recent_senders = set()

    def send_message(self, receiving_node: BaseNode) -> Optional[List[BaseMessage]]:
        """
        Sends messages from the node's message storage to the receiving node based on the
        `message_selection_strategy`.

        - "first": Sends the first available message.
        - "last": Sends the last available message.
        - "all": Sends all available messages.

        If no messages to send, or should not send to the receiving node, returns None.
        """
        if receiving_node.id in self._recent_senders:
            return None

        if not self.messages:
            return None

        messages_to_send: List[BaseMessage] = []

        if self.message_selection_strategy == "first":
            message_to_send = None
            for sender_id, message_list in self.messages.items():
                if message_list:
                    message_to_send_entry = message_list[0]
                    message_to_send = message_to_send_entry[0]
                    break  # Send the first message found and stop iterating
            if message_to_send:
                messages_to_send = [message_to_send]

        elif self.message_selection_strategy == "last":
            message_to_send = None
            last_message_list = None
            for sender_id, message_list in self.messages.items():
                if message_list:
                    last_message_list = (
                        message_list  # keep updating to the last non-empty list
                    )

            if last_message_list:
                message_to_send_entry = last_message_list[
                    -1
                ]  # take the last element of the last list
                message_to_send = message_to_send_entry[0]
                if message_to_send:
                    messages_to_send = [message_to_send]

        elif self.message_selection_strategy == "all":
            for sender_id, message_list in self.messages.items():
                if message_list:
                    for message_entry in message_list:
                        messages_to_send.append(
                            message_entry[0] * message_entry[1]
                        )  # send all copies of the message

        if messages_to_send:
            return messages_to_send
        else:
            return None

    def receive_message(
        self, messages: List[BaseMessage], sending_node: BaseNode
    ) -> None:
        """
        Receives and stores messages.
        """
        self._recent_senders.add(sending_node.id)

        if sending_node.id not in self.messages:
            self.messages[sending_node.id] = []
        for message in messages:
            already_exists = False
            for existing_message_entry in self.messages[sending_node.id]:
                existing_message = existing_message_entry[0]
                if existing_message.id == message.id:
                    existing_message_entry[1] += 1
                    already_exists = True
                    break
            if not already_exists:
                self.messages[sending_node.id].append([message, 1])

        self._recent_senders = set()

    def on_collision_complete(self):
        """
        Resets the recent senders after a collision.
        """
        self._recent_senders = set()

    def on_simulation_step_end(self):
        pass
