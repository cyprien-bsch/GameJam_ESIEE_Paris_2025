from entities.enemy import Enemy
from entities.direction import Direction
from entities.projectiles import Projectile
import math
import arcade
import random
from utils.animation import AnimationUtil




class Archer(Enemy):
    shoot_sound = arcade.load_sound(f"assets/sounds/arrow-swish.mp3")
    textures_dict = None
    def __init__(self, x: float, y: float, direction: Direction = Direction.LEFT, projectiles: arcade.SpriteList = None, targets: arcade.SpriteList = None, image: str = "assets/images/Archer_Red.png", team: int = 0):
        super().__init__(x, y, direction, projectiles, targets)
        self.arrow_speed = random.uniform(6, 9)
        self.shoot_delay = 72
        self.shoot_timer = 0
        self.scale = 0.5
        self.image = image
        self.team = team  # 0 for left team (red), 1 for right team (yellow)



        self.init_anim_frames()

    def init_anim_frames(self):
        # Taille d'une frame
        self.frame_width = 192
        self.frame_height = 192
        self.columns = 6  # nombre de frames par ligne
        self.anim_types = ["idle", "walk", "shoot"] # une ligne par type d'animation

        if Archer.textures_dict is not None:
            self.textures_dict = Archer.textures_dict
            # État initial
            self.state = "idle"
            self.frame_index = 0
            self.frame_time = 0.2
            self.texture = self.textures_dict[self.state][self.direction][0]
            return

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
            "shoot": {
                Direction.RIGHT: right_facing_textures["shoot"],
                Direction.LEFT: left_facing_textures["shoot"],
                Direction.UP: right_facing_textures["shoot"],
                Direction.DOWN: left_facing_textures["shoot"],
            }
        }

        Archer.textures_dict = self.textures_dict  # Cache for future instances

        # État initial
        self.state = "idle"
        self.frame_index = 0
        self.frame_time = 0.2
        self.texture = self.textures_dict[self.state][self.direction][0]

    def die(self, item_manager=None):
        super().die(item_manager)
        self.state = "idle"
        self.frame_index = 0

    def is_on_screen(self, camera_pos, screen_width, screen_height):
        """Check if the archer is visible on screen."""
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

    def update_animation(self, delta_time: float = 1/60):
        self.frame_time -= delta_time
        if self.frame_time <= 0:
            self.frame_time = 0.2 if self.state == "shoot" else 0.1
            self.frame_index += 1
            frames = self.textures_dict[self.state][self.direction]
            self.frame_index %= len(frames)
            self.texture = frames[self.frame_index]



    def update(self, delta_time = None, camera_pos=None, screen_width=None, screen_height=None):
        if self.is_dead:
            return
        
        on_screen = False
        if camera_pos and screen_width and screen_height:
            on_screen = self.is_on_screen(camera_pos, screen_width, screen_height)

        

        self.target = self.nearest_target()

        if self.target is None:
            self.state = "walk"
            if self.direction == Direction.RIGHT:
                self.center_x += 1
            elif self.direction == Direction.LEFT:
                self.center_x -= 1
            self.update_animation(delta_time)
            return

        if self.target is not None and self.distance(self.target) > 300:
            self.state = "walk"
            if self.target.center_x > self.center_x:
                self.direction = Direction.RIGHT
                self.center_x += 1
            elif self.target.center_x < self.center_x:
                self.direction = Direction.LEFT
                self.center_x -= 1

            if self.target.center_y < self.center_y:
                self.center_y -= 1
            else:
                self.center_y += 1
            self.update_animation(delta_time)
            return

        if self.target is not None and self.distance(self.target) <= 300:
            self.state = "shoot"
            self.direction = Direction.LEFT if self.target.center_x < self.center_x else Direction.RIGHT
            self.shoot_timer += 1

        if self.target is not None and self.shoot_timer >= self.shoot_delay:
            self.shoot_arrow(on_screen=on_screen)
            self.shoot_timer = 0

        
        self.update_animation(delta_time)


    def shoot_arrow(self, on_screen: bool = False):
        if self.target is not None:
            # Play sound only if the archer is on screen
            if on_screen:
                arcade.play_sound(Archer.shoot_sound)

            # Calculate vector to target
            target_x, target_y = self.center_x - self.target.center_x, self.center_y - self.target.center_y

            self.direction = Direction.LEFT if target_x > 0 else Direction.RIGHT

            # Calculate the distance to the target
            distance = math.sqrt(target_x**2 + target_y**2)

            # Normalize the vector and scale by speed to get dx and dy
            if distance > 0:
                dx = -target_x * (self.arrow_speed / distance)
                dy = -target_y * (self.arrow_speed / distance)

                arrow = Projectile(self.center_x, self.center_y, dx, dy, team=self.team)
                self.projectiles.append(arrow)