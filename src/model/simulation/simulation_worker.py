import multiprocessing as mp
import pickle
import random
import uuid
from queue import Empty
from time import sleep
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
            "target": node.target,
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
        step_delay: float = 0.0,
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
        self.step_delay = step_delay

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
            self._send_current_state()

            for node in self.grid.nodes:
                node.on_simulation_step_end()
                node.move()
            self.step += 1
            sleep(self.step_delay)

    def _send_current_state(self):
        """Send current state through queue."""
        current_state = self._get_current_state()
        self.results.append(current_state)
        self.results_queue.put(current_state)

    def _simulate_step(self) -> None:
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
            # Handle node_a sending to node_b
            if node_a.target:
                message_A_to_B = node_a.on_target_send(node_b)
                if message_A_to_B is not None:
                    node_b.on_target_received(message_A_to_B, node_a)
            else:
                message_A_to_B = node_a.send_message(node_b)
                if message_A_to_B is not None:
                    if node_b.target:
                        node_b.on_target_received(message_A_to_B, node_a)
                    else:
                        node_b.receive_message(message_A_to_B, node_a)

            # Handle node_b sending to node_a
            if node_b.target:
                message_B_to_A = node_b.on_target_send(node_a)
                if message_B_to_A is not None:
                    node_a.on_target_received(message_B_to_A, node_b)
            else:
                message_B_to_A = node_b.send_message(node_a)
                if message_B_to_A is not None:
                    if node_a.target:
                        node_a.on_target_received(message_B_to_A, node_b)
                    else:
                        node_a.receive_message(message_B_to_A, node_b)

            node_a.on_collision_complete()
            node_b.on_collision_complete()
