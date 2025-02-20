from typing import List

from model.node.BaseNode import BaseNode
from model.node.SprayAndWaitLimitedNode import SprayAndWaitLimitedNode
from model.node.SprayAndWaitNode import SprayAndWaitNode

AVAILABLE_NODES: List[type[BaseNode]] = [SprayAndWaitNode, SprayAndWaitLimitedNode]


def get_node_by_name(name: str) -> BaseNode:
    """
    Get a node by its name

    """
    for node in AVAILABLE_NODES:
        if node.name == name:
            return node()
    raise ValueError(f"Node with name {name} not found")
