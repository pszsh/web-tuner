import json
import os

def load_config(path="config.json"):
    """Load configuration from a JSON file."""
    with open(path, "r") as f:
        return json.load(f)

OUTPUT_DIR = "generated_data"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def export_json(data, name):
    """Helper function to export a dictionary to a JSON file."""
    path = os.path.join(OUTPUT_DIR, f"{name}.json")
    with open(path, "w") as f:
        json.dump(data, f, indent=2)
    print(f"Exported: {path}")

def generate_chord_definitions(config=None):
    """Generate chord definitions for triads, 7ths, 6ths, and extended chords."""
    chords = {
        "triads": {
            "major": [0, 4, 7],
            "minor": [0, 3, 7],
            "diminished": [0, 3, 6]
        },
        "sevenths": {
            "maj7": [0, 4, 7, 11],
            "min7": [0, 3, 7, 10],
            "dom7": [0, 4, 7, 10],
            "m7b5": [0, 3, 6, 10]
        },
        "sixths": {
            "major6": [0, 4, 7, 9],
            "minor6": [0, 3, 7, 9],
            "dim": [0, 3, 6, 9],
            "6_9": [0, 2, 4, 7, 9]
        },
        "ext": {
            "maj9": [0, 2, 4, 7, 11],
            "sus2": [0, 2, 7],
            "sus4": [0, 5, 7],
            "majmin7": [0, 4, 7, 10],
            "augmented": [0, 4, 8],
            "dim7": [0, 3, 6, 9],
            "#11": [0, 4, 6, 11],
            "5maj9": [0, 2, 7],
            "5maj7_9": [0, 2, 7, 11]
        }
    }
    export_json(chords, "chord_definitions")
    return chords

def main():
    config = load_config()
    generate_chord_definitions(config)

if __name__ == "__main__":
    main()
