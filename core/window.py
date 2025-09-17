import arcade
from arcade.gui import UIManager, UITextureButton
import xml.etree.ElementTree as ET
from entities.player import Player
from entities.direction import Direction
from entities.knight import Knight
from utils.dialogue import Dialogue
from entities.archer import Archer
from entities.peon import Peon
from entities.projectiles import Projectile
from settings import SCREEN_WIDTH, SCREEN_HEIGHT
import random
from core.game_phases import GamePhase, phase_length
from core.scene_manager import SceneManager, GameScene

class GameWindow(arcade.Window):
    def __init__(self, width, height, title):
        super().__init__(width, height, title)
        self.player = arcade.SpriteList()
        self.knight = arcade.SpriteList()
        self.enemies = [arcade.SpriteList(), arcade.SpriteList()]
        self.projectiles = [arcade.SpriteList(), arcade.SpriteList()]
        self.solid_decorations = arcade.SpriteList()
        self.tile_map = None
        self.scene = None
        self.set_mouse_visible(True)
        self.phase = GamePhase.MENU
        self.phase_timer = 0
        self.camera = arcade.camera.Camera2D()  # caméra pour la scène
        self.gui_camera = arcade.camera.Camera2D()  # caméra fixe pour HUD
        self.knight_heart_texture = arcade.load_texture("assets/images/Heart.png")
        self.physics_engine = None
        self.dialogue_manager = Dialogue()
        self.scene_manager = None  # Sera initialisé dans setup()
        self.paused = False 
        self._bgm_sound = None
        self._bgm_player = None

        # Gestionnaire UI
        self.ui_manager = UIManager()
        self.ui_manager.enable()
        self.play_button = None
        self.setup_menu()

        # Background music: load and start looping immediately (menu + gameplay)
        try:
            self._bgm_sound = arcade.Sound("assets/music/broom&doom_main_theme.mp3", streaming=True)
            self._bgm_player = self._bgm_sound.play(loop=True, volume=0.6)
        except Exception as e:
            print(f"Warning: failed to start background music: {e}")

    def center_camera_to_sprite(self, sprite: arcade.Sprite):
        self.camera.position = (sprite.center_x, sprite.center_y)

    def cycle_phase(self):
        self.phase_timer += 1
        if self.phase != GamePhase.MENU and self.phase_timer >= phase_length(self.phase) * 60:
            self.phase_timer = 0
            if self.phase == GamePhase.REST:
                self.phase = GamePhase.WAR_START
            elif self.phase == GamePhase.WAR_START:
                self.phase = GamePhase.IN_WAR
            elif self.phase == GamePhase.IN_WAR:
                self.phase = GamePhase.WAR_END
            elif self.phase == GamePhase.WAR_END:
                self.phase = GamePhase.REST

    def setup(self):
        # 1) Load and render the Tiled map
        try:
            self.tile_map = arcade.load_tilemap("assets/map/Map.tmx", scaling=1.0)
            self.scene = arcade.Scene.from_tilemap(self.tile_map)
        except Exception as e:
            print(f"Warning: failed to load tilemap: {e}")
            
        # Initialiser le gestionnaire de scènes
        self.scene_manager = SceneManager(self, self.dialogue_manager)

        # 2) Extract collision objects from the Tiled map (objects with class/type 'collision')
        try:
            tree = ET.parse("assets/map/Map.tmx")
            root = tree.getroot()

            self.map_height_tiles = int(root.attrib.get("height", "0"))
            self.tile_height = int(root.attrib.get("tileheight", "0"))
            self.total_map_height_px = self.map_height_tiles * self.tile_height

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
                        center_y = self.total_map_height_px - (y + height / 2.0)

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
        player_sprite = Player(800, 800, self.solid_decorations, self.enemies)
        player_sprite.scale = 2
        self.player.append(player_sprite)

        knight_sprite = Knight(900, 800, self.solid_decorations, self.enemies)
        knight_sprite.scale = 2
        self.knight.append(knight_sprite)
        
        try:
            if len(self.player) > 0 and isinstance(self.solid_decorations, arcade.SpriteList):
                self.physics_engine = arcade.PhysicsEngineSimple(self.player[0], self.solid_decorations)
        except Exception as e:
            print(f"Warning: failed to create physics engine: {e}")


    def on_draw(self):
        self.clear()
        if self.phase == GamePhase.MENU:
            arcade.draw_text(
                "BROOM & DOOM",
                self.width / 2,
                self.height / 2 + 50,
                arcade.color.WHITE,
                36,
                anchor_x="center",
                anchor_y="center"
            )
            self.ui_manager.draw()
            return

        with self.camera.activate():
            if self.scene is not None:
                self.scene.draw()
            self.player.draw()
            for p in self.player:
                p.draw()
            self.knight.draw()
            for enemy_list in self.enemies:
                enemy_list.draw()
            for projectile_list in self.projectiles:
                projectile_list.draw()
            self.solid_decorations.draw()



        with self.gui_camera.activate():
            # Afficher l'objectif et la progression de la scène actuelle
            if self.scene_manager:
                self.scene_manager.draw_objective(self.width, self.height)
                
            self.dialogue_manager.draw(self.width, self.height)

            if self.paused:
                
                arcade.draw_lrbt_rectangle_filled(
                    0, self.width, 0, self.height,
                    (0, 0, 0, 150)  # noir semi-transparent
                )

            
                pause_texture = arcade.load_texture("assets/images/pause_button.png")
                arcade.draw_texture_rect(
                pause_texture,
                rect=arcade.LBWH(
                self.width // 2-32, 
                self.height // 2-32,   
                64,
                64
            ),
            angle=0
        )

            # HUD coeurs
            if len(self.knight) > 0:
                for i in range(self.knight[0].current_health):
                    arcade.draw_texture_rect(
                        self.knight_heart_texture,
                        rect=arcade.LBWH(30 + i * 20, 0, 40, 40),
                        angle=0,
                        alpha=255
                    )
            
            if self.player[0].current_health <= 0:
                arcade.draw_text(
                    "GAME OVER",
                    self.width // 2, self.height // 2,
                    arcade.color.RED,
                    40,
                    anchor_x="center", anchor_y="center"
                )


    def is_in_collidable_objects(self, sprite: arcade.Sprite) -> bool:
        return arcade.check_for_collision_with_list(sprite, self.solid_decorations) or \
               arcade.check_for_collision_with_list(sprite, self.knight)

    def filter_out_dead_enemies(self, enemy_list: arcade.SpriteList) -> arcade.SpriteList:
        return arcade.SpriteList([enemy for enemy in enemy_list if not getattr(enemy, 'is_dead', False)])

    def check_collision(self):
        player = self.player[0]
        if (arcade.check_for_collision_with_list(player, self.filter_out_dead_enemies(self.enemies[0])) or
            arcade.check_for_collision_with_list(player, self.filter_out_dead_enemies(self.enemies[1])) or
            arcade.check_for_collision_with_list(player, self.projectiles[0]) or
            arcade.check_for_collision_with_list(player, self.projectiles[1])):
            player.color = arcade.color.RED
            if player.invincible_timer <= 0:   # éviter de perdre tous les cœurs d'un coup
                player.take_damage(1)          # <-- il perd 1 cœur
                player.invincible_timer = 1.0

        for left_enemy in self.enemies[0]:
            if arcade.check_for_collision_with_list(left_enemy, self.projectiles[1]):
                left_enemy.die()
        for right_enemy in self.enemies[1]:
            if arcade.check_for_collision_with_list(right_enemy, self.projectiles[0]):
                right_enemy.die()

        if arcade.check_for_collision_with_list(self.player[0], self.knight):
            self.dialogue_manager.start("knight_intro")

    def on_update(self, delta_time):
        if self.paused:
            return
        # Clamp anomolously large frame times (can happen on first frame/load)
        dt = min(max(delta_time, 0.0), 1/30)
        self.cycle_phase()
        
        # Mettre à jour le gestionnaire de scènes
        if self.scene_manager:
            self.scene_manager.update(dt)
        
        if self.phase == GamePhase.WAR_START:
            if random.random() < 0.05:
                self.enemies[0].append(Peon(1500, self.knight[0].center_y + 600 * random.random(), Direction.LEFT, self.enemies[1], image="assets/images/Warrior_Red.png"))
            if random.random() < 0.05:
                self.enemies[1].append(Peon(300, self.knight[0].center_y + 600 * random.random(), Direction.RIGHT, self.enemies[0], image="assets/images/Warrior_Yellow.png"))

            if random.random() < 0.05:
                self.enemies[0].append(Archer(1500, self.knight[0].center_y + 600 * random.random(), Direction.LEFT, self.projectiles[0], self.enemies[1], image="assets/images/Archer_Red.png"))
            if random.random() < 0.05:
                self.enemies[1].append(Archer(300, self.knight[0].center_y + 600 * random.random(), Direction.RIGHT, self.projectiles[1], self.enemies[0], image="assets/images/Archer_Yellow.png"))



        self.player.update(dt)
        self.knight.update(dt)
        self.dialogue_manager.update(dt)
        for enemy_list in self.enemies:
            enemy_list.update(dt)
        for projectile_list in self.projectiles:
            projectile_list.update(dt)
        self.check_collision()
        self.center_camera_to_sprite(self.knight[0] if len(self.knight) > 0 else self.player[0])


    def start_game(self, event=None):
        self.phase = GamePhase.REST
        self.phase_timer = 0
        # vider les listes pour éviter doublons
        self.player.clear()
        self.knight.clear()
        self.enemies[0].clear()
        self.enemies[1].clear()
        self.projectiles[0].clear()
        self.projectiles[1].clear()
        self.solid_decorations.clear()
        self.ui_manager.clear()
        self.scene_manager = None  # Réinitialiser le gestionnaire de scènes
        self.setup()

    def on_key_press(self, symbol, modifiers):
        
        if self.phase != GamePhase.MENU:
            if symbol == arcade.key.ESCAPE:
                self.paused = not self.paused
                return
            
            if symbol in [arcade.key.UP, arcade.key.DOWN, arcade.key.LEFT, arcade.key.RIGHT,
                          arcade.key.SPACE, arcade.key.Z, arcade.key.Q, arcade.key.S, arcade.key.D]:
                if not self.paused:  
                    self.player[0].on_key_press(symbol, modifiers)
                    self.player.update()

            if symbol == arcade.key.ENTER:
                self.dialogue_manager.advance()

    def on_key_release(self, symbol, modifiers):
        if symbol in [arcade.key.UP, arcade.key.DOWN, arcade.key.LEFT, arcade.key.RIGHT,
                      arcade.key.SPACE, arcade.key.Z, arcade.key.Q, arcade.key.S, arcade.key.D]:
            self.player[0].on_key_release(symbol, modifiers)
            self.player.update()

    def setup_menu(self):
        """Créer le menu avec titre et bouton Play centré sous le titre"""
        # Vider le UIManager
        self.ui_manager.clear()

        # Créer un layout vertical
        layout = arcade.gui.UIBoxLayout()

        # Titre
        title = arcade.gui.UITextArea(
            text="BROOM & DOOM",
            width=400,
            height=50,
            font_size=36,
            font_name="Arial",
            text_color=arcade.color.WHITE,
            align="center"
        )

        # Bouton Play
        play_texture = arcade.load_texture("assets/images/play_button2.png")
        play_button = arcade.gui.UITextureButton(
            texture=play_texture,
            width=64,
            height=64
        )
        play_button.on_click = self.start_game
        layout.add(play_button)

        # Centrer le layout sur l'écran
        layout.center_x = self.width // 2-20
        layout.center_y = 60

        # Ajouter le layout au UIManager
        self.ui_manager.add(layout)

    def on_close(self):
        # Stop background music when closing the window
        try:
            if self._bgm_player is not None:
                self._bgm_player.pause()
                self._bgm_player = None
        except Exception:
            pass
        try:
            if self._bgm_sound is not None:
                self._bgm_sound = None
        except Exception:
            pass
        return super().on_close()
