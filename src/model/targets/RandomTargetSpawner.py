from random import gauss, shuffle

from model.setting.model_settings import SupportedEntity, RangeSetting
from model.targets.BaseTargetSpawner import BaseTargetSpawner


class RandomTargetSpawner(BaseTargetSpawner):
    """
    Randomly Assigns targets to nodes.
    """

    name = "Random Spawner"

    description = "Randomly assigns nodes as targets"

    randomness: float = 10
    """
    How much percentage of nodes should be targets.
    """

    variance: float = 0
    """
    How much variance should be allowed in the randomness.
    """

    settings = [
        RangeSetting(
            name="Randomness",
            description="Percentage of nodes that should be targets.",
            min_range=0,
            max_range=100,
            step=1,
            default_value=10,
            entity_type=SupportedEntity.TARGET_SPAWNER,
            attributes=["randomness"],
        ),
        RangeSetting(
            name="Variance",
            description="How much variance should be allowed in the randomness.",
            min_range=0,
            max_range=100,
            step=1,
            default_value=0,
            entity_type=SupportedEntity.TARGET_SPAWNER,
            attributes=["variance"],
        ),
    ]

    entity_type = SupportedEntity.TARGET_SPAWNER

    def mark_targets(self, nodes):
        """
        Mark nodes as targets based on randomness and variance.
        """
        num_nodes = len(nodes)
        # Convert randomness and variance from percentage to a 0-1 range
        mean_targets = (self.randomness / 100) * num_nodes
        std_dev = (self.variance / 100) * num_nodes
        num_targets = int(max(0, min(num_nodes, gauss(mean_targets, std_dev))))
        shuffle(nodes)
        for i in range(num_nodes):
            nodes[i].target = i < num_targets

        return nodes
