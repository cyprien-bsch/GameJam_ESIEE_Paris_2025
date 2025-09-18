import arcade
from entities.direction import Direction
from entities.base_character import BaseCharacter
import random
from entities.projectiles import Projectile
from utils.animation import AnimationUtil
import math

 

class Knight(BaseCharacter):
    def __init__(self, x: float, y: float, solid_decorations: arcade.SpriteList = None, enemy_lists: list[arcade.SpriteList] = None):
        super().__init__()
        self.center_x = x
        self.center_y = y
        self.direction = Direction.RIGHT
        self.cell_size = 32
        self.speed = 64
        self.solid_decorations = solid_decorations if solid_decorations is not None else arcade.SpriteList()  # Liste des obstacles
        self.path = [
            (Direction.RIGHT, 10),
            (Direction.UP, 5),
            (Direction.LEFT, 20),
            (Direction.UP, 5)
        ]
        self.enemy_lists = enemy_lists if enemy_lists is not None else []
        self.current_step = 0
        self.steps_moved = 0
        self.mood = "idle"  # "idle", "walk", "attack"
        self.attack_timer = 0.0
        self.ATTACK_COOLDOWN = 0.4  # secondes

        # Attributes for random walking
        self.walk_timer = 0.0
        self.walk_duration = random.uniform(1.0, 3.0) # Time to walk in one direction

        self.init_anim_frames()
        self.current_health = 20
        self.max_health = 20
        self.is_dead = False

        self.battlecry_sound = arcade.load_sound("assets/sounds/foward.mp3")
        self.hit_sound = arcade.load_sound("assets/sounds/swordK.mp3")
        
        # Deactivation system
        self.is_deactivated = False
        self.deactivation_timer = 0.0
        self.DEACTIVATION_DURATION = 2.0  # 2 seconds
        self.DEACTIVATION_THRESHOLD = 0  # Deactivate when health drops to 0
        self.original_color = (255, 255, 255)  # Store original color
        self.deactivated_color = (255, 255, 0)  # Yellow color when deactivated
        
        # Hit feedback and invincibility system (similar to player)
        self.invincible_timer = 0.0
        self.hit_flash_timer = 0.0
        self.hit_flash_duration = 0.15  # Flash red for 0.15 seconds
        self.blink_timer = 0.0
        self.blink_interval = 0.1  # Blink every 0.1 seconds during invincibility
        
        # Heart texture for health display
        self.heart_texture = arcade.load_texture("assets/images/Heart.png")

        self.kill_streak = 0

        self.previous_direction = self.direction  # To handle corners

    def take_damage(self, amount=1):
        """Handle taking damage and check for deactivation"""
        if self.is_dead or self.is_deactivated or self.invincible_timer > 0:
            return

        self.mood = "attack"  # Switch to attack mode when hit
        
        self.current_health = max(0, self.current_health - amount)
        
        # Trigger hit feedback effects (similar to player)
        self.hit_flash_timer = self.hit_flash_duration
        self.color = (255, 100, 100)  # Flash red
        self.blink_timer = 0.0  # Reset blink timer
        
        # Set invincibility timer (from BaseCharacter logic)
        self.invincible_timer = 1.0
        
        # Check if knight should be deactivated
        if self.current_health <= self.DEACTIVATION_THRESHOLD and not self.is_deactivated:
            self.deactivate()
        
        # Check if knight should die
        if self.current_health <= 0:
            self.die()

    def deactivate(self):
        """Deactivate the knight temporarily"""
        self.is_deactivated = True
        self.deactivation_timer = self.DEACTIVATION_DURATION
        self.color = self.deactivated_color
        self.mood = "idle"  # Stop attacking when deactivated

    def reactivate(self):
        """Reactivate the knight"""
        self.is_deactivated = False
        self.deactivation_timer = 0.0
        self.color = self.original_color
        # Restore health to at least 1 HP when reactivating
        self.current_health = max(1, self.max_health)
        # Reset death state
        self.is_dead = False
        self.alpha = 255  # Restore full opacity
        # Grant invincibility after reactivation (like player after being hit)
        self.invincible_timer = 1.0  # 1 second of invincibility
        self.blink_timer = 0.0  # Reset blink timer

    def die(self):
        """Handle knight death"""
        self.is_dead = True
        self.current_health = 0
        # Keep yellow color when dead (don't change color here)
        # Keep normal alpha (don't make semi-transparent)


    def init_anim_frames(self):
        self.frame_width = 32
        self.frame_height = 32
        self.columns = 6
        self.anim_types = ["idle", "walk", "_", "", "attack"]

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
            },
            "attack": {
                Direction.RIGHT: right_facing_textures["attack"],
                Direction.LEFT: left_facing_textures["attack"],
                Direction.UP: right_facing_textures["attack"],
                Direction.DOWN: left_facing_textures["attack"],
                Direction.UP_RIGHT: right_facing_textures["attack"],
                Direction.UP_LEFT: left_facing_textures["attack"],
                Direction.DOWN_RIGHT: right_facing_textures["attack"],
                Direction.DOWN_LEFT: left_facing_textures["attack"],
            }
        }

        self.state = "idle"
        self.frame_index = 0
        self.frame_time = 0.1
        self.texture = self.textures_dict[self.state][self.direction][0]


    def nearest_target(self):
        nearest_enemy = None
        min_distance = float('inf')

        for enemy_list in self.enemy_lists:
            for enemy in enemy_list:
                distance = math.sqrt((self.center_x - enemy.center_x) ** 2 + (self.center_y - enemy.center_y) ** 2)
                if distance < min_distance and not enemy.is_dead:
                    min_distance = distance
                    nearest_enemy = enemy

        return nearest_enemy

    def update_animation(self, delta_time: float = 1/60):
        self.frame_time -= delta_time
        if self.frame_time <= 0:
            self.frame_time = 0.1
            self.frame_index += 1

            if self.state == "attack":
                if self.frame_index == 1 and random.random() < 0.2:
                    arcade.play_sound(self.battlecry_sound, volume=1.2)
                if self.frame_index == 4 and random.random() < 0.5:
                    arcade.play_sound(self.hit_sound, volume=1.5)

            frames = self.textures_dict[self.state][self.direction]
            if self.frame_index >= len(frames):
                self.frame_index = 0
            self.texture = frames[self.frame_index]

    def _move(self, direction: Direction, delta_time: float):
        """
        Moves the sprite with wall-following logic using previous_direction to avoid getting stuck.
        """
        original_x = self.center_x
        original_y = self.center_y

        # Determine movement vector based on the intended direction
        dx, dy = 0, 0
        if direction in [Direction.RIGHT, Direction.UP_RIGHT, Direction.DOWN_RIGHT]: dx = 1
        if direction in [Direction.LEFT, Direction.UP_LEFT, Direction.DOWN_LEFT]: dx = -1
        if direction in [Direction.UP, Direction.UP_RIGHT, Direction.UP_LEFT]: dy = 1
        if direction in [Direction.DOWN, Direction.DOWN_RIGHT, Direction.DOWN_LEFT]: dy = -1

        # Attempt primary movement
        self.center_x += self.speed * delta_time * dx
        self.center_y += self.speed * delta_time * dy

        # --- Collision Handling ---
        if arcade.check_for_collision_with_list(self, self.solid_decorations):
            # Revert primary movement
            self.center_x = original_x
            self.center_y = original_y

            # --- Secondary Movement (Wall Following) ---
            # If we hit a wall while trying to go UP, and we were previously going LEFT, now try RIGHT.
            if direction in [Direction.UP, Direction.UP_LEFT, Direction.UP_RIGHT] and self.previous_direction in [Direction.LEFT, Direction.UP_LEFT]:
                self.center_x += self.speed * delta_time
            
            # If we hit a wall while trying to go UP, and we were previously going RIGHT, now try LEFT.
            elif direction in [Direction.UP, Direction.UP_LEFT, Direction.UP_RIGHT] and self.previous_direction in [Direction.RIGHT, Direction.UP_RIGHT]:
                self.center_x -= self.speed * delta_time

            # If we hit a wall going LEFT or RIGHT, the default action is to try going UP.
            elif direction in [Direction.LEFT, Direction.UP_LEFT, Direction.RIGHT, Direction.UP_RIGHT]:
                self.previous_direction = direction
                self._move(Direction.UP, delta_time)  # Recursive call to try moving UP


    def update(self, delta_time: float = 1/60):
        # Update hit feedback effects (similar to player)
        if self.hit_flash_timer > 0:
            self.hit_flash_timer = max(0.0, self.hit_flash_timer - delta_time)
            if self.hit_flash_timer <= 0:
                # Reset to appropriate color when flash ends
                if self.is_deactivated:
                    self.color = self.deactivated_color  # Stay yellow if deactivated
                else:
                    self.color = self.original_color  # Return to white if active
        
        # Update blinking effect during invincibility (after flash ends)
        if self.invincible_timer > 0 and self.hit_flash_timer <= 0:
            self.blink_timer += delta_time
            if self.blink_timer >= self.blink_interval:
                self.blink_timer = 0.0
                # Toggle alpha between 100 and 255 for blinking effect
                self.alpha = 100 if self.alpha == 255 else 255
        elif self.invincible_timer <= 0:
            # Ensure full opacity when not invincible
            self.alpha = 255
        
        # Update invincibility timer
        if self.invincible_timer > 0:
            self.invincible_timer -= delta_time
        
        # Handle deactivation timer
        if self.is_deactivated:
            self.deactivation_timer -= delta_time
            if self.deactivation_timer <= 0:
                self.reactivate()
            return  # Don't do anything else while deactivated
        
        # Don't update if dead
        if self.is_dead:
            self.state = "idle"
            self.update_animation(delta_time)
            self.current_step = 0
            self.steps_moved = 0
            return

        if self.current_step >= len(self.path):
            self.state = "idle"
            self.update_animation(delta_time)
            self.current_step = 0
            self.steps_moved = 0
            return

        if self.mood == "idle":
            self.state = "idle"
            self.update_animation(delta_time)
            if random.random() < 0.01:  # 1% de chance par frame de changer d'état
                self.mood = "walk"
            return
        
        if self.mood == "attack":
            self.speed = 96
            target = self.nearest_target()
            if target and (\
                (math.sqrt((self.center_x - target.center_x) ** 2 + (self.center_y - target.center_y) ** 2) < 50 and self.state == "attack") or \
                (math.sqrt((self.center_x - target.center_x) ** 2 + (self.center_y - target.center_y) ** 2) < 30 and self.state != "attack")):
                if self.state != "attack":
                    self.state = "attack"
                    self.frame_index = 0
                self.attack_timer += delta_time
                if self.attack_timer >= self.ATTACK_COOLDOWN:
                    target.die()
                    self.kill_streak += 1
                    self.attack_timer = 0.0
                    if random.random() < 0.1:  # 90% de chance de rester en mode attaque
                        self.mood = "walk"
                        self.kill_streak = 0
            elif target:

                #If too far, stop attacking
                if math.sqrt((self.center_x - target.center_x) ** 2 + (self.center_y - target.center_y) ** 2) > 700:
                    self.state = "walk"
                    self.mood = "walk"
                    self.kill_streak = 0
                    return

                self.state = "walk"
                # Determine direction towards target
                dx = target.center_x - self.center_x
                dy = target.center_y - self.center_y
                
                # This is a simplified way to get a direction enum, can be improved
                if abs(dx) > abs(dy):
                    self.direction = Direction.RIGHT if dx > 0 else Direction.LEFT
                else:
                    self.direction = Direction.UP if dy > 0 else Direction.DOWN
                
                self._move(self.direction, delta_time)
            else:
                self.mood = "walk"
                self.kill_streak = 0

        if self.mood == "walk":
            self.state = "walk"
            self.speed = 64
            
            # Update random walk timer
            self.walk_timer -= delta_time
            if self.walk_timer <= 0:
                # --- New logic to choose direction based on X position ---
                map_center_x = 1400
                
                # Determine preferred horizontal direction
                preferred_x_direction = None
                if self.center_x < map_center_x - 200: # to create a small deadzone
                    preferred_x_direction = Direction.RIGHT
                elif self.center_x > map_center_x + 200: # to create a small deadzone
                    preferred_x_direction = Direction.LEFT

                # Build a weighted list of possible directions
                possible_directions = [Direction.UP, Direction.DOWN] # Always possible to go up/down
                
                if preferred_x_direction:
                    # Add the preferred direction multiple times to increase its weight
                    possible_directions.extend([preferred_x_direction] * 3) 
                else:
                    # If near the center, add left/right with normal weight
                    possible_directions.extend([Direction.LEFT, Direction.RIGHT, Direction.UP_RIGHT, Direction.UP_LEFT])
                
                self.direction = random.choice(possible_directions)
                self.walk_timer = random.uniform(1.0, 3.0) # Walk for 1-3 seconds

            # Use the refactored move method
            self._move(self.direction, delta_time)

            if random.random() < 0.005:  # 0.5% de chance par frame de changer d'état
                self.mood = "attack"
            elif random.random() < 0.002:  # 0.2% de chance par frame de changer d'état
                self.mood = "idle"
        
        self.update_animation(delta_time)

    def draw(self):
        """Custom draw method to display knight with hearts in bottom left corner"""
        # Draw the knight sprite first
        super().draw()
        
        # Draw hearts in bottom left corner of screen (not relative to knight position)
        heart_size = 20
        spacing = 30  # Increased spacing to prevent overlap
        start_x = 15  # Distance from left edge of screen
        start_y = 15  # Distance from bottom edge of screen
        
        for i in range(self.current_health):
            arcade.draw_texture_rect(
                self.heart_texture,
                rect=arcade.LBWH(
                    start_x + i * spacing,
                    start_y,
                    heart_size,
                    heart_size
                ),
                angle=0,
                alpha=255
            )


