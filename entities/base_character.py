import arcade


class BaseCharacter(arcade.Sprite):
    def __init__(self):
        super().__init__()
        self.max_health = 5
        self.current_health = self.max_health
        self.invincible_timer = 0.0

    def update(self, delta_time: float | None = None):
        dt = delta_time if delta_time is not None else 1/60
        if self.invincible_timer > 0:
            self.invincible_timer = max(0.0, self.invincible_timer - dt)

    def take_damage(self, amount: int = 1):
        if self.invincible_timer > 0:
            return
        self.current_health = max(0, self.current_health - amount)
        self.invincible_timer = 1.0

    def heal(self, amount: int = 1):
        self.current_health = min(self.max_health, self.current_health + amount)


