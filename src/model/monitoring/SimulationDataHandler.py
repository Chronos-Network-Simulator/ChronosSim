import json
from collections import defaultdict
from pathlib import Path
from threading import Lock
from typing import Dict, List, Optional

from pubsub import pub

from model.monitoring.DataTypes import SimulationState, DataclassJSONEncoder
from model.monitoring.SimulationGraphGenerator import SimulationGraphGenerator
from model.monitoring.SimulationSession import SimulationSession, SimulationProperties


class SimulationDataHandler:

    graph_generator: "SimulationGraphGenerator" = None

    def __init__(self, base_output_dir: str = "outputs"):
        self.base_output_dir = Path(base_output_dir)
        self.base_output_dir.mkdir(parents=True, exist_ok=True)
        self.current_session: Optional[SimulationSession] = None
        self.simulations: Dict[str, List[SimulationState]] = defaultdict(list)
        self.write_lock = Lock()
        self.message_count_cache = {}

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
        self.graph_generator = SimulationGraphGenerator(self)
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
        return self.current_session

    def process_simulation_state(self, state_data: dict) -> SimulationState:
        """
        Process incoming simulation state and write to disk.
        Ensures a session exists before processing.
        """
        state = SimulationState.__json_decode__(state_data)
        self.simulations[state.simulation_id].append(state)
        self._write_state_to_disk(state)

        pub.sendMessage(
            "simulation.state_updated",
            simulation_id=state.simulation_id,
        )

        return state

    def _write_state_to_disk(self, state: SimulationState):
        """Write simulation state to JSON file within the current session."""
        if not self.current_session:
            raise RuntimeError("No active session found")

        with self.write_lock:
            sim_dir = self.current_session.get_simulation_dir(state.simulation_id)
            file_path = sim_dir / f"step_{state.step}.json"

            with open(file_path, "w") as f:
                json.dump(state, f, cls=DataclassJSONEncoder)
