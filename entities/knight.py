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
    

class Knight(arcade.Sprite):
    def __init__(self, x: float, y: float):
        super().__init__()
        self.center_x = x
        self.center_y = y
        self.direction = Direction.RIGHT

        # Paramètres de mouvement
        self.cell_size = 32       # Taille d’une case en pixels
        self.speed = 64           # Pixels/seconde
        self.path = [
            (Direction.RIGHT, 5),  # Avancer 5 cases à droite
            (Direction.UP, 3),     # Puis 3 cases vers le haut
            (Direction.LEFT, 5),   # Puis 5 cases à gauche
            (Direction.UP, 2)    # Puis 2 cases vers le haut
        ]
        self.current_step = 0
        self.steps_moved = 0

        self.init_anim_frames()


    def init_anim_frames(self):
        # Taille d'une frame
        self.frame_width = 32
        self.frame_height = 32
        self.columns = 6  # nombre de frames par ligne
        self.anim_types = ["idle", "walk"] # une ligne par type d'animation

        # Chargement des textures (orientées vers la droite)
        right_facing_textures = AnimationUtil.load_textures_from_spritesheet(
            "assets/images/MiniCavalierMan.png",
            self.frame_width, self.frame_height, self.columns, self.anim_types
        )

        # Création des textures orientées vers la gauche en les retournant
        left_facing_textures = {}
        for anim_type, textures in right_facing_textures.items():
            left_facing_textures[anim_type] = [arcade.Texture(image=texture.image).flip_left_right() for texture in textures]

        # Dict textures : state -> direction -> list[arcade.Texture]
        self.textures_dict = {
            "idle": {
                Direction.RIGHT: right_facing_textures["idle"],
                Direction.LEFT: left_facing_textures["idle"],
                Direction.UP: right_facing_textures["idle"],
                Direction.DOWN: left_facing_textures["idle"],
            },
            "walk": {
                Direction.RIGHT: right_facing_textures["walk"],
                Direction.LEFT: left_facing_textures["walk"],
                Direction.UP: right_facing_textures["walk"],
                Direction.DOWN: left_facing_textures["walk"],
            }
        }

        # État initial
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
        # Si le chemin est terminé, on recommence
        if self.current_step >= len(self.path):
            self.state = "idle"
            self.update_animation(delta_time)
            self.current_step = 0
            self.steps_moved = 0

        self.state = "walk"

        # Récupère la direction et le nombre de cases de l’étape courante
        dir_target, steps_target = self.path[self.current_step]
        self.direction = dir_target

        # Déplacement selon la direction
        if dir_target == Direction.RIGHT:
            self.center_x += self.speed * delta_time
        elif dir_target == Direction.LEFT:
            self.center_x -= self.speed * delta_time
        elif dir_target == Direction.UP:
            self.center_y += self.speed * delta_time
        elif dir_target == Direction.DOWN:
            self.center_y -= self.speed * delta_time

        # Compte le nombre de cases parcourues
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



