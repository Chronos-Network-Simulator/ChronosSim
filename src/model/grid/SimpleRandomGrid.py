import random
from typing import List, Tuple

from model.grid.BaseSimulationGrid import BaseSimulationGrid
from model.node.BaseNode import BaseNode
from model.setting.model_settings import NumericSetting


class SimpleRandomGrid(BaseSimulationGrid):

    name: str = "Simple Square Grid"

    description: str = (
        "A simple square grid that places nodes randomly within the grid. The grid is divided into a number of regions in order to reduce calculations required to detect collisions."
    )

    icon: str = "dots-grid"

    settings = [
        NumericSetting(
            name="Grid Size",
            description = "The size of the grid in Kilometers",
            min_value=1,
            max_value=20,
            default_value=5,
            callback= lambda x, y: print(f"Grid size was changed by {x} to {y}")
        ),
    ]

    def _get_region(self, x: float, y: float) -> Tuple[int, int]:
        return int(x // self.region_size), int(y // self.region_size)

    def place_node(self, node: BaseNode):
        if 0 <= node.position[0] <= self.width and 0 <= node.position[1] <= self.length:
            self.nodes.append(node)
            region = self._get_region(*node.position)
            if region not in self.grid:
                self.grid[region] = []
            self.grid[region].append(node)
        else:
            raise ValueError("Node position out of grid bounds")

    def auto_place_nodes(self, num_nodes: int, node_type: type[BaseNode]):
        for _ in range(num_nodes):
            x = random.uniform(0, self.width)
            y = random.uniform(0, self.length)
            node = node_type(x, y)
            self.place_node(node)

    def get_node(self, node_id: str) -> BaseNode | None:
        for node in self.nodes:
            if node.id == node_id:
                return node
        return None

    def detect_collision(self, node: BaseNode) -> List[BaseNode]:
        region = self._get_region(*node.position)
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
                    if distance <= node.detection_range:
                        colliding_nodes.append(other_node)
        return colliding_nodes

    def get_nodes(self) -> List[BaseNode]:
        return self.nodes
