import math
import random
from typing import List, Tuple, Set

from model.grid import BaseSimulationGrid
from model.node.BaseNode import BaseNode
from model.setting.model_settings import NumericSetting, SupportedEntity


class CityGrid(BaseSimulationGrid):
    name: str = "City Street Grid"
    description: str = (
        "A grid representing a city with streets and building blocks. Nodes (people) "
        "are placed only in building areas, with clear streets between blocks. The grid "
        "follows a Manhattan-style layout with perpendicular streets forming building blocks."
    )
    icon: str = "city"

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
        NumericSetting(
            name="Street Width",
            description="Width of streets in meters",
            min_value=30,
            max_value=100,
            default_value=50,
            attributes=["street_width"],
            entity_type=SupportedEntity.GRID,
        ),
        NumericSetting(
            name="Block Size",
            description="Size of building blocks in meters",
            min_value=100,
            max_value=500,
            default_value=400,
            attributes=["block_size"],
            entity_type=SupportedEntity.GRID,
        ),
    ]

    width: int = 5000
    length: int = 5000
    region_size: int = 500
    street_width: int = 50
    block_size: int = 400

    def __init__(self):
        super().__init__()
        self.street_locations: Set[Tuple[int, int]] = set()
        self._initialize_streets()

    def _initialize_streets(self):
        """Initialize the street grid based on block size and street width."""
        # Calculate street positions
        total_block = self.block_size + self.street_width

        # Create horizontal streets
        for y in range(0, self.length, total_block):
            for x in range(0, self.width):
                street_region = self._get_region(x, y)
                self.street_locations.add(street_region)

        # Create vertical streets
        for x in range(0, self.width, total_block):
            for y in range(0, self.length):
                street_region = self._get_region(x, y)
                self.street_locations.add(street_region)

    def _is_on_street(self, position: Tuple[float, float]) -> bool:
        """Determine if a position is on a street."""
        x, y = position
        total_block = self.block_size + self.street_width

        # Check if position is on a horizontal street
        dist_to_horiz = y % total_block
        on_horiz = dist_to_horiz < self.street_width

        # Check if position is on a vertical street
        dist_to_vert = x % total_block
        on_vert = dist_to_vert < self.street_width

        return on_horiz or on_vert

    def _get_valid_building_position(self) -> Tuple[float, float]:
        """Generate a random position within a building block."""
        total_block = self.block_size + self.street_width

        # Get random block coordinates
        block_x = random.randint(0, (self.width // total_block) - 1)
        block_y = random.randint(0, (self.length // total_block) - 1)

        # Calculate the start position of the block
        start_x = block_x * total_block + self.street_width
        start_y = block_y * total_block + self.street_width

        # Generate random position within the block
        x = random.uniform(start_x, start_x + self.block_size)
        y = random.uniform(start_y, start_y + self.block_size)

        return (x, y)

    def place_node(self, node: BaseNode) -> bool:
        """Place a node in the grid, ensuring it's in a valid building area."""
        if self._is_on_street(node.position):
            return False

        if 0 <= node.position[0] <= self.width and 0 <= node.position[1] <= self.length:
            self.nodes.append(node)
            self.add_node_to_grid(node)
            return True
        return False

    def auto_place_nodes(self, num_nodes: int, node: BaseNode) -> int:
        """
        Automatically place nodes in building areas only.
        """
        placed_count = 0

        for _ in range(num_nodes):
            new_node = type(node).deserialize(node.serialize())
            new_node.position = self._get_valid_building_position()

            if self.place_node(new_node):
                placed_count += 1

        return placed_count

    def detect_collision(self, node: BaseNode) -> List[BaseNode]:
        """
        Detect collisions with other nodes within building areas.
        """
        colliding_nodes = []
        region = self._get_region(node.position[0], node.position[1])
        neighboring_regions = self._get_neighbors(region)

        for reg in neighboring_regions:
            if reg in self.grid:
                for other_node in self.grid[reg]:
                    if other_node is node:
                        continue

                    distance = math.dist(node.position, other_node.position)
                    if distance <= node.detection_range:
                        colliding_nodes.append(other_node)

        return colliding_nodes
