import random
from typing import Dict, List, Tuple
from simulator.grid.BaseSimulationGrid import BaseSimulationGrid
from simulator.node.BaseNode import BaseNode


class SimpleRandomGrid(BaseSimulationGrid):

    name: str = "Simple Random Grid"

    description: str = (
        "A simple grid that places nodes randomly within the grid. The grid is divided into a number of regions in order to reduce calculations required to detect collisions."
    )

    region_size: int = 50
    """
    The size of the regions that the grid is divided into.
    """

    nodes: List[BaseNode] = []
    """
    The list of nodes that are in the grid.
    """

    grid: Dict[Tuple[int, int], List[BaseNode]] = {}
    """
    The grid is a dictionary of (x, y) coordinates to a list of nodes that are in that region.
    """

    def __init__(self, width: int, length: int):
        self.width = width
        self.length = length

    def _get_region(self, x: float, y: float) -> Tuple[int, int]:
        return int(x // self.region_size), int(y // self.region_size)

    def place_node(self, node: BaseNode):
        if 0 <= node.x <= self.width and 0 <= node.y <= self.length:
            self.nodes.append(node)
            region = self._get_region(node.x, node.y)
            if region not in self.grid:
                self.grid[region] = []
            self.grid[region].append(node)
        else:
            raise ValueError("Node position out of grid bounds")

    def auto_place_nodes(self, num_nodes: int, node_type: type):
        for _ in range(num_nodes):
            x = random.uniform(0, self.width)
            y = random.uniform(0, self.length)
            node = node_type(x, y)
            self.place_node(node)

    def get_node(self, node_id: str):
        for node in self.nodes:
            if node.node_id == node_id:
                return node
        return None

    def detect_collision(self, node: BaseNode) -> List[BaseNode]:
        region = self._get_region(node.x, node.y)
        nearby_regions = [
            (region[0] + dx, region[1] + dy) for dx in [-1, 0, 1] for dy in [-1, 0, 1]
        ]
        colliding_nodes = []
        for reg in nearby_regions:
            if reg in self.grid:
                for other_node in self.grid[reg]:
                    if other_node == node:
                        continue  # ignore self collisions
                    distance = (
                        (node.x - other_node.x) ** 2 + (node.y - other_node.y) ** 2
                    ) ** 0.5
                    if distance <= node.detection_radius:
                        colliding_nodes.append(other_node)
        return colliding_nodes

    def get_nodes(self) -> List[BaseNode]:
        return self.nodes
