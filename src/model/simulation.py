import random
from pprint import pprint

from pubsub import pub

from exception.exception import ConfigError
from model.grid.BaseSimulationGrid import BaseSimulationGrid
from model.message.BaseMessage import BaseMessage
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

    message_template: BaseMessage | None = BaseMessage(
        original_content="Demo Message", creator_id="0"
    )
    """
    Stores a template on the message that will be generated at random throughout the network.
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
            pub.sendMessage(topicName="simulation.grid_changed", grid=grid)
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
                node=node,
            )
        elif self.status == "running":
            raise ConfigError("Cannot set node while simulation is running")
        elif self.status == "paused":
            raise ConfigError("Stop the simulation before changing the node")

    def run_simulation(self, steps: int) -> None:
        """
        Runs the simulation for a specified number of steps.
        """
        if self.grid is None:
            raise ConfigError("Cannot run simulation without a grid")
        if self.node is None:
            raise ConfigError("Cannot run simulation without a node type")

        self.status = "running"
        num_nodes = 400
        placed_count = self.grid.auto_place_nodes(num_nodes, self.node)

        if placed_count != num_nodes:
            raise ConfigError(
                f"Only {placed_count} nodes were placed out of {num_nodes}"
            )

        try:
            for _ in range(steps):
                if self.status != "running":
                    break
                self._simulate_step()
                for node in self.grid.nodes:
                    node.on_simulation_step_end()
                pub.sendMessage("simulation.step_complete")
                print("Simulation step completed")
        finally:
            self.status = "stopped"
            for node in self.grid.nodes:
                pprint(node.messages)

    def _simulate_step(self) -> None:
        """
        Performs a simulation step using a two-phase, order-insensitive approach.

        Phase 1: Collect all unique collision pairs.
        Phase 2: Process each collision pair where each node can decide
                 to send a message to the other.
        """
        collision_pairs = set()

        # Phase 1: Collect unique collision pairs.
        for node in self.grid.nodes:
            colliding_nodes = self.grid.detect_collision(node)
            for other_node in colliding_nodes:
                # Avoid self-collision.
                if node is other_node:
                    continue

                # Use a canonical ordering based on a unique identifier.
                if node.id < other_node.id:
                    pair = (node, other_node)
                else:
                    pair = (other_node, node)
                collision_pairs.add(pair)

        # Introduce randomness by shuffling the collision pairs.
        collision_pairs_list = list(collision_pairs)
        random.shuffle(collision_pairs_list)

        # Phase 2: Process each collision pair.
        for node_a, node_b in collision_pairs_list:
            # Node A attempts to send a message to Node B.
            message_A_to_B = node_a.send_message(node_b)
            if message_A_to_B is not None:
                node_b.receive_message(message_A_to_B, node_a)

            # Node B attempts to send a message to Node A.
            message_B_to_A = node_b.send_message(node_a)
            if message_B_to_A is not None:
                node_a.receive_message(message_B_to_A, node_b)

            node_a.on_collision_complete()
            node_b.on_collision_complete()
