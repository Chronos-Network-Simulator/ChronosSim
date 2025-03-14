import json
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional


@dataclass
class NodeState:
    id: str
    position: tuple
    message_count: int
    target: bool

    def __json_encode__(self) -> dict:
        return {
            "id": self.id,
            "position": list(self.position),
            "message_count": self.message_count,
            "target": self.target,
        }

    @classmethod
    def __json_decode__(cls, data: dict) -> "NodeState":
        return cls(
            id=data["id"],
            position=tuple(data["position"]),
            message_count=data["message_count"],
            target=data["target"],
        )


@dataclass
class Message:
    id: str
    content: str
    creator: str
    created_time: int
    hops: int

    def __json_encode__(self) -> dict:
        return {
            "id": self.id,
            "content": self.content,
            "creator": self.creator,
            "created_time": self.created_time,
            "hops": self.hops,
        }

    @classmethod
    def __json_decode__(cls, data: dict) -> "Message":
        return cls(
            id=data["id"],
            content=data["content"],
            creator=data["creator"],
            created_time=data["created_time"],
            hops=data["hops"],
        )


@dataclass
class SimulationStepMetrics:
    """Metrics collected during each simulation step"""

    metadata_bytes_sent: int = 0
    payload_bytes_sent: int = 0
    messages_exchanged: int = 0
    summaries_exchanged: int = 0
    nodes_encountered: int = 0
    phase_data: Dict = field(default_factory=dict)

    def __json_encode__(self) -> dict:
        return {
            "metadata_bytes_sent": self.metadata_bytes_sent,
            "payload_bytes_sent": self.payload_bytes_sent,
            "messages_exchanged": self.messages_exchanged,
            "summaries_exchanged": self.summaries_exchanged,
            "nodes_encountered": self.nodes_encountered,
            "phase_data": self.phase_data,
        }

    @classmethod
    def __json_decode__(cls, data: dict) -> "SimulationStepMetrics":
        return cls(
            metadata_bytes_sent=data["metadata_bytes_sent"],
            payload_bytes_sent=data["payload_bytes_sent"],
            messages_exchanged=data["messages_exchanged"],
            summaries_exchanged=data["summaries_exchanged"],
            nodes_encountered=data["nodes_encountered"],
            phase_data=data["phase_data"],
        )


@dataclass
class SimulationState:
    simulation_id: str
    step: int
    node_states: List[NodeState]
    messages: List[Message]
    status: str
    success_messages: List[Message]
    step_metrics: Optional[dict] = None  # Stores metric data about each step

    def __json_encode__(self) -> dict:
        return {
            "simulation_id": self.simulation_id,
            "step": self.step,
            "node_states": [node.__json_encode__() for node in self.node_states],
            "messages": [msg.__json_encode__() for msg in self.messages],
            "status": self.status,
            "timestamp": datetime.now().isoformat(),
            "success_messages": [
                msg.__json_encode__() for msg in self.success_messages
            ],
            "step_metrics": self.step_metrics,
        }

    @classmethod
    def __json_decode__(cls, data: dict) -> "SimulationState":
        return cls(
            simulation_id=data["simulation_id"],
            step=data["step"],
            node_states=[
                NodeState.__json_decode__(node) for node in data["node_states"]
            ],
            messages=[Message.__json_decode__(msg) for msg in data["messages"]],
            status=data["status"],
            success_messages=[
                Message.__json_decode__(msg) for msg in data["success_messages"]
            ],
            step_metrics=data["step_metrics"],
        )


class DataclassJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if hasattr(o, "__json_encode__"):
            return o.__json_encode__()
        return super().default(o)


def dataclass_json_decode(cls, json_data):
    if hasattr(cls, "__json_decode__"):
        return cls.__json_decode__(json_data)
    return json_data
