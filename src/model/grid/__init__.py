from typing import List

from model.grid.BaseSimulationGrid import BaseSimulationGrid
from model.grid.CitySimulationGrid import CityGrid
from model.grid.PondyFrenchStreetGrid import PondicherryGrid
from model.grid.SimpleRandomGrid import SimpleRandomGrid

AVAILABLE_GRIDS: List[type[BaseSimulationGrid]] = [SimpleRandomGrid, CityGrid, PondicherryGrid]


def get_grid_by_name(name: str) -> BaseSimulationGrid:
    """
    Get a grid by its name

    :param name: The name of the grid to get
    :type name: str
    :return: The grid with the specified name
    :rtype: BaseSimulationGrid
    """
    for grid in AVAILABLE_GRIDS:
        if grid.name == name:
            return grid()
    raise ValueError(f"Grid with name {name} not found")
