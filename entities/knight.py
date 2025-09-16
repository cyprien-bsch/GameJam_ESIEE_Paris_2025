import arcade
from enum import Enum
import random
from entities.projectiles import Projectile


class Direction(Enum):
    LEFT = 0
    RIGHT = 1
    UP = 2
    DOWN = 3


class Knight(arcade.Sprite):
    def __init__(self, x: float, y: float, direction: Direction = Direction.RIGHT, projectiles: arcade.SpriteList = None):
        super().__init__("assets/images/MiniCavalierMan.png", 1.0)
        self.center_x = x
        self.center_y = y
        self.direction = direction
        self.projectiles = projectiles if projectiles is not None else arcade.SpriteList()

        # Paramètres de mouvement
        self.cell_size = 32       # Taille d’une case en pixels
        self.speed = 64           # Pixels/seconde
        self.path = [
            (Direction.RIGHT, 5),  # Avancer 5 cases à droite
            (Direction.UP, 3)      # Puis 3 cases vers le haut
        ]
        self.current_step = 0
        self.steps_moved = 0

    def update(self, delta_time: float = 1/60):
        # Si le chemin est terminé, ne fait rien
        if self.current_step >= len(self.path):
            return

        # Récupère la direction et le nombre de cases de l’étape courante
        dir_target, steps_target = self.path[self.current_step]

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

        # Tir aléatoire
        if random.random() < 0.01:
            self.shoot()

    def shoot(self):
        velocity = 5
        if self.direction == Direction.LEFT:
            projectile = Projectile(self.center_x, self.center_y, -velocity, 0)
        else:
            projectile = Projectile(self.center_x, self.center_y, velocity, 0)
        self.projectiles.append(projectile)
