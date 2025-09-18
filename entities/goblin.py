import arcade
from entities.enemy import Enemy
from entities.direction import Direction
from utils.animation import AnimationUtil
from entities.projectiles import Projectile
import math


class Goblin(Enemy):
    def __init__(self, x: float, y: float, direction: Direction = Direction.LEFT,
                 projectiles: arcade.SpriteList = None, targets: arcade.SpriteList = None,
                 team: int = 0):
        super().__init__(x, y, direction, projectiles, targets)

        # Stats
        self.speed = 48
        self.max_health = 3
        self.current_health = self.max_health
        self.attack_range = 150     # distance de tir
        self.attack_cooldown = 1.5  # secondes
        self.attack_timer = 0
        self.state = "idle"
        self.team = team  # 0 = rouge, 1 = jaune

        self.init_anim_frames()

    def init_anim_frames(self):
        frame_width = 32   # adapte à ta spritesheet gobelin
        frame_height = 32
        columns = 8
        anim_types = ["idle", "walk", "attack"]

        right_textures = AnimationUtil.load_textures_from_spritesheet(
            "assets/images/Goblin.png",
            frame_width, frame_height, columns, anim_types
        )

        left_textures = {}
        for anim, frames in right_textures.items():
            left_textures[anim] = [arcade.Texture(image=tex.image).flip_left_right() for tex in frames]

        self.textures_dict = {
            "idle": {
                Direction.RIGHT: right_textures["idle"],
                Direction.LEFT: left_textures["idle"]
            },
            "walk": {
                Direction.RIGHT: right_textures["walk"],
                Direction.LEFT: left_textures["walk"]
            },
            "attack": {
                Direction.RIGHT: right_textures["attack"],
                Direction.LEFT: left_textures["attack"]
            },
        }

        self.frame_index = 0
        self.frame_time = 0.12
        self.texture = self.textures_dict["idle"][self.direction][0]

    def update_animation(self, delta_time: float = 1/60):
        self.frame_time -= delta_time
        if self.frame_time <= 0:
            self.frame_time = 0.12
            self.frame_index += 1
            frames = self.textures_dict[self.state][self.direction]
            if self.frame_index >= len(frames):
                self.frame_index = 0
            self.texture = frames[self.frame_index]

    def shoot_fireball(self, target):
        dx = target.center_x - self.center_x
        dy = target.center_y - self.center_y
        dist = max(1, math.sqrt(dx * dx + dy * dy))
        vel_x = (dx / dist) * 200
        vel_y = (dy / dist) * 200

        # Charger les frames de la boule depuis la spritesheet du gobelin
        fireball_frames = arcade.load_spritesheet(
            "assets/images/Goblin.png",
            sprite_width=64,
            sprite_height=64,
            columns=8,
            count=8,      # ⚠️ adapte pour la ligne où est la boule
            margin=0
        )

        fireball = Projectile("assets/images/Goblin.png", 1.0, animated=True)
        fireball.textures_list = fireball_frames[4:7]  # ← ex: frames 4,5,6 = boule
        fireball.texture = fireball.textures_list[0]

        fireball.center_x = self.center_x
        fireball.center_y = self.center_y
        fireball.change_x = vel_x
        fireball.change_y = vel_y
        fireball.team = self.team

        self.projectiles.append(fireball)


    def update(self, delta_time: float = 1/60):
        if self.is_dead:
            return

        self.target = self.nearest_target()
        if self.target:
            dx = self.target.center_x - self.center_x
            dy = self.target.center_y - self.center_y
            dist = math.sqrt(dx * dx + dy * dy)

            if dist < self.attack_range:
                self.state = "attack"
                self.attack_timer += delta_time
                if self.attack_timer >= self.attack_cooldown:
                    self.shoot_fireball(self.target)
                    self.attack_timer = 0
            else:
                self.state = "walk"
                step = self.speed * delta_time
                self.center_x += (dx/dist) * step
                self.center_y += (dy/dist) * step
        else:
            self.state = "idle"

        self.update_animation(delta_time)
