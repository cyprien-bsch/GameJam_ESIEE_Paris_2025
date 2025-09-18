import arcade
from enum import Enum

class ItemType(Enum):
    EQUIPMENT = 1       # Équipement standard
    CLEANING_TOOL = 2   # Outils de nettoyage (balai, aspirateur)
    QUEST_ITEM = 3      # Objets de quête spécifiques (gourde d'eau périmée, etc.)
    COLLECTIBLE = 4     # Objets étranges à collectionner
    CURRENCY = 5        # Monnaie pour acheter des améliorations

class Item(arcade.Sprite):
    def __init__(self, x, y, image_path, name, item_type=ItemType.COLLECTIBLE, description="", value=1):
        super().__init__(image_path)
        self.center_x = x
        self.center_y = y
        self.name = name
        self.item_type = item_type
        self.description = description
        self.value = value
        self.collected = False
        self.scale = 0.5  # Échelle par défaut pour les items
    
    def collect(self):
        """Marque l'item comme collecté et le retire de l'écran."""
        self.collected = True
        self.remove_from_sprite_lists()
        return self.name
    
    def use(self):
        """Utilise l'item. À surcharger dans les sous-classes."""
        pass
