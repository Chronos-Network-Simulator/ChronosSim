import multiprocessing as mp
import pickle
from dataclasses import dataclass
from enum import Enum
from pprint import pprint
from queue import Empty
from typing import Dict

from kivy.clock import Clock
from kivy.clock import ClockEvent
from pubsub import pub

from exception.exception import ConfigError
from model.grid.BaseSimulationGrid import BaseSimulationGrid
from model.message.BaseMessage import BaseMessage
from model.message_spawner.base_message_spawner import BaseMessageSpawner
from model.monitoring.SimulationDataHandler import SimulationDataHandler
from model.monitoring.SimulationSession import SimulationProperties
from model.node import BaseNode
from model.simulation.simulation_worker import SimulationWorker
from model.targets.BaseTargetSpawner import BaseTargetSpawner


class SimulationState(Enum):
    Empty = "empty"
    RUNNING = "running"
    PAUSED = "paused"


@dataclass
class SimulationControl:
    command: str
    data: dict = None


@dataclass
class SimulationEntry:
    worker: SimulationWorker
    current_step: int
    process: mp.Process


class SimulationManager:
    status: SimulationState = SimulationState.Empty
    """
    The status of the simulation
    """
    step_count: int = 1
    """
    The number of steps the simulation should run for
    """
    num_workers: int = mp.cpu_count()
    """
    Number of workers to use to run the simulation. Defaults to the numbers
    of threads on your machine.
    """
    num_simulations: int = 1
    """
    Number of concurrent simulations to run at once. Use this property to remove
    bias and variance by averaging results from multiple simulations.
    """
    step_delay: int = 1
    """
    The amount of delay in seconds between each step. Defaults to 0 i.e. no delay.
    """
    simulations: Dict[str, SimulationEntry] = {}
    """
    List of all the active simulations
    """
    grid: BaseSimulationGrid | None
    """
    The configured grid implementation to use for the simulation.
    """
    node: BaseNode | None
    """
    The configured node implementation to use for the simulation.
    """
    message_template: BaseMessage | None = BaseMessage(
        original_content="Demo Message", creator_id="0", created_time=0
    )
    """
    Message template to be used to render the messages in the simulation.
    """
    message_spawner: BaseMessageSpawner | None = None
    """
    The configured message spawner to use for the simulation.
    """

    target_spawner: BaseTargetSpawner | None = None
    """
    The configured target spawner to use for the simulation.
    """

    data_handler: SimulationDataHandler = SimulationDataHandler()
    """
    The Data handler is the core of the simulations data tracking. It creates simulation sessions,
    stores raw simulation state and other processed state to folders and retains optimized in
    memory caches for other components to read from.
    """

    _collector_event: ClockEvent | None = None
    """
    Internal reference to the Kivy Clock event for collecting results.
    """

    _control_queue: mp.Queue
    """
    Multiprocessing queue for sending control commands to simulation workers.
    """

    _results_queue: mp.Queue
    """
    Multiprocessing queue for receiving results from simulation workers.
    """

    _node_count: int = 1
    """
    Internal variable to store the number of nodes in teh simulation. Use the 
    property instead of this value.
    """

    @property
    def node_count(self) -> int:
        return self._node_count

    @node_count.setter
    def node_count(self, value: int) -> None:
        if value < 0:
            raise ConfigError("Node count must be a positive integer")
        self._node_count = value
        self._update_ui()

    def __init__(self):
        self.clear_simulation()

    def clear_simulation(self):
        self._control_queue = mp.Queue()
        self._results_queue = mp.Queue()
        self.simulations = {}
        self.status = SimulationState.Empty
        self._collector_event = None

    def reset_user_configs(self) -> None:
        """
        Resets the user configurable options back to their defaults
        """
        self.set_grid(None)
        self.set_node(None)
        self.set_message_spawner(None)
        self.set_target_spawner(None)
        self.node_count = 1
        self.step_count = 1

    def _update_ui(self) -> None:
        """
        Updates the UI pre-simulation run(i.e. simulation state is empty). This is used
        to visualize the grid and nodes before the simulation starts.
        The grid will automatically render without the need of this function. However,
        nodes and message spawning will need to be updated.
        :return: None
        """

        if self.grid is not None and self.node:
            self.grid.clear_grid()
            self.grid.auto_place_nodes(self.node_count, self.node)
            if self.target_spawner:
                self.grid.nodes = self.target_spawner.mark_targets(self.grid.nodes)
            pub.sendMessage("simulation.grid_updated")
        if (
            self.grid
            and self.node
            and self.message_template
            and self.message_spawner
            and self.target_spawner
        ):
            self.message_spawner.init_spawn_messages(
                self.grid.nodes, self.message_template
            )

    def _ensure_editable(self) -> None:
        if self.status == "running":
            raise ConfigError("Cannot modify simulation while it is running")
        elif self.status == "paused":
            raise ConfigError("Stop the simulation before making changes")

    def set_grid(self, grid: BaseSimulationGrid | None) -> None:
        self._ensure_editable()
        self.grid = grid
        self._update_ui()
        pub.sendMessage("simulation.grid_type_changed", grid=grid)

    def set_node(self, node: BaseNode | None) -> None:
        self._ensure_editable()
        self.node = node
        self._update_ui()
        pub.sendMessage("simulation.node_changed", node=node)

    def set_message_spawner(self, message_spawner: BaseMessageSpawner | None) -> None:
        self._ensure_editable()
        self.message_spawner = message_spawner
        pub.sendMessage(
            "simulation.message_spawner_changed", message_spawner=message_spawner
        )

    def set_target_spawner(self, target_spawner: BaseTargetSpawner | None) -> None:
        self._ensure_editable()
        self.target_spawner = target_spawner
        self._update_ui()
        pub.sendMessage(
            "simulation.target_spawner_changed", target_spawner=target_spawner
        )

    def create_simulations(self) -> None:
        """Create multiple identical simulation instances."""
        if self.grid and self.node and self.message_spawner:
            if self.status == SimulationState.Empty:
                for _ in range(self.num_simulations):
                    worker = SimulationWorker(
                        pickled_node_type=pickle.dumps(self.node),
                        pickled_grid_type=pickle.dumps(self.grid),
                        pickled_message_spawner=pickle.dumps(self.message_spawner),
                        pickled_message_template=pickle.dumps(self.message_template),
                        node_count=self.node_count,
                        step_count=self.step_count,
                        control_queue=self._control_queue,
                        results_queue=self._results_queue,
                        step_delay=self.step_delay,
                    )
                    sim_id = worker.simulation_id
                    process = mp.Process(
                        target=worker.simulate, name=f"Chronos-Sim-{sim_id}"
                    )
                    self.simulations[sim_id] = SimulationEntry(
                        worker=worker, current_step=0, process=process
                    )
                # create the simulation session in the data handler
                self.data_handler.create_session(
                    simulation_properties=SimulationProperties(
                        simulation_count=self.num_simulations,
                        steps=self.step_count,
                        workers=self.num_workers,
                        simulation_delay=self.step_delay,
                        grid_type=self.grid.__class__.__name__,
                        grid_length=self.grid.length,
                        grid_width=self.grid.width,
                        region_size=self.grid.region_size,
                        node_type=self.node.__class__.__name__,
                        node_count=self.node_count,
                        detection_range=self.node.detection_range,
                        movement_range=self.node.movement_range,
                        message_text=self.message_template.original_content,
                        message_size=self.message_template.size,
                        message_spawner_type=self.message_spawner.__class__.__name__,
                        spawn_frequency=self.message_spawner.spawn_rate_frequency,
                        spawn_frequency_variation=self.message_spawner.spawn_rate_frequency_variance,
                        spawn_rate=self.message_spawner.spawn_rate,
                        spawn_rate_variation=self.message_spawner.spawn_rate_variance,
                        random_seed=self.message_spawner.random_seed,
                    )
                )
            elif self.status == SimulationState.PAUSED:
                pass
            else:
                raise ConfigError("Simulation is already running")
        else:
            raise ConfigError("Grid, Node, and Message Spawner must be set")

    def play(self):
        """Start or resume all simulations."""
        if self.status in [SimulationState.PAUSED, SimulationState.Empty]:
            # Start each simulation process if not already running
            if self.status == SimulationState.Empty:
                for sim in self.simulations.values():
                    if not sim.process.is_alive():
                        sim.process.start()
            self._control_queue.put(SimulationControl(command="resume"))
            self.status = SimulationState.RUNNING
            self._start_results_collector()
        else:
            raise ConfigError("Simulation is already running")

    def pause(self):
        """Pause all simulations."""
        if self.status == SimulationState.RUNNING:
            self._control_queue.put(SimulationControl(command="pause"))
            self.status = SimulationState.PAUSED
            pub.sendMessage("simulation.state_changed", state=self.status)

            # Cancel the collector when paused
            if self._collector_event:
                self._collector_event.cancel()
                self._collector_event = None
        else:
            raise ConfigError("Simulation is not running")

    def stop(self):
        """Stop all simulations."""
        self._control_queue.put(SimulationControl(command="stop"))
        for sim_id, sim in list(self.simulations.items()):
            if sim.process.is_alive():  # Check if process is still running
                sim.process.join(5)  # wait for 5 seconds to gracefully stop
                if sim.process.is_alive():
                    sim.process.terminate()  # Force terminate if still running

        # Cancel the collector when stopped
        if self._collector_event:
            self._collector_event.cancel()
            self._collector_event = None

        self.status = SimulationState.Empty
        self.clear_simulation()
        pub.sendMessage("simulation.state_changed", state=self.status)

    def step(self):
        """Execute a single step for all simulations."""
        if self.status in [SimulationState.Empty, SimulationState.PAUSED]:
            processes = []
            for sim_id, sim in self.simulations.items():
                process = mp.Process(
                    target=self._execute_single_step,
                    args=(sim.worker,),
                    name=f"Chronos-Sim-Step-{sim_id}",
                )
                process.start()
                processes.append(process)
                sim.current_step += 1

            # Wait for all processes to complete
            for process in processes:
                process.join()

            # Collect results immediately for step execution
            self._collect_immediate_results()
            self.clear_simulation()
        else:
            raise ConfigError("Simulation is not paused")

    def _execute_single_step(self, worker):
        """Execute a single simulation step."""
        worker._simulate_step()
        worker.capture_state()
        for node in worker.grid.nodes:
            node.on_simulation_step_end()
            node.move()
        # Send results through queue
        result = worker._get_current_state()
        self._results_queue.put(result)

    def _collect_results(self, dt):
        """Collect results method for Kivy Clock scheduler."""
        if self.status != SimulationState.RUNNING:
            # Cancel the scheduled event if simulation is not running
            if self._collector_event:
                self._collector_event.cancel()
                self._collector_event = None
            return False

        try:
            while not self._results_queue.empty():
                result = self._results_queue.get_nowait()
                if result:
                    sim_id = result.get("simulation_id")
                    if sim_id:
                        pub.sendMessage(
                            "simulation.result_updated",
                            simulation_id=sim_id,
                            result=result,
                        )
                        state = self.data_handler.process_simulation_state(result)
        except Empty:
            pass
        return True

    def _collect_immediate_results(self):
        """Collect results immediately without scheduling."""
        while not self._results_queue.empty():
            try:
                result = self._results_queue.get_nowait()
                if result:
                    sim_id = result.get("simulation_id")
                    if sim_id:
                        pub.sendMessage(
                            "simulation.result_updated",
                            simulation_id=sim_id,
                            result=result,
                        )
                        pprint(result)
            except Empty:
                break

    def _start_results_collector(self):
        """Start the Kivy Clock scheduler for collecting results."""
        if self._collector_event:
            self._collector_event.cancel()

        # Schedule the collector to run every 1/30th of a second (adjust as needed)
        self._collector_event = Clock.schedule_interval(self._collect_results, 0.5)
