import arcade
import settings
from entities.direction import Direction
from entities.base_character import BaseCharacter
import random
import math
from entities.projectiles import Projectile

 

class Enemy(BaseCharacter):
    def __init__(self, x: float, y: float, direction: Direction = Direction.LEFT, projectiles: arcade.SpriteList = None, targets: arcade.SpriteList = None):
        super().__init__()
        self.center_x = x
        self.center_y = y
        self.direction = direction
        self.moving = 0
        self.target = None
        self.projectiles = projectiles if projectiles is not None else arcade.SpriteList()
        self.targets = targets if targets is not None else arcade.SpriteList()
        self.target_distance_limit = 500
        self.is_dead = False
        self.speed = 90

    def die(self, item_manager=None):
        self.is_dead = True
        self.alpha = 50
        
        # Drop coins when enemy dies
        if item_manager:
            coin_value = 1  # Each enemy drops 1 coin
            item_manager.add_coins(coin_value)
            item_manager.spawn_coin_display(self.center_x, self.center_y, coin_value)
        


    def distance(self, enemy):
        x1, y1 = self.center_x, self.center_y
        x2, y2 = enemy.center_x, enemy.center_y

        return math.sqrt(((x1 - x2) ** 2) + ((y1 - y2) ** 2))
    

    def nearest_target(self):
        current_distance, minimal_distance = 0, self.target_distance_limit
        nearest_target = None

        for target in self.targets:
            # Skip dead targets
            if hasattr(target, 'is_dead') and target.is_dead:
                continue
            # Skip targets with 0 health
            if hasattr(target, 'current_health') and target.current_health <= 0:
                continue
                
            current_distance = self.distance(target)
            if current_distance < minimal_distance:
                nearest_target = target
                minimal_distance = current_distance
        
        return nearest_target


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
            self.direction = Direction.DOWN if new_dir == 0 else Direction.UP
        elif self.direction == Direction.LEFT:
            self.direction = Direction.UP if new_dir == 0 else Direction.DOWN
        
        elif self.direction == Direction.DOWN:
            self.direction = Direction.LEFT if new_dir == 0 else Direction.RIGHT
        elif self.direction == Direction.UP:
            self.direction = Direction.RIGHT if new_dir == 0 else Direction.LEFT
            

    def update(self, delta_time = None):
        if self.is_dead:
            self.alpha = 50
            return
        dt = delta_time if delta_time is not None else 1/60
        step = max(1.0, self.speed * dt)
        if self.direction == Direction.RIGHT:
            self.center_x += step
        elif self.direction == Direction.LEFT:
            self.center_x -= step
        elif self.direction == Direction.DOWN:
            self.center_y += step
        elif self.direction == Direction.UP:
            self.center_y -= step
        elif self.direction == Direction.TARGET and self.target is not None:
            dx = self.target.center_x - self.center_x
            dy = self.target.center_y - self.center_y
            dist = max(1e-6, math.sqrt(dx * dx + dy * dy))
            self.center_x += (dx / dist) * step
            self.center_y += (dy / dist) * step
            
        if self.center_x < 0:
            self.center_x = settings.SCREEN_WIDTH
        elif self.center_x > settings.SCREEN_WIDTH:
            self.center_x = 0

        if self.center_y < 0:
            self.center_y = settings.SCREEN_HEIGHT
        elif self.center_y > settings.SCREEN_HEIGHT:
            self.center_y = 0
        super().update(delta_time)

    