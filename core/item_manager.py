import arcade
from entities.item import Item, ItemType
from entities.animated_coin import AnimatedCoin

class ItemManager:
    """Manages player inventory, coins, and item interactions."""
    
    def __init__(self, player=None):
        self.coins = 0
        self.inventory = {}
        self.coin_sprites = arcade.SpriteList()
        self.coin_display_timer = {}  # Track coin display timers
        self.player = player  # Reference to the player for healing
        
    def add_coins(self, amount: int):
        """Add coins to the player's total. Every 6 coins, reset count to 0 and heal player."""
        self.coins += amount
        
        # Check if we have 6 or more coins
        if self.coins >= 6:
            # Calculate how many HP points to restore (in case we get more than 6 coins at once)
            hp_to_restore = self.coins // 6
            
            # Reset coins to remainder
            self.coins = self.coins % 6
            
            # Heal the player if we have a reference to them
            if self.player and hasattr(self.player, 'heal') and hasattr(self.player, 'current_health') and hasattr(self.player, 'max_health'):
                # Only heal if not at max health
                if self.player.current_health < self.player.max_health:
                    self.player.heal(hp_to_restore)
                    print(f"Player healed for {hp_to_restore} HP! Current health: {self.player.current_health}/{self.player.max_health}")
                else:
                    print(f"Player already at max health ({self.player.max_health}), coins reset but no healing applied.")
        
    def remove_coins(self, amount: int) -> bool:
        """Remove coins from the player's total. Returns True if successful."""
        if self.coins >= amount:
            self.coins -= amount
            return True
        return False
        
    def get_coins(self) -> int:
        """Get the current coin count."""
        return self.coins
        
    def add_item(self, item_name: str, quantity: int = 1):
        """Add an item to the inventory."""
        if item_name in self.inventory:
            self.inventory[item_name] += quantity
        else:
            self.inventory[item_name] = quantity
            
    def remove_item(self, item_name: str, quantity: int = 1) -> bool:
        """Remove an item from the inventory. Returns True if successful."""
        if item_name in self.inventory and self.inventory[item_name] >= quantity:
            self.inventory[item_name] -= quantity
            if self.inventory[item_name] == 0:
                del self.inventory[item_name]
            return True
        return False
        
    def has_item(self, item_name: str, quantity: int = 1) -> bool:
        """Check if the player has a specific item in sufficient quantity."""
        return item_name in self.inventory and self.inventory[item_name] >= quantity
        
    def spawn_coin_display(self, x: float, y: float, value: int = 1):
        """Spawn a coin display at the specified location that will disappear after 1 second."""
        coin = CoinDisplay(x, y, value)
        self.coin_sprites.append(coin)
        self.coin_display_timer[coin] = 1.0  # 1 second display time
        
    def update(self, delta_time: float):
        """Update coin displays and remove expired ones."""
        expired_coins = []
        
        for coin in self.coin_display_timer:
            self.coin_display_timer[coin] -= delta_time
            if self.coin_display_timer[coin] <= 0:
                expired_coins.append(coin)
                
        # Remove expired coins
        for coin in expired_coins:
            coin.remove_from_sprite_lists()
            del self.coin_display_timer[coin]
            
    def draw_coin_displays(self):
        """Draw all active coin displays."""
        self.coin_sprites.draw()
        
    def draw_ui(self, player_x: float, player_y: float):
        """Draw the coin counter above the player."""
        # Draw coin counter above player
        coin_text = f"Coins: {self.coins}"
        arcade.draw_text(
            coin_text,
            player_x - 30,  # Offset to center above player
            player_y + 40,  # Above the player
            arcade.color.YELLOW,
            font_size=12,
            font_name="Arial"
        )


class CoinDisplay(AnimatedCoin):
    """A temporary animated coin sprite that appears when an enemy is defeated."""
    
    def __init__(self, x: float, y: float, value: int = 1):
        super().__init__(x, y, scale=0.9)  # Use AnimatedCoin constructor (3x bigger)
        self.value = value
        
        # Add some upward movement for visual effect
        self.change_y = 50  # Move upward slowly
        
    def update(self, delta_time: float = 1/60):
        """Update the coin display position and animation."""
        super().update(delta_time)  # This will handle the animation
        # Gradually slow down the upward movement
        self.change_y *= 0.95