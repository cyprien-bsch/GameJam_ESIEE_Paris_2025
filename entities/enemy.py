import arcade
from enum import Enum

class Direction(Enum):
    LEFT = 0
    RIGHT = 1

class Enemy(arcade.Sprite):
    def __init__(self, x: float, y: float, direction: Direction = Direction.LEFT):
        super().__init__(":resources:images/enemies/fishGreen.png", 1.0)
        self.center_x = x
        self.center_y = y
        self.direction = direction

    def update(self, delta_time = None):
        self.center_x += 1 if self.direction == Direction.RIGHT else -1
