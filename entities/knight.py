import arcade
from enum import Enum
import random
from entities.projectiles import Projectile
from utils.animation import AnimationUtil


class Direction(Enum):
    LEFT = 0
    RIGHT = 1
    UP = 2
    DOWN = 3
    UP_RIGHT = 4
    UP_LEFT = 5
    DOWN_RIGHT = 6
    DOWN_LEFT = 7

class Knight(arcade.Sprite):
    def __init__(self, x: float, y: float, solid_decorations: arcade.SpriteList):
        super().__init__()
        self.center_x = x
        self.center_y = y
        self.direction = Direction.RIGHT
        self.cell_size = 32
        self.speed = 64
        self.solid_decorations = solid_decorations  # Liste des obstacles
        self.path = [
            (Direction.RIGHT, 5),
            (Direction.UP, 3),
            (Direction.LEFT, 5),
            (Direction.UP, 2)
        ]
        self.current_step = 0
        self.steps_moved = 0
        self.init_anim_frames()


    def init_anim_frames(self):
        self.frame_width = 32
        self.frame_height = 32
        self.columns = 6
        self.anim_types = ["idle", "walk"]

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
            }
        }

        self.state = "idle"
        self.frame_index = 0
        self.frame_time = 0.1
        self.texture = self.textures_dict[self.state][self.direction][0]


    def update_animation(self, delta_time: float = 1/60):
        self.frame_time -= delta_time
        if self.frame_time <= 0:
            self.frame_time = 0.1
            self.frame_index += 1
            frames = self.textures_dict[self.state][self.direction]
            if self.frame_index >= len(frames):
                self.frame_index = 0
            self.texture = frames[self.frame_index]

    def update(self, delta_time: float = 1/60):
        if self.current_step >= len(self.path):
            self.state = "idle"
            self.update_animation(delta_time)
            self.current_step = 0
            self.steps_moved = 0
            return

        self.state = "walk"
        dir_target, steps_target = self.path[self.current_step]
        self.direction = dir_target

        # Calcul du déplacement
        dx, dy = 0, 0
        if dir_target == Direction.RIGHT:
            dx = 1
        elif dir_target == Direction.LEFT:
            dx = -1
        elif dir_target == Direction.UP:
            dy = 1
        elif dir_target == Direction.DOWN:
            dy = -1

        # Normalisation diagonale
        if dx != 0 and dy != 0:
            norm = (2 ** 0.5)
            dx /= norm
            dy /= norm

        move_x = dx * self.speed * delta_time
        move_y = dy * self.speed * delta_time

        # Déplacement avec collision
        self.center_x += move_x
        if arcade.check_for_collision_with_list(self, self.solid_decorations):
            self.center_x -= move_x  # Reculer si collision

        self.center_y += move_y
        if arcade.check_for_collision_with_list(self, self.solid_decorations):
            self.center_y -= move_y  # Reculer si collision

        # Compte des cases parcourues
        self.steps_moved += self.speed * delta_time / self.cell_size
        if self.steps_moved >= steps_target:
            self.current_step += 1
            self.steps_moved = 0

        self.update_animation(delta_time)

        self.max_health = 5
        self.current_health = self.max_health

    def take_damage(self, amount=1):
        self.current_health = max(0, self.current_health - amount)

    def heal(self, amount=1):
        self.current_health = min(self.max_health, self.current_health + amount)


        self.update_animation(delta_time)