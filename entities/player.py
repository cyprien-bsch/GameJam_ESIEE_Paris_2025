import arcade
from utils.animation import AnimationUtil
from enum import Enum
from utils.item import Coin

class Direction(Enum):
    LEFT = "left"
    RIGHT = "right"
    UP = "up"
    DOWN = "down"

class Player(arcade.Sprite):
    def __init__(self, x: float, y: float, solid_decorations: arcade.SpriteList, enemy_lists: list[arcade.SpriteList]):
        super().__init__()
        self.center_x = x
        self.center_y = y
        self.change_x = 0
        self.change_y = 0
        self.speed = 200
        self.solid_decorations = solid_decorations
        self.enemy_lists = enemy_lists
        self.is_brooming = False
        self.direction = Direction.DOWN

        # Brooming attributes
        self.brooming_enemy = None
        self.broom_timer = 0.0
        self.BROOM_TIME_TO_REMOVE = 3.0

        self.init_anim_frames()

    def init_anim_frames(self):
        # Taille d'une frame
        self.frame_width = 32
        self.frame_height = 32
        self.columns = 6  # nombre de frames par ligne
        self.anim_types = ["idle", "walk", "", "broom"] # une ligne par type d'animation

        # Chargement des textures (orientées vers la droite)
        right_facing_textures = AnimationUtil.load_textures_from_spritesheet(
            "assets/images/Player.png",
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
            "broom": {
                Direction.RIGHT: right_facing_textures["broom"],
                Direction.LEFT: left_facing_textures["broom"],
                Direction.UP: right_facing_textures["broom"],
                Direction.DOWN: left_facing_textures["broom"],
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
            self.frame_index %= len(frames)
            self.texture = frames[self.frame_index]

    def update(self, delta_time = None):
        dt = delta_time if delta_time else 1/60
        move_x = self.change_x * dt

        already_collided = arcade.check_for_collision_with_list(self, self.solid_decorations)

        # Handle brooming logic
        if self.is_brooming and self.brooming_enemy:
            # Check if still colliding with the same enemy
            if arcade.check_for_collision(self, self.brooming_enemy):
                self.broom_timer += dt
                if self.broom_timer >= self.BROOM_TIME_TO_REMOVE:
                    self.brooming_enemy.items.append(Coin())
                    self.brooming_enemy.remove_from_sprite_lists()

                    self.brooming_enemy = None # Stop brooming
                    self.is_brooming = False # End the action
                    self.state = "idle"
            else:
                # No longer colliding, reset
                self.brooming_enemy = None
                self.broom_timer = 0
            
            # Player is locked in place while brooming an enemy
            self.update_animation(dt)
            return

        # --- Normal Movement ---
        move_x = self.change_x * dt
        self.center_x += move_x
        if arcade.check_for_collision_with_list(self, self.solid_decorations) and not already_collided:
            self.center_x -= move_x

        move_y = self.change_y * dt
        self.center_y += move_y
        if arcade.check_for_collision_with_list(self, self.solid_decorations) and not already_collided:
            self.center_y -= move_y

        # Définir état
        self.state = "walk" if self.change_x != 0 or self.change_y != 0 else "idle"

        if self.is_brooming:
            self.state = "broom"

        # Définir direction
        if self.change_x > 0:
            self.direction = Direction.RIGHT
        elif self.change_x < 0:
            self.direction = Direction.LEFT
        elif self.change_y > 0:
            self.direction = Direction.UP
        elif self.change_y < 0:
            self.direction = Direction.DOWN

        # Mise à jour animation
        self.update_animation(delta_time)

    def on_key_press(self, symbol, modifiers):
        if symbol == arcade.key.SPACE:
            self.is_brooming = True
            self.state = "broom"
            self.frame_index = 0
            self.frame_time = 0.1
            self.change_x = 0
            self.change_y = 0

            # Check if we are starting to broom a dead enemy
            for enemy_list in self.enemy_lists:
                for enemy in enemy_list:
                    # Assuming enemy has an 'is_dead' attribute
                    if arcade.check_for_collision(self, enemy) and getattr(enemy, 'is_dead', False):
                        self.brooming_enemy = enemy
                        self.broom_timer = 0
                        return # Found an enemy to broom, stop checking
            return

        if self.is_brooming:
            return

        if symbol == arcade.key.UP or symbol == arcade.key.Z:
            self.change_y = self.speed
        elif symbol == arcade.key.DOWN or symbol == arcade.key.S:
            self.change_y = -self.speed
        elif symbol == arcade.key.LEFT or symbol == arcade.key.Q:
            self.change_x = -self.speed
        elif symbol == arcade.key.RIGHT or symbol == arcade.key.D:
            self.change_x = self.speed

    def on_key_release(self, symbol, modifiers):

        if symbol == arcade.key.SPACE:
            self.is_brooming = False
            self.brooming_enemy = None # Clear target
            self.broom_timer = 0 # Reset timer
            self.state = "idle"
            self.frame_index = 0
            self.frame_time = 0.1
            return

        if symbol == arcade.key.UP or symbol == arcade.key.Z:
            self.change_y = 0
        elif symbol == arcade.key.DOWN or symbol == arcade.key.S:
            self.change_y = 0
        elif symbol == arcade.key.LEFT or symbol == arcade.key.Q:
            self.change_x = 0
        elif symbol == arcade.key.RIGHT or symbol == arcade.key.D:
            self.change_x = 0
