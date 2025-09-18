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
                 screen_width=600, screen_height=600, depth_manager=None):
        self.spawner_locations = spawner_locations
        self.enemies = enemies  # [red_team, yellow_team]
        self.projectiles = projectiles  # [red_projectiles, yellow_projectiles]
        self.knight = knight
        self.player = player
        self.depth_manager = depth_manager  # For perspective sorting
        
        # Spawning configuration
        self.spawn_rate = 0.02  # 2% chance per frame during war phase
        self.max_units_per_team = 20  # Maximum units per team
        
        # Proximity-based activation settings
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.activation_distance = 2000.0  # Increased from default to make spawners easier to trigger
        self.activated_spawners = set()  # Track which spawners have been activated
        
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
    
    def check_proximity_and_activate(self, player_x, player_y, camera_x=None, camera_y=None):
        """
        Check if player is close enough to any spawner and activate it once.
        
        Args:
            player_x: Player's current x position
            player_y: Player's current y position
            camera_x: Camera's current x position (optional, defaults to player_x)
            camera_y: Camera's current y position (optional, defaults to player_y)
        """
        # Use player position as camera center if not provided
        if camera_x is None:
            camera_x = player_x
        if camera_y is None:
            camera_y = player_y
            
        print(f"DEBUG: Checking proximity for {len(self.red_spawners + self.yellow_spawners)} spawners")
        print(f"DEBUG: Red spawners: {self.red_spawners}")
        print(f"DEBUG: Yellow spawners: {self.yellow_spawners}")
        print(f"DEBUG: Activation distance: {self.activation_distance}")
        
        for i, (spawner_x, spawner_y) in enumerate(self.red_spawners + self.yellow_spawners):
            # Skip if this spawner was already activated
            spawner_id = f"{spawner_x}_{spawner_y}"
            if spawner_id in self.activated_spawners:
                print(f"DEBUG: Spawner {i} at ({spawner_x}, {spawner_y}) already activated")
                continue
                
            # Calculate distance between player and spawner
            distance = ((player_x - spawner_x) ** 2 + (player_y - spawner_y) ** 2) ** 0.5
            print(f"DEBUG: Spawner {i} at ({spawner_x}, {spawner_y}): distance = {distance:.1f}")
            
            # If player is close enough, activate this spawner once
            if distance <= self.activation_distance:
                print(f"DEBUG: ACTIVATING spawner at ({spawner_x}, {spawner_y})!")
                self.activated_spawners.add(spawner_id)
                self._activate_spawner(spawner_x, spawner_y, camera_x, camera_y)
    
    def _activate_spawner(self, spawner_x, spawner_y, camera_x, camera_y):
        """
        Activate a single spawner to generate units once.
        
        Args:
            spawner_x: X coordinate of the spawner
            spawner_y: Y coordinate of the spawner
            camera_x: Camera's current x position
            camera_y: Camera's current y position
        """
        print(f"DEBUG: _activate_spawner called for ({spawner_x}, {spawner_y})")
        
        # Determine which team this spawner belongs to
        if (spawner_x, spawner_y) in self.red_spawners:
            team = "red"
            enemy_list = self.enemies[0]  # Red team
            print(f"DEBUG: Activating RED spawner, enemy_list length: {len(enemy_list)}")
        else:
            team = "yellow"
            enemy_list = self.enemies[1]  # Yellow team
            print(f"DEBUG: Activating YELLOW spawner, enemy_list length: {len(enemy_list)}")
            
        # Spawn 8-15 units at off-screen locations
        import random
        num_units = random.randint(8, 15)
        print(f"DEBUG: Spawning {num_units} units for {team} team")
        
        # Calculate off-screen spawn positions
        spawn_positions = self._calculate_offscreen_positions(
            camera_x, camera_y, spawner_x, spawner_y, num_units
        )
        print(f"DEBUG: Calculated {len(spawn_positions)} spawn positions")
        
        for i, spawn_pos in enumerate(spawn_positions):
            # Randomly choose unit type with different probabilities
            unit_type = self._choose_random_unit_type()
            print(f"DEBUG: Spawning unit {i+1}/{num_units}: {unit_type} at ({spawn_pos[0]:.1f}, {spawn_pos[1]:.1f})")
            self._spawn_unit_for_team(team, enemy_list, [spawn_pos], unit_type)
            print(f"DEBUG: After spawning, enemy_list length: {len(enemy_list)}")
    
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
    
    def _spawn_unit_for_team(self, team, enemy_list, spawners: List, unit_type=None):
        """Spawn a unit for a specific team from one of their spawners."""
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
            x_offset = 50  # Spawn slightly to the right of spawner
        else:  # Yellow team
            direction = Direction.RIGHT
            warrior_image = "assets/images/Warrior_Yellow.png"
            archer_image = "assets/images/Archer_Yellow.png"
            x_offset = -50  # Spawn slightly to the left of spawner
        
        # Create and add the unit
        if unit_type == "peon":
            unit = Peon(
                spawner[0] + x_offset, 
                spawner[1] + random.uniform(-30, 30),  # Small random Y offset
                direction, 
                targets, 
                image=warrior_image
            )
        else:  # archer
            unit = Archer(
                spawner[0] + x_offset, 
                spawner[1] + random.uniform(-30, 30),  # Small random Y offset
                direction, 
                self.projectiles[team_index], 
                targets, 
                image=archer_image, 
                team=team_index
            )
        
        # Add to appropriate enemy list
        enemy_list.append(unit)
        
        # Add to depth manager for perspective sorting
        if self.depth_manager:
            self.depth_manager.add_sprite(unit)
    
    def get_spawner_count(self) -> Dict[str, int]:
        """Get count of spawners by team for debugging."""
        return {
            "red_spawners": len(self.red_spawners),
            "yellow_spawners": len(self.yellow_spawners)
        }