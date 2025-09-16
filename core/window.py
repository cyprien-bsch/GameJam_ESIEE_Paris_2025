import arcade
from entities.player import Player
from entities.enemy import Enemy

class GameWindow(arcade.Window):
    def __init__(self, width, height, title):
        super().__init__(width, height, title)
        self.player = arcade.SpriteList()
        self.enemies = arcade.SpriteList()
        self.set_mouse_visible(True)

    def setup(self):
        self.player.append(Player(100, 100))
        self.enemies.append(Enemy(400, 300))

    def on_draw(self):
        self.clear()
        self.player.draw()
        self.enemies.draw()

    def on_update(self, delta_time):
        self.player.update()
        self.enemies.update()
        if arcade.check_for_collision_with_list(self.player[0], self.enemies):
            self.player[0].color = arcade.color.RED
        else: 
            self.player[0].color = arcade.color.WHITE

    def on_key_press(self, symbol, modifiers):
        if symbol == arcade.key.ESCAPE:
            arcade.close_window()
        if symbol in [arcade.key.UP, arcade.key.DOWN, arcade.key.LEFT, arcade.key.RIGHT]:
            self.player[0].on_key_press(symbol, modifiers)
            self.player.update()
    
    def on_key_release(self, symbol, modifiers):
        if symbol in [arcade.key.UP, arcade.key.DOWN, arcade.key.LEFT, arcade.key.RIGHT]:
            self.player[0].on_key_release(symbol, modifiers)
            self.player.update()