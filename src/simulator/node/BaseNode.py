import abc
from ast import Tuple


class BaseNode(abc):
    """
    Represents a node in the simulation network.
    """

    name: str = None
    """
    The name of this node type
    """

    position: Tuple[float, float] = None
    """
    Position of the node in the simulation grid
    """

    detection_range: float = None
    """
    The range in meters a node can detect another node
    """

    def __init__(self):
        pass
