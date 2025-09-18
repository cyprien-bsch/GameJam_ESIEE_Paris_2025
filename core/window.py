import arcade
from arcade.gui import UIManager, UITextureButton
from entities.player import Player
from entities.direction import Direction
from entities.knight import Knight
from utils.dialogue import Dialogue
from entities.projectiles import Projectile
from settings import SCREEN_WIDTH, SCREEN_HEIGHT
import random
from core.game_phases import GamePhase, phase_length
from core.scene_manager import SceneManager, GameScene
from core.map_manager import MapManager
from core.army_spawner import ArmySpawner

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
        
        # Map manager for handling map loading and spawning
        self.map_manager = MapManager(debug_mode=False)
        self.spawned_entities = {}
        
        # Initialize army spawner (will be set up after map loading)
        self.army_spawner = None

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
        # 1) Load and render the Tiled map using MapManager
        self.tile_map, self.scene = self.map_manager.load_map()
        
        # 2) Parse map data (collisions and spawn points)
        self.map_manager.parse_map_data()
        
        # 3) Get collision sprites from map manager
        self.solid_decorations = self.map_manager.get_collision_sprites()
            
        # Initialiser le gestionnaire de scènes
        self.scene_manager = SceneManager(self, self.dialogue_manager)

        # 4) Spawn entities using the map manager
        self.spawned_entities = self.map_manager.spawn_entities(
            self.player, self.knight, self.enemies
        )
        
        # 5) Initialize army spawner with spawner locations
        spawner_locations = {name: entity for name, entity in self.spawned_entities.items() 
                           if hasattr(entity, 'spawn_type') and 'spawner' in entity.spawn_type}
        self.army_spawner = ArmySpawner(
            spawner_locations, self.enemies, self.projectiles, self.knight, self.player,
            screen_width=SCREEN_WIDTH, screen_height=SCREEN_HEIGHT
        )
        
        # 6) Create physics engine with the collision sprites
        try:
            if len(self.player) > 0 and isinstance(self.solid_decorations, arcade.SpriteList):
                self.physics_engine = arcade.PhysicsEngineSimple(self.player[0], self.solid_decorations)
        except Exception as e:
            print(f"Warning: failed to create physics engine: {e}")


    def on_draw(self):
       

        if self.phase == GamePhase.MENU:
            # Dessiner le SpriteList contenant l'image de fond
            self.menu_background_list.draw()
            # Dessiner le bouton Play
            self.ui_manager.draw()
            return
        
        with self.camera.activate():
            if self.scene is not None:
                self.scene.draw()
            
            # Dessiner les collisions si en mode debug
            if hasattr(self.map_manager, 'debug_mode') and self.map_manager.debug_mode:
                self.solid_decorations.draw()
            
            self.player.draw()
            for p in self.player:
                p.draw()
            self.knight.draw()
            for enemy_list in self.enemies:
                enemy_list.draw()
            for projectile_list in self.projectiles:
                projectile_list.draw()
            
            # Dessiner les informations de debug du map manager
            self.map_manager.draw_debug_info()



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
        
        # Only check collisions if player is alive
        if player.current_health > 0:
            # Check player collision with enemies
            if (arcade.check_for_collision_with_list(player, self.filter_out_dead_enemies(self.enemies[0])) or
                arcade.check_for_collision_with_list(player, self.filter_out_dead_enemies(self.enemies[1]))):
                if player.invincible_timer <= 0:   # éviter de perdre tous les cœurs d'un coup
                    player.take_damage(1)          # <-- il perd 1 cœur
            
            # Check player collision with projectiles from both teams and remove them
            all_projectiles = arcade.SpriteList()
            all_projectiles.extend(self.projectiles[0])
            all_projectiles.extend(self.projectiles[1])
            
            hit_projectiles = arcade.check_for_collision_with_list(player, all_projectiles)
            if hit_projectiles:
                if player.invincible_timer <= 0:
                    player.take_damage(1)
                for projectile in hit_projectiles:
                    projectile.remove_from_sprite_lists()
        
        # Check knight collision with projectiles from both teams and remove them
        if len(self.knight) > 0:
            knight = self.knight[0]
            all_projectiles = arcade.SpriteList()
            all_projectiles.extend(self.projectiles[0])
            all_projectiles.extend(self.projectiles[1])
            knight_hit_projectiles = arcade.check_for_collision_with_list(knight, all_projectiles)
            if knight_hit_projectiles:
                if knight.invincible_timer <= 0:
                    knight.take_damage(1)
                for projectile in knight_hit_projectiles:
                    projectile.remove_from_sprite_lists()

        # Check enemy collision with projectiles from opposing teams only
        for left_enemy in self.enemies[0]:
            # Only check collision if enemy is alive
            if not left_enemy.is_dead:
                # Left enemies (team 0) can only be hit by right team projectiles (team 1)
                hit_projectiles = [p for p in arcade.check_for_collision_with_list(left_enemy, self.projectiles[1]) if getattr(p, 'team', None) == 1]
                if hit_projectiles:
                    left_enemy.die()
                    for projectile in hit_projectiles:
                        projectile.remove_from_sprite_lists()
                    
        for right_enemy in self.enemies[1]:
            # Only check collision if enemy is alive
            if not right_enemy.is_dead:
                # Right enemies (team 1) can only be hit by left team projectiles (team 0)
                hit_projectiles = [p for p in arcade.check_for_collision_with_list(right_enemy, self.projectiles[0]) if getattr(p, 'team', None) == 0]
                if hit_projectiles:
                    right_enemy.die()
                    for projectile in hit_projectiles:
                        projectile.remove_from_sprite_lists()

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
            # Use proximity-based army spawner activation with camera position
            if self.army_spawner and len(self.player) > 0:
                player_sprite = self.player[0]
                # Pass camera position for off-screen spawning calculations
                camera_x, camera_y = self.camera.position
                self.army_spawner.check_proximity_and_activate(
                    player_sprite.center_x, player_sprite.center_y,
                    camera_x, camera_y
                )



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
            # Toggle debug mode with F1
            if symbol == arcade.key.F1:
                self.map_manager.toggle_debug_mode()
                return
                
            # Print debug info with F2
            if symbol == arcade.key.F2:
                self.map_manager.print_debug_info()
                if self.army_spawner:
                    spawner_counts = self.army_spawner.get_spawner_count()
                    print(f"Army spawners: {spawner_counts}")
                return
                
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
        self.ui_manager.clear()

        # Créer un Sprite pour l'image de fond
        self.menu_background_sprite = arcade.Sprite("assets/images/affiche.png")
        self.menu_background_sprite.center_x = self.width // 2
        self.menu_background_sprite.center_y = self.height // 2
        self.menu_background_sprite.width = self.width
        self.menu_background_sprite.height = self.height

        # Mettre le sprite dans une SpriteList
        self.menu_background_list = arcade.SpriteList()
        self.menu_background_list.append(self.menu_background_sprite)

        # Bouton Play
        layout = arcade.gui.UIBoxLayout()
        play_texture = arcade.load_texture("assets/images/button_play_yellow.png")
        play_button = arcade.gui.UITextureButton(texture=play_texture, width=100, height=100)
        play_button.on_click = self.start_game
        layout.add(play_button)
        layout.center_x = self.width // 2 - 45
        layout.center_y = self.height // 2 - 100
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
