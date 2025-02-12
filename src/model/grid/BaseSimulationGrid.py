from abc import ABC, abstractmethod
from typing import Dict, List, Tuple

from model.node.BaseNode import BaseNode
from model.setting.model_settings import BaseModelSetting


class BaseSimulationGrid(ABC):

    name: str
    """
    Name of this simulation Grid
    """

    description: str
    """
    Description of this simulation grid
    """

    icon: str
    """
    The material Design Icon to display to represent this grid type
    """

    settings: [BaseModelSetting]
    """
    A list of settings that should be exposed to configure this model.
    """

    width: int
    """
    Width in meters of this simulation grid.
    """

    length: int
    """
    Length in meters of this simulation grid.
    """

    region_size: int
    """
    Every Grid must be divided into regions to reduce the number of calculations required to detect collisions.
    This is the size of the regions that the grid is divided into. Regions are square.
    """

    nodes: List[BaseNode]
    """
    List of nodes in the grid
    """

    grid: Dict[Tuple[int, int], List[BaseNode]]
    """
    The grid is a dictionary of region codes to the nodes that are present in each of these regions.
    Region codes are calculated by dividing the grid into regions of size region_size and assigning a code to each region
    from (0, 0) to (width // region_size, length // region_size)
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
    def auto_place_nodes(self, num_nodes: int, node_type: type[BaseNode]):
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
    def detect_collision(self, node: BaseNode) -> List[BaseNode]:
        """
        Detects if a node is colliding with another node in the grid. A collision
        is determined if a node enters another nodes detection range marked by the
        respective nodes detection range. Collision is only consdiered for nodes within
        the same or nearby regions.

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
