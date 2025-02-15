import multiprocessing as mp
import pickle
import random
import uuid
from pprint import pprint
from queue import Empty
from typing import List

from model.grid import BaseSimulationGrid
from model.message_spawner import BaseMessageSpawner
from model.node import BaseNode


def _capture_node_states(nodes: List[BaseNode]):
    """Captures the current state of all nodes."""
    return [
        {
            "id": node.id,
            "position": node.position,
            "message_count": len(node.messages) if node.messages else 0,
        }
        for node in nodes
    ]


def _capture_messages(nodes: List[BaseNode]):
    """Captures all messages in the system."""
    messages = []
    for node in nodes:
        if node.messages:
            messages.extend(
                [
                    {
                        "content": msg.original_content,
                        "creator": msg.creator_id,
                        "time": msg.created_time,
                    }
                    for msg in node.messages
                ]
            )
    return messages


class SimulationWorker:
    """
    The simulation model run inside each worker process.
    Now includes shared results handling and improved control queue management.
    """

    grid: BaseSimulationGrid

    nodes: BaseNode

    message_spawner: BaseMessageSpawner

    def __init__(
        self,
        pickled_node_type: bytes,
        pickled_grid_type: bytes,
        pickled_message_spawner: bytes,
        pickled_message_template: bytes,
        node_count: int,
        step_count: int,
        control_queue: mp.Queue,
        results_queue: mp.Queue,
    ):
        self.node = pickle.loads(pickled_node_type)
        self.grid = pickle.loads(pickled_grid_type)
        self.message_spawner = pickle.loads(pickled_message_spawner)
        self.message_template = pickle.loads(pickled_message_template)
        self.node_count = node_count
        self.step_count = step_count
        self.status = "stop"
        self.simulation_id = uuid.uuid4().hex
        self.control_queue = control_queue
        self.results_queue = results_queue
        self.step = 0
        self.results = []
        pprint(vars(self.message_spawner))
        pprint(vars(self.message_template))

    def _get_current_state(self):
        """Get current simulation state."""
        return {
            "simulation_id": self.simulation_id,
            "step": self.step,
            "node_states": _capture_node_states(self.grid.nodes),
            "messages": _capture_messages(self.grid.nodes),
            "status": self.status,
        }

    def simulate(self):
        """Main simulation loop with result reporting."""
        while self.step < self.step_count:
            try:
                control = self.control_queue.get_nowait()
                if control.command == "pause":
                    self.status = "paused"
                    self._send_current_state()
                    control = self.control_queue.get()
                    if control.command == "stop":
                        self.status = "stopped"
                    self.status = "running"
                elif control.command == "stop":
                    self.status = "stopped"
            except Empty:
                pass
            # let the message spawner create messages
            self.message_spawner.spawn_messages(
                self.grid.nodes, self.step, self.message_template
            )
            self._simulate_step()
            self.capture_state()
            self._send_current_state()

            for node in self.grid.nodes:
                node.on_simulation_step_end()
                node.move()
            self.step += 1

    def _send_current_state(self):
        """Send current state through queue."""
        current_state = self._get_current_state()
        self.results_queue.put(current_state)

    def _simulate_step(self) -> None:
        """Simulation step logic remains unchanged."""
        collision_pairs = set()

        # Phase 1: Collect unique collision pairs
        for node in self.grid.nodes:
            colliding_nodes = self.grid.detect_collision(node)
            for other_node in colliding_nodes:
                if node.id == other_node.id:
                    continue
                if node.id < other_node.id:
                    pair = (node, other_node)
                else:
                    pair = (other_node, node)
                collision_pairs.add(pair)

        # Shuffle collision pairs for randomness
        collision_pairs_list = list(collision_pairs)
        random.shuffle(collision_pairs_list)

        # Phase 2: Process collisions
        for node_a, node_b in collision_pairs_list:
            message_A_to_B = node_a.send_message(node_b)
            if message_A_to_B is not None:
                node_b.receive_message(message_A_to_B, node_a)

            message_B_to_A = node_b.send_message(node_a)
            if message_B_to_A is not None:
                node_a.receive_message(message_B_to_A, node_b)

            node_a.on_collision_complete()
            node_b.on_collision_complete()

    def capture_state(self) -> None:
        """Capture state with additional metadata."""
        step_results = {
            "simulation_id": self.simulation_id,
            "step": self.step,
            "node_states": _capture_node_states(self.grid.nodes),
            "messages": _capture_messages(self.grid.nodes),
            "status": self.status,
        }
        self.results.append(step_results)
