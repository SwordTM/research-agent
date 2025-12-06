"""Manim Slides Generator - Creates visual slide presentations for concepts."""

from manim import *
from manim_slides import Slide
from pathlib import Path
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from models.roadmap import Concept, ConceptType


class ConceptSlide(Slide):
    """Base class for concept visualization slides."""
    
    def construct_title_slide(self, title: str, subtitle: str = ""):
        """Create a title slide."""
        title_text = Text(title, font_size=48, weight=BOLD)
        title_text.to_edge(UP, buff=1)
        
        if subtitle:
            subtitle_text = Text(subtitle, font_size=32, color=GRAY)
            subtitle_text.next_to(title_text, DOWN, buff=0.5)
            self.play(Write(title_text), Write(subtitle_text))
            self.next_slide()
            return VGroup(title_text, subtitle_text)
        else:
            self.play(Write(title_text))
            self.next_slide()
            return title_text
    
    def construct_bullet_points(self, points: list, title: str = ""):
        """Create a slide with bullet points."""
        if title:
            title_text = Text(title, font_size=40, weight=BOLD)
            title_text.to_edge(UP, buff=0.5)
            self.play(Write(title_text))
        
        bullets = VGroup()
        for i, point in enumerate(points):
            bullet = Text(f"• {point}", font_size=28)
            bullets.add(bullet)
        
        bullets.arrange(DOWN, aligned_edge=LEFT, buff=0.4)
        if title:
            bullets.next_to(title_text, DOWN, buff=0.8)
        else:
            bullets.move_to(ORIGIN)
        
        for bullet in bullets:
            self.play(FadeIn(bullet, shift=RIGHT))
            self.wait(0.3)
        
        self.next_slide()
        return bullets


class CNNArchitectureSlide(ConceptSlide):
    """Example slide for CNN architecture visualization."""
    
    def construct(self):
        # Title slide
        self.construct_title_slide(
            "Convolutional Neural Network",
            "Architecture Overview"
        )
        
        # Architecture diagram
        title = Text("CNN Layers", font_size=40, weight=BOLD)
        title.to_edge(UP, buff=0.5)
        self.play(Write(title))
        
        # Create layer boxes
        input_layer = Rectangle(width=1.5, height=2, color=BLUE, fill_opacity=0.3)
        input_label = Text("Input\n28×28", font_size=20)
        input_label.move_to(input_layer)
        input_group = VGroup(input_layer, input_label)
        
        conv1 = Rectangle(width=1.2, height=1.8, color=GREEN, fill_opacity=0.3)
        conv1_label = Text("Conv\n32×3×3", font_size=18)
        conv1_label.move_to(conv1)
        conv1_group = VGroup(conv1, conv1_label)
        
        pool1 = Rectangle(width=1, height=1.5, color=YELLOW, fill_opacity=0.3)
        pool1_label = Text("Pool\n2×2", font_size=18)
        pool1_label.move_to(pool1)
        pool1_group = VGroup(pool1, pool1_label)
        
        conv2 = Rectangle(width=0.9, height=1.3, color=GREEN, fill_opacity=0.3)
        conv2_label = Text("Conv\n64×3×3", font_size=16)
        conv2_label.move_to(conv2)
        conv2_group = VGroup(conv2, conv2_label)
        
        fc = Rectangle(width=0.8, height=3, color=RED, fill_opacity=0.3)
        fc_label = Text("FC\n128", font_size=18)
        fc_label.move_to(fc)
        fc_group = VGroup(fc, fc_label)
        
        output = Rectangle(width=0.8, height=1, color=PURPLE, fill_opacity=0.3)
        output_label = Text("Output\n10", font_size=18)
        output_label.move_to(output)
        output_group = VGroup(output, output_label)
        
        # Arrange layers
        layers = VGroup(input_group, conv1_group, pool1_group, conv2_group, fc_group, output_group)
        layers.arrange(RIGHT, buff=0.5)
        layers.move_to(ORIGIN)
        
        # Animate layers
        for layer in layers:
            self.play(FadeIn(layer, shift=UP))
            self.wait(0.2)
        
        # Add arrows
        arrows = VGroup()
        for i in range(len(layers) - 1):
            arrow = Arrow(
                layers[i].get_right(),
                layers[i + 1].get_left(),
                buff=0.1,
                color=WHITE
            )
            arrows.add(arrow)
            self.play(GrowArrow(arrow))
        
        self.next_slide()
        
        # Key features
        self.play(FadeOut(layers), FadeOut(arrows), FadeOut(title))
        self.construct_bullet_points([
            "Convolutional layers extract features",
            "Pooling reduces spatial dimensions",
            "Fully connected layers for classification",
            "ReLU activation for non-linearity"
        ], "Key Features")


def generate_concept_slides(concept: Concept, output_dir: str = "./output") -> str:
    """
    Generate Manim Slides for a given concept.
    
    Args:
        concept: The concept to visualize
        output_dir: Directory to save the generated slides
        
    Returns:
        Path to the generated HTML slides
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # For now, use the CNN example
    # In production, you would dynamically generate slides based on concept type
    slide_class = CNNArchitectureSlide
    
    # Render the slides
    # This would be called via command line in practice
    # manim-slides render script.py SlideClass
    # manim-slides convert SlideClass output.html
    
    html_path = output_path / f"{concept.id}.html"
    
    return str(html_path)


if __name__ == "__main__":
    # Test rendering
    from models.roadmap import Concept, ConceptType
    
    test_concept = Concept(
        id="cnn_architecture",
        title="CNN Architecture",
        description="Convolutional Neural Network architecture",
        concept_type=ConceptType.ARCHITECTURE,
        importance_score=0.9
    )
    
    output = generate_concept_slides(test_concept)
    print(f"Generated slides at: {output}")
