from flask import Flask, render_template_string, request, redirect, url_for
import json
import os

app = Flask(__name__)
DATA_FILE = "mcu_data.json"

DEFAULT_DATA = {
    "universe_info": {
        "title": "Marvel Cinematic Universe (MCU) Syllabus",
        "description": "The Marvel Cinematic Universe is an American media franchise and shared universe centered on superhero films and series."
    },
    "characters": [
        {
            "id": "iron_man",
            "name": "Iron Man (Tony Stark)",
            "alias": "The Genius Billionaire Philanthropist",
            "bio": "Tony Stark is a brilliant industrialist, master engineer, and founding member of the Avengers.",
            "photo_url": "https://images.unsplash.com/photo-1635863138275-d9b33299680b?w=500",
            "movies": [
                {
                    "title": "Iron Man (2008)",
                    "duration": "126 mins",
                    "importance": "Origin story kicking off the entire MCU."
                }
            ]
        }
    ]
}

def load_data():
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(DEFAULT_DATA, f, indent=4)
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

BASE_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MCU Syllabus</title>
    <style>
        :root { --bg: #0b0c10; --card: #1f2833; --red: #e62429; --text: #c5c6c7; --white: #fff; }
        body { font-family: 'Segoe UI', sans-serif; background: var(--bg); color: var(--text); margin: 0; padding: 0; line-height: 1.6; }
        header { background: #12141d; border-bottom: 4px solid var(--red); padding: 1.5rem; text-align: center; }
        header h1 { margin: 0; color: var(--white); }
        nav { background: #12141d; padding: 0.8rem; text-align: center; border-bottom: 1px solid #2e3147; }
        nav a { color: var(--text); text-decoration: none; margin: 0 1rem; font-weight: 600; }
        nav a:hover { color: var(--red); }
        .container { max-width: 800px; margin: 2rem auto; padding: 0 1rem; }
        .card { background: var(--card); border-radius: 8px; padding: 1.5rem; margin-bottom: 1.5rem; border: 1px solid #2e3147; }
        .btn { background: var(--red); color: white; padding: 0.5rem 1rem; border-radius: 4px; text-decoration: none; display: inline-block; font-weight: bold; border: none; cursor: pointer; }
        .btn:hover { background: #c51d22; }
        input, textarea { width: 100%; padding: 0.6rem; margin: 0.4rem 0 1rem 0; background: #0b0c10; border: 1px solid #2e3147; color: white; border-radius: 4px; box-sizing: border-box; }
        label { color: var(--white); font-weight: 600; font-size: 0.9rem; }
        .char-img { width: 100%; height: 250px; object-fit: cover; border-radius: 6px; margin-bottom: 1rem; }
        .movie-box { background: rgba(0,0,0,0.25); border-left: 4px solid var(--red); padding: 1rem; margin-bottom: 0.8rem; border-radius: 0 4px 4px 0; }
        .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(230px, 1fr)); gap: 1rem; }
    </style>
</head>
<body>
    <header><h1>Marvel Cinematic Universe</h1></header>
    <nav>
        <a href="/">Home</a>
        <a href="/admin">⚙️ Web Admin Panel</a>
    </nav>
    <div class="container">
        {% block content %}{% endblock %}
    </div>
</body>
</html>
"""

@app.route("/")
def index():
    data = load_data()
    return render_template_string(BASE_TEMPLATE.replace("{% block content %}", """
    <div class="card">
        <h2>About the MCU</h2>
        <p>{{ data.universe_info.description }}</p>
    </div>
    <h2>Character Syllabus Directory</h2>
    <div class="grid">
        {% for char in data.characters %}
        <div class="card" style="text-align: center;">
            {% if char.photo_url %}<img src="{{ char.photo_url }}" class="char-img">{% endif %}
            <h3>{{ char.name }}</h3>
            <p style="color: #ff6569; font-size: 0.85rem;">{{ char.alias }}</p>
            <a href="/character/{{ char.id }}" class="btn">View Syllabus</a>
        </div>
        {% endfor %}
    </div>
    """), data=data)

@app.route("/character/<char_id>")
def character_detail(char_id):
    data = load_data()
    char = next((c for c in data["characters"] if c["id"] == char_id), None)
    if not char: return "Character not found", 404
    return render_template_string(BASE_TEMPLATE.replace("{% block content %}", """
    <div class="card">
        {% if char.photo_url %}<img src="{{ char.photo_url }}" class="char-img" style="height: 320px;">{% endif %}
        <h2>{{ char.name }}</h2>
        <p style="color: #ff6569; font-weight: bold;">{{ char.alias }}</p>
        <p>{{ char.bio }}</p>
    </div>
    <div class="card">
        <h2>Cinematic Syllabus & Movies</h2>
        {% for m in char.movies %}
        <div class="movie-box">
            <div style="font-size: 1.1rem; font-weight: bold; color: white;">{{ m.title }}</div>
            <div style="color: #ff6569; font-size: 0.9rem;">Screen Time: {{ m.duration }}</div>
            <p><strong>Importance:</strong> {{ m.importance }}</p>
        </div>
        {% endfor %}
    </div>
    <a href="/" class="btn">← Back to Home</a>
    """), char=char)

@app.route("/admin", methods=["GET", "POST"])
def admin():
    data = load_data()
    if request.method == "POST":
        name = request.form.get("name")
        char_id = name.lower().replace(" ", "_").replace("(", "").replace(")", "")
        alias = request.form.get("alias")
        bio = request.form.get("bio")
        photo_url = request.form.get("photo_url")
        
        movie_title = request.form.get("movie_title")
        movie_duration = request.form.get("movie_duration")
        movie_importance = request.form.get("movie_importance")
        
        new_movie = {"title": movie_title, "duration": movie_duration, "importance": movie_importance} if movie_title else None

        existing = next((c for c in data["characters"] if c["id"] == char_id), None)
        if existing:
            if photo_url: existing["photo_url"] = photo_url
            if bio: existing["bio"] = bio
            if new_movie: existing["movies"].append(new_movie)
        else:
            data["characters"].append({
                "id": char_id, "name": name, "alias": alias, "bio": bio, "photo_url": photo_url,
                "movies": [new_movie] if new_movie else []
            })
        save_data(data)
        return redirect(url_for('admin'))

    return render_template_string(BASE_TEMPLATE.replace("{% block content %}", """
    <div class="card">
        <h2>⚙️ Web Admin Dashboard</h2>
        <p>Fill out this form directly on the website to add characters and movies instantly!</p>
        <form method="POST">
            <label>Character Full Name:</label>
            <input type="text" name="name" placeholder="e.g. Thor Odinson" required>
            <label>Alias / Title:</label>
            <input type="text" name="alias" placeholder="e.g. God of Thunder">
            <label>Character Biography:</label>
            <textarea name="bio" rows="3" placeholder="Brief character background..."></textarea>
            <label>Photo Image URL:</label>
            <input type="text" name="photo_url" placeholder="https://image-link.com/thor.jpg">
            
            <hr style="border-color: #2e3147; margin: 1.5rem 0;">
            <h3>Movie Appearance</h3>
            <label>Movie Title & Year:</label>
            <input type="text" name="movie_title" placeholder="e.g. Thor (2011)">
            <label>Duration / Screen Time:</label>
            <input type="text" name="movie_duration" placeholder="e.g. 115 mins (Lead)">
            <label>Narrative Importance:</label>
            <textarea name="movie_importance" rows="2" placeholder="Why this film matters..."></textarea>
            
            <button type="submit" class="btn" style="width: 100%; margin-top: 1rem;">Add to Website</button>
        </form>
    </div>
    """))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)