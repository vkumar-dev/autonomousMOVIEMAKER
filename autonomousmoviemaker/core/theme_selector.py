"""
Theme Matrix Selector for autonomousMOVIEMAKER.

Randomly selects values from different dimensions in the movie theme matrix
and formats them into a cohesive movie concept.
"""

import json
import random
from pathlib import Path
from typing import Dict, Any

THEME_MATRIX_FILE = Path(__file__).parent / "theme_matrix.json"
OUTPUT_FILE = Path.cwd() / "selected_theme.json"

def load_theme_matrix() -> Dict[str, list]:
    """Load the movie theme matrix configuration."""
    with open(THEME_MATRIX_FILE, "r") as f:
        return json.load(f)

def pick_random(lst: list) -> Any:
    """Pick a random element from a list."""
    return random.choice(lst)

def generate_movie_concept() -> Dict[str, Any]:
    """
    Select random elements from each dimension in the matrix config,
    and generate a movie concept.
    """
    matrix = load_theme_matrix()
    
    genre = pick_random(matrix["genres"])
    visual_style = pick_random(matrix["visual_styles"])
    mood = pick_random(matrix["moods"])
    color_palette = pick_random(matrix["color_palettes"])
    setting = pick_random(matrix["settings"])
    theme = pick_random(matrix["themes"])
    camera_style = pick_random(matrix["camera_styles"])
    pacing = pick_random(matrix["pacing_types"])
    
    # Title templates suitable for movies
    title_templates = [
        "Echoes of {theme_short}",
        "The {genre} Paradox",
        "Chronicles of {setting_short}",
        "Shadows in the {setting_short}",
        "Project {theme_short}",
        "{genre}: Rise of the Machine",
        "Lost in {setting_short}",
        "The {theme_short} Conspiracy",
        "Before the {setting_short} Fades",
        "Fragments of {theme_short}"
    ]
    
    # Extract short versions of setting and theme for title templates
    setting_short = setting.replace("A ", "").replace("An ", "").split(" at ")[0].split(" in ")[0].split(" beneath ")[0].strip().title()
    theme_short = theme.replace("The ", "").replace("A ", "").split(" that ")[0].split(" across ")[0].split(" behind ")[0].strip().title()
    if len(theme_short.split()) > 4:
        theme_short = " ".join(theme_short.split()[:3])
        
    title_template = pick_random(title_templates)
    title = title_template.format(
        setting_short=setting_short,
        theme_short=theme_short,
        genre=genre.split()[0]
    )
    
    # Build prompt/concept summary
    concept_prompt = (
        f"A {genre} movie set in {setting.lower()}. "
        f"The story explores the theme of {theme.lower()}. "
        f"The visual style is {visual_style.lower()} with a {color_palette.lower()} color palette. "
        f"The camera work features {camera_style.lower()} to create a {mood.lower()} atmosphere with {pacing.lower()} pacing."
    )
    
    concept_data = {
        "title": title,
        "genre": genre,
        "visual_style": visual_style,
        "mood": mood,
        "color_palette": color_palette,
        "setting": setting,
        "theme": theme,
        "camera_style": camera_style,
        "pacing": pacing,
        "prompt": concept_prompt
    }
    
    return concept_data

def main():
    print("🎲 Selecting random movie concept from matrix...")
    try:
        concept = generate_movie_concept()
        
        print("\n🎬 --- SELECTED MOVIE CONCEPT ---")
        print(f"📌 Title:         {concept['title']}")
        print(f"🎭 Genre:         {concept['genre']}")
        print(f"🎨 Visual Style:  {concept['visual_style']}")
        print(f"🌈 Color Palette: {concept['color_palette']}")
        print(f"🏢 Setting:       {concept['setting']}")
        print(f"🔑 Core Theme:    {concept['theme']}")
        print(f"🎥 Camera Style:  {concept['camera_style']}")
        print(f"⏱️ Pacing:        {concept['pacing']}")
        print("\n📝 FULL PROMPT CONCEPT:")
        print(concept["prompt"])
        print("---------------------------------\n")
        
        # Save to selected_theme.json
        with open(OUTPUT_FILE, "w") as f:
            json.dump(concept, f, indent=2)
        print(f"✅ Saved concept to {OUTPUT_FILE}")
        
    except Exception as e:
        print(f"❌ Error during concept generation: {e}")
        exit(1)

if __name__ == "__main__":
    main()
