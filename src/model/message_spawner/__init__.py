from typing import List

from model.message_spawner.base_message_spawner import BaseMessageSpawner
from model.message_spawner.random_message_spawner import BasicRandomMessageSpawner

AVAILABLE_MESSAGE_SPAWNERS: List[type[BaseMessageSpawner]] = [BasicRandomMessageSpawner]


def get_message_spawner_by_name(name: str) -> BaseMessageSpawner:
    """
    Get a node by its name

    """
    for node in AVAILABLE_MESSAGE_SPAWNERS:
        if node.name == name:
            return node()
    raise ValueError(f"Message Spawner with name {name} not found")
