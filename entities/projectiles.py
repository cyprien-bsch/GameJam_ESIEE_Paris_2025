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
        self.total_distance = 0
        self.max_distance = 500

    def update(self, delta_time=None):
        self.center_x += self.change_x
        self.center_y += self.change_y
        self.total_distance += math.sqrt(self.change_x**2 + self.change_y**2)
        if self.total_distance >= self.max_distance:
            self.remove_from_sprite_lists()

        
