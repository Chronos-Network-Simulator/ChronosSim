import copy
import math
import random
from typing import List

from model.grid import BaseSimulationGrid
from model.node.BaseNode import BaseNode
from model.setting.model_settings import NumericSetting, SupportedEntity


class SimpleRandomGrid(BaseSimulationGrid):

    name: str = "Simple Square Grid"
    description: str = (
        "A simple square grid that places nodes randomly within the grid. The grid is divided into a number of regions in order to reduce calculations required to detect collisions."
    )
    icon: str = "dots-grid"

    settings = [
        NumericSetting(
            name="Grid Size",
            description="The size of the grid in meters",
            min_value=2000,
            max_value=20000,
            default_value=2000,
            attributes=["width", "length"],
            entity_type=SupportedEntity.GRID,
        ),
        NumericSetting(
            name="Region Size",
            description="The size of the regions in meters",
            min_value=500,
            max_value=1000,
            default_value=500,
            attributes=["region_size"],
            entity_type=SupportedEntity.GRID,
        ),
    ]

    width: int = 5000
    length: int = 5000
    region_size: int = 500

    def __init__(self):
        super().__init__()

    def place_node(self, node: BaseNode) -> bool:
        if 0 <= node.position[0] <= self.width and 0 <= node.position[1] <= self.length:
            self.nodes.append(node)
            self.add_node_to_grid(node)
            return True
        return False

    def auto_place_nodes(self, num_nodes: int, node: BaseNode) -> int:
        placed_count = 0

        for _ in range(num_nodes):
            x = random.uniform(0, self.width)
            y = random.uniform(0, self.length)

            # Create a deep copy of the simulation's node prototype
            new_node = copy.deepcopy(node)

            new_node.position = (x, y)
            if self.place_node(new_node):
                placed_count += 1
        return placed_count

    def detect_collision(self, node: BaseNode) -> List[BaseNode]:
        colliding_nodes = []
        region = self._get_region(node.position[0], node.position[1])
        neighboring_regions = self._get_neighbors(region)

        for reg in neighboring_regions:
            if reg in self.grid:
                for other_node in self.grid[reg]:
                    if other_node is node:
                        continue
                    distance = math.dist(
                        node.position, other_node.position
                    )  # Use math.dist
                    if distance <= node.detection_range:
                        colliding_nodes.append(other_node)
        if colliding_nodes:
            print(colliding_nodes)

        return colliding_nodes
