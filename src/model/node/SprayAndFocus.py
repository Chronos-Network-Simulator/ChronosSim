from collections import defaultdict
from typing import List, Optional, Literal, Dict
from model.message.BaseMessage import BaseMessage
from model.node import BaseNode
from model.setting.model_settings import SupportedEntity, OptionSetting

class SprayAndFocusNode(BaseNode):
    """
    A node that implements the Spray and Focus routing protocol.
    In the spray phase, it works similar to Spray and Wait.
    In the focus phase, it uses utility-based forwarding to make routing decisions.
    """
    name = "Spray N Focus"
    description = (
        "Implements the Spray and Focus protocol with utility-based forwarding. "
        "Initially sprays message copies, then uses encounter history to make "
        "intelligent forwarding decisions in the focus phase."
    )
    icon = "target"

    message_selection_strategy: Literal["First", "Last", "All"] = "First"
    utility_threshold: float = 0.5  # Threshold for utility-based forwarding

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
        OptionSetting(
            name="Utility Threshold",
            description="Minimum utility value required for forwarding in focus phase",
            entity_type=SupportedEntity.NODE,
            attributes=["utility_threshold"],
            options=[
                {"text": "0.3", "icon": "low-priority"},
                {"text": "0.5", "icon": "medium-priority"},
                {"text": "0.7", "icon": "high-priority"},
            ],
            default_value="0.5",
        )
    ]

    def __init__(self):
        super().__init__()
        self._recent_senders = set()
        self.messages: Dict[BaseMessage, int] = defaultdict(int)
        self.last_encounter_times: Dict[str, float] = defaultdict(float)
        self.encounter_counts: Dict[str, int] = defaultdict(int)
        self.current_time = 0.0

    def calculate_utility(self, node_id: str) -> float:
        """
        Calculate utility value for a node based on encounter history.
        Higher values indicate better forwarding candidates.
        """
        if node_id not in self.encounter_counts:
            return 0.0

        encounter_frequency = self.encounter_counts[node_id]
        time_since_last_encounter = self.current_time - self.last_encounter_times[node_id]

        # Utility increases with encounter frequency and decreases with time since last encounter
        utility = (encounter_frequency / (time_since_last_encounter + 1.0))
        return min(1.0, utility)

    def send_message(self, receiving_node: BaseNode) -> Optional[List[BaseMessage]]:
        if receiving_node.id in self._recent_senders:
            return None

        if not self.messages:
            return None

        # Update encounter history
        self.last_encounter_times[receiving_node.id] = self.current_time
        self.encounter_counts[receiving_node.id] += 1

        messages_to_send: List[BaseMessage] = []

        # Get candidate messages based on selection strategy
        if self.message_selection_strategy == "First":
            candidates = [next(iter(self.messages))]
        elif self.message_selection_strategy == "Last":
            candidates = [list(self.messages.keys())[-1]]
        else:  # "All"
            candidates = list(self.messages.keys())

        # Apply utility-based forwarding
        utility = self.calculate_utility(receiving_node.id)

        for message in candidates:
            if self.messages[message] > 1:
                # Spray phase - split message copies
                copies_to_send = self.messages[message] // 2
                self.messages[message] -= copies_to_send
                messages_to_send.extend([message] * copies_to_send)
            elif utility >= self.utility_threshold:
                # Focus phase - forward based on utility
                messages_to_send.append(message)
                self.messages[message] = 0  # Transfer the message

        return messages_to_send if messages_to_send else None

    def receive_message(self, messages: List[BaseMessage], sending_node: BaseNode):
        self._recent_senders.add(sending_node.id)

        # Update encounter history
        self.last_encounter_times[sending_node.id] = self.current_time
        self.encounter_counts[sending_node.id] += 1

        for message in messages:
            self.messages[message] = 1  # Store one copy of each new message

    def on_collision_complete(self):
        self._recent_senders = set()

    def on_simulation_step_end(self):
        self.current_time += 1.0  # Update simulation time

    def on_message_create(self, message: BaseMessage):
        self.messages[message] = 1  # Start with one copy of new message

    def on_target_received(self, messages: List[BaseMessage], sending_node: BaseNode):
        return None

    def on_target_send(self, receiving_node: BaseNode) -> Optional[BaseMessage]:
        return None