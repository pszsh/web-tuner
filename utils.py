# web-tuner/utils.py
import json
import os

def load_config(path="config.json"):
    with open(path) as f:
        return json.load(f)

def export_json(data, name, output_dir="generated_data"): # Added output_dir as parameter with default
    os.makedirs(output_dir, exist_ok=True)
    path = os.path.join(output_dir, f"{name}.json")
    with open(path, "w") as f:
        json.dump(data, f, indent=2)
    print(f"Exported: {path}")