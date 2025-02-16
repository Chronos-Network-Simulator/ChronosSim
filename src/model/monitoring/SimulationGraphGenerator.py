from collections import defaultdict
from pathlib import Path
from typing import List

import matplotlib.pyplot as plt
import numpy as np

from model.monitoring.DataTypes import SimulationState


class SimulationGraphGenerator:
    def __init__(self, data_handler: "SimulationDataHandler"):
        self.data_handler = data_handler
        self.session = data_handler.current_session
        if not self.session:
            raise RuntimeError("No active session in data handler")

    def generate_all_graphs(self):
        """Generate all graphs for each simulation and aggregated data."""
        for sim_id, states in self.data_handler.simulations.items():
            if states:  # Only process if we have data
                graphs_dir = self.session.get_graphs_dir(sim_id)
                self._generate_simulation_graphs(sim_id, states, graphs_dir)

        # Generate aggregated graphs if we have data
        if self.data_handler.simulations:
            self._generate_aggregated_graphs()

    def _generate_simulation_graphs(
        self, sim_id: str, states: List[SimulationState], output_dir: Path
    ):
        """Generate graphs for a single simulation."""
        steps = [state.step for state in states]

        # Message propagation over time with success messages
        plt.figure(figsize=(10, 6))
        total_messages = [len(state.messages) for state in states]
        success_messages = [len(state.success_messages) for state in states]

        plt.plot(steps, total_messages, "-b", label="Total Messages")
        plt.plot(steps, success_messages, "-g", label="Successful Messages")
        plt.title(f"Message Propagation and Success - Simulation {sim_id}")
        plt.xlabel("Step")
        plt.ylabel("Number of Messages")
        plt.grid(True)
        plt.legend()
        plt.savefig(output_dir / "message_propagation.png")
        plt.close()

        # Success rate over time
        plt.figure(figsize=(10, 6))
        success_rates = [
            (
                (len(state.success_messages) / len(state.messages) * 100)
                if state.messages
                else 0
            )
            for state in states
        ]
        plt.plot(steps, success_rates, "-g")
        plt.title(f"Message Success Rate Over Time - Simulation {sim_id}")
        plt.xlabel("Step")
        plt.ylabel("Success Rate (%)")
        plt.grid(True)
        plt.savefig(output_dir / "success_rate.png")
        plt.close()

        # Message delivery time distribution
        plt.figure(figsize=(10, 6))
        delivery_times = []
        for state in states:
            for msg in state.success_messages:
                delivery_time = state.step - msg.created_time
                delivery_times.append(delivery_time)

        if delivery_times:
            plt.hist(delivery_times, bins=20)
            plt.title(f"Message Delivery Time Distribution - Simulation {sim_id}")
            plt.xlabel("Delivery Time (steps)")
            plt.ylabel("Number of Messages")
            plt.grid(True)
            plt.savefig(output_dir / "delivery_times.png")
            plt.close()

        # Previous graphs...
        self._generate_basic_graphs(sim_id, states, output_dir)

    def _generate_basic_graphs(
        self, sim_id: str, states: List[SimulationState], output_dir: Path
    ):
        """Generate the original set of basic graphs."""
        steps = [state.step for state in states]

        # Message hop distribution
        hop_counts = defaultdict(int)
        for state in states:
            for msg in state.success_messages:  # Only counting successful messages
                hop_counts[msg.hops] += 1

        if hop_counts:
            plt.figure(figsize=(10, 6))
            hops, counts = zip(*sorted(hop_counts.items()))
            plt.bar(hops, counts)
            plt.title(f"Successful Message Hop Distribution - Simulation {sim_id}")
            plt.xlabel("Number of Hops")
            plt.ylabel("Message Count")
            plt.grid(True)
            plt.savefig(output_dir / "hop_distribution.png")
            plt.close()

        # Node message distribution and target nodes (unchanged)
        plt.figure(figsize=(10, 6))
        final_state = states[-1]
        message_counts = [node.message_count for node in final_state.node_states]
        plt.hist(message_counts, bins=20)
        plt.title(f"Node Message Distribution - Simulation {sim_id}")
        plt.xlabel("Messages per Node")
        plt.ylabel("Number of Nodes")
        plt.grid(True)
        plt.savefig(output_dir / "node_message_distribution.png")
        plt.close()

        plt.figure(figsize=(10, 6))
        target_nodes = [
            sum(1 for node in state.node_states if node.target) for state in states
        ]
        plt.plot(steps, target_nodes, "-r", label="Target Nodes")
        plt.title(f"Target Node Count Over Time - Simulation {sim_id}")
        plt.xlabel("Step")
        plt.ylabel("Number of Target Nodes")
        plt.grid(True)
        plt.legend()
        plt.savefig(output_dir / "target_nodes.png")
        plt.close()

    def _generate_aggregated_graphs(self):
        """Generate graphs aggregating data across all simulations."""
        graphs_dir = self.session.session_dir / "aggregated_graphs"
        graphs_dir.mkdir(exist_ok=True)

        # Prepare data structures for aggregation
        max_steps = max(
            len(states) for states in self.data_handler.simulations.values()
        )
        message_counts = np.zeros((len(self.data_handler.simulations), max_steps))
        success_counts = np.zeros((len(self.data_handler.simulations), max_steps))
        success_rates = np.zeros((len(self.data_handler.simulations), max_steps))

        # Collect delivery times across all simulations
        all_delivery_times = []

        for i, states in enumerate(self.data_handler.simulations.values()):
            # Message counts
            counts = [len(state.messages) for state in states]
            message_counts[i, : len(counts)] = counts

            # Success counts and rates
            successes = [len(state.success_messages) for state in states]
            success_counts[i, : len(successes)] = successes

            # Calculate success rates
            rates = [
                (
                    (len(state.success_messages) / len(state.messages) * 100)
                    if state.messages
                    else 0
                )
                for state in states
            ]
            success_rates[i, : len(rates)] = rates

            # Collect delivery times
            for state in states:
                for msg in state.success_messages:
                    delivery_time = state.step - msg.created_time
                    all_delivery_times.append(delivery_time)

        # Average success rate with confidence interval
        plt.figure(figsize=(10, 6))
        steps = range(max_steps)
        mean_rates = np.mean(success_rates, axis=0)
        std_rates = np.std(success_rates, axis=0)

        plt.plot(steps, mean_rates, "-g", label="Mean Success Rate")
        plt.fill_between(
            steps,
            mean_rates - std_rates,
            mean_rates + std_rates,
            alpha=0.2,
            color="g",
            label="±1 Std Dev",
        )

        plt.title("Average Message Success Rate Across All Simulations")
        plt.xlabel("Step")
        plt.ylabel("Success Rate (%)")
        plt.grid(True)
        plt.legend()
        plt.savefig(graphs_dir / "average_success_rate.png")
        plt.close()

        # Aggregate delivery time distribution
        if all_delivery_times:
            plt.figure(figsize=(10, 6))
            plt.hist(all_delivery_times, bins=20)
            plt.title("Aggregate Message Delivery Time Distribution")
            plt.xlabel("Delivery Time (steps)")
            plt.ylabel("Number of Messages")
            plt.grid(True)
            plt.savefig(graphs_dir / "aggregate_delivery_times.png")
            plt.close()

        # Previous aggregated graphs...
        self._generate_basic_aggregated_graphs(
            graphs_dir, max_steps, message_counts, success_counts
        )

    def _generate_basic_aggregated_graphs(
        self,
        graphs_dir: Path,
        max_steps: int,
        message_counts: np.ndarray,
        success_counts: np.ndarray,
    ):
        """Generate the original set of aggregated graphs."""
        steps = range(max_steps)

        # Average message counts with success overlay
        plt.figure(figsize=(10, 6))
        mean_messages = np.mean(message_counts, axis=0)
        std_messages = np.std(message_counts, axis=0)
        mean_successes = np.mean(success_counts, axis=0)
        std_successes = np.std(success_counts, axis=0)

        plt.plot(steps, mean_messages, "-b", label="Mean Total Messages")
        plt.fill_between(
            steps,
            mean_messages - std_messages,
            mean_messages + std_messages,
            alpha=0.2,
            color="b",
            label="±1 Std Dev (Total)",
        )

        plt.plot(steps, mean_successes, "-g", label="Mean Successful Messages")
        plt.fill_between(
            steps,
            mean_successes - std_successes,
            mean_successes + std_successes,
            alpha=0.2,
            color="g",
            label="±1 Std Dev (Success)",
        )

        plt.title("Average Message Counts Across All Simulations")
        plt.xlabel("Step")
        plt.ylabel("Number of Messages")
        plt.grid(True)
        plt.legend()
        plt.savefig(graphs_dir / "average_message_counts.png")
        plt.close()
