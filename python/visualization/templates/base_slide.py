from manim import *
from manim_slides import Slide

class BaseSlide(Slide):
    """Base class for all research paper slides with consistent styling."""
    
    def construct(self):
        # Set default colors
        self.camera.background_color = "#1e1e1e"
        Text.set_default(font="Sans-serif", color=WHITE)
        Tex.set_default(color=WHITE)
        MathTex.set_default(color=WHITE)
        
    def create_title(self, text):
        """Create a standard title."""
        title = Text(text, font_size=48, weight=BOLD).to_edge(UP)
        underline = Line(LEFT, RIGHT, color=BLUE).match_width(title).next_to(title, DOWN, buff=0.1)
        return VGroup(title, underline)
        
    def create_bullet_list(self, items, width=10):
        """Create a bulleted list."""
        bullets = VGroup()
        for item in items:
            dot = Dot(color=BLUE)
            text = Text(item, font_size=32).next_to(dot, RIGHT)
            line = VGroup(dot, text)
            bullets.add(line)
            
        bullets.arrange(DOWN, aligned_edge=LEFT, buff=0.5)
        return bullets
