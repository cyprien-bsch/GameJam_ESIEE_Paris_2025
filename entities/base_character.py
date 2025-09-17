import arcade


class BaseCharacter(arcade.Sprite):
    def __init__(self):
        super().__init__()
        self.max_health = 5
        self.current_health = self.max_health
        self.invincible_timer = 0.0
        
        # Hit feedback system
        self.hit_flash_timer = 0.0
        self.hit_flash_duration = 0.15  # Flash red for 0.15 seconds
        self.original_color = (255, 255, 255)  # Store original color
        self.blink_timer = 0.0
        self.blink_interval = 0.1  # Blink every 0.1 seconds during invincibility

    def update(self, delta_time: float | None = None):
        dt = delta_time if delta_time is not None else 1/60
        
        # Update invincibility timer
        if self.invincible_timer > 0:
            self.invincible_timer = max(0.0, self.invincible_timer - dt)
        
        # Update hit flash effect
        if self.hit_flash_timer > 0:
            self.hit_flash_timer = max(0.0, self.hit_flash_timer - dt)
            if self.hit_flash_timer <= 0:
                # Reset to original color when flash ends
                self.color = self.original_color
        
        # Update blinking effect during invincibility (after flash ends)
        if self.invincible_timer > 0 and self.hit_flash_timer <= 0:
            self.blink_timer += dt
            if self.blink_timer >= self.blink_interval:
                self.blink_timer = 0.0
                # Toggle alpha between 100 and 255 for blinking effect
                self.alpha = 100 if self.alpha == 255 else 255
        else:
            # Ensure full opacity when not invincible
            self.alpha = 255

    def take_damage(self, amount: int = 1):
        if self.invincible_timer > 0:
            return
        
        self.current_health = max(0, self.current_health - amount)
        self.invincible_timer = 1.0
        
        # Trigger hit feedback effects
        self.hit_flash_timer = self.hit_flash_duration
        self.color = (255, 100, 100)  # Flash red
        self.blink_timer = 0.0  # Reset blink timer

    def heal(self, amount: int = 1):
        self.current_health = min(self.max_health, self.current_health + amount)


