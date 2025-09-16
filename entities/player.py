import arcade
from utils.animation import AnimationUtil

class Player(arcade.Sprite):
    def __init__(self, x: float, y: float, solid_decorations: arcade.SpriteList = None):
        super().__init__()
        self.center_x = x
        self.center_y = y
        self.change_x = 0
        self.change_y = 0
        self.speed = 200
        self.solid_decorations = solid_decorations if solid_decorations is not None else arcade.SpriteList()

        # Taille d'une frame
        self.frame_width = 40
        self.frame_height = 48
        self.columns = 4  # nombre de frames par ligne
        self.directions = ["down", "up", "right", "left"]

        # Chargement des textures avec l'utilitaire
        idle_textures = AnimationUtil.load_textures_from_spritesheet(
            "assets/images/Character_Idle.png",
            self.frame_width, self.frame_height, self.columns, self.directions
        )
        walk_textures = AnimationUtil.load_textures_from_spritesheet(
            "assets/images/Character_Walk.png",
            self.frame_width, self.frame_height, self.columns, self.directions
        )

        # Dict textures : state -> direction -> list[arcade.Texture]
        self.textures_dict = {
            "idle": idle_textures,
            "walk": walk_textures
        }

        # État initial
        self.state = "idle"
        self.direction = "down"
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
        move_x = self.change_x * (delta_time if delta_time else 1/60)

        already_collided = arcade.check_for_collision_with_list(self, self.solid_decorations)

        self.center_x += move_x
        if arcade.check_for_collision_with_list(self, self.solid_decorations) and not already_collided:
            self.center_x -= move_x

        move_y = self.change_y * (delta_time if delta_time else 1/60)

        self.center_y += move_y
        if arcade.check_for_collision_with_list(self, self.solid_decorations) and not already_collided:
            self.center_y -= move_y

        # Définir état
        self.state = "walk" if self.change_x != 0 or self.change_y != 0 else "idle"

        # Définir direction
        if self.change_x > 0:
            self.direction = "right"
        elif self.change_x < 0:
            self.direction = "left"
        elif self.change_y > 0:
            self.direction = "up"
        elif self.change_y < 0:
            self.direction = "down"

        # Mise à jour animation
        self.update_animation(delta_time)

    def on_key_press(self, symbol, modifiers):
        if symbol == arcade.key.UP:
            if self.change_y == 0:
                self.change_y = self.speed
            else:
                self.change_y = 0
        elif symbol == arcade.key.DOWN:
            if self.change_y == 0:
                self.change_y = -self.speed
            else:
                self.change_y = 0
        elif symbol == arcade.key.LEFT:
            if self.change_x == 0:
                self.change_x = -self.speed
            else:
                self.change_x = 0
        elif symbol == arcade.key.RIGHT:
            if self.change_x == 0:
                self.change_x = self.speed
            else:
                self.change_x = 0

    def on_key_release(self, symbol, modifiers):
        if symbol == arcade.key.UP:
            if self.change_y == self.speed:
                self.change_y = 0
            else:
                self.change_y = -self.speed
        elif symbol == arcade.key.DOWN:
            if self.change_y == -self.speed:
                self.change_y = 0
            else:
                self.change_y = self.speed
        elif symbol == arcade.key.LEFT:
            if self.change_x == -self.speed:
                self.change_x = 0
            else:
                self.change_x = self.speed
        elif symbol == arcade.key.RIGHT:
            if self.change_x == self.speed:
                self.change_x = 0
            else:
                self.change_x = -self.speed
