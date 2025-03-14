import random
from typing import List
from model.message.BaseMessage import BaseMessage
from model.message_spawner.base_message_spawner import BaseMessageSpawner
from model.node import BaseNode
from model.setting.model_settings import NumericSetting, SupportedEntity, RangeSetting


class NaturalDisasterMessageSpawner(BaseMessageSpawner):
    """
    A message spawner that simulates communication patterns during a natural disaster.

    The spawner follows three distinct phases:
    1. Pre-disaster: Low message activity (quiet network)
    2. Disaster event: Sudden burst of messages across many nodes
    3. Recovery: Rapid initial falloff followed by more gradual return to normal

    This simulates real disaster scenarios where there's an initial surge of messages
    as the disaster occurs, followed by a quick drop in communication volume.
    """

    name = "Natural Disaster Spawner"
    description = "Simulates message patterns during a natural disaster with quiet start, sudden burst, and rapid falloff."
    icon = "weather-hurricane"

    # Phase timing (in simulation steps)
    pre_disaster_duration = 20  # Quiet period before disaster
    disaster_peak_step = 25  # Step at which the disaster peaks
    initial_falloff_duration = 10  # Steps for the initial rapid falloff
    recovery_duration = 30  # Steps for the remainder of recovery

    # Message rate multipliers for each phase
    pre_disaster_rate_multiplier = 0.2  # 20% of normal spawn rate before disaster
    disaster_peak_multiplier = 12.0  # 12x normal spawn rate at disaster peak
    post_initial_falloff_multiplier = 2.0  # Falloff to 2x normal rate rapidly
    post_recovery_multiplier = 0.5  # 50% of normal rate after recovery

    # Inherit base settings and add disaster-specific settings
    settings = BaseMessageSpawner.settings + [
        NumericSetting(
            name="Pre-Disaster Duration",
            description="Number of simulation steps before the disaster event occurs.",
            default_value=20,
            min_value=1,
            max_value=100,
            attributes=["pre_disaster_duration"],
            entity_type=SupportedEntity.MESSAGE_SPAWNER,
        ),
        NumericSetting(
            name="Disaster Peak Step",
            description="Simulation step at which the disaster peaks (must be greater than Pre-Disaster Duration).",
            default_value=25,
            min_value=5,
            max_value=100,
            attributes=["disaster_peak_step"],
            entity_type=SupportedEntity.MESSAGE_SPAWNER,
        ),
        NumericSetting(
            name="Initial Falloff Duration",
            description="Steps for the initial rapid falloff after disaster peak.",
            default_value=10,
            min_value=1,
            max_value=50,
            attributes=["initial_falloff_duration"],
            entity_type=SupportedEntity.MESSAGE_SPAWNER,
        ),
        NumericSetting(
            name="Recovery Duration",
            description="Steps for the remainder of recovery after initial falloff.",
            default_value=30,
            min_value=1,
            max_value=100,
            attributes=["recovery_duration"],
            entity_type=SupportedEntity.MESSAGE_SPAWNER,
        ),
        RangeSetting(
            name="Pre-Disaster Rate Multiplier",
            description="Message rate before disaster as a percentage of the base rate.",
            default_value=20,
            min_range=0,
            max_range=100,
            entity_type=SupportedEntity.MESSAGE_SPAWNER,
            attributes=["pre_disaster_rate_multiplier"],
            step=1,
        ),
        RangeSetting(
            name="Disaster Peak Multiplier",
            description="Message rate at disaster peak as a multiplier of the base rate.",
            default_value=12,
            min_range=1,
            max_range=20,
            entity_type=SupportedEntity.MESSAGE_SPAWNER,
            attributes=["disaster_peak_multiplier"],
            step=1,
        ),
        RangeSetting(
            name="Post-Initial Falloff Multiplier",
            description="Message rate after initial falloff as a multiplier of the base rate.",
            default_value=2,
            min_range=0.5,
            max_range=10,
            entity_type=SupportedEntity.MESSAGE_SPAWNER,
            attributes=["post_initial_falloff_multiplier"],
            step=1,
        ),
        RangeSetting(
            name="Post-Recovery Multiplier",
            description="Message rate after full recovery as a percentage of the base rate.",
            default_value=50,
            min_range=0,
            max_range=100,
            entity_type=SupportedEntity.MESSAGE_SPAWNER,
            attributes=["post_recovery_multiplier"],
            step=5,
        ),
    ]

    def __init__(self):
        super().__init__()
        self._last_spawn_step = 0
        self._next_spawn_step = 0
        self._rng = random.Random()  # Default RNG, will be reset with seed if provided

    def init_spawn_messages(
        self, nodes: List[BaseNode], message_template: BaseMessage
    ) -> None:
        """
        Initial message spawn before simulation starts.
        Very few messages during this phase to represent the quiet network.
        """
        if not nodes or not message_template:
            return

        # Set up RNG with the provided seed if any
        self._rng = random.Random(self.random_seed)

        # We want minimal initial messages to simulate the quiet before the disaster
        initial_spawn_rate = self.spawn_rate * self.pre_disaster_rate_multiplier
        target_spawn_count = (initial_spawn_rate / 100.0) * len(nodes)
        num_initial_spawns = self._calculate_spawn_count(
            target_spawn_count, self.spawn_rate_variance
        )

        # Make sure we don't try to spawn more messages than we have valid nodes
        valid_nodes = [node for node in nodes if not getattr(node, "target", False)]
        num_initial_spawns = min(num_initial_spawns, len(valid_nodes))

        if num_initial_spawns > 0:
            nodes_to_spawn_in = self._rng.sample(
                valid_nodes, min(num_initial_spawns, len(valid_nodes))
            )
            self._spawn_messages_in_nodes(
                nodes_to_spawn_in, message_template=message_template, step=0
            )

        self.init_spawned = True
        self._calculate_next_spawn_step(0)

    def spawn_messages(
        self, nodes: List[BaseNode], step: int, message_template: BaseMessage
    ) -> None:
        """
        Main message spawning method that controls the disaster simulation phases.
        """
        if not nodes or not message_template:
            return

        # Skip if it's not time to spawn yet
        if step < self._next_spawn_step:
            return

        # Update last spawn step and calculate next one
        self._last_spawn_step = step
        self._calculate_next_spawn_step(step)

        # Calculate the current phase multiplier based on simulation step
        phase_multiplier = self._calculate_phase_multiplier(step)

        # Apply the phase multiplier to the spawn rate
        adjusted_spawn_rate = self.spawn_rate * phase_multiplier
        target_spawn_count = (adjusted_spawn_rate / 100.0) * len(nodes)

        # Calculate actual spawn count with variance
        num_spawns = self._calculate_spawn_count(
            target_spawn_count, self.spawn_rate_variance
        )

        # Get valid nodes and spawn messages
        valid_nodes = [node for node in nodes if not getattr(node, "target", False)]
        num_spawns = min(num_spawns, len(valid_nodes))

        if num_spawns > 0:
            # Use the RNG to select nodes
            nodes_to_spawn_in = self._rng.sample(valid_nodes, num_spawns)
            self._spawn_messages_in_nodes(nodes_to_spawn_in, message_template, step)

    def _calculate_phase_multiplier(self, step: int) -> float:
        """
        Calculate the message rate multiplier based on the current disaster phase.

        Returns a multiplier value that will be applied to the base spawn rate:
        - Pre-disaster: Low multiplier for quiet period
        - During disaster: High multiplier that peaks at disaster_peak_step
        - Initial falloff: Rapid decrease in messaging (quadratic falloff)
        - Recovery: More gradual decrease to post-recovery level
        """
        # Pre-disaster phase (quiet)
        if step < self.pre_disaster_duration:
            return self.pre_disaster_rate_multiplier

        # Disaster sudden onset phase (rapid increase)
        elif step < self.disaster_peak_step:
            # Exponential increase from pre-disaster to peak
            progress = (step - self.pre_disaster_duration) / (
                self.disaster_peak_step - self.pre_disaster_duration
            )
            # Use a power function for faster rise to peak
            progress_squared = progress**2
            return self.pre_disaster_rate_multiplier + progress_squared * (
                self.disaster_peak_multiplier - self.pre_disaster_rate_multiplier
            )

        # Disaster peak (single step with maximum messages)
        elif step == self.disaster_peak_step:
            return self.disaster_peak_multiplier

        # Initial rapid falloff phase
        elif step <= self.disaster_peak_step + self.initial_falloff_duration:
            # Quadratic falloff for rapid initial decrease
            progress = (step - self.disaster_peak_step) / self.initial_falloff_duration
            # Square the progress to create a steeper initial drop
            drop_factor = progress**2
            return self.disaster_peak_multiplier - drop_factor * (
                self.disaster_peak_multiplier - self.post_initial_falloff_multiplier
            )

        # Secondary recovery phase (more gradual)
        elif (
            step
            <= self.disaster_peak_step
            + self.initial_falloff_duration
            + self.recovery_duration
        ):
            progress = (
                step - (self.disaster_peak_step + self.initial_falloff_duration)
            ) / self.recovery_duration
            return (
                self.post_initial_falloff_multiplier * (1 - progress)
                + self.post_recovery_multiplier * progress
            )

        # Post-recovery phase (new normal)
        else:
            return self.post_recovery_multiplier

    def _calculate_next_spawn_step(self, current_step: int) -> None:
        """
        Calculate the next step at which messages should be spawned.
        During the disaster peak and immediate aftermath, spawning is more frequent.
        """
        # Calculate base frequency with variance
        base_frequency = self.spawn_rate_frequency
        if self.spawn_rate_frequency_variance > 0:
            frequency_variance = self._rng.randint(
                -self.spawn_rate_frequency_variance, self.spawn_rate_frequency_variance
            )
            base_frequency = max(1, base_frequency + frequency_variance)

        # During disaster peak and immediate aftermath, messages should spawn much more frequently
        if (
            current_step >= self.pre_disaster_duration - 2
            and current_step <= self.disaster_peak_step + 5
        ):
            # Spawn messages very frequently during disaster peak (up to 75% more frequently)
            base_frequency = max(1, int(base_frequency * 0.25))
        # Still relatively frequent during initial falloff
        elif current_step <= self.disaster_peak_step + self.initial_falloff_duration:
            # Spawn messages more frequently during initial falloff (up to 50% more frequently)
            base_frequency = max(1, int(base_frequency * 0.5))

        self._next_spawn_step = current_step + base_frequency

    def _calculate_spawn_count(
        self, target_spawn_count: float, spawn_rate_variance_percentage: float
    ) -> int:
        """
        Helper method to calculate the number of spawns, applying variance if needed.
        """
        if spawn_rate_variance_percentage > 0:
            variance = (spawn_rate_variance_percentage / 100.0) * target_spawn_count
            return max(
                0,
                int(self._rng.gauss(target_spawn_count, variance)),
            )
        else:
            return max(0, int(target_spawn_count))

    def _spawn_messages_in_nodes(
        self,
        nodes: List[BaseNode],
        message_template: BaseMessage,
        step: int = None,
    ) -> None:
        """
        Helper method to spawn messages in the provided nodes.
        """
        for node in nodes:
            new_message = message_template.duplicate(
                node.id, step=step, copy_time=False
            )
            if step is not None:
                new_message.created_time = step  # Set timestamp to current step
            node.on_message_create(new_message)
