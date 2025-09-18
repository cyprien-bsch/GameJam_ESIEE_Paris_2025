from entities.enemy import Enemy, Direction
from entities.projectiles import Projectile
from utils.item import Item
import math
import arcade
import random


class Peon(Enemy):
    def __init__(self, x: float, y: float, direction: Direction = Direction.LEFT, items:Item = None, targets: arcade.SpriteList = None):
        super().__init__(x, y, direction, 1.0, targets)
        self.target_distance_limit = 500
        self.attack_timer = 0
        self.attack_delay = random.uniform(80, 100) 
        self.scale = 0.5


    def sword_attack(self):
        self.target.remove_from_sprite_lists()


    def update(self, delta_time = None):
        self.target = self.nearest_target()
        self.attack_timer += 1
        if self.target is None:
            if self.direction == Direction.RIGHT:
                self.center_x += 1
            elif self.direction == Direction.LEFT:
                self.center_x -= 1

        elif self.distance(self.target) > 50:
            self.center_x += 1 if self.target.center_x > self.center_x else -1
            if self.target.center_y < self.center_y:
                self.center_y -= 1
            else:
                self.center_y += 1
            return
        
        elif self.attack_timer >= self.attack_delay:
            self.attack_timer = 0
            self.sword_attack()
        

    