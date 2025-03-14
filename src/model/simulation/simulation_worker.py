import multiprocessing as mp
import pickle
import random
import uuid
from queue import Empty
from time import sleep
from typing import List
from model.grid import BaseSimulationGrid
from model.message.BaseMessage import BaseMessage
from model.message_spawner import BaseMessageSpawner
from model.monitoring.DataTypes import SimulationStepMetrics
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
                        "id": msg.id,
                        "content": msg.original_content,
                        "creator": msg.creator_id,
                        "created_time": msg.created_time,
                        "hops": msg.hops,
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

    success_messages: List[BaseMessage]

    def __init__(
        self,
        node_type: type[BaseNode],
        grid_type: type[BaseSimulationGrid],
        sim_data: dict,
        pickled_message_spawner: bytes,
        pickled_message_template: bytes,
        node_count: int,
        step_count: int,
        control_queue: mp.Queue,
        results_queue: mp.Queue,
        step_delay: float = 0.0,
    ):
        self.node_type = node_type
        self.grid_type = grid_type
        self.grid = grid_type.deserialize(sim_data, node_type=self.node_type)
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
        self.success_messages = []

    def _capture_success_messages(self):
        """Captures all messages in the system."""
        messages = []
        messages.extend(
            [
                {
                    "id": msg.id,
                    "content": msg.original_content,
                    "creator": msg.creator_id,
                    "created_time": msg.created_time,
                    "hops": msg.hops,
                }
                for msg in self.success_messages
            ]
        )
        return messages

    def _get_current_state(self):
        """Get current simulation state."""
        return {
            "simulation_id": self.simulation_id,
            "step": self.step,
            "node_states": _capture_node_states(self.grid.nodes),
            "messages": _capture_messages(self.grid.nodes),
            "status": self.status,
            "success_messages": self._capture_success_messages(),
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
            metrics = self._simulate_step()
            self._send_current_state(metrics)

            for node in self.grid.nodes:
                node.on_simulation_step_end()
                node.move()
            self.step += 1
            sleep(self.step_delay)

    def _send_current_state(
        self, step_metrics: SimulationStepMetrics | None = None
    ) -> None:
        """Send current state through queue."""
        current_state = self._get_current_state()
        if step_metrics:
            current_state["step_metrics"] = step_metrics.__json_encode__()
        self.results.append(current_state)
        self.results_queue.put(current_state)

    def _simulate_step(self) -> SimulationStepMetrics:
        # Initialize step metrics with empty phase data
        step_metrics = SimulationStepMetrics()
        step_metrics.phase_data = {
            "pre_collision": {"bytes": 0, "count": 0},
            "message_exchange": {"bytes": 0, "count": 0},
        }

        # Phase 1: Collect unique collision pairs
        collision_pairs = set()
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

        # Track unique node encounters
        step_metrics.nodes_encountered = len(collision_pairs)

        # Shuffle collision pairs for randomness
        collision_pairs_list: List[tuple[BaseNode, BaseNode]] = list(collision_pairs)
        random.shuffle(collision_pairs_list)

        # Phase 2: Pre-collision metadata exchange (only for non-target nodes)
        pre_collision_data = {}
        for node_a, node_b in collision_pairs_list:
            # Skip metadata exchange if either node is a target node
            if node_a.target or node_b.target:
                continue

            # Exchange metadata
            metadata_a_to_b = node_a.pre_collision(node_b)
            metadata_b_to_a = node_b.pre_collision(node_a)

            # Only process and store if both nodes returned valid metadata
            if metadata_a_to_b is not None and metadata_b_to_a is not None:
                # Calculate metadata size
                metadata_a_size = self._calculate_metadata_size(metadata_a_to_b)
                metadata_b_size = self._calculate_metadata_size(metadata_b_to_a)
                if (metadata_a_size + metadata_b_size) > 0:
                    # Update metrics
                    step_metrics.metadata_bytes_sent += (
                        metadata_a_size + metadata_b_size
                    )
                    step_metrics.summaries_exchanged += 2
                    step_metrics.phase_data["pre_collision"]["bytes"] += (
                        metadata_a_size + metadata_b_size
                    )
                    step_metrics.phase_data["pre_collision"]["count"] += 2

                # Process metadata and determine what to request
                request_a_to_b = node_a.process_pre_collision(metadata_b_to_a, node_b)
                request_b_to_a = node_b.process_pre_collision(metadata_a_to_b, node_a)

                # Only store the requests if both nodes returned valid requests
                if request_a_to_b is not None and request_b_to_a is not None:
                    # Store the requests for use in the next phase
                    pre_collision_data[(node_a.id, node_b.id)] = (
                        request_a_to_b,
                        request_b_to_a,
                    )

        # Phase 3: Process collisions with requested messages
        for node_a, node_b in collision_pairs_list:
            # Handle target nodes first - this is always handled through the target interface,
            # regardless of whether nodes implement the metadata protocol or not
            if node_a.target or node_b.target:
                if node_a.target:
                    message_B_to_A = node_b.on_send_to_target(node_a)
                    if message_B_to_A is not None:
                        node_a.on_receive_as_target(message_B_to_A, node_b)
                        increment_hops(message_B_to_A)

                        # Track payload size for target messages
                        payload_size = self._calculate_payload_size(message_B_to_A)
                        step_metrics.payload_bytes_sent += payload_size
                        step_metrics.messages_exchanged += len(message_B_to_A)
                        step_metrics.phase_data["message_exchange"]["bytes"] += (
                            payload_size
                        )
                        step_metrics.phase_data["message_exchange"]["count"] += len(
                            message_B_to_A
                        )
                        # add to success messages
                        self.success_messages.extend(message_B_to_A)

                if node_b.target:
                    message_A_to_B = node_a.on_send_to_target(node_b)
                    if message_A_to_B is not None:
                        node_b.on_receive_as_target(message_A_to_B, node_a)
                        increment_hops(message_A_to_B)

                        # Track payload size for target messages
                        payload_size = self._calculate_payload_size(message_A_to_B)
                        step_metrics.payload_bytes_sent += payload_size
                        step_metrics.messages_exchanged += len(message_A_to_B)
                        step_metrics.phase_data["message_exchange"]["bytes"] += (
                            payload_size
                        )
                        step_metrics.phase_data["message_exchange"]["count"] += len(
                            message_A_to_B
                        )
                        # Add to success messages
                        self.success_messages.extend(message_A_to_B)
            else:
                # For regular nodes, check if they use the multi-phase approach
                pair_key = (node_a.id, node_b.id)
                if pair_key in pre_collision_data:
                    # These nodes support the multi-phase protocol
                    request_a_to_b, request_b_to_a = pre_collision_data[pair_key]

                    # Handle node_a sending requested messages to node_b
                    message_A_to_B = node_a.send_requested_messages(
                        request_b_to_a, node_b
                    )
                    if message_A_to_B is not None:
                        node_b.receive_message(message_A_to_B, node_a)
                        increment_hops(message_A_to_B)
                        # Track payload size for messages exchanged
                        payload_size = self._calculate_payload_size(message_A_to_B)
                        step_metrics.payload_bytes_sent += payload_size
                        step_metrics.messages_exchanged += len(message_A_to_B)
                        step_metrics.phase_data["message_exchange"]["bytes"] += (
                            payload_size
                        )
                        step_metrics.phase_data["message_exchange"]["count"] += len(
                            message_A_to_B
                        )

                    # Handle node_b sending requested messages to node_a
                    message_B_to_A = node_b.send_requested_messages(
                        request_a_to_b, node_a
                    )
                    if message_B_to_A is not None:
                        node_a.receive_message(message_B_to_A, node_b)
                        increment_hops(message_B_to_A)
                        # Track payload size for messages exchanged
                        payload_size = self._calculate_payload_size(message_B_to_A)
                        step_metrics.payload_bytes_sent += payload_size
                        step_metrics.messages_exchanged += len(message_B_to_A)
                        step_metrics.phase_data["message_exchange"]["bytes"] += (
                            payload_size
                        )
                        step_metrics.phase_data["message_exchange"]["count"] += len(
                            message_B_to_A
                        )
                else:
                    # These nodes do not support the multi-phase protocol
                    # or the metadata exchange failed
                    # Use the fallback simple message exchange

                    # Handle node_a sending to node_b
                    message_A_to_B = node_a.send_message(node_b)
                    if message_A_to_B is not None:
                        node_b.receive_message(message_A_to_B, node_a)
                        increment_hops(message_A_to_B)

                        # Track payload size for fallback mode
                        payload_size = self._calculate_payload_size(message_A_to_B)
                        step_metrics.payload_bytes_sent += payload_size
                        step_metrics.messages_exchanged += len(message_A_to_B)
                        step_metrics.phase_data["message_exchange"]["bytes"] += (
                            payload_size
                        )
                        step_metrics.phase_data["message_exchange"]["count"] += len(
                            message_A_to_B
                        )

                    # Handle node_b sending to node_a
                    message_B_to_A = node_b.send_message(node_a)
                    if message_B_to_A is not None:
                        node_a.receive_message(message_B_to_A, node_b)
                        increment_hops(message_B_to_A)

                        # Track payload size for fallback mode
                        payload_size = self._calculate_payload_size(message_B_to_A)
                        step_metrics.payload_bytes_sent += payload_size
                        step_metrics.messages_exchanged += len(message_B_to_A)
                        step_metrics.phase_data["message_exchange"]["bytes"] += (
                            payload_size
                        )
                        step_metrics.phase_data["message_exchange"]["count"] += len(
                            message_B_to_A
                        )

            # Finalize the collision for both nodes
            node_a.on_collision_complete()
            node_b.on_collision_complete()

        # Phase 4: End of simulation step
        for node in self.grid.nodes:
            node.on_simulation_step_end()

        # return the step metrics for this step
        return step_metrics

    def _calculate_metadata_size(self, metadata: dict) -> int:
        """Calculate the size of the metadata more accurately using pickle."""
        if not metadata:
            return 0
        # Use pickle to get a more accurate byte representation
        return len(pickle.dumps(metadata))

    def _calculate_payload_size(self, messages: List[BaseMessage]) -> int:
        """Calculate the size of the payload."""
        if not messages:
            return 0
        return len(pickle.dumps(messages))


def increment_hops(messages: List[BaseMessage]) -> List[BaseMessage]:
    """Increment the hops of all messages."""
    for message in messages:
        message.hops += 1
    return messages
