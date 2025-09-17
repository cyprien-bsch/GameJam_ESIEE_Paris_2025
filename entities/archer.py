from entities.enemy import Enemy, Direction
from entities.projectiles import Projectile
import math
import arcade
import random

class Archer(Enemy):
    def __init__(self, x: float, y: float, direction: Direction = Direction.LEFT, projectiles: arcade.SpriteList = None, targets: arcade.SpriteList = None):
        super().__init__(x, y, direction, projectiles, targets)
        self.arrow_speed = random.uniform(4, 6)
        self.shoot_delay = random.uniform(80, 100) 
        self.shoot_timer = 0
        self.scale = 0.5



    def update(self, delta_time = None):
        self.target = self.nearest_target()
        self.shoot_timer += 1

        if self.target is None:
            if self.direction == Direction.RIGHT:
                self.center_x += 1
            elif self.direction == Direction.LEFT:
                self.center_x -= 1
            return

        if self.target is not None and self.distance(self.target) > 300:
            self.center_x += 1 if self.target.center_x > self.center_x else -1
            if self.target.center_y > self.center_y:
                self.center_y -= 1
            else:
                self.center_y += 1
            return

        if self.target is not None and self.shoot_timer >= self.shoot_delay:
            self.shoot_arrow()
            self.shoot_timer = 0


    def shoot_arrow(self):
        if self.target is not None:
            # Calculate vector to target
            target_x, target_y = self.center_x - self.target.center_x, self.center_y - self.target.center_y

            # Calculate the distance to the target
            distance = math.sqrt(target_x**2 + target_y**2)

            # Normalize the vector and scale by speed to get dx and dy
            if distance > 0:
                dx = -target_x * (self.arrow_speed / distance)
                dy = -target_y * (self.arrow_speed / distance)

                arrow = Projectile(self.center_x, self.center_y, dx, dy)
                self.projectiles.append(arrow)