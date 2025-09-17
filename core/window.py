import arcade
import xml.etree.ElementTree as ET
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
        return 1
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
        self.tile_map = None
        self.scene = None
        self.set_mouse_visible(True)
        self.phase = GamePhase.MENU
        self.phase_timer = 0
        self.camera = arcade.camera.Camera2D()  # caméra pour la scène
        self.gui_camera = arcade.camera.Camera2D()  # caméra fixe pour HUD
        self.physics_engine = None
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
        # 1) Load and render the Tiled map
        try:
            self.tile_map = arcade.load_tilemap("assets/map/Map.tmx", scaling=1.0)
            self.scene = arcade.Scene.from_tilemap(self.tile_map)
        except Exception as e:
            print(f"Warning: failed to load tilemap: {e}")

        # 2) Extract collision objects from the Tiled map (objects with class/type 'collision')
        try:
            tree = ET.parse("assets/map/Map.tmx")
            root = tree.getroot()

            map_height_tiles = int(root.attrib.get("height", "0"))
            tile_height = int(root.attrib.get("tileheight", "0"))
            total_map_height_px = map_height_tiles * tile_height

            for obj_group in root.findall("objectgroup"):
                layer_name = obj_group.attrib.get("name", "").lower()
                is_collision_layer = layer_name in {"collision", "collisions", "obstacles"}

                for obj in obj_group.findall("object"):
                    obj_class = obj.attrib.get("class") or obj.attrib.get("type")
                    is_collision_class = (obj_class or "").lower() == "collision"

                    if not (is_collision_layer or is_collision_class):
                        continue

                    try:
                        x = float(obj.attrib.get("x", 0))
                        y = float(obj.attrib.get("y", 0))
                        width = float(obj.attrib.get("width", 0))
                        height = float(obj.attrib.get("height", 0))

                        # Convert Tiled (top-left origin) to Arcade (bottom-left origin)
                        center_x = x + width / 2.0
                        center_y = total_map_height_px - (y + height / 2.0)

                        collider = arcade.SpriteSolidColor(int(max(1, width)), int(max(1, height)), color=(0, 0, 0, 0))
                        collider.center_x = center_x
                        collider.center_y = center_y
                        # Keep invisible for gameplay; comment out next line to visualize
                        collider.alpha = 0
                        self.solid_decorations.append(collider)
                    except Exception as inner_e:
                        print(f"Warning: failed to create collider from object: {inner_e}")
        except Exception as e:
            print(f"Warning: failed to parse collisions from TMX: {e}")

        # 3) Create player and physics using the collision sprites
        player_sprite = Player(100, 100, self.solid_decorations, self.enemies)
        player_sprite.scale = 2
        self.player.append(player_sprite)

        knight_sprite = Knight(300, 300)
        knight_sprite.scale = 2
        self.knight.append(knight_sprite)
        
        try:
            if len(self.player) > 0 and isinstance(self.solid_decorations, arcade.SpriteList):
                self.physics_engine = arcade.PhysicsEngineSimple(self.player[0], self.solid_decorations)
        except Exception as e:
            print(f"Warning: failed to create physics engine: {e}")

        # Example enemies for existing gameplay loop
        self.enemies[0].append(Enemy(400, 300, Direction.LEFT, self.projectiles[0]))
        self.enemies[1].append(Enemy(600, 300, Direction.RIGHT, self.projectiles[1]))

    def on_draw(self):
        self.clear()
        with self.camera.activate():
            if self.scene is not None:
                self.scene.draw()
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
                left_enemy.die()
        for right_enemy in self.enemies[1]:
            if arcade.check_for_collision_with_list(right_enemy, self.projectiles[0]):
                right_enemy.die()

        # Quand collision avec le knight
        if arcade.check_for_collision_with_list(self.player[0], self.knight):
            self.dialogue_manager.start("knight_intro")

    # Update all game objects each frame (delta time is time since last update)
    def on_update(self, delta_time):
        # Clamp anomolously large frame times (can happen on first frame/load)
        dt = min(max(delta_time, 0.0), 1/30)
        self.cycle_phase()
        
        if self.phase == GamePhase.WAR_START:
            if random.random() < 0.02:
                self.enemies[0].append(Archer(800, 100 + 400 * random.random(), Direction.LEFT, self.projectiles[0], self.enemies[1], image="assets/images/Archer_Red.png"))
            if random.random() < 0.02:
                self.enemies[1].append(Archer(0, 100 + 400 * random.random(), Direction.RIGHT, self.projectiles[1], self.enemies[0], image="assets/images/Archer_Yellow.png"))

        if self.phase == GamePhase.WAR_END:
            self.enemies[0].clear()
            self.enemies[1].clear()
            self.projectiles[0].clear()
            self.projectiles[1].clear()


        self.player.update(dt)
        self.knight.update(dt)
        self.dialogue_manager.update(dt)
        for enemy_list in self.enemies:
            enemy_list.update(dt)
        for projectile_list in self.projectiles:
            projectile_list.update(dt)
        self.check_collision()

        # Center camera on the player
        if len(self.player) > 0:
            self.center_camera_to_sprite(self.knight[0] if len(self.knight) > 0 else self.player[0])

        #self.center_camera_to_sprite(self.player[0])


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