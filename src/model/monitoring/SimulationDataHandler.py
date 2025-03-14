from collections import defaultdict
from pathlib import Path
from threading import Lock
from typing import Dict, Optional, Iterator, Set
import json
import gc  # For explicit garbage collection

from pubsub import pub
from model.monitoring.DataTypes import SimulationState, DataclassJSONEncoder
from model.monitoring.SimulationSession import SimulationSession, SimulationProperties


class SimulationDataHandler:
    def __init__(self, base_output_dir: str = "outputs"):
        self.base_output_dir = Path(base_output_dir)
        self.base_output_dir.mkdir(parents=True, exist_ok=True)
        self.current_session: Optional[SimulationSession] = None
        self._simulation_metadata: Dict[str, Dict] = defaultdict(dict)
        self.write_lock = Lock()
        self._cached_steps: Dict[str, Set[int]] = defaultdict(set)
        self._graph_generator = None  # Lazy load when needed

    @property
    def graph_generator(self):
        """Lazy load the graph generator only when needed"""
        from model.monitoring.SimulationGraphGenerator import SimulationGraphGenerator

        if self._graph_generator is None:
            self._graph_generator = SimulationGraphGenerator(self)
        return self._graph_generator

    def create_session(
        self, simulation_properties: SimulationProperties
    ) -> SimulationSession:
        """
        Creates a new simulation session. Each session can contain multiple simulations,
        each with their own directory for raw states and graphs.
        """
        self.current_session = SimulationSession(
            self.base_output_dir, properties=simulation_properties
        )
        # Clear any cached state information
        self._simulation_metadata.clear()
        self._cached_steps.clear()
        return self.current_session

    def load_session(self, session_id: str) -> Optional[SimulationSession]:
        """
        Loads an existing session by ID.
        Returns None if session doesn't exist.
        """
        session_dir = self.base_output_dir / session_id
        if not session_dir.exists():
            return None
        self.current_session = SimulationSession(self.base_output_dir, session_id)
        # Discover existing simulation IDs and steps
        for sim_dir in session_dir.glob("simulation_*"):
            sim_id = sim_dir.name
            # Just store step numbers, not actual state data
            self._cached_steps[sim_id] = {
                int(f.stem.split("_")[1]) for f in sim_dir.glob("step_*.json")
            }

            # Optionally load basic metadata about each simulation
            if self._cached_steps[sim_id]:
                max_step = max(self._cached_steps[sim_id])
                self._simulation_metadata[sim_id] = {
                    "max_step": max_step,
                    "total_states": len(self._cached_steps[sim_id]),
                }

        return self.current_session

    def process_simulation_state(self, state_data: dict) -> SimulationState:
        """
        Process incoming simulation state and write to disk.
        Ensures a session exists before processing.
        """
        state = SimulationState.__json_decode__(state_data)
        sim_id = state.simulation_id

        # Update metadata instead of storing the full state
        self._update_simulation_metadata(state)
        self._cached_steps[sim_id].add(state.step)

        # Write to disk immediately
        self._write_state_to_disk(state)

        # Notify subscribers
        pub.sendMessage(
            "simulation.state_updated",
            simulation_id=sim_id,
        )
        state_to_return = state
        del state
        gc.collect()  # Encourage garbage collection

        return state_to_return

    def _update_simulation_metadata(self, state: SimulationState):
        """Update minimal metadata about the simulation state"""
        sim_id = state.simulation_id
        metadata = self._simulation_metadata[sim_id]

        # Update basic stats
        metadata["latest_step"] = state.step
        max_step = metadata.get("max_step", 0)
        if state.step > max_step:
            metadata["max_step"] = state.step

        # Track count
        if "total_states" not in metadata:
            metadata["total_states"] = 0
        metadata["total_states"] = len(self._cached_steps[sim_id])

    def _write_state_to_disk(self, state: SimulationState):
        """Write simulation state to JSON file within the current session."""
        if not self.current_session:
            raise RuntimeError("No active session found")

        with self.write_lock:
            sim_dir = self.current_session.get_simulation_dir(state.simulation_id)
            file_path = sim_dir / f"step_{state.step}.json"
            with open(file_path, "w") as f:
                json.dump(state, f, cls=DataclassJSONEncoder)

    # Iterator-based access to simulation states
    def get_simulation_states(self, sim_id: str) -> Iterator[SimulationState]:
        """
        Generator that yields states for a simulation one at a time,
        reading from disk as needed instead of storing all in memory.
        """
        if not self.current_session:
            return

        sim_dir = self.current_session.get_simulation_dir(sim_id)
        if not sim_dir.exists():
            return

        # Iterate through steps in order
        steps = sorted(self._cached_steps.get(sim_id, set()))
        for step in steps:
            file_path = sim_dir / f"step_{step}.json"
            if file_path.exists():
                with open(file_path, "r") as f:
                    state_data = json.load(f)
                    yield SimulationState.__json_decode__(state_data)

                    # Help garbage collector
                    gc.collect()

    def get_state(self, sim_id: str, step: int) -> Optional[SimulationState]:
        """Get a specific simulation state by ID and step"""
        if not self.current_session:
            return None

        file_path = (
            self.current_session.get_simulation_dir(sim_id) / f"step_{step}.json"
        )
        if not file_path.exists():
            return None

        with open(file_path, "r") as f:
            state_data = json.load(f)
            return SimulationState.__json_decode__(state_data)

    def get_latest_state(self, sim_id: str) -> Optional[SimulationState]:
        """Get the latest state for a simulation"""
        if not self.current_session or sim_id not in self._simulation_metadata:
            return None

        latest_step = self._simulation_metadata[sim_id].get("latest_step")
        if latest_step is None:
            return None

        return self.get_state(sim_id, latest_step)
