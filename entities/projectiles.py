import arcade
from settings import SCREEN_WIDTH, SCREEN_HEIGHT
import math

class Projectile(arcade.Sprite):
    def __init__(self, x, y, dx, dy):
        super().__init__("assets/images/Arrow_right.png", 0.5)
        self.center_x = x
        self.center_y = y
        self.change_x = dx
        self.change_y = dy
        self.angle = math.degrees(math.atan2(-self.change_y, self.change_x))

    def update(self, delta_time=None):
        self.center_x += self.change_x
        self.center_y += self.change_y

        # Supprimer si sort de l’écran
        if self.top < 0 or self.bottom > SCREEN_HEIGHT or self.right < 0 or self.left > SCREEN_WIDTH:
            self.remove_from_sprite_lists()
