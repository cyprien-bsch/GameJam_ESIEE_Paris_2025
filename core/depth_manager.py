import arcade
from typing import List, Union


class DepthManager:
    """
    Manages depth sorting for sprites based on Y coordinates to create perspective.
    Lower Y coordinates (bottom of screen) appear in front of higher Y coordinates.
    """
    
    def __init__(self):
        self.drawable_sprites = arcade.SpriteList()
        self.needs_sorting = True
        self._last_positions = {}
    
    def add_sprite(self, sprite: arcade.Sprite):
        """Add a sprite to be managed by the depth system."""
        if sprite not in self.drawable_sprites:
            self.drawable_sprites.append(sprite)
            self.needs_sorting = True
    
    def remove_sprite(self, sprite: arcade.Sprite):
        """Remove a sprite from the depth system."""
        if sprite in self.drawable_sprites:
            self.drawable_sprites.remove(sprite)
            if sprite in self._last_positions:
                del self._last_positions[sprite]
    
    def add_sprite_list(self, sprite_list: arcade.SpriteList):
        """Add all sprites from a sprite list to the depth system."""
        for sprite in sprite_list:
            self.add_sprite(sprite)
    
    def check_for_movement(self):
        """Check if any sprites have moved and mark for re-sorting if needed."""
        for sprite in self.drawable_sprites:
            sprite_id = id(sprite)
            current_pos = (sprite.center_x, sprite.center_y)
            
            if sprite_id not in self._last_positions or self._last_positions[sprite_id] != current_pos:
                self._last_positions[sprite_id] = current_pos
                self.needs_sorting = True
                break
    
    def sort_by_depth(self):
        """Sort sprites by Y coordinate for proper depth rendering."""
        if self.needs_sorting:
            # Sort by Y coordinate in descending order (higher Y values drawn first)
            # This makes sprites with lower Y coordinates appear in front
            self.drawable_sprites.sort(key=lambda sprite: sprite.center_y, reverse=True)
            self.needs_sorting = False
    
    def update(self):
        """Update the depth manager - check for movement and sort if needed."""
        self.check_for_movement()
        self.sort_by_depth()
    
    def draw(self):
        """Draw all managed sprites in the correct depth order."""
        self.update()
        self.drawable_sprites.draw()
    
    def clear(self):
        """Clear all sprites from the depth manager."""
        self.drawable_sprites.clear()
        self._last_positions.clear()
        self.needs_sorting = True