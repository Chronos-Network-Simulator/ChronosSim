import random
from typing import List

from model.message.BaseMessage import BaseMessage
from model.message_spawner.base_message_spawner import BaseMessageSpawner
from model.node import BaseNode


class BasicRandomMessageSpawner(BaseMessageSpawner):
    """
    A basic message spawner that spawns messages randomly in nodes at random intervals.
    """

    name = "Random Spawner"
    description = "Spawns messages randomly in nodes at random intervals."
    icon = "view-grid-compact"

    def init_spawn_messages(
        self,
        nodes: List[BaseNode],
        message_template: BaseMessage,
    ) -> None:
        if not nodes or not message_template:
            return
        # recreate the rng for each simulation step
        self._rng = random.Random(self.random_seed)
        target_spawn_count = (self.spawn_rate / 100.0) * len(nodes)
        num_initial_spawns = self._calculate_spawn_count(
            target_spawn_count, self.spawn_rate_variance
        )

        num_initial_spawns = min(num_initial_spawns, len(nodes))

        if num_initial_spawns > 0:
            valid_nodes = [node for node in nodes if not getattr(node, "target", False)]
            nodes_to_spawn_in = random.sample(
                valid_nodes, min(num_initial_spawns, len(valid_nodes))
            )
            self._spawn_messages_in_nodes(
                nodes_to_spawn_in, message_template=message_template
            )

    def spawn_messages(
        self, nodes: List[BaseNode], step: int, message_template: BaseMessage
    ) -> None:
        if not nodes or not message_template:
            return
        # recreate the rng for each simulation step
        self._rng = random.Random(self.random_seed)
        # Calculate spawn count for this step
        spawn_rate_percentage = self.spawn_rate
        spawn_rate_variance_percentage = self.spawn_rate_variance
        target_spawn_count = (spawn_rate_percentage / 100.0) * len(nodes)
        num_spawns = self._calculate_spawn_count(
            target_spawn_count, spawn_rate_variance_percentage
        )

        valid_nodes = [node for node in nodes if not getattr(node, "target", False)]
        num_spawns = min(num_spawns, len(valid_nodes))
        if num_spawns > 0:
            nodes_to_spawn_in = random.sample(valid_nodes, num_spawns)
            self._spawn_messages_in_nodes(nodes_to_spawn_in, message_template, step)

    def _calculate_spawn_count(
        self, target_spawn_count: float, spawn_rate_variance_percentage: float
    ) -> int:
        """Helper method to calculate the number of spawns, applying variance if needed."""
        if spawn_rate_variance_percentage > 0:
            return max(
                0,
                int(
                    self._rng.gauss(target_spawn_count, spawn_rate_variance_percentage)
                ),
            )
        else:
            return max(0, int(target_spawn_count))

    def _spawn_messages_in_nodes(
        self,
        nodes: List[BaseNode],
        message_template: BaseMessage,
        step: int = None,
    ) -> None:
        """Helper method to spawn messages in the provided nodes."""
        for node in nodes:
            new_message = message_template.duplicate(node.id, copy_time=False)
            if step is not None:
                new_message.created_time = step  # Set timestamp to current step
            node.on_message_create(new_message)
