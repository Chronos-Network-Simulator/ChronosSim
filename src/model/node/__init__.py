from typing import List

from model.node.BaseNode import BaseNode
from model.node.EpidemicRouting import EpidemicRoutingNode
from model.node.SprayAndWaitNode import SprayAndWaitNode
from model.node.SprayAndFocus import SprayAndFocusNode

AVAILABLE_NODES: List[type[BaseNode]] = [
    SprayAndWaitNode, SprayAndFocusNode, EpidemicRoutingNode
]


def get_node_by_name(name: str) -> BaseNode:
    """
    Get a node by its name

    """
    for node in AVAILABLE_NODES:
        if node.name == name:
            return node()
    raise ValueError(f"Node with name {name} not found")
