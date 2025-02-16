import json
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict
from typing import Optional


@dataclass
class SimulationProperties:
    simulation_count: int
    steps: int
    workers: int
    simulation_delay: int
    grid_type: str
    grid_length: int
    grid_width: int
    region_size: int
    node_type: str
    node_count: int
    detection_range: float
    movement_range: float
    message_text: str
    message_size: int
    message_spawner_type: str
    spawn_frequency: int
    spawn_frequency_variation: int
    spawn_rate: float
    spawn_rate_variation: float
    random_seed: int


def convert_simulation_properties_to_nested_json(
    properties: SimulationProperties,
) -> Dict:
    """
    Converts SimulationProperties into a nested JSON structure with logically grouped parameters.

    Args:
        properties: SimulationProperties dataclass instance

    Returns:
        Dict with nested structure grouping related parameters
    """
    # Convert dataclass to dictionary first
    flat_dict = asdict(properties)

    return {
        "simulation_meta": {
            "id": "",
            "count": flat_dict["simulation_count"],
            "steps": flat_dict["steps"],
            "workers": flat_dict["workers"],
            "delay": flat_dict["simulation_delay"],
            "random_seed": flat_dict["random_seed"],
        },
        "grid_configuration": {
            "type": flat_dict["grid_type"],
            "dimensions": {
                "length": flat_dict["grid_length"],
                "width": flat_dict["grid_width"],
                "region_size": flat_dict["region_size"],
            },
        },
        "node_configuration": {
            "type": flat_dict["node_type"],
            "count": flat_dict["node_count"],
            "ranges": {
                "detection": flat_dict["detection_range"],
                "movement": flat_dict["movement_range"],
            },
        },
        "message_configuration": {
            "content": {
                "text": flat_dict["message_text"],
                "size": flat_dict["message_size"],
            },
            "spawning": {
                "type": flat_dict["message_spawner_type"],
                "frequency": {
                    "base": flat_dict["spawn_frequency"],
                    "variation": flat_dict["spawn_frequency_variation"],
                },
                "rate": {
                    "base": flat_dict["spawn_rate"],
                    "variation": flat_dict["spawn_rate_variation"],
                },
            },
        },
    }


class SimulationSession:
    """
    Represents a simulation session that can contain multiple simulations.
    Each session has its own directory with simulation data and graphs.
    """

    def __init__(
        self,
        base_dir: Path,
        session_id: Optional[str] = None,
        properties: Optional[SimulationProperties] = None,
    ):
        self.session_id = session_id or datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.session_dir = base_dir / self.session_id
        self.session_dir.mkdir(parents=True, exist_ok=True)
        if properties:
            props = convert_simulation_properties_to_nested_json(properties)
            props["simulation_meta"]["id"] = self.session_id
            config_path = self.session_dir / "config.json"
            with open(config_path, "w") as f:
                json.dump(
                    props,
                    f,
                    indent=4,  # Makes it readable
                )
        self.simulation_dirs: Dict[str, Path] = {}

    def get_simulation_dir(self, simulation_id: str) -> Path:
        """Get or create a directory for a specific simulation in this session."""
        if simulation_id not in self.simulation_dirs:
            sim_dir = self.session_dir / simulation_id
            sim_dir.mkdir(exist_ok=True)
            self.simulation_dirs[simulation_id] = sim_dir
        return self.simulation_dirs[simulation_id]

    def get_graphs_dir(self, simulation_id: str) -> Path:
        """Get or create a graphs directory for a specific simulation."""
        sim_dir = self.get_simulation_dir(simulation_id)
        graphs_dir = sim_dir / "graphs"
        graphs_dir.mkdir(exist_ok=True)
        return graphs_dir
