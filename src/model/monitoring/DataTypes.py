import json
from dataclasses import dataclass
from datetime import datetime
from typing import List


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
    content: str
    creator: str
    created_time: int
    hops: int

    def __json_encode__(self) -> dict:
        return {
            "content": self.content,
            "creator": self.creator,
            "created_time": self.created_time,
            "hops": self.hops,
        }

    @classmethod
    def __json_decode__(cls, data: dict) -> "Message":
        return cls(
            content=data["content"],
            creator=data["creator"],
            created_time=data["created_time"],
            hops=data["hops"],
        )


@dataclass
class SimulationState:
    simulation_id: str
    step: int
    node_states: List[NodeState]
    messages: List[Message]
    status: str

    def __json_encode__(self) -> dict:
        return {
            "simulation_id": self.simulation_id,
            "step": self.step,
            "node_states": [node.__json_encode__() for node in self.node_states],
            "messages": [msg.__json_encode__() for msg in self.messages],
            "status": self.status,
            "timestamp": datetime.now().isoformat(),
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
        )


class DataclassJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if hasattr(obj, "__json_encode__"):
            return obj.__json_encode__()
        return super().default(obj)


def dataclass_json_decode(cls, json_data):
    if hasattr(cls, "__json_decode__"):
        return cls.__json_decode__(json_data)
    return json_data
