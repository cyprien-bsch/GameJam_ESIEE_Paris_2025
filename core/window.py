import arcade
from entities.player import Player
from entities.enemy import Enemy, Direction
from entities.knight import Knight
from utils.dialogue import Dialogue
from entities.archer import Archer
from entities.projectiles import Projectile
from enum import Enum
from settings import SCREEN_WIDTH, SCREEN_HEIGHT
import random

class GamePhase(Enum):
    MENU = 1
    REST = 2
    WAR_START = 3
    IN_WAR = 4
    WAR_END = 5
    GAME_OVER = 0

def phase_length(phase: GamePhase) -> int:
    if phase == GamePhase.REST:
        return 10
    if phase == GamePhase.WAR_START:
        return 5
    if phase == GamePhase.IN_WAR:
        return 20
    if phase == GamePhase.WAR_END:
        return 3
    return 0

class GameWindow(arcade.Window):
    def __init__(self, width, height, title):
        super().__init__(width, height, title)
        self.player = arcade.SpriteList()
        self.knight = arcade.SpriteList()
        #left and right enemies for direction
        self.enemies = [arcade.SpriteList(), arcade.SpriteList()]
        #left and right projectiles 
        self.projectiles = [arcade.SpriteList(), arcade.SpriteList()]
        self.solid_decorations = arcade.SpriteList()
        self.background = None
        self.set_mouse_visible(True)
        self.phase = GamePhase.MENU
        self.phase_timer = 0
        self.camera = arcade.camera.Camera2D()  # caméra pour la scène
        self.gui_camera = arcade.camera.Camera2D()  # caméra fixe pour HUD
        self.dialogue_manager = Dialogue()

    def center_camera_to_sprite(self, sprite: arcade.Sprite):
        target_pos = (sprite.center_x, sprite.center_y)
        # La caméra 2D prend des coordonnées "world"
        self.camera.position = target_pos


    def cycle_phase(self):
        self.phase_timer += 1
        if self.phase_timer >= phase_length(self.phase) * 60: # assuming 60 FPS
            self.phase_timer = 0
            if self.phase == GamePhase.MENU:
                self.phase = GamePhase.REST
            elif self.phase == GamePhase.REST:
                self.phase = GamePhase.WAR_START
            elif self.phase == GamePhase.WAR_START:
                self.phase = GamePhase.IN_WAR
            elif self.phase == GamePhase.IN_WAR:
                self.phase = GamePhase.WAR_END
            elif self.phase == GamePhase.WAR_END:
                self.phase = GamePhase.REST
            print("Phase changed to:", self.phase)

    def setup(self):
        player_sprite = Player(100, 100, self.solid_decorations)
        player_sprite.scale = 1.5
        self.player.append(player_sprite)

        knight_sprite = Knight(200, 200)
        knight_sprite.scale = 2
        self.knight.append(knight_sprite)
        
        self.background = arcade.load_texture("assets/images/background.png")
        for i in range(10):
            self.solid_decorations.append(arcade.Sprite(":resources:/images/tiles/rock.png", 0.5, center_x=random.random()*SCREEN_WIDTH, center_y=random.random()*SCREEN_HEIGHT))

    def on_draw(self):
        self.clear()
        with self.camera.activate():
            arcade.draw_texture_rect(
                self.background,
                rect=arcade.LBWH(-self.width, -self.height, self.width * 2, self.height * 2),
                angle=0, alpha=255
            )
            self.player.draw()
            self.knight.draw()
            for enemy_list in self.enemies:
                enemy_list.draw()
            for projectile_list in self.projectiles:
                projectile_list.draw()
            
            self.solid_decorations.draw()

        with self.gui_camera.activate():
            arcade.draw_text(f"Phase: {self.phase.name}", 10, self.height - 20, arcade.color.WHITE, 14)
            # affiche le dialogue
            self.dialogue_manager.draw(self.width, self.height)

        


    def is_in_collidable_objects(self, sprite: arcade.Sprite) -> bool:
        return arcade.check_for_collision_with_list(sprite, self.solid_decorations) or \
               arcade.check_for_collision_with_list(sprite, self.knight)

    # Check collisions and do actions for each
    def check_collision(self):
        if (arcade.check_for_collision_with_list(self.player[0], self.enemies[0])
        or arcade.check_for_collision_with_list(self.player[0], self.enemies[1])
        or arcade.check_for_collision_with_list(self.player[0], self.projectiles[0])
        or arcade.check_for_collision_with_list(self.player[0], self.projectiles[1])):
            self.player[0].color = arcade.color.RED
        else: 
            self.player[0].color = arcade.color.WHITE
        
        for left_enemy in self.enemies[0]:
            if arcade.check_for_collision_with_list(left_enemy, self.projectiles[1]):
                left_enemy.remove_from_sprite_lists()
        for right_enemy in self.enemies[1]:
            if arcade.check_for_collision_with_list(right_enemy, self.projectiles[0]):
                right_enemy.remove_from_sprite_lists()

        # Quand collision avec le knight
        if arcade.check_for_collision_with_list(self.player[0], self.knight):
            self.dialogue_manager.start("knight_intro")

    # Update all game objects each frame (delta time is time since last update)
    def on_update(self, delta_time):
        self.cycle_phase()
        
        if self.phase == GamePhase.WAR_START:
            if random.random() < 0.1:
                self.enemies[0].append(Archer(800, 100 + 400 * random.random(), Direction.LEFT, self.projectiles[0], self.enemies[1]))
            if random.random() < 0.1:
                self.enemies[1].append(Archer(0, 100 + 400 * random.random(), Direction.RIGHT, self.projectiles[1], self.enemies[0]))

        if self.phase == GamePhase.WAR_END:
            self.enemies[0].clear()
            self.enemies[1].clear()
            self.projectiles[0].clear()
            self.projectiles[1].clear()


        self.player.update(delta_time)
        self.knight.update(delta_time)
        self.dialogue_manager.update(delta_time)
        for enemy_list in self.enemies:
            enemy_list.update(delta_time)
        for projectile_list in self.projectiles:
            projectile_list.update(delta_time)
        self.check_collision()

        self.center_camera_to_sprite(self.knight[0] if len(self.knight) > 0 else self.player[0])
        #self.center_camera_to_sprite(self.enemies[0][0] if len(self.enemies[0]) > 0 else self.enemies[1][0] if len(self.enemies[1]) > 0 else self.player[0])


    def on_key_press(self, symbol, modifiers):
        if symbol == arcade.key.ESCAPE:
            arcade.close_window()
        if symbol in [arcade.key.UP, arcade.key.DOWN, arcade.key.LEFT, arcade.key.RIGHT, arcade.key.SPACE, arcade.key.Z, arcade.key.Q, arcade.key.S, arcade.key.D]:
            self.player[0].on_key_press(symbol, modifiers)
            self.player.update()
        
        if symbol == arcade.key.ENTER:
            self.dialogue_manager.advance()

    
    def on_key_release(self, symbol, modifiers):
        if symbol in [arcade.key.UP, arcade.key.DOWN, arcade.key.LEFT, arcade.key.RIGHT, arcade.key.SPACE, arcade.key.Z, arcade.key.Q, arcade.key.S, arcade.key.D]:
            self.player[0].on_key_release(symbol, modifiers)
            self.player.update()