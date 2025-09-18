import arcade
import random
from typing import Dict, List
from entities.archer import Archer
from entities.peon import Peon
from entities.direction import Direction


class ArmySpawner:
    """Manages army spawning from designated spawner locations."""
    
    def __init__(self, spawner_locations: Dict[str, any], enemies: List[arcade.SpriteList], 
                 projectiles: List[arcade.SpriteList], knight: arcade.SpriteList, player: arcade.SpriteList, 
                 screen_width=600, screen_height=600, depth_manager=None, window=None):
        self.spawner_locations = spawner_locations
        self.enemies = enemies  # [red_team, yellow_team]
        self.projectiles = projectiles  # [red_projectiles, yellow_projectiles]
        self.knight = knight
        self.player = player
        self.depth_manager = depth_manager  # For perspective sorting
        self.window = window
        
        # Spawning configuration
        self.spawn_rate = 0.02  # 2% chance per frame during war phase
        self.max_units_per_team = 20  # Maximum units per team
        
        # Proximity-based activation settings
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.activation_distance = 500.0  # Distance in pixels to activate spawners
        self.activated_spawners = set()  # Track which spawners have been activated (single use)
        
        # Separate spawners by team
        self.red_spawners = []
        self.yellow_spawners = []
        
        self._categorize_spawners()
    
    def _categorize_spawners(self):
        """Categorize spawners by team based on their type."""
        for name, spawner in self.spawner_locations.items():
            if hasattr(spawner, 'spawn_type'):
                if spawner.spawn_type == "red_spawner":
                    self.red_spawners.append((spawner.x, spawner.y))
                elif spawner.spawn_type == "yellow_spawner":
                    self.yellow_spawners.append((spawner.x, spawner.y))
    
    def _create_target_list(self, team: int) -> arcade.SpriteList:
        """Create target list for a specific team."""
        targets = arcade.SpriteList()
        
        # Add knight and player as targets
        if len(self.knight) > 0:
            targets.append(self.knight[0])
        if len(self.player) > 0:
            targets.append(self.player[0])
        
        # Add opposing team enemies as targets
        opposing_team = 1 - team  # 0 becomes 1, 1 becomes 0
        for enemy in self.enemies[opposing_team]:
            if not getattr(enemy, 'is_dead', False):
                targets.append(enemy)
        
        return targets
    
    def check_proximity_and_activate(self, player_x, player_y, camera_x=None, camera_y=None, delta_time=0.0):
        """Check if player is close enough to any spawner to activate it."""
        # Use camera position if provided, otherwise use player position
        check_x = camera_x if camera_x is not None else player_x
        check_y = camera_y if camera_y is not None else player_y
        
        # Check all red spawners
        for i, (spawner_x, spawner_y) in enumerate(self.red_spawners):
            distance = ((check_x - spawner_x) ** 2 + (check_y - spawner_y) ** 2) ** 0.5
            spawner_key = f"red_{spawner_x}_{spawner_y}"
            
            if distance <= self.activation_distance and spawner_key not in self.activated_spawners:
                # print(f"ACTIVATED Red spawner at ({spawner_x:.1f}, {spawner_y:.1f})")
                self._activate_spawner(spawner_x, spawner_y, check_x, check_y)
                self.activated_spawners.add(spawner_key)
        
        # Check all yellow spawners
        for i, (spawner_x, spawner_y) in enumerate(self.yellow_spawners):
            distance = ((check_x - spawner_x) ** 2 + (check_y - spawner_y) ** 2) ** 0.5
            spawner_key = f"yellow_{spawner_x}_{spawner_y}"
            
            if distance <= self.activation_distance and spawner_key not in self.activated_spawners:
                # print(f"ACTIVATED Yellow spawner at ({spawner_x:.1f}, {spawner_y:.1f})")
                self._activate_spawner(spawner_x, spawner_y, check_x, check_y)
                self.activated_spawners.add(spawner_key)
    
    def _activate_spawner(self, spawner_x, spawner_y, camera_x, camera_y):
        """
        Activate a single spawner and spawn units for the appropriate team.
        
        Args:
            spawner_x: X coordinate of the spawner
            spawner_y: Y coordinate of the spawner
            camera_x: Camera's current x position
            camera_y: Camera's current y position
        """
        # Determine which team this spawner belongs to
        if (spawner_x, spawner_y) in self.red_spawners:
            team = "red"
            enemy_list = self.enemies[0]  # Red team
        else:
            team = "yellow"
            enemy_list = self.enemies[1]  # Yellow team
            
        # Spawn 8-15 units at off-screen locations
        import random
        num_units = random.randint(8, 15)
        
        # Calculate off-screen spawn positions
        spawn_positions = self._calculate_offscreen_positions(
            camera_x, camera_y, spawner_x, spawner_y, num_units
        )
        
        for spawn_pos in spawn_positions:
            # Randomly choose unit type with different probabilities
            unit_type = self._choose_random_unit_type()
            self._spawn_unit_for_team(team, enemy_list, [spawn_pos], unit_type, self.window)
    
    def _calculate_offscreen_positions(self, camera_x, camera_y, spawner_x, spawner_y, num_units):
        """
        Calculate spawn positions outside the visible screen area.
        
        Args:
            camera_x: Camera center x position
            camera_y: Camera center y position
            spawner_x: Original spawner x position
            spawner_y: Original spawner y position
            num_units: Number of units to spawn
            
        Returns:
            List of (x, y) positions outside screen bounds
        """
        import random
        
        # Screen bounds relative to camera
        half_width = self.screen_width // 2
        half_height = self.screen_height // 2
        
        # Add buffer to ensure units are truly off-screen
        buffer = 100
        
        # Calculate screen edges
        left_edge = camera_x - half_width - buffer
        right_edge = camera_x + half_width + buffer
        top_edge = camera_y + half_height + buffer
        bottom_edge = camera_y - half_height - buffer
        
        positions = []
        
        # Determine which side of screen to spawn based on spawner position relative to camera
        dx = spawner_x - camera_x
        dy = spawner_y - camera_y
        
        for i in range(num_units):
            # Choose spawn side based on spawner direction with some randomness
            if abs(dx) > abs(dy):  # Spawner is more horizontal from camera
                if dx > 0:  # Spawner is to the right, spawn from right edge
                    x = right_edge + random.uniform(0, 50)
                    y = camera_y + random.uniform(-half_height, half_height)
                else:  # Spawner is to the left, spawn from left edge
                    x = left_edge - random.uniform(0, 50)
                    y = camera_y + random.uniform(-half_height, half_height)
            else:  # Spawner is more vertical from camera
                if dy > 0:  # Spawner is above, spawn from top edge
                    x = camera_x + random.uniform(-half_width, half_width)
                    y = top_edge + random.uniform(0, 50)
                else:  # Spawner is below, spawn from bottom edge
                    x = camera_x + random.uniform(-half_width, half_width)
                    y = bottom_edge - random.uniform(0, 50)
            
            # Add some random spread
            x += random.uniform(-30, 30)
            y += random.uniform(-30, 30)
            
            positions.append((x, y))
        
        return positions
    
    def _choose_random_unit_type(self):
        """
        Choose a random unit type with weighted probabilities.
        
        Returns:
            String representing unit type
        """
        import random
        
        # 60% Peon, 40% Archer for more variety
        return "peon" if random.random() < 0.6 else "archer"

    def spawn_armies(self):
        """
        Legacy method - now does nothing as we use proximity-based activation.
        Kept for compatibility but spawning is handled by check_proximity_and_activate.
        """
        pass  # No longer spawn continuously
    
    def _is_position_safe(self, x, y, window):
        """
        Check if a position is safe for spawning (not in collidable objects).
        
        Args:
            x: X coordinate to check
            y: Y coordinate to check
            window: Game window instance for collision checking
            
        Returns:
            bool: True if position is safe, False otherwise
        """
        # Create a temporary sprite to test collision
        temp_sprite = arcade.Sprite()
        temp_sprite.center_x = x
        temp_sprite.center_y = y
        temp_sprite.width = 32  # Typical unit size
        temp_sprite.height = 32
        
        # Check collision with solid decorations and knights
        return not window.is_in_collidable_objects(temp_sprite)
    
    def _find_safe_spawn_position(self, spawner_x, spawner_y, window, max_attempts=20):
        """
        Find a safe spawn position within a 300x300 area around the spawner.
        
        Args:
            spawner_x: Spawner X coordinate
            spawner_y: Spawner Y coordinate
            window: Game window instance for collision checking
            max_attempts: Maximum attempts to find a safe position
            
        Returns:
            tuple: (x, y) coordinates of safe position, or original spawner position if none found
        """
        safe_area_size = 300
        half_area = safe_area_size // 2
        
        for _ in range(max_attempts):
            # Generate random position within 300x300 area around spawner
            x = spawner_x + random.uniform(-half_area, half_area)
            y = spawner_y + random.uniform(-half_area, half_area)
            
            if self._is_position_safe(x, y, window):
                return x, y
        
        # If no safe position found, return spawner position (fallback)
        return spawner_x, spawner_y

    def _spawn_unit_for_team(self, team, enemy_list, spawners: List, unit_type=None, window=None):
        """
        Spawn a single unit for the specified team at a safe location within 300x300 area around spawner.
        
        Args:
            team: Team identifier ("red" or "yellow")
            enemy_list: The sprite list to add the new unit to
            spawners: List of spawner positions [(x, y), ...]
            unit_type: Optional unit type ("peon" or "archer"), randomly chosen if None
            window: Game window instance for collision checking
        """
        
        if not spawners:
            return
        
        # Choose random spawner
        spawner = random.choice(spawners)
        
        # Create target list for this team
        if team == "red":
            team_index = 0
        else:
            team_index = 1
        targets = self._create_target_list(team_index)
        
        # Determine unit type (use provided type or default random selection)
        if unit_type is None:
            unit_type = "peon" if random.random() < 0.7 else "archer"
        
        # Set team-specific properties
        if team == "red":  # Red team
            direction = Direction.LEFT
            warrior_image = "assets/images/Warrior_Red.png"
            archer_image = "assets/images/Archer_Red.png"
        else:  # Yellow team
            direction = Direction.RIGHT
            warrior_image = "assets/images/Warrior_Yellow.png"
            archer_image = "assets/images/Archer_Yellow.png"
        
        # Find safe spawn position within 300x300 area
        if window:
            final_x, final_y = self._find_safe_spawn_position(spawner[0], spawner[1], window)
        else:
            # Fallback to original logic if no window provided
            x_offset = 50 if team == "red" else -50
            final_x = spawner[0] + x_offset
            final_y = spawner[1] + random.uniform(-30, 30)
        
        # Create and add the unit
        try:
            if unit_type == "peon":
                unit = Peon(
                    final_x, 
                    final_y,  # Small random Y offset
                    direction, 
                    targets, 
                    image=warrior_image
                )
            else:  # archer
                unit = Archer(
                    final_x, 
                    final_y,  # Small random Y offset
                    direction, 
                    self.projectiles[team_index], 
                    targets, 
                    image=archer_image, 
                    team=team_index
                )
            
            # Add to appropriate enemy list
            enemy_list.append(unit)
            
            # Add to depth manager for perspective sorting
            if hasattr(window, 'depth_manager') and window.depth_manager:
                window.depth_manager.add_sprite(unit)
                
        except Exception as e:
            import traceback
            traceback.print_exc()
    
    def get_spawner_count(self) -> Dict[str, int]:
        """Get the count of spawners by team."""
        return {
            "red": len(self.red_spawners),
            "yellow": len(self.yellow_spawners)
        }