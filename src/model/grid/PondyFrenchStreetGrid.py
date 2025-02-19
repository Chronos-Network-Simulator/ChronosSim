import math
import random
from typing import List, Tuple, Set, Dict
from enum import Enum
from model.grid import BaseSimulationGrid
from model.node.BaseNode import BaseNode
from model.setting.model_settings import NumericSetting, OptionSetting, SupportedEntity


class QuarterType(Enum):
    FRENCH = "french"
    TAMIL = "tamil"
    CANAL = "canal"
    BEACH = "beach"


class PondicherryGrid(BaseSimulationGrid):
    name: str = "Pondicherry City Grid"
    description: str = (
        "A grid representing Pondicherry's unique layout with French Quarter (White Town), "
        "Tamil Quarter, and the canal separating them. Features the characteristic "
        "perpendicular streets of French Quarter and the organic layout of Tamil Quarter."
    )
    icon: str = "landmark"

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
            min_value=20,
            max_value=80,
            default_value=40,
            attributes=["street_width"],
            entity_type=SupportedEntity.GRID,
        ),
        NumericSetting(
            name="Block Size",
            description="Size of building blocks in meters",
            min_value=100,
            max_value=500,
            default_value=300,
            attributes=["block_size"],
            entity_type=SupportedEntity.GRID,
        ),
        NumericSetting(
            name="Canal Width",
            description="Width of the central canal in meters",
            min_value=30,
            max_value=100,
            default_value=50,
            attributes=["canal_width"],
            entity_type=SupportedEntity.GRID,
        ),
    ]

    width: int = 5000
    length: int = 5000
    region_size: int = 500
    street_width: int = 40
    block_size: int = 300
    canal_width: int = 50

    def __init__(self):
        super().__init__()
        self.street_locations: Set[Tuple[int, int]] = set()
        self.quarter_map: Dict[Tuple[int, int], QuarterType] = {}
        self._initialize_city_layout()

    def _initialize_city_layout(self):
        """Initialize the Pondicherry city layout with different quarters."""
        # Define quarter boundaries
        french_quarter_width = self.width // 3
        canal_start = french_quarter_width
        canal_end = canal_start + self.canal_width

        # Initialize French Quarter (regular grid)
        self._initialize_french_quarter(0, french_quarter_width)

        # Initialize Canal
        self._initialize_canal(canal_start, canal_end)

        # Initialize Tamil Quarter (organic layout)
        self._initialize_tamil_quarter(canal_end, self.width)

        # Initialize Beach Promenade
        self._initialize_beach_promenade()

    def _initialize_french_quarter(self, start_x: int, end_x: int):
        """Initialize the regular grid pattern of French Quarter."""
        total_block = self.block_size + self.street_width

        # Create horizontal streets
        for y in range(0, self.length, total_block):
            for x in range(start_x, end_x):
                region = self._get_region(x, y)
                self.street_locations.add(region)
                self.quarter_map[region] = QuarterType.FRENCH

        # Create vertical streets
        for x in range(start_x, end_x, total_block):
            for y in range(0, self.length):
                region = self._get_region(x, y)
                self.street_locations.add(region)
                self.quarter_map[region] = QuarterType.FRENCH

    def _initialize_tamil_quarter(self, start_x: int, end_x: int):
        """Initialize the organic layout of Tamil Quarter with irregular streets."""
        # Create main arterial roads
        for x in range(start_x, end_x, self.block_size * 2):
            for y in range(0, self.length):
                if random.random() < 0.8:  # 80% chance of street continuity
                    region = self._get_region(x, y)
                    self.street_locations.add(region)
                    self.quarter_map[region] = QuarterType.TAMIL

        # Create connecting streets with some randomness
        for y in range(0, self.length, self.block_size):
            for x in range(start_x, end_x):
                if random.random() < 0.3:  # 30% chance of street
                    region = self._get_region(x, y)
                    self.street_locations.add(region)
                    self.quarter_map[region] = QuarterType.TAMIL

    def _initialize_canal(self, start_x: int, end_x: int):
        """Initialize the central canal."""
        for x in range(start_x, end_x):
            for y in range(0, self.length):
                region = self._get_region(x, y)
                self.street_locations.add(region)
                self.quarter_map[region] = QuarterType.CANAL

    def _initialize_beach_promenade(self):
        """Initialize the Beach Promenade along the eastern edge."""
        promenade_width = 100  # meters
        for x in range(self.width - promenade_width, self.width):
            for y in range(0, self.length):
                region = self._get_region(x, y)
                self.street_locations.add(region)
                self.quarter_map[region] = QuarterType.BEACH

    def _get_quarter_type(self, position: Tuple[float, float]) -> QuarterType:
        """Determine which quarter a position falls in."""
        region = self._get_region(position[0], position[1])
        return self.quarter_map.get(region, QuarterType.TAMIL)

    def _get_valid_building_position(self) -> Tuple[float, float]:
        """Generate a random position within a valid building area."""
        while True:
            x = random.uniform(0, self.width)
            y = random.uniform(0, self.length)
            position = (x, y)

            # Check if position is valid (not on street, canal, or beach)
            if not self._is_on_street(position):
                quarter = self._get_quarter_type(position)
                if quarter not in [QuarterType.CANAL, QuarterType.BEACH]:
                    return position

    def _is_on_street(self, position: Tuple[float, float]) -> bool:
        """Determine if a position is on a street, canal, or beach."""
        region = self._get_region(position[0], position[1])
        return region in self.street_locations

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
        """Automatically place nodes in valid building areas."""
        placed_count = 0

        for _ in range(num_nodes):
            new_node = node.duplicate()
            new_node.position = self._get_valid_building_position()

            if self.place_node(new_node):
                placed_count += 1

        return placed_count

    def detect_collision(self, node: BaseNode) -> List[BaseNode]:
        """Detect collisions with other nodes, considering building areas."""
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
