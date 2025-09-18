import arcade
import xml.etree.ElementTree as ET
from typing import Dict, List, Tuple, Optional
from entities.player import Player
from entities.knight import Knight
from entities.archer import Archer
from entities.peon import Peon
from entities.dragon import DragonSpawn


class SpawnPoint:
    """Represents a spawn point with position and type information."""
    def __init__(self, name: str, x: float, y: float, spawn_type: str = None):
        self.name = name
        self.x = x
        self.y = y
        self.spawn_type = spawn_type or self._determine_type_from_name(name)
    
    def _determine_type_from_name(self, name: str) -> str:
        """Determine spawn type from the object name."""
        name_lower = name.lower()
        if "player" in name_lower:
            return "player"
        elif "knight" in name_lower:
            return "knight"
        elif "yellowspawner" in name_lower or "yellow_spawner" in name_lower or "yellow" in name_lower:
            return "yellow_spawner"
        elif "redspawner" in name_lower or "red_spawner" in name_lower or "red" in name_lower:
            return "red_spawner"
        elif "archer" in name_lower:
            return "archer"
        elif "peon" in name_lower:
            return "peon"
        elif "dragon" in name_lower:
            return "dragon"
        else:
            return "unknown"


class MapManager:
    """Manages map loading, collision detection, and entity spawning."""
    
    def __init__(self, map_path: str = "assets/map/Map.tmx", debug_mode: bool = False):
        self.map_path = map_path
        self.debug_mode = debug_mode
        self.tile_map = None
        self.scene = None
        self.collision_sprites = arcade.SpriteList()
        self.spawn_points: Dict[str, SpawnPoint] = {}
        
        # Map dimensions
        self.map_height_tiles = 0
        self.tile_height = 0
        self.total_map_height_px = 0
        
        # Debug visualization
        self.debug_sprites = arcade.SpriteList()
        
    def load_map(self) -> Tuple[arcade.TileMap, arcade.Scene]:
        """Load the Tiled map and create the scene."""
        try:
            self.tile_map = arcade.load_tilemap(self.map_path, scaling=1.0)
            self.scene = arcade.Scene.from_tilemap(self.tile_map)
            if self.debug_mode:
                print(f"✓ Map loaded successfully: {self.map_path}")
            return self.tile_map, self.scene
        except Exception as e:
            print(f"Error loading tilemap: {e}")
            return None, None
    
    def parse_map_data(self):
        """Parse the TMX file to extract collision objects and spawn points."""
        try:
            tree = ET.parse(self.map_path)
            root = tree.getroot()
            
            # Get map dimensions
            self.map_height_tiles = int(root.attrib.get("height", "0"))
            self.tile_height = int(root.attrib.get("tileheight", "0"))
            self.total_map_height_px = self.map_height_tiles * self.tile_height
            
            if self.debug_mode:
                print(f"Map dimensions: {self.map_height_tiles} tiles × {self.tile_height}px = {self.total_map_height_px}px total height")
            
            # Parse object groups
            for obj_group in root.findall("objectgroup"):
                layer_name = obj_group.attrib.get("name", "").lower()
                
                if self.debug_mode:
                    print(f"Processing layer: {layer_name}")
                
                if layer_name in {"obstacles", "collision", "collisions"}:
                    self._parse_collision_objects(obj_group)
                elif layer_name == "spawner":
                    self._parse_spawn_objects(obj_group)
                    
        except Exception as e:
            print(f"Error parsing map data: {e}")
    
    def _parse_collision_objects(self, obj_group):
        """Parse collision objects from an object group."""
        for obj in obj_group.findall("object"):
            obj_class = obj.attrib.get("class") or obj.attrib.get("type")
            is_collision_class = (obj_class or "").lower() == "collision"
            
            # Accept objects in collision layers or with collision class
            if not is_collision_class:
                # If we're in a collision layer, accept all objects
                layer_name = obj_group.attrib.get("name", "").lower()
                if layer_name not in {"obstacles", "collision", "collisions"}:
                    continue
            
            try:
                x = float(obj.attrib.get("x", 0))
                y = float(obj.attrib.get("y", 0))
                width = float(obj.attrib.get("width", 0))
                height = float(obj.attrib.get("height", 0))
                
                # Convert Tiled (top-left origin) to Arcade (bottom-left origin)
                center_x = x + width / 2.0
                center_y = self.total_map_height_px - (y + height / 2.0)
                
                # Create collision sprite
                collider = arcade.SpriteSolidColor(
                    int(max(1, width)), 
                    int(max(1, height)), 
                    color=(255, 0, 0, 128) if self.debug_mode else (0, 0, 0, 0)
                )
                collider.center_x = center_x
                collider.center_y = center_y
                
                # Make invisible for gameplay unless in debug mode
                if not self.debug_mode:
                    collider.alpha = 0
                
                self.collision_sprites.append(collider)
                
                if self.debug_mode:
                    print(f"  Collision object: ({center_x}, {center_y}) size: {width}×{height}")
                    
            except Exception as e:
                print(f"Error creating collision object: {e}")
    
    def _parse_spawn_objects(self, obj_group):
        """Parse spawn point objects from an object group."""
        for obj in obj_group.findall("object"):
            try:
                name = obj.attrib.get("name", "")
                x = float(obj.attrib.get("x", 0))
                y = float(obj.attrib.get("y", 0))
                obj_class = obj.attrib.get("class") or obj.attrib.get("type")
                
                # Convert Tiled coordinates to Arcade coordinates
                arcade_x = x
                arcade_y = self.total_map_height_px - y
                
                spawn_point = SpawnPoint(name, arcade_x, arcade_y, obj_class)
                self.spawn_points[name] = spawn_point
                
                if self.debug_mode:
                    print(f"  Spawn point '{name}' ({spawn_point.spawn_type}): ({arcade_x}, {arcade_y})")
                    
                    # Create debug visualization for spawn points
                    debug_sprite = arcade.SpriteSolidColor(32, 32, color=(0, 255, 0, 180))
                    debug_sprite.center_x = arcade_x
                    debug_sprite.center_y = arcade_y
                    self.debug_sprites.append(debug_sprite)
                    
            except Exception as e:
                print(f"Error parsing spawn object: {e}")
    
    def spawn_entities(self, player_list: arcade.SpriteList, knight_list: arcade.SpriteList, 
                      enemies: List[arcade.SpriteList], dragon_list: arcade.SpriteList = None) -> Dict[str, arcade.Sprite]:
        """Spawn entities at their designated spawn points."""
        spawned_entities = {}
        
        # Create dragon list if not provided
        if dragon_list is None:
            dragon_list = arcade.SpriteList()
        
        for name, spawn_point in self.spawn_points.items():
            try:
                entity = None
                
                if spawn_point.spawn_type == "player":
                    # Include dragons in the enemy lists so player can broom them
                    all_enemy_lists = enemies + ([dragon_list] if dragon_list else [])
                    entity = Player(spawn_point.x, spawn_point.y, self.collision_sprites, all_enemy_lists)
                    entity.scale = 2
                    player_list.append(entity)
                    
                elif spawn_point.spawn_type == "knight":
                    entity = Knight(spawn_point.x, spawn_point.y, self.collision_sprites, enemies)
                    entity.scale = 2
                    knight_list.append(entity)
                    
                elif spawn_point.spawn_type == "dragon":
                    entity = DragonSpawn(spawn_point.x, spawn_point.y)
                    dragon_list.append(entity)
                    
                elif spawn_point.spawn_type in ["yellow_spawner", "red_spawner"]:
                    # These are spawner locations, not direct entity spawns
                    # Store the spawn point for later use by spawning systems
                    spawned_entities[name] = spawn_point
                    if self.debug_mode:
                        print(f"Registered spawner: {name} at ({spawn_point.x}, {spawn_point.y})")
                    continue
                
                if entity:
                    spawned_entities[name] = entity
                    if self.debug_mode:
                        print(f"Spawned {spawn_point.spawn_type}: {name} at ({spawn_point.x}, {spawn_point.y})")
                        
            except Exception as e:
                print(f"Error spawning entity {name}: {e}")
        
        return spawned_entities
    
    def get_collision_sprites(self) -> arcade.SpriteList:
        """Get the collision sprites for physics engine."""
        return self.collision_sprites
    
    def get_spawn_point(self, name: str) -> Optional[SpawnPoint]:
        """Get a specific spawn point by name."""
        return self.spawn_points.get(name)
    
    def get_spawn_points_by_type(self, spawn_type: str) -> List[SpawnPoint]:
        """Get all spawn points of a specific type."""
        return [sp for sp in self.spawn_points.values() if sp.spawn_type == spawn_type]
    
    def toggle_debug_mode(self):
        """Toggle debug visualization mode."""
        self.debug_mode = not self.debug_mode
        
        # Update collision sprite visibility
        for sprite in self.collision_sprites:
            if self.debug_mode:
                sprite.color = (255, 0, 0)
                sprite.alpha = 128
            else:
                sprite.alpha = 0
        
        # print(f"DEBUG mode: {'ON' if self.debug_mode else 'OFF'}")
    
    def draw_debug_info(self):
        """Draw debug information if debug mode is enabled."""
        if not self.debug_mode:
            return
            
        # Draw debug sprites (spawn points)
        self.debug_sprites.draw()
        
        # Draw text labels for spawn points
        for name, spawn_point in self.spawn_points.items():
            arcade.draw_text(
                f"{name}\n({spawn_point.spawn_type})",
                spawn_point.x - 50, spawn_point.y + 20,
                arcade.color.WHITE,
                font_size=10,
                anchor_x="center"
            )
    
    def print_debug_info(self):
        """Print detailed debug information about the map."""
        print("\n=== MAP DEBUG INFO ===")
        print(f"Map file: {self.map_path}")
        print(f"Map dimensions: {self.map_height_tiles} tiles × {self.tile_height}px")
        print(f"Total height: {self.total_map_height_px}px")
        print(f"Collision objects: {len(self.collision_sprites)}")
        print(f"Spawn points: {len(self.spawn_points)}")
        
        print("\nSpawn Points:")
        for name, spawn_point in self.spawn_points.items():
            print(f"  {name}: {spawn_point.spawn_type} at ({spawn_point.x:.1f}, {spawn_point.y:.1f})")
        
        print("\nSpawn Types Summary:")
        type_counts = {}
        for sp in self.spawn_points.values():
            type_counts[sp.spawn_type] = type_counts.get(sp.spawn_type, 0) + 1
        for spawn_type, count in type_counts.items():
            print(f"  {spawn_type}: {count}")
        print("=====================\n")