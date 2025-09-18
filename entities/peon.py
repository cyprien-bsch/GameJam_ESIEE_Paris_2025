from entities.enemy import Enemy
from entities.direction import Direction
from entities.projectiles import Projectile
import math
import arcade
import random
from utils.animation import AnimationUtil


class Peon(Enemy):
    def __init__(self, x: float, y: float, direction: Direction = Direction.LEFT, targets: arcade.SpriteList = None, image: str = "assets/images/Warrior_Red.png"):
        super().__init__(x, y, direction, None, targets)
        self.target_distance_limit = 500
        self.attack_timer = 0
        self.attack_delay = random.uniform(80, 100) 
        self.scale = 0.5
        self.image = image

        # Pre-load attack sounds
        self.attack_sounds = [arcade.load_sound(f"assets/sounds/swordS{i}.mp3") for i in range(1, 7)]

        self.init_anim_frames()

    def init_anim_frames(self):
        # Taille d'une frame
        self.frame_width = 192
        self.frame_height = 192
        self.columns = 6  # nombre de frames par ligne
        self.anim_types = ["idle", "walk", "attack", "", "attack_up", "_", "attack_down"] # une ligne par type d'animation

        # Chargement des textures (orientées vers la droite)
        right_facing_textures = AnimationUtil.load_textures_from_spritesheet(
            self.image,
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
            },
            "attack": {
                Direction.RIGHT: right_facing_textures["attack"],
                Direction.LEFT: left_facing_textures["attack"],
                Direction.UP: right_facing_textures["attack"],
                Direction.DOWN: left_facing_textures["attack"],
            },
            "attack_up": {
                Direction.RIGHT: right_facing_textures["attack_up"],
                Direction.LEFT: left_facing_textures["attack_up"],
                Direction.UP: right_facing_textures["attack_up"],
                Direction.DOWN: left_facing_textures["attack_up"],
            },
            "attack_down": {
                Direction.RIGHT: right_facing_textures["attack_down"],
                Direction.LEFT: left_facing_textures["attack_down"],
                Direction.UP: right_facing_textures["attack_down"],
                Direction.DOWN: left_facing_textures["attack_down"],
            }
        }

        # État initial
        self.state = "idle"
        self.frame_index = 0
        self.frame_time = 0.1
        self.texture = self.textures_dict[self.state][self.direction][0]

    def is_on_screen(self, camera_pos, screen_width, screen_height):
        """Check if the peon is visible on screen."""
        left_boundary = camera_pos[0] - screen_width / 2
        right_boundary = camera_pos[0] + screen_width / 2
        top_boundary = camera_pos[1] + screen_height / 2
        bottom_boundary = camera_pos[1] - screen_height / 2

        return (
            self.right > left_boundary and
            self.left < right_boundary and
            self.top > bottom_boundary and
            self.bottom < top_boundary
        )

    def update_animation(self, delta_time: float = 1/60, on_screen: bool = False):
        self.frame_time -= delta_time
        if self.frame_time <= 0:
            self.frame_time = 0.1
            self.frame_index += 1
            frames = self.textures_dict[self.state][self.direction]
            if self.frame_index == 3 and self.state.startswith("attack") and on_screen:
                # Play a random sword sound only if on screen
                sound_to_play = random.choice(self.attack_sounds)
                arcade.play_sound(sound_to_play)
            if self.frame_index >= len(frames):
                self.frame_index = 0
            self.texture = frames[self.frame_index]

    def die(self, item_manager=None):
        super().die(item_manager)

    def sword_attack(self):
        if self.target is not None:
            self.state = "attack"
            self.frame_index = 0
            # Use take_damage method if available, otherwise use die method
            if hasattr(self.target, 'take_damage'):
                self.target.take_damage(1)
            else:
                self.target.die()

    def update(self, delta_time=None, camera_pos=None, screen_width=None, screen_height=None):
        if self.is_dead:
            return
        
        on_screen = False
        if camera_pos and screen_width and screen_height:
            on_screen = self.is_on_screen(camera_pos, screen_width, screen_height)

        if on_screen:
            self.update_animation(delta_time, on_screen=on_screen)

        self.target = self.nearest_target()
        if self.target is None:
            self.state = "walk"
            if self.direction == Direction.RIGHT:
                self.center_x += 1
            elif self.direction == Direction.LEFT:
                self.center_x -= 1

        elif self.distance(self.target) > 50:
            no_side_movement = self.target.center_x == self.center_x
            self.center_x += 1 if self.target.center_x > self.center_x else -1 if self.target.center_x < self.center_x else 0
            self.state = "walk"
            if self.target.center_y < self.center_y:
                self.center_y -= random.uniform(0.1, 0.2) if not no_side_movement else 1
            elif self.target.center_y > self.center_y:
                self.center_y += random.uniform(0.1, 0.2) if not no_side_movement else 1
            self.attack_timer = 0
        
        elif self.attack_timer >= self.attack_delay:
            self.attack_timer = 0
            self.sword_attack()
        else:
            if abs(self.target.center_y - self.center_y) > abs(self.target.center_x - self.center_x) * 2 and self.target.center_y > self.center_y:
                self.state = "attack_down"
            elif abs(self.target.center_y - self.center_y) > abs(self.target.center_x - self.center_x) * 2 and self.target.center_y < self.center_y:
                self.state = "attack_up"
            else:
                self.state = "attack"
            self.attack_timer += 1



