import arcade
from entities.base_character import BaseCharacter


class DragonSpawn(BaseCharacter):
    """A dead dragon that needs to be cleaned by the player."""
    
    def __init__(self, x: float, y: float):
        super().__init__()
        self.center_x = x
        self.center_y = y
        
        # Load the dragon slayed texture
        self.texture = arcade.load_texture("assets/images/dragon_slayed.png")
        
        # Dragon is already dead, so set health to 0
        self.max_health = 0
        self.current_health = 0
        self.is_dead = True
        
        # Dragon doesn't move
        self.change_x = 0
        self.change_y = 0
        
        # Scale the dragon appropriately - make it 10 times smaller
        self.scale = 0.15
        
        # Dragon needs cleaning
        self.needs_cleaning = True
        self.is_cleaned = False
        
        # Interaction properties
        self.can_interact = True
        self.interaction_distance = 64  # Distance at which player can interact
        
    def update(self, delta_time: float = 1/60):
        """Update the dragon (mostly just visual effects)."""
        # Call parent update for any base functionality
        super().update(delta_time)
        
        # Dragon doesn't move or do anything special when dead
        # Could add subtle animation effects here if needed
        pass
    
    def clean(self):
        """Mark the dragon as cleaned and remove it from the game."""
        if self.needs_cleaning:
            self.needs_cleaning = False
            self.is_cleaned = True
            # Remove the dragon from all sprite lists it belongs to
            self.remove_from_sprite_lists()
            print("The dragon has been cleaned and removed!")
    
    def is_player_nearby(self, player_x: float, player_y: float) -> bool:
        """Check if the player is close enough to interact with the dragon."""
        distance = ((self.center_x - player_x) ** 2 + (self.center_y - player_y) ** 2) ** 0.5
        return distance <= self.interaction_distance