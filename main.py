import arcade
from core.window import GameWindow
import settings

def main():
    window = GameWindow(settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT, settings.SCREEN_TITLE)
    window.setup()
    arcade.run()

if __name__ == "__main__":
    main()
