import math
import random
from typing import List

from model.grid import BaseSimulationGrid
from model.node.BaseNode import BaseNode
from model.setting.model_settings import NumericSetting, SupportedEntity


class SimpleRandomGrid(BaseSimulationGrid):
    name: str = "Simple Square Grid"
    description: str = "A simple square grid that places nodes randomly within the grid. The grid is divided into a number of regions in order to reduce calculations required to detect collisions."
    icon: str = "dots-grid"

    settings = [
        NumericSetting(
            name="Grid Size",
            description="The size of the grid in meters",
            min_value=2000,
            max_value=20000,
            default_value=5000,
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

            # serialize the node and deserialize it to get a new node
            new_node = type(node).deserialize(node.serialize(True))
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

        return colliding_nodes

    def serialize(self) -> dict:
        """
        Serialize the grid to be able to be passed to parallel workers in the simulation.
        All grids must implement this method
        """
        serialized = {
            "name": self.name,
            "description": self.description,
            "icon": self.icon,
            "width": self.width,
            "length": self.length,
            "region_size": self.region_size,
            # Serialize nodes using their own serialize methods
            "nodes": [node.serialize(False) for node in self.nodes],
            # Convert grid dictionary keys to strings for JSON serialization
            "grid": {
                str(region): [node.id for node in nodes]
                for region, nodes in self.grid.items()
            },
        }
        return serialized

    @classmethod
    def deserialize(cls, data: dict, node_type: type[BaseNode]) -> "BaseSimulationGrid":
        grid = cls()

        grid.name = data["name"]
        grid.description = data["description"]
        grid.icon = data["icon"]
        grid.width = data["width"]
        grid.length = data["length"]
        grid.region_size = data["region_size"]

        # Create a map to quickly look up nodes by ID
        node_map = {}

        # First, deserialize all the nodes
        for node_data in data["nodes"]:
            # Determine node class and deserialize
            # This assumes BaseNode.deserialize is implemented correctly
            node = node_type.deserialize(node_data)
            grid.nodes.append(node)
            node_map[node.id] = node

        # Now rebuild the grid structure
        # Convert string region keys back to tuples
        for region_str, node_ids in data["grid"].items():
            # Convert string representation of tuple back to actual tuple
            # The format is expected to be something like "(x, y)"
            region_tuple = eval(
                region_str
            )  # Be careful with eval, this assumes trusted input

            # Add nodes to this region
            grid.grid[region_tuple] = [
                node_map[node_id] for node_id in node_ids if node_id in node_map
            ]

        return grid
