import arcade
from utils.animation import AnimationUtil


class AnimatedCoin(arcade.Sprite):
    """An animated coin sprite that cycles through frames from MonedaD.png spritesheet."""
    
    def __init__(self, x: float = 0, y: float = 0, scale: float = 1.0):
        super().__init__()
        self.center_x = x
        self.center_y = y
        self.scale = scale
        
        # Animation properties
        self.frame_index = 0
        self.frame_time = 0.0
        self.frame_duration = 0.15  # Time between frames (slower than character animations)
        
        self.init_animation_frames()
        
    def init_animation_frames(self):
        """Initialize the coin animation frames from the spritesheet."""
        # MonedaD.png is 80x16 pixels with 5 columns, so each frame is 16x16
        self.frame_width = 16
        self.frame_height = 16
        self.columns = 5
        
        # Load textures from the coin spritesheet
        try:
            coin_textures = AnimationUtil.load_textures_from_spritesheet(
                "assets/images/MonedaD.png",
                self.frame_width, self.frame_height, self.columns, ["spin"]
            )
            self.animation_frames = coin_textures["spin"]
        except:
            # Fallback: load as single texture if spritesheet parsing fails
            self.animation_frames = [arcade.load_texture("assets/images/MonedaD.png")]
        
        # Set initial texture
        if self.animation_frames:
            self.texture = self.animation_frames[0]
    
    def update(self, delta_time: float = 1/60):
        """Update the coin animation."""
        super().update()
        self.update_animation(delta_time)
    
    def update_animation(self, delta_time: float = 1/60):
        """Update the animation frame."""
        self.frame_time += delta_time
        
        if self.frame_time >= self.frame_duration:
            self.frame_time = 0.0
            self.frame_index = (self.frame_index + 1) % len(self.animation_frames)
            self.texture = self.animation_frames[self.frame_index]