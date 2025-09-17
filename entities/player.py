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

        # --- Animations ---
        self.frame_width = 40
        self.frame_height = 48
        self.columns = 4
        self.directions = ["left", "right", "up", "down"]

        idle_textures = AnimationUtil.load_textures_from_spritesheet(
            "assets/images/Character_Idle.png",
            self.frame_width, self.frame_height, self.columns, self.directions
        )
        walk_textures = AnimationUtil.load_textures_from_spritesheet(
            "assets/images/Character_Walk.png",
            self.frame_width, self.frame_height, self.columns, self.directions
        )

        self.textures_dict = {
            "idle": idle_textures,
            "walk": walk_textures
        }

        self.state = "idle"
        self.direction = "down"
        self.frame_index = 0
        self.frame_time = 0.1
        self.texture = self.textures_dict[self.state][self.direction][0]

        # --- Vie ---
        self.max_health = 5
        self.current_health = self.max_health
        self.invincible_timer = 0
        self.heart_texture = arcade.load_texture("assets/images/Heart.png")

    def update_animation(self, delta_time: float = 1 / 60):
        self.frame_time -= delta_time
        if self.frame_time <= 0:
            self.frame_time = 0.1
            self.frame_index += 1
            frames = self.textures_dict[self.state][self.direction]
            self.frame_index %= len(frames)
            self.texture = frames[self.frame_index]

    def update(self, delta_time=None):
        move_x = self.change_x * (delta_time if delta_time else 1 / 60)
        already_collided = arcade.check_for_collision_with_list(self, self.solid_decorations)

        self.center_x += move_x
        if arcade.check_for_collision_with_list(self, self.solid_decorations) and not already_collided:
            self.center_x -= move_x

        move_y = self.change_y * (delta_time if delta_time else 1 / 60)
        self.center_y += move_y
        if arcade.check_for_collision_with_list(self, self.solid_decorations) and not already_collided:
            self.center_y -= move_y

        # État
        self.state = "walk" if self.change_x != 0 or self.change_y != 0 else "idle"

        # Direction
        if self.change_x > 0:
            self.direction = "right"
        elif self.change_x < 0:
            self.direction = "left"
        elif self.change_y > 0:
            self.direction = "up"
        elif self.change_y < 0:
            self.direction = "down"

        # Animation
        self.update_animation(delta_time)

        # Invincibilité
        if self.invincible_timer > 0:
            self.invincible_timer -= delta_time if delta_time else 1 / 60


        if self.invincible_timer > 0:
    # clignotement quand invincible
            if int(self.invincible_timer * 10) % 2 == 0:
                self.alpha = 128   # semi-transparent
            else:
                self.alpha = 255   # normal
        else:
            self.alpha = 255

    def draw(self):
        arcade.draw_texture_rect(
            self.texture,
            rect=arcade.LBWH(
                self.center_x - self.width / 2,
                self.center_y - self.height / 2,
                self.width,
                self.height
            ),
            angle=self.angle,
            alpha=255
        )

        spacing = 10   # espace entre les coeurs
        offset_y = 40  # hauteur au-dessus du joueur
        for i in range(self.current_health):
            arcade.draw_texture_rect(
                self.heart_texture,
                rect=arcade.LBWH(
                    self.center_x - (self.current_health - 1) * spacing / 2 + i * spacing - 10,
                    self.center_y + offset_y - 10,
                    20, 20  # largeur, hauteur du coeur affiché
                ),
                angle=0,
                alpha=255
            )




    # --- Vie ---
    def take_damage(self, amount=1):
        if self.invincible_timer <= 0:  # applique les dégâts seulement si pas invincible
            self.current_health = max(0, self.current_health - amount)
            self.invincible_timer = 1.0  # 1 seconde d’invincibilité

    def heal(self, amount=1):
        self.current_health = min(self.max_health, self.current_health + amount)

    # --- Contrôles ---
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
