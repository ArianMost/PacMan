class CheatMode:
    """Manages cheat toggles for testing."""

    def __init__(self) -> None:
        """Initialize all cheats to off."""
        self.enabled: bool = False
        self.invincible: bool = False
        self.ghosts_frozen: bool = False
        self.speed_boost: bool = False
        # How much faster the player moves when speed_boost is active
        self.player_speed_multiplier: float = 2.0

    def toggle_master(self) -> None:
        """Toggle the master switch for all cheats."""
        self.enabled = not self.enabled

    def toggle_invincible(self) -> None:
        """Toggle player invincibility."""
        self.invincible = not self.invincible

    def toggle_ghosts_frozen(self) -> None:
        """Toggle freezing the ghosts in place."""
        self.ghosts_frozen = not self.ghosts_frozen

    def toggle_speed_boost(self) -> None:
        """Toggle the player's speed boost."""
        self.speed_boost = not self.speed_boost
