import arcade
from utils.animation import AnimationUtil
from enum import Enum

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
        arcade.play_sound(self.hit_sound)

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

        self.state = "idle"
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

        # État
        self.state = "walk" if self.change_x != 0 or self.change_y != 0 else "idle"


        if self.is_brooming:
            self.state = "broom"


        if self.change_x > 0:
            self.direction = Direction.RIGHT
        elif self.change_x < 0:
            self.direction = Direction.LEFT
        elif self.change_y > 0:
            self.direction = Direction.UP
        elif self.change_y < 0:
            self.direction = Direction.DOWN

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
        offset_y = 10  # hauteur au-dessus du joueur
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

        arcade.play_sound(self.hit_sound)

    def heal(self, amount=1):
        self.current_health = min(self.max_health, self.current_health + amount)

    # --- Contrôles ---
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
                    if arcade.check_for_collision(self, enemy) and enemy.is_dead:
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
