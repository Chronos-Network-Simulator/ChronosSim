import random
from abc import ABC, abstractmethod
from typing import List

from model.message.BaseMessage import BaseMessage
from model.node import BaseNode
from model.setting.model_setting_mixin import ModelSettingMixin
from model.setting.model_settings import NumericSetting, SupportedEntity, RangeSetting


class BaseMessageSpawner(ModelSettingMixin, ABC):
    """
    A message spawner is responsible for spawning messages inside nodes at random intervals of the simulation
    steps.
    """

    name: str
    """
    Name of the Message Spawner
    """

    description: str
    """
    Description of the Message Spawner
    """

    icon: str
    """
    The material Design Icon to display to represent this message spawner type
    https://pictogrammers.com/library/mdi/
    """

    _random_seed: int | None = None
    """
    Underlying random seed value. Use the random_seed property to access and modify.
    """

    @property
    def random_seed(self) -> int | None:
        """
        Optional random seed to ensure reproducibility of message spawning.
        If set to an integer, the same seed will be used for random number generation in each simulation run,
        making the spawning behavior deterministic. If 0 or None, a new seed will be used for each run, resulting in
        potentially different spawning patterns.
        """
        return self._random_seed

    @random_seed.setter
    def random_seed(self, value: float) -> None:
        """
        Setter for the random seed. Recreates the random number generator if the seed value changes.
        A value of 0.0 is interpreted as no seed, meaning a new seed will be generated for each run.
        """
        old_seed = self._random_seed
        if value == 0.0:  # Treat 0.0 as no seed
            self._random_seed = None
        elif value is not None:
            self._random_seed = int(value)  # Ensure seed is an integer if provided
        else:
            self._random_seed = None

        if self._random_seed != old_seed:  # Recreate rng only if seed value changed
            if self._random_seed is None:
                self._rng = random.Random()  # No seed, system time based
            else:
                self._rng = random.Random(self._random_seed)  # Seed provided

    spawn_rate: float = 10
    """
    The average percentage of nodes that should spawn a message during each spawning interval.
    For example, if spawn_rate is 10 and there are 100 nodes, approximately 10 nodes will spawn a message.
    If it's a proportion, it should be a value between 0 and 1.
    """

    spawn_rate_variance: float = 5
    """
    The variance percentage in the number of nodes that should spawn a message.
    This variance is used to introduce randomness. For example, if the spawn_rate is 10 and the variance is 2,
    the actual number of nodes spawning could be around 10 +/- 2 (depending on the random distribution used).
    """

    spawn_rate_frequency: int = 10
    """
    The average number of simulation steps between each message spawning event.
    Messages will be spawned approximately every `spawn_rate_frequency` simulation steps.
    """

    spawn_rate_frequency_variance: int = 5
    """
    The variance in the frequency of message spawning, measured in simulation steps.
    This variance introduces randomness to the spawning interval. For example, if `spawn_rate_frequency` is 10 and
    `spawn_rate_frequency_variance` is 2, the actual interval between spawning events might be around 10 +/- 2
    simulation steps (depending on the random distribution used). Specify the distribution in the class docstring.
    """

    init_spawned: bool = False
    """
    If the initial messages where spawned or not inside the grid.
    """

    _rng: random.Random
    """
    Random number generator used to introduce randomness in the spawning behavior.
    """

    settings = [
        NumericSetting(
            name="Seed",
            description="Random seed for message spawning. If set, the same seed will be used for each simulation run. 0 means no seed.",
            default_value=0.0,
            min_value=0,
            max_value=2**32 - 1,
            attributes=["random_seed"],
            entity_type=SupportedEntity.MESSAGE_SPAWNER,
        ),
        RangeSetting(
            name="Spawn Rate",
            description="Average % of nodes that should spawn a message during each spawning interval.",
            default_value=10,
            min_range=0,
            max_range=100,
            entity_type=SupportedEntity.MESSAGE_SPAWNER,
            attributes=["spawn_rate"],
            step=1,
        ),
        NumericSetting(
            name="Spawn Rate Variance",
            description="Variance in the number of nodes that should spawn a message.",
            default_value=5,
            min_value=0,
            max_value=100,
            attributes=["spawn_rate_variance"],
            entity_type=SupportedEntity.MESSAGE_SPAWNER,
        ),
        RangeSetting(
            name="Spawn Rate Frequency",
            description="Average number of simulation steps between each message spawning event.",
            default_value=10,
            min_range=1,
            max_range=100,
            entity_type=SupportedEntity.MESSAGE_SPAWNER,
            attributes=["spawn_rate_frequency"],
            step=1,
        ),
        NumericSetting(
            name="Spawn Rate Frequency Variance",
            description="Variance in the frequency of message spawning.",
            default_value=5,
            min_value=0,
            max_value=100,
            attributes=["spawn_rate_frequency_variance"],
            entity_type=SupportedEntity.MESSAGE_SPAWNER,
        ),
    ]

    @abstractmethod
    def init_spawn_messages(
        self, nodes: List[BaseNode], message_template: BaseMessage
    ) -> None:
        """
        This method is called once at the beginning of the simulation, *before* the simulation steps begin.
        It is intended to trigger an initial message spawning event to set a baseline state for the simulation.
        Implementations should define the logic for this initial spawning, such as creating and injecting a set of
        messages into the network represented by the provided `nodes`.
        """

    @abstractmethod
    def spawn_messages(
        self, nodes: List[BaseNode], step: int, message_template: BaseMessage
    ) -> None:
        """
        This method is called by the simulation framework at *each* simulation step, after advancing the simulation time.
        Implementations should define the logic for spawning new messages during each step, based on the spawner's
        configuration (e.g., spawn rate, frequency, message template). This method is responsible for the ongoing
        injection of messages into the network throughout the simulation.

        :param message_template: The message template to spawn
        :param nodes: The nodes in the simulation
        :param step: The current simulation step
        """
