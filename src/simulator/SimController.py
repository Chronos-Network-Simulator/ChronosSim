from simulator.grid import BaseSimulationGrid


class SimController:
    """
    Master Controller of th4e simulation. Is responsible for loading nodes
    into the simulation and starting the simulation

    """

    starting_num_nodes: int = 0
    """
    The number of nodes that are in the network at the start of the simulation
    """

    grid: BaseSimulationGrid = None
    """
    The grid that the simulation is taking place on.
    """

    def __init__(self):
        pass
