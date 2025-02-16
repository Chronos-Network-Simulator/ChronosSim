from abc import abstractmethod, ABC
from typing import List

from model.node import BaseNode
from model.setting.model_setting_mixin import ModelSettingMixin


class BaseTargetSpawner(ABC, ModelSettingMixin):
    """
    Target Spawner classes are run at the start of each simulation and mark nodes as target nodes. Any messages received by these
    nodes are considered to have reached their target destination and the simulation invokes the target hit callback for each node.
    The target spawner is responsible for marking nodes as targets.
    """

    description: str
    """
    A description of the target spawner.
    """

    @abstractmethod
    def mark_targets(self, nodes: List[BaseNode]) -> List[BaseNode]:
        """
        Mark nodes as targets.
        """
        pass
