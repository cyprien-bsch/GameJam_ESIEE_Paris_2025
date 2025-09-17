import arcade
import settings
from enum import Enum
import random
import math
from entities.projectiles import Projectile

class Direction(Enum):
    LEFT = 1
    BOTTOM = 2
    RIGHT = 3
    TOP = 4
    TARGET = 5

class Enemy(arcade.Sprite):
    def __init__(self, x: float, y: float, direction: Direction = Direction.LEFT, projectiles: arcade.SpriteList = None, targets: arcade.SpriteList = None):
        super().__init__(":resources:images/enemies/fishGreen.png", 1.0)
        self.center_x = x
        self.center_y = y
        self.direction = direction
        self.moving = 0
        self.target = None
        self.projectiles = projectiles if projectiles is not None else arcade.SpriteList()
        self.targets = targets if targets is not None else arcade.SpriteList()
        self.target_distance_limit = 500
        self.is_dead = False

    def die(self):
        self.is_dead = True
        self.alpha = 50
        


    def distance(self, enemy):
        x1, y1 = self.center_x, self.center_y
        x2, y2 = enemy.center_x, enemy.center_y

        return math.sqrt(((x1 - x2) ** 2) + ((y1 - y2) ** 2))
    

    def nearest_target(self):
        current_distance, minimal_distance = 0, self.target_distance_limit
        nearest_target = None


        for target in self.targets:
            current_distance = self.distance(target)
            if (current_distance < minimal_distance):
                nearest_target = target
                minimal_distance = current_distance
        
        if nearest_target is not None:
            return self.center_x - nearest_target.center_x, self.center_y - nearest_target.center_y
        return None


    def update_direction(self):
        if self.is_dead:
            self.alpha = 50
            return
        self.moving = 0

        self.target = self.nearest_target()

        if (self.target is not None):
            self.direction = Direction.TARGET
        else:
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
        if self.is_dead:
            self.alpha = 50
            return
        if self.direction == Direction.RIGHT:
            self.center_x += 1
        elif self.direction == Direction.LEFT:
            self.center_x -= 1
        
        elif self.direction == Direction.BOTTOM:
            self.center_y += 1
        elif self.direction == Direction.TOP:
            self.center_y -= 1
        
        elif self.direction == Direction.TARGET:
            self.center_x += self.target[0]
            self.center_y += self.target[1]
            
        if self.center_x < 0:
            self.center_x = settings.SCREEN_WIDTH
        elif self.center_x > settings.SCREEN_WIDTH:
            self.center_x = 0

        if self.center_y < 0:
            self.center_y = settings.SCREEN_HEIGHT
        elif self.center_y > settings.SCREEN_HEIGHT:
            self.center_y = 0
        


    