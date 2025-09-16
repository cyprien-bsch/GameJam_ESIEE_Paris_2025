import arcade
from enum import Enum
import random
from entities.projectiles import Projectile

class Direction(Enum):
    LEFT = 0
    RIGHT = 1

class Enemy(arcade.Sprite):
    def __init__(self, x: float, y: float, direction: Direction = Direction.LEFT, projectiles: arcade.SpriteList = None):
        super().__init__(":resources:images/enemies/fishGreen.png", 1.0)
        self.center_x = x
        self.center_y = y
        self.direction = direction
        self.projectiles = projectiles if projectiles is not None else arcade.SpriteList()

    def update(self, delta_time = None):
        self.center_x += 1 if self.direction == Direction.RIGHT else -1
        if self.center_x < 0:
            self.center_x = 800
        elif self.center_x > 800:
            self.center_x = 0
        
        if random.random() < 0.01:
            self.shoot()


    def shoot(self):
        if self.direction == Direction.LEFT:
            projectile = Projectile(self.center_x, self.center_y, -5, 0)
        else:
            projectile = Projectile(self.center_x, self.center_y, 5, 0)
        self.projectiles.append(projectile)