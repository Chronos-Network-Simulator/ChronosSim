from collections import defaultdict
from pathlib import Path
from typing import Set

import matplotlib.pyplot as plt
import numpy as np


class SimulationGraphGenerator:
    def __init__(self, data_handler: "SimulationDataHandler"):
        self.data_handler = data_handler
        self.session = data_handler.current_session
        if not self.session:
            raise RuntimeError("No active session in data handler")

    def generate_all_graphs(self):
        if not self.session:
            return

        sim_ids = set()
        for sim_id in self._get_simulation_ids():
            sim_ids.add(sim_id)
            graphs_dir = self.session.get_graphs_dir(sim_id)
            self._generate_simulation_graphs(sim_id, graphs_dir)
            self._generate_data_transmission_graphs(sim_id, graphs_dir)
            self._generate_phase_data_graphs(sim_id, graphs_dir)
            self._generate_unique_message_graphs(sim_id, graphs_dir)

        if sim_ids:
            self._generate_aggregated_graphs(sim_ids)
            self._generate_aggregated_unique_message_graphs(sim_ids)

    def _get_simulation_ids(self) -> Set[str]:
        if not self.data_handler._simulation_metadata:
            return set()
        return set(self.data_handler._simulation_metadata.keys())

    def _extract_unique_message_metrics(self, sim_id: str):
        all_messages = set()
        successful_messages = set()
        step_data = []

        for state in self.data_handler.get_simulation_states(sim_id):
            current_messages = set(msg.id for msg in state.messages)
            all_messages.update(current_messages)

            current_successes = set(msg.id for msg in state.success_messages)
            successful_messages.update(current_successes)

            step_data.append(
                {
                    "step": state.step,
                    "total_unique_messages": len(all_messages),
                    "total_unique_successes": len(successful_messages),
                    "unique_success_rate": (
                        len(successful_messages) / len(all_messages) * 100
                    )
                    if all_messages
                    else 0,
                    "new_unique_messages": len(
                        current_messages - (all_messages - current_messages)
                    ),
                    "new_unique_successes": len(
                        current_successes - (successful_messages - current_successes)
                    ),
                }
            )

        return step_data

    def _generate_simulation_graphs(self, sim_id: str, output_dir: Path):
        steps = []
        total_messages = []
        success_messages = []
        delivery_times = []
        hop_counts = defaultdict(int)

        for state in self.data_handler.get_simulation_states(sim_id):
            steps.append(state.step)
            total_messages.append(len(state.messages))
            success_messages.append(len(state.success_messages))

            for msg in state.success_messages:
                delivery_times.append(state.step - msg.created_time)
                hop_counts[msg.hops] += 1

        if not steps:
            return

        # Message propagation and success
        plt.figure(figsize=(10, 6))
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
            (s / t * 100) if t else 0 for s, t in zip(success_messages, total_messages)
        ]
        plt.plot(steps, success_rates, "-g")
        plt.title(f"Message Success Rate Over Time - Simulation {sim_id}")
        plt.xlabel("Step")
        plt.ylabel("Success Rate (%)")
        plt.grid(True)
        plt.savefig(output_dir / "success_rate.png")
        plt.close()

        # Message delivery time distribution
        if delivery_times:
            plt.figure(figsize=(10, 6))
            plt.hist(delivery_times, bins=20)
            plt.title(f"Message Delivery Time Distribution - Simulation {sim_id}")
            plt.xlabel("Delivery Time (steps)")
            plt.ylabel("Number of Messages")
            plt.grid(True)
            plt.savefig(output_dir / "delivery_times.png")
            plt.close()

        # Message hop distribution
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

        # Get final state for node statistics
        final_state = self.data_handler.get_latest_state(sim_id)
        if final_state:
            # Node message distribution
            plt.figure(figsize=(10, 6))
            message_counts = [node.message_count for node in final_state.node_states]
            plt.hist(message_counts, bins=20)
            plt.title(f"Node Message Distribution - Simulation {sim_id}")
            plt.xlabel("Messages per Node")
            plt.ylabel("Number of Nodes")
            plt.grid(True)
            plt.savefig(output_dir / "node_message_distribution.png")
            plt.close()

        # Target node count over time
        target_nodes = []
        for state in self.data_handler.get_simulation_states(sim_id):
            target_nodes.append(sum(1 for node in state.node_states if node.target))

        plt.figure(figsize=(10, 6))
        plt.plot(steps, target_nodes, "-r", label="Target Nodes")
        plt.title(f"Target Node Count Over Time - Simulation {sim_id}")
        plt.xlabel("Step")
        plt.ylabel("Number of Target Nodes")
        plt.grid(True)
        plt.legend()
        plt.savefig(output_dir / "target_nodes.png")
        plt.close()

    def _generate_data_transmission_graphs(self, sim_id: str, output_dir: Path):
        steps = []
        metadata_bytes = []
        payload_bytes = []
        total_bytes = []
        messages_exchanged = []
        summaries_exchanged = []
        nodes_encountered = []

        for state in self.data_handler.get_simulation_states(sim_id):
            steps.append(state.step)

            if state.step_metrics and isinstance(state.step_metrics, dict):
                metadata_bytes.append(state.step_metrics.get("metadata_bytes_sent", 0))
                payload_bytes.append(state.step_metrics.get("payload_bytes_sent", 0))
                total_bytes.append(
                    state.step_metrics.get("metadata_bytes_sent", 0)
                    + state.step_metrics.get("payload_bytes_sent", 0)
                )
                messages_exchanged.append(
                    state.step_metrics.get("messages_exchanged", 0)
                )
                summaries_exchanged.append(
                    state.step_metrics.get("summaries_exchanged", 0)
                )
                nodes_encountered.append(state.step_metrics.get("nodes_encountered", 0))
            else:
                metadata_bytes.append(0)
                payload_bytes.append(0)
                total_bytes.append(0)
                messages_exchanged.append(0)
                summaries_exchanged.append(0)
                nodes_encountered.append(0)

        if not any(total_bytes):
            return

        # Bytes sent over time
        plt.figure(figsize=(10, 6))
        plt.plot(steps, metadata_bytes, "-r", label="Metadata Bytes")
        plt.plot(steps, payload_bytes, "-b", label="Payload Bytes")
        plt.plot(steps, total_bytes, "-g", label="Total Bytes")
        plt.title(f"Data Transmission Over Time - Simulation {sim_id}")
        plt.xlabel("Step")
        plt.ylabel("Bytes")
        plt.grid(True)
        plt.legend()
        plt.savefig(output_dir / "data_transmission.png")
        plt.close()

        # Cumulative bytes sent
        plt.figure(figsize=(10, 6))
        cum_metadata = np.cumsum(metadata_bytes)
        cum_payload = np.cumsum(payload_bytes)
        cum_total = np.cumsum(total_bytes)

        plt.plot(steps, cum_metadata, "-r", label="Cumulative Metadata Bytes")
        plt.plot(steps, cum_payload, "-b", label="Cumulative Payload Bytes")
        plt.plot(steps, cum_total, "-g", label="Cumulative Total Bytes")
        plt.title(f"Cumulative Data Transmission - Simulation {sim_id}")
        plt.xlabel("Step")
        plt.ylabel("Bytes")
        plt.grid(True)
        plt.legend()
        plt.savefig(output_dir / "cumulative_data_transmission.png")
        plt.close()

        # Data exchange metrics
        plt.figure(figsize=(10, 6))
        plt.plot(steps, messages_exchanged, "-b", label="Messages Exchanged")
        plt.plot(steps, summaries_exchanged, "-r", label="Summaries Exchanged")
        plt.title(f"Message Exchange Metrics - Simulation {sim_id}")
        plt.xlabel("Step")
        plt.ylabel("Count")
        plt.grid(True)
        plt.legend()
        plt.savefig(output_dir / "message_exchange_metrics.png")
        plt.close()

        # Nodes encountered vs data sent
        if any(nodes_encountered):
            plt.figure(figsize=(10, 6))
            plt.scatter(nodes_encountered, total_bytes)
            plt.title(f"Nodes Encountered vs Data Sent - Simulation {sim_id}")
            plt.xlabel("Nodes Encountered")
            plt.ylabel("Total Bytes Sent")
            plt.grid(True)
            plt.savefig(output_dir / "nodes_vs_data.png")
            plt.close()

    def _generate_phase_data_graphs(self, sim_id: str, output_dir: Path):
        steps = []
        pre_collision_bytes = []
        pre_collision_count = []
        message_exchange_bytes = []
        message_exchange_count = []
        has_phase_data = False

        for state in self.data_handler.get_simulation_states(sim_id):
            steps.append(state.step)

            phase_data = (
                state.step_metrics.get("phase_data", {}) if state.step_metrics else {}
            )
            if phase_data:
                has_phase_data = True

            pre_coll = phase_data.get("pre_collision", {})
            pre_collision_bytes.append(pre_coll.get("bytes", 0))
            pre_collision_count.append(pre_coll.get("count", 0))

            msg_exch = phase_data.get("message_exchange", {})
            message_exchange_bytes.append(msg_exch.get("bytes", 0))
            message_exchange_count.append(msg_exch.get("count", 0))

        if not has_phase_data:
            return

        # Bytes by phase
        plt.figure(figsize=(10, 6))
        plt.plot(steps, pre_collision_bytes, "-r", label="Pre-Collision Phase")
        plt.plot(steps, message_exchange_bytes, "-b", label="Message Exchange Phase")
        plt.title(f"Data Transmission by Phase - Simulation {sim_id}")
        plt.xlabel("Step")
        plt.ylabel("Bytes")
        plt.grid(True)
        plt.legend()
        plt.savefig(output_dir / "phase_data_bytes.png")
        plt.close()

        # Counts by phase
        plt.figure(figsize=(10, 6))
        plt.plot(steps, pre_collision_count, "-r", label="Pre-Collision Events")
        plt.plot(steps, message_exchange_count, "-b", label="Message Exchange Events")
        plt.title(f"Events by Phase - Simulation {sim_id}")
        plt.xlabel("Step")
        plt.ylabel("Count")
        plt.grid(True)
        plt.legend()
        plt.savefig(output_dir / "phase_event_counts.png")
        plt.close()

    def _generate_unique_message_graphs(self, sim_id: str, output_dir: Path):
        metrics = self._extract_unique_message_metrics(sim_id)
        if not metrics:
            return

        steps = [m["step"] for m in metrics]
        total_unique = [m["total_unique_messages"] for m in metrics]
        unique_successes = [m["total_unique_successes"] for m in metrics]
        success_rates = [m["unique_success_rate"] for m in metrics]
        new_messages = [m["new_unique_messages"] for m in metrics]
        new_successes = [m["new_unique_successes"] for m in metrics]

        # Unique message counts
        plt.figure(figsize=(10, 6))
        plt.plot(steps, total_unique, "-b", label="Total Unique Messages")
        plt.plot(steps, unique_successes, "-g", label="Unique Successful Messages")
        plt.title(f"Unique Message Tracking - Simulation {sim_id}")
        plt.xlabel("Step")
        plt.ylabel("Number of Unique Messages")
        plt.grid(True)
        plt.legend()
        plt.savefig(output_dir / "unique_message_counts.png")
        plt.close()

        # Unique message success rate
        plt.figure(figsize=(10, 6))
        plt.plot(steps, success_rates, "-g")
        plt.title(f"Unique Message Success Rate - Simulation {sim_id}")
        plt.xlabel("Step")
        plt.ylabel("Success Rate (%)")
        plt.grid(True)
        plt.savefig(output_dir / "unique_success_rate.png")
        plt.close()

        # New unique messages per step
        plt.figure(figsize=(10, 6))
        plt.plot(steps, new_messages, "-b", label="New Unique Messages")
        plt.plot(steps, new_successes, "-g", label="New Unique Successes")
        plt.title(f"New Unique Messages Per Step - Simulation {sim_id}")
        plt.xlabel("Step")
        plt.ylabel("Count")
        plt.grid(True)
        plt.legend()
        plt.savefig(output_dir / "new_unique_messages.png")
        plt.close()

    def _generate_aggregated_graphs(self, sim_ids: Set[str]):
        graphs_dir = self.session.session_dir / "aggregated_graphs"
        graphs_dir.mkdir(exist_ok=True)

        # Get max steps across simulations
        max_steps = 0
        for sim_id in sim_ids:
            metadata = self.data_handler._simulation_metadata.get(sim_id, {})
            max_step = metadata.get("max_step", 0)
            max_steps = max(max_steps, max_step + 1)  # +1 since steps are 0-indexed

        # Prepare data arrays
        sim_count = len(sim_ids)
        message_counts = np.zeros((sim_count, max_steps))
        success_counts = np.zeros((sim_count, max_steps))
        success_rates = np.zeros((sim_count, max_steps))
        metadata_bytes = np.zeros((sim_count, max_steps))
        payload_bytes = np.zeros((sim_count, max_steps))
        total_bytes = np.zeros((sim_count, max_steps))
        messages_exchanged = np.zeros((sim_count, max_steps))
        summaries_exchanged = np.zeros((sim_count, max_steps))
        all_delivery_times = []

        # Collect data from each simulation
        for i, sim_id in enumerate(sim_ids):
            for state in self.data_handler.get_simulation_states(sim_id):
                step = state.step

                # Message counts and rates
                message_counts[i, step] = len(state.messages)
                success_counts[i, step] = len(state.success_messages)
                success_rates[i, step] = (
                    (len(state.success_messages) / len(state.messages) * 100)
                    if state.messages
                    else 0
                )

                # Delivery times
                for msg in state.success_messages:
                    all_delivery_times.append(state.step - msg.created_time)

                # Data transmission metrics
                if state.step_metrics:
                    metadata_bytes[i, step] = state.step_metrics.get(
                        "metadata_bytes_sent", 0
                    )
                    payload_bytes[i, step] = state.step_metrics.get(
                        "payload_bytes_sent", 0
                    )
                    total_bytes[i, step] = (
                        metadata_bytes[i, step] + payload_bytes[i, step]
                    )
                    messages_exchanged[i, step] = state.step_metrics.get(
                        "messages_exchanged", 0
                    )
                    summaries_exchanged[i, step] = state.step_metrics.get(
                        "summaries_exchanged", 0
                    )

        steps = range(max_steps)

        # Average success rate with confidence interval
        plt.figure(figsize=(10, 6))
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

        # Generate data transmission graphs
        self._generate_aggregated_transmission_graphs(
            graphs_dir,
            max_steps,
            metadata_bytes,
            payload_bytes,
            total_bytes,
            messages_exchanged,
            summaries_exchanged,
        )

    def _generate_aggregated_transmission_graphs(
        self,
        graphs_dir: Path,
        max_steps: int,
        metadata_bytes: np.ndarray,
        payload_bytes: np.ndarray,
        total_bytes: np.ndarray,
        messages_exchanged: np.ndarray,
        summaries_exchanged: np.ndarray,
    ):
        steps = range(max_steps)

        # Average bytes sent with confidence intervals
        plt.figure(figsize=(10, 6))
        mean_metadata = np.mean(metadata_bytes, axis=0)
        std_metadata = np.std(metadata_bytes, axis=0)
        mean_payload = np.mean(payload_bytes, axis=0)
        std_payload = np.std(payload_bytes, axis=0)
        mean_total = np.mean(total_bytes, axis=0)
        std_total = np.std(total_bytes, axis=0)

        plt.plot(steps, mean_metadata, "-r", label="Mean Metadata Bytes")
        plt.fill_between(
            steps,
            mean_metadata - std_metadata,
            mean_metadata + std_metadata,
            alpha=0.2,
            color="r",
        )
        plt.plot(steps, mean_payload, "-b", label="Mean Payload Bytes")
        plt.fill_between(
            steps,
            mean_payload - std_payload,
            mean_payload + std_payload,
            alpha=0.2,
            color="b",
        )
        plt.plot(steps, mean_total, "-g", label="Mean Total Bytes")
        plt.fill_between(
            steps, mean_total - std_total, mean_total + std_total, alpha=0.2, color="g"
        )
        plt.title("Average Data Transmission Across All Simulations")
        plt.xlabel("Step")
        plt.ylabel("Bytes")
        plt.grid(True)
        plt.legend()
        plt.savefig(graphs_dir / "average_data_transmission.png")
        plt.close()

        # Cumulative average bytes sent
        plt.figure(figsize=(10, 6))
        cum_mean_metadata = np.cumsum(mean_metadata)
        cum_mean_payload = np.cumsum(mean_payload)
        cum_mean_total = np.cumsum(mean_total)

        plt.plot(steps, cum_mean_metadata, "-r", label="Cumulative Metadata Bytes")
        plt.plot(steps, cum_mean_payload, "-b", label="Cumulative Payload Bytes")
        plt.plot(steps, cum_mean_total, "-g", label="Cumulative Total Bytes")
        plt.title("Average Cumulative Data Transmission Across All Simulations")
        plt.xlabel("Step")
        plt.ylabel("Bytes")
        plt.grid(True)
        plt.legend()
        plt.savefig(graphs_dir / "average_cumulative_data.png")
        plt.close()

        # Average message exchange metrics
        plt.figure(figsize=(10, 6))
        mean_messages = np.mean(messages_exchanged, axis=0)
        std_messages = np.std(messages_exchanged, axis=0)
        mean_summaries = np.mean(summaries_exchanged, axis=0)
        std_summaries = np.std(summaries_exchanged, axis=0)

        plt.plot(steps, mean_messages, "-b", label="Mean Messages Exchanged")
        plt.fill_between(
            steps,
            mean_messages - std_messages,
            mean_messages + std_messages,
            alpha=0.2,
            color="b",
        )
        plt.plot(steps, mean_summaries, "-r", label="Mean Summaries Exchanged")
        plt.fill_between(
            steps,
            mean_summaries - std_summaries,
            mean_summaries + std_summaries,
            alpha=0.2,
            color="r",
        )
        plt.title("Average Message Exchange Metrics Across All Simulations")
        plt.xlabel("Step")
        plt.ylabel("Count")
        plt.grid(True)
        plt.legend()
        plt.savefig(graphs_dir / "average_message_exchange.png")
        plt.close()

        # Average bytes per message
        plt.figure(figsize=(10, 6))
        bytes_per_message = np.zeros_like(mean_total)
        for i in range(len(mean_total)):
            if mean_messages[i] > 0:
                bytes_per_message[i] = mean_total[i] / mean_messages[i]

        plt.plot(steps, bytes_per_message, "-g")
        plt.title("Average Bytes per Message Across All Simulations")
        plt.xlabel("Step")
        plt.ylabel("Bytes per Message")
        plt.grid(True)
        plt.savefig(graphs_dir / "average_bytes_per_message.png")
        plt.close()

        # Metadata to payload ratio
        plt.figure(figsize=(10, 6))
        metadata_ratio = np.zeros_like(mean_total)
        for i in range(len(mean_total)):
            if mean_total[i] > 0:
                metadata_ratio[i] = (mean_metadata[i] / mean_total[i]) * 100

        plt.plot(steps, metadata_ratio, "-r")
        plt.title("Average Metadata to Total Bytes Ratio Across All Simulations")
        plt.xlabel("Step")
        plt.ylabel("Metadata Percentage of Total (%)")
        plt.grid(True)
        plt.savefig(graphs_dir / "average_metadata_ratio.png")
        plt.close()

    def _generate_aggregated_unique_message_graphs(self, sim_ids: Set[str]):
        graphs_dir = self.session.session_dir / "aggregated_graphs"
        graphs_dir.mkdir(exist_ok=True)

        all_sim_metrics = []
        for sim_id in sim_ids:
            metrics = self._extract_unique_message_metrics(sim_id)
            if metrics:
                all_sim_metrics.append(metrics)

        if not all_sim_metrics:
            return

        max_steps = max(len(metrics) for metrics in all_sim_metrics)
        sim_count = len(all_sim_metrics)

        unique_messages = np.zeros((sim_count, max_steps))
        unique_successes = np.zeros((sim_count, max_steps))
        unique_success_rates = np.zeros((sim_count, max_steps))

        for i, metrics in enumerate(all_sim_metrics):
            for j, m in enumerate(metrics):
                unique_messages[i, j] = m["total_unique_messages"]
                unique_successes[i, j] = m["total_unique_successes"]
                unique_success_rates[i, j] = m["unique_success_rate"]

        steps = range(max_steps)

        # Plot average unique message counts
        plt.figure(figsize=(10, 6))
        mean_unique = np.mean(unique_messages, axis=0)
        std_unique = np.std(unique_messages, axis=0)
        mean_successes = np.mean(unique_successes, axis=0)
        std_successes = np.std(unique_successes, axis=0)

        plt.plot(steps, mean_unique, "-b", label="Mean Unique Messages")
        plt.fill_between(
            steps,
            mean_unique - std_unique,
            mean_unique + std_unique,
            alpha=0.2,
            color="b",
        )
        plt.plot(steps, mean_successes, "-g", label="Mean Unique Successes")
        plt.fill_between(
            steps,
            mean_successes - std_successes,
            mean_successes + std_successes,
            alpha=0.2,
            color="g",
        )
        plt.title("Average Unique Message Counts Across All Simulations")
        plt.xlabel("Step")
        plt.ylabel("Number of Unique Messages")
        plt.grid(True)
        plt.legend()
        plt.savefig(graphs_dir / "average_unique_messages.png")
        plt.close()

        # Plot average unique success rate
        plt.figure(figsize=(10, 6))
        mean_rates = np.mean(unique_success_rates, axis=0)
        std_rates = np.std(unique_success_rates, axis=0)

        plt.plot(steps, mean_rates, "-g", label="Mean Unique Success Rate")
        plt.fill_between(
            steps, mean_rates - std_rates, mean_rates + std_rates, alpha=0.2, color="g"
        )
        plt.title("Average Unique Message Success Rate Across All Simulations")
        plt.xlabel("Step")
        plt.ylabel("Success Rate (%)")
        plt.grid(True)
        plt.legend()
        plt.savefig(graphs_dir / "average_unique_success_rate.png")
        plt.close()
