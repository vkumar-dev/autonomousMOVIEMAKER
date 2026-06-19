import os
import json
from pathlib import Path

def update_gallery():
    print("🎬 Updating Movie Gallery...")
    output_dir = Path("output")
    docs_dir = Path("docs")
    index_file = docs_dir / "index.html"
    
    if not output_dir.exists():
        print("ℹ️ No output directory found. Skipping gallery update.")
        return

    movies = []
    # Each movie is in its own subdirectory in output/
    for movie_path in output_dir.iterdir():
        if movie_path.is_dir():
            script_json = movie_path / "script.json"
            if script_json.exists():
                with open(script_json, "r") as f:
                    data = json.load(f)
                    
                # Look for mp4 files in the output directory
                video_file = None
                potential_video = movie_path / f"{movie_path.name}_full.mp4"
                
                if potential_video.exists():
                    video_file = f"output/{movie_path.name}/{potential_video.name}"
                else:
                    # Look for any mp4 ending with _full.mp4 in the folder
                    full_mp4s = list(movie_path.glob("*_full.mp4"))
                    if full_mp4s:
                        video_file = f"output/{movie_path.name}/{full_mp4s[0].name}"
                    else:
                        # Fallback to any mp4
                        mp4s = list(movie_path.glob("*.mp4"))
                        if mp4s:
                            video_file = f"output/{movie_path.name}/{mp4s[0].name}"
                
                movies.append({
                    "title": data.get("title", "Untitled"),
                    "logline": data.get("logline", ""),
                    "genre": ", ".join(data.get("genre", [])),
                    "duration": f"{data.get('total_duration', 0) / 60:.1f}m",
                    "folder": movie_path.name,
                    "video": video_file,
                    "path": f"output/{movie_path.name}"
                })

    if not movies:
        print("ℹ️ No movies found in output directory.")
        return

    # Generate the gallery HTML
    gallery_html = """
    <section class="gallery" id="movie-catalog">
        <div class="container">
            <div class="section-header">
                <span class="section-label">🎬 Premiere</span>
                <h2>Movie Catalog</h2>
                <p>Browse all autonomously generated cinematic masterpieces</p>
            </div>
            <div class="features-grid">
    """
    
    for movie in movies:
        video_link = f'<a href="../{movie["video"]}" class="btn btn-primary" style="margin-top: 10px;">Watch Movie</a>' if movie["video"] else '<span style="color: var(--text-secondary); font-size: 0.8rem;">Processing video...</span>'
        gallery_html += f"""
                <div class="feature-card">
                    <div class="feature-icon">📽️</div>
                    <h3>{movie['title']}</h3>
                    <p><strong>Genre:</strong> {movie['genre']} | <strong>Duration:</strong> {movie['duration']}</p>
                    <p style="margin-top: 8px;">{movie['logline']}</p>
                    <div style="margin-top: 16px; display: flex; gap: 10px; align-items: center;">
                        <a href="../{movie['path']}/README.md" class="btn btn-secondary">Read Script</a>
                        {video_link}
                    </div>
                </div>
        """
        
    gallery_html += """
            </div>
        </div>
    </section>
    """

    # Inject into index.html
    # We'll replace the Features section or insert after Hero
    with open(index_file, "r") as f:
        content = f.read()

    # Find where to inject. We'll look for <!-- Hero Section --> end or <!-- Features Section --> start
    if "<!-- Movie Gallery -->" in content:
        # Update existing gallery
        import re
        content = re.sub(r'<!-- Movie Gallery -->.*?<!-- End Movie Gallery -->', 
                         f'<!-- Movie Gallery -->{gallery_html}<!-- End Movie Gallery -->', 
                         content, flags=re.DOTALL)
    else:
        # Insert before Features Section
        content = content.replace('<!-- Features Section -->', 
                                f'<!-- Movie Gallery -->{gallery_html}<!-- End Movie Gallery -->\n    <!-- Features Section -->')

    with open(index_file, "w") as f:
        f.write(content)
        
    print(f"✅ Gallery updated with {len(movies)} movies.")

if __name__ == "__main__":
    update_gallery()
