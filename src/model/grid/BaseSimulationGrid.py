import math
from abc import ABC, abstractmethod
from typing import Dict, List, Tuple, Optional

from model.node.BaseNode import BaseNode
from model.setting.model_setting_mixin import ModelSettingMixin
from model.setting.model_settings import SupportedEntity


class BaseSimulationGrid(ModelSettingMixin, ABC):

    name: str
    """
    The name of this simulation grid
    """

    description: str
    """
    Description of this simulation grid
    """

    icon: str
    """
    The material Design Icon to display to represent this grid type
    https://pictogrammers.com/library/mdi/
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
    This is the size of the regions that the grid is divided into. Regions are square. Region size is in meters
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

    entity_type = SupportedEntity.GRID

    def __init__(self):
        super().__init__()
        self.nodes = []
        self.grid: Dict[Tuple[int, int], List[BaseNode]] = {}

    def get_node(self, node_id: str) -> Optional[BaseNode]:
        for node in self.nodes:
            if node.id == node_id:
                return node
        return None

    def get_nodes(self) -> List[BaseNode]:
        return self.nodes

    def _get_region(self, x: float, y: float) -> Tuple[int, int]:
        region_x = int(x // self.region_size)
        region_y = int(y // self.region_size)
        return region_x, region_y

    def _get_neighbors(self, region: Tuple[int, int]) -> List[Tuple[int, int]]:
        """Returns the neighboring regions including the region itself."""
        x, y = region
        neighbors = []
        for i in range(-1, 2):
            for j in range(-1, 2):
                nx, ny = x + i, y + j
                if 0 <= nx < math.ceil(
                    self.width / self.region_size
                ) and 0 <= ny < math.ceil(
                    self.length / self.region_size
                ):  # Check bounds
                    neighbors.append((nx, ny))
        return neighbors

    def add_node_to_grid(self, node: BaseNode):
        """Adds a node to the grid dictionary."""
        region = self._get_region(node.position[0], node.position[1])
        if region not in self.grid:
            self.grid[region] = []
        self.grid[region].append(node)

    def remove_node_from_grid(self, node: BaseNode):
        """Removes a node from the grid dictionary."""
        region = self._get_region(node.position[0], node.position[1])
        if region in self.grid:
            self.grid[region].remove(node)
            if not self.grid[region]:  # Remove empty regions
                del self.grid[region]

    def clear_grid(self):
        """Clears the grid of all nodes."""
        self.grid.clear()
        self.nodes.clear()

    def update_node_position(
        self, node: BaseNode, new_position: Tuple[float, float]
    ) -> bool:
        """Updates the node's position in the grid."""
        old_region = self._get_region(node.position[0], node.position[1])
        new_region = self._get_region(new_position[0], new_position[1])

        if old_region != new_region:  # Only update if region has changed
            self.remove_node_from_grid(node)
            node.position = new_position
            self.add_node_to_grid(node)
            return True
        else:
            node.position = new_position
            return False

    @abstractmethod
    def place_node(self, node: BaseNode) -> bool:
        """
        Places a node in a position within the grid. It is upto the grid implementation
        to decide whether the node can be placed in that region or not.

        :param node: Node with the location to be placed
        :type node: BaseNode
        :return: True if the node was placed, False otherwise.
        """

    @abstractmethod
    def auto_place_nodes(self, num_nodes: int, node: BaseNode) -> bool:
        """
        Automatically places a number of nodes in the grid. The nodes are placed
        in random locations within the grid. Creates a deep copy of the passed in node.

        :param num_nodes: Number of nodes to place
        :type num_nodes: int
        :param node: Node to create copies of and place
        :type node: BaseNode
        :return: True if the nodes were placed, False otherwise.
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
        :return: List of nodes that the node is colliding with

        """
