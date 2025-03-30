import os
import json
from itertools import combinations, product
from triad import build_note_map

NOTE_INDEX, _ = build_note_map()

def load_config(path="config.json"):
    print(f"Loading config from: {path}") # DEBUG
    with open(path, "r") as f:
        config = json.load(f)
        print(f"Loaded config: {config}") # DEBUG
        return config

def interval_name(semitones):
    interval_map = {
        0: "P1", 1: "m2", 2: "M2", 3: "m3", 4: "M3", 5: "P4",
        6: "TT", 7: "P5", 8: "m6", 9: "M6", 10: "m7", 11: "M7"
    }
    return interval_map.get(semitones % 12, f"+{semitones}")

def export_json(data, name):
    output_dir = "generated_data"
    os.makedirs(output_dir, exist_ok=True)
    path = os.path.join(output_dir, f"{name}.json")
    with open(path, "w") as f:
        json.dump(data, f, indent=2)
    print(f"Exported: {path}")

def generate_interval_pairs(config):
    tuning = config["tuning"]
    max_frets = config.get("frets")
    num_strings = len(tuning)

    interval_data = []
    pair_count_before_filter = 0

    print(f"Number of strings (num_strings): {num_strings}") # DEBUG: Print num_strings value

    for size in range(2, num_strings + 1):  # Support chord shapes of size 2 to full string count
        for string_group in combinations(range(num_strings), size):
            print(f"String group: {string_group}")  # DEBUG
    for fret_group in product(range(6), repeat=size):
                print(f"  Fret group: {fret_group}")  # DEBUG
                pair_count_before_filter += 1

                pairwise_intervals = []
                for i in range(size):
                    for j in range(i + 1, size):
                        s_i, s_j = string_group[i], string_group[j]
                        f_i, f_j = fret_group[i], fret_group[j]
                        semitones = (NOTE_INDEX[tuning[s_j]] + f_j - NOTE_INDEX[tuning[s_i]] - f_i) % 12
                        pairwise_intervals.append({
                            "strings": [s_i, s_j],
                            "name": interval_name(semitones),
                            "semitones": semitones
                        })

                interval_data.append({
                    "string_group": list(string_group),
                    "fret_positions": list(fret_group),
                    "intervals": pairwise_intervals
                })

    export_json(interval_data, "interval_triads")
    print(f"Generated {len(interval_data)} interval triads with max_frets={max_frets} and {num_strings} strings.") # Changed print message
    print(f"Total pairs generated before shape filter: {pair_count_before_filter}") # Renamed print message
    return interval_data

def main():
    config = load_config()
    generate_interval_pairs(config)

if __name__ == "__main__":
    main()