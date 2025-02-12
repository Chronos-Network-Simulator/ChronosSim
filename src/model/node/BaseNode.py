from abc import ABC
from typing import Tuple


class BaseNode(ABC):
    """
    Represents a node in the simulation network.
    """

    id: str
    """
    The unique identifier of this node
    """

    name: str
    """
    The name of this node type
    """

    position: Tuple[float, float]
    """
    Position of the node in the simulation grid
    """

    detection_range: float = 0
    """
    The range in meters a node can detect another node
    """

    def __init__(self):
        pass
