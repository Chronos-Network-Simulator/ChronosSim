from model.targets.RandomTargetSpawner import RandomTargetSpawner

AVAILABLE_TARGET_SPAWNERS = [RandomTargetSpawner]


def get_target_spawner_by_name(name: str) -> RandomTargetSpawner:
    """
    Get a target spawner by its name

    """
    for target_spawner in AVAILABLE_TARGET_SPAWNERS:
        if target_spawner.name == name:
            return target_spawner()
    raise ValueError(f"Target spawner with name {name} not found")
