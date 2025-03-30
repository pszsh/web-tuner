import chords as chord
import intervals as interval
import triad as triads
from utils import load_config
import json
from jinja2 import Template
import os

def render_chords_html():
    config = load_config()
    max_fret = config.get("frets", 4)
    num_strings = len(config.get("tuning", ["G", "C", "E", "A"]))

    with open("generated_data/triad_chords.json") as f:
        matched_chords = json.load(f)

    filtered_chords = []
    for match in matched_chords:
        if "fingering" in match:
            match["fret_positions"] = match["fingering"]
            filtered_chords.append(match)
        else:
            print(f"Warning: Skipped match without fret_positions: {match}")

    with open("template.html") as f:
        template = Template(f.read())

    html = template.render(chords=filtered_chords, max_fret=max_fret, num_strings=num_strings, config=config)
    
    # Inject theme stylesheet link
    theme_link = '<link id="theme-stylesheet" rel="stylesheet" href="chords-default.css">'
    html = html.replace('<head>', f'<head>{theme_link}')

    os.makedirs("www", exist_ok=True)
    with open("www/chords.html", "w") as f:
        f.write(html)
    print("Rendered HTML report to www/chords.html")

def main():
    chord.main()
    interval.main()
    triads.main()
    render_chords_html()

if __name__ == "__main__":
    main()
