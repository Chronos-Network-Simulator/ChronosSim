from pubsub import pub

from exception.exception import ConfigError
from model.grid.BaseSimulationGrid import BaseSimulationGrid
from model.node import BaseNode


class SimulationModel:

    status: str
    """
    The current status of the simulation. Can take on the following values:
    - empty: The simulation has not been initialized
    - running: The simulation is currently running
    - paused: The simulation is currently paused
    - stopped: The simulation has been stopped and needs to be cleared
    """

    grid: BaseSimulationGrid | None
    """
    The grid that the simulation is running on.
    """

    node: BaseNode | None
    """
    The node type that the simulation is running with.
    """

    def initialize(self) -> None:
        """
        Initializes the simulation model
        """
        self.status = "empty"
        self.set_grid(None)
        self.set_node(None)

    def set_grid(self, grid: BaseSimulationGrid | None) -> None:
        """
        Sets the grid for the simulation to run on and notifies all subscribers

        :param grid: The grid to set the simulation to run on
        :type grid: BaseSimulationGrid
        """
        if (self.status == "empty") or (self.status == "stopped"):
            self.grid = grid
            pub.sendMessage(
                topicName="simulation.grid_changed",
                grid_type=grid.name if grid else "None",
            )
        elif self.status == "running":
            raise ConfigError("Cannot set grid while simulation is running")
        elif self.status == "paused":
            raise ConfigError("Stop the simulation before changing the grid")

    def set_node(self, node: BaseNode | None) -> None:
        """
        Sets the node for the simulation to run with and notifies all subscribers

        :param node: The node to set the simulation to run with
        :type node: BaseNode
        """
        if (self.status == "empty") or (self.status == "stopped"):
            self.node = node
            pub.sendMessage(
                topicName="simulation.node_changed",
                node_type=node.name if node else "None",
            )
        elif self.status == "running":
            raise ConfigError("Cannot set node while simulation is running")
        elif self.status == "paused":
            raise ConfigError("Stop the simulation before changing the node")
