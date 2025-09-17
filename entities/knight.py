import arcade
from entities.direction import Direction
from entities.base_character import BaseCharacter
import random
from entities.projectiles import Projectile
from utils.animation import AnimationUtil
import math

 

class Knight(BaseCharacter):
    def __init__(self, x: float, y: float, solid_decorations: arcade.SpriteList = None, enemy_lists: list[arcade.SpriteList] = None):
        super().__init__()
        self.center_x = x
        self.center_y = y
        self.direction = Direction.RIGHT
        self.cell_size = 32
        self.speed = 64
        self.solid_decorations = solid_decorations if solid_decorations is not None else arcade.SpriteList()  # Liste des obstacles
        self.path = [
            (Direction.RIGHT, 10),
            (Direction.UP, 5),
            (Direction.LEFT, 20),
            (Direction.UP, 5)
        ]
        self.enemy_lists = enemy_lists if enemy_lists is not None else []
        self.current_step = 0
        self.steps_moved = 0
        self.mood = "idle"  # "idle", "walk", "attack"
        self.attack_timer = 0.0
        self.ATTACK_COOLDOWN = 0.4  # secondes
        self.init_anim_frames()
        self.current_health = 5
        self.max_health = 5
        self.is_dead = False

    def die(self):
        """Handle knight death"""
        self.is_dead = True
        self.current_health = 0
        self.alpha = 128  # Make knight semi-transparent when dead


    def init_anim_frames(self):
        self.frame_width = 32
        self.frame_height = 32
        self.columns = 6
        self.anim_types = ["idle", "walk", "_", "", "attack"]

        right_facing_textures = AnimationUtil.load_textures_from_spritesheet(
            "assets/images/MiniCavalierMan.png",
            self.frame_width, self.frame_height, self.columns, self.anim_types
        )

        left_facing_textures = {}
        for anim_type, textures in right_facing_textures.items():
            left_facing_textures[anim_type] = [arcade.Texture(image=texture.image).flip_left_right() for texture in textures]

        # Pour diagonales, on réutilise textures droite/gauche pour l’exemple
        self.textures_dict = {
            "idle": {
                Direction.RIGHT: right_facing_textures["idle"],
                Direction.LEFT: left_facing_textures["idle"],
                Direction.UP: right_facing_textures["idle"],
                Direction.DOWN: left_facing_textures["idle"],
                Direction.UP_RIGHT: right_facing_textures["idle"],
                Direction.UP_LEFT: left_facing_textures["idle"],
                Direction.DOWN_RIGHT: right_facing_textures["idle"],
                Direction.DOWN_LEFT: left_facing_textures["idle"],
            },
            "walk": {
                Direction.RIGHT: right_facing_textures["walk"],
                Direction.LEFT: left_facing_textures["walk"],
                Direction.UP: right_facing_textures["walk"],
                Direction.DOWN: left_facing_textures["walk"],
                Direction.UP_RIGHT: right_facing_textures["walk"],
                Direction.UP_LEFT: left_facing_textures["walk"],
                Direction.DOWN_RIGHT: right_facing_textures["walk"],
                Direction.DOWN_LEFT: left_facing_textures["walk"],
            },
            "attack": {
                Direction.RIGHT: right_facing_textures["attack"],
                Direction.LEFT: left_facing_textures["attack"],
                Direction.UP: right_facing_textures["attack"],
                Direction.DOWN: left_facing_textures["attack"],
                Direction.UP_RIGHT: right_facing_textures["attack"],
                Direction.UP_LEFT: left_facing_textures["attack"],
                Direction.DOWN_RIGHT: right_facing_textures["attack"],
                Direction.DOWN_LEFT: left_facing_textures["attack"],
            }
        }

        self.state = "idle"
        self.frame_index = 0
        self.frame_time = 0.1
        self.texture = self.textures_dict[self.state][self.direction][0]


    def nearest_target(self):
        nearest_enemy = None
        min_distance = float('inf')

        for enemy_list in self.enemy_lists:
            for enemy in enemy_list:
                distance = math.sqrt((self.center_x - enemy.center_x) ** 2 + (self.center_y - enemy.center_y) ** 2)
                if distance < min_distance and not enemy.is_dead:
                    min_distance = distance
                    nearest_enemy = enemy

        return nearest_enemy

    def update_animation(self, delta_time: float = 1/60):
        self.frame_time -= delta_time
        if self.frame_time <= 0:
            self.frame_time = 0.1
            self.frame_index += 1
            frames = self.textures_dict[self.state][self.direction]
            if self.frame_index >= len(frames):
                self.frame_index = 0
            self.texture = frames[self.frame_index]

    def _move(self, direction: Direction, delta_time: float):
        """
        Moves the sprite in a given direction with collision detection.
        """
        dx, dy = 0, 0
        if direction in [Direction.RIGHT, Direction.UP_RIGHT, Direction.DOWN_RIGHT]:
            dx = 1
        if direction in [Direction.LEFT, Direction.UP_LEFT, Direction.DOWN_LEFT]:
            dx = -1
        if direction in [Direction.UP, Direction.UP_RIGHT, Direction.UP_LEFT]:
            dy = 1
        if direction in [Direction.DOWN, Direction.DOWN_RIGHT, Direction.DOWN_LEFT]:
            dy = -1

        # Normalize for diagonal movement to maintain constant speed
        if dx != 0 and dy != 0:
            norm = math.sqrt(2)
            dx /= norm
            dy /= norm

        move_x = dx * self.speed * delta_time
        move_y = dy * self.speed * delta_time

        # Move with collision detection, if collision, revert and go 90 degrees
        self.center_x += move_x
        if arcade.check_for_collision_with_list(self, self.solid_decorations):
            self.center_x -= move_x
            self._move(Direction.UP if dy == 0 else Direction.DOWN, delta_time)

        self.center_y += move_y
        if arcade.check_for_collision_with_list(self, self.solid_decorations):
            self.center_y -= move_y
            self._move(Direction.LEFT if dx == 0 else Direction.RIGHT, delta_time)

    def update(self, delta_time: float = 1/60):
        if self.current_step >= len(self.path):
            self.state = "idle"
            self.update_animation(delta_time)
            self.current_step = 0
            self.steps_moved = 0
            return

        if self.mood == "idle":
            self.state = "idle"
            self.update_animation(delta_time)
            if random.random() < 0.01:  # 1% de chance par frame de changer d'état
                self.mood = "walk"
            return
        
        if self.mood == "attack":
            self.speed = 96
            target = self.nearest_target()
            if target and (\
                (math.sqrt((self.center_x - target.center_x) ** 2 + (self.center_y - target.center_y) ** 2) < 50 and self.state == "attack") or \
                (math.sqrt((self.center_x - target.center_x) ** 2 + (self.center_y - target.center_y) ** 2) < 30 and self.state != "attack")):
                if self.state != "attack":
                    self.state = "attack"
                    self.frame_index = 0
                self.attack_timer += delta_time
                if self.attack_timer >= self.ATTACK_COOLDOWN:
                    target.die()
                    self.attack_timer = 0.0
                    if random.random() < 0.5:  # 50% de chance de rester en mode attaque
                        self.mood = "idle"
            elif target:
                
                self.state = "walk"
                # Determine direction towards target
                dx = target.center_x - self.center_x
                dy = target.center_y - self.center_y
                
                # This is a simplified way to get a direction enum, can be improved
                if abs(dx) > abs(dy):
                    self.direction = Direction.RIGHT if dx > 0 else Direction.LEFT
                else:
                    self.direction = Direction.UP if dy > 0 else Direction.DOWN
                
                self._move(self.direction, delta_time)
            else:
                self.mood = "walk"

        if self.mood == "walk":
            self.state = "walk"
            self.speed = 64
            dir_target, steps_target = self.path[self.current_step]
            self.direction = dir_target

            # Use the refactored move method
            self._move(dir_target, delta_time)

            # Compte des cases parcourues
            self.steps_moved += self.speed * delta_time / self.cell_size
            if self.steps_moved >= steps_target:
                self.current_step += 1
                self.steps_moved = 0

            self.max_health = 5
            self.current_health = self.max_health

            if random.random() < 0.005:  # 0.5% de chance par frame de changer d'état
                self.mood = "attack"
            elif random.random() < 0.002:  # 0.2% de chance par frame de changer d'état
                self.mood = "idle"
        
        self.update_animation(delta_time)

        
