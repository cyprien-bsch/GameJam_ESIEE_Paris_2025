import arcade
import settings
from enum import Enum
import random
from entities.projectiles import Projectile

class Direction(Enum):
    LEFT = 1
    BOTTOM = 2
    RIGHT = 3
    TOP = 4

class Enemy(arcade.Sprite):
    def __init__(self, x: float, y: float, direction: Direction = Direction.LEFT, projectiles: arcade.SpriteList = None):
        super().__init__(":resources:images/enemies/fishGreen.png", 1.0)
        self.center_x = x
        self.center_y = y
        self.direction = direction
        self.moving = 0
        self.projectiles = projectiles if projectiles is not None else arcade.SpriteList()


    def update_direction(self):
        self.moving = 0
        
        new_dir = round(random.random())

        if self.direction == Direction.RIGHT:
            self.direction = Direction.BOTTOM if new_dir == 0 else Direction.TOP
        elif self.direction == Direction.LEFT:
            self.direction = Direction.TOP if new_dir == 0 else Direction.BOTTOM
        
        elif self.direction == Direction.BOTTOM:
            self.direction = Direction.LEFT if new_dir == 0 else Direction.RIGHT
        elif self.direction == Direction.TOP:
            self.direction = Direction.RIGHT if new_dir == 0 else Direction.LEFT
            

    def update(self, delta_time = None):
        if self.direction == Direction.RIGHT:
            self.center_x += 1
        elif self.direction == Direction.LEFT:
            self.center_x -= 1
        
        elif self.direction == Direction.BOTTOM:
            self.center_y += 1
        elif self.direction == Direction.TOP:
            self.center_y -= 1
            
        if self.center_x < 0:
            self.center_x = settings.SCREEN_WIDTH
        elif self.center_x > settings.SCREEN_WIDTH:
            self.center_x = 0

        if self.center_y < 0:
            self.center_y = settings.SCREEN_HEIGHT
        elif self.center_y > settings.SCREEN_HEIGHT:
            self.center_y = 0
        
        if random.random() < 0.01:
            self.shoot()
        
        self.moving += 1
        if (self.moving > 300 and random.random() < 0.01):
            self.update_direction()


    def shoot(self):
        dir_x, dir_y = 0, 0
        if self.direction == Direction.RIGHT:
            dir_x = 1
        if self.direction == Direction.LEFT:
            dir_x = -1
        if self.direction == Direction.BOTTOM:
            dir_y = 1
        if self.direction == Direction.TOP:
            dir_y = -1
        
        projectile = Projectile(self.center_x, self.center_y, 5 * dir_x, 5 * dir_y)
        self.projectiles.append(projectile)