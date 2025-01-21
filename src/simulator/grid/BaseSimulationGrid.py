from abc import ABC, abstractmethod
from typing import List
from simulator.node.BaseNode import BaseNode


class BaseSimulationGrid(ABC):

    name: str = None
    """
    Name of this simulation Grid
    """

    width: int = None
    """
    Width in meters of this simulation grid.
    """

    length: int = None
    """
    Length in meters of this simulation grid.
    """

    @abstractmethod
    def place_node(self, node: BaseNode):
        """
        Places a node in a position within the grid. It is upto the grid implementation
        to decide whether the node can be placed in that region or not.

        :param node: Node with the location to be placed
        :type node: BaseNode
        """

    @abstractmethod
    def auto_place_nodes(self, num_nodes: int, node_type: BaseNode):
        """
        Automatically places a number of nodes in the grid. The nodes are placed
        in random locations within the grid.

        :param num_nodes: Number of nodes to place
        :type num_nodes: int
        :param node_type: Type of node to place
        :type node_type: type
        """

    @abstractmethod
    def get_node(self, node_id: str):
        """
        Gets a node from the grid based on its ID

        :param node_id: ID of the node to get
        :type node_id: int
        """

    @abstractmethod
    def detect_collision(self, node: BaseNode) -> bool:
        """
        Detects if a node is colliding with another node in the grid. A collision
        is determined if a node enters another nodes detection range marked by the
        respective nodes detection range.

        :param node: Node to check for collision
        :type node: BaseNode
        :return: True if there is a collision, False otherwise.
        :rtype: bool
        """

    @abstractmethod
    def get_nodes(self) -> List[BaseNode]:
        """
        Get all the nodes in the grid
        """
