# triads.py
import os
import json
from itertools import product, combinations
from utils import load_config, export_json # Import from utils

def build_note_map():
    base_notes = ['C', 'C#', 'D', 'D#', 'E', 'F',
                  'F#', 'G', 'G#', 'A', 'A#', 'B']
    enharmonic_keys = ['Cb', 'B#', 'Db', 'C##', 'Eb', 'D##', 'Fb', 'E#', 'Gb', 'F##', 'Ab', 'G##', 'Bb', 'A##']
    enharmonic_vals = ['B',  'C',  'C#',  'D',   'D#',  'E',   'E',  'F',  'F#', 'G',   'G#', 'A',   'A#', 'B']
    note_map = {}
    reverse_note_map = {}
    for i, note in enumerate(base_notes):
        note_map[note] = i
        reverse_note_map[i] = note
    for enh, actual in zip(enharmonic_keys, enharmonic_vals):
        note_map[enh] = note_map[actual]
    return note_map, reverse_note_map

def load_json(name):
    path = os.path.join("generated_data", f"{name}.json")
    print(f"Loading JSON from: {path}")
    with open(path, "r") as f:
        data = json.load(f)
        print(f"Loaded data from {name}.json: {data}")
        return data

def count_effective_fingers(fingering, num_strings):
    fretted = [(i, int(f)) for i, f in enumerate(fingering) if f not in ("x", "X", "0")]
    if not fretted:
        return 0
    fingers_used = set()
    frets = {}
    for idx, fret in fretted:
        if fret not in frets:
            frets[fret] = []
        frets[fret].append(idx)

    for fret, strings in frets.items():
        if len(strings) >= 2:
            start = min(strings)
            end = max(strings)
            if end - start <= 4:
                valid = True
                for i in range(start, end + 1):
                    val = fingering[i]
                    if val not in ("x", "X"):
                        try:
                            if int(val) < fret:
                                valid = False
                                break
                        except ValueError:
                            valid = False
                            break
                if valid:
                    fingers_used.add((fret, "barre"))

    for fret, strings in frets.items():
        if fret not in fingers_used:
            fingers_used.add(fret)

    return sum(2 if isinstance(f, tuple) and f[1] == "barre" else 1 for f in fingers_used)

def find_chord_fingerings(config):
    chords = load_json("chord_definitions")
    results = []
    generated_fingerings = set()

    string_tunings = config.get("tuning", ["G", "C", "E", "A"])
    NUM_STRINGS = len(string_tunings)
    MAX_FRET = config.get("frets", 4)
    MAX_FINGERS = config.get("max_fingers", 3)
    print(f"MAX_FRET: {MAX_FRET}, MAX_FINGERS: {MAX_FINGERS}")

    all_chords = {}
    for chord_type, chord_group in chords.items(): # Corrected loop
        print(f"Processing chord group: {chord_type}") # Optional debug print
        for chord_name_in_group, intervals in chord_group.items(): # Iterate through chords in each group
            full_chord_name = f"{chord_name_in_group.capitalize()} {chord_type.capitalize()[:-1]}" # Corrected chord name: "Major Triad" -> "Major" and capitalize names
            all_chords[full_chord_name] = {
                "intervals": intervals,
                "type": chord_type,
                "name": chord_name_in_group
            }

    print("All chords to search:", all_chords) # Print the FINAL all_chords dictionary
    print(f"Using tuning: {config.get('tuning')}") # DEBUG: Print tuning

    note_map, reverse_note_map = build_note_map()

    fret_options_no_x = [str(fret) for fret in range(MAX_FRET + 1)] + ["x"]

    print("Starting chord processing loop...")
    for chord_name, chord_data in all_chords.items():
        intervals = chord_data["intervals"]
        print(f"\n--- Processing chord: {chord_name}, intervals: {intervals} ---")
        interval_set = set(intervals)
        print(f"  Target interval set (semitones): {interval_set}") # DEBUG

        semitone_intervals_needed = set() # Assuming intervals in chord_definitions are names, convert to semitones
        for interval_value in intervals: # Now intervals are already semitones from chord_definitions.json
            semitone_intervals_needed.add(interval_value) # Use interval_value directly

        interval_set = semitone_intervals_needed # Now interval_set is in semitones, and correctly populated

        for test_fingering_tuple in product(fret_options_no_x, repeat=NUM_STRINGS):
            test_fingering = list(test_fingering_tuple)

            fretted_notes_semitones = []
            for i, fret in enumerate(test_fingering):
                if fret not in ("x", "X"):
                    tuning_note = string_tunings[i].strip()  # Changed here
                    note_semitone = (note_map[tuning_note] + int(fret)) % 12
                    fretted_notes_semitones.append(note_semitone)

            def is_valid_mute_config(fingering):
                for i, f in enumerate(fingering):
                    if f in ("x", "X") and i not in (0, len(fingering) - 1):
                        return False
                return True

            if not is_valid_mute_config(test_fingering) or count_effective_fingers(test_fingering, NUM_STRINGS) > MAX_FINGERS:
                continue

            unique_fretted_notes = sorted(list(set(fretted_notes_semitones))) # Get unique notes for root check

            if len(unique_fretted_notes) < len(intervals):
                continue

            for potential_root_semitone in unique_fretted_notes: # Iterate through unique notes as potential roots
                intervals_in_fingering = set()
                for note_semitone in fretted_notes_semitones:
                    interval = (note_semitone - potential_root_semitone) % 12
                    intervals_in_fingering.add(interval)

                print(f"  Fingering: {test_fingering}, Notes (semitones): {fretted_notes_semitones}, Potential Root: {reverse_note_map.get(potential_root_semitone)}, Intervals in Fingering: {intervals_in_fingering}, Required Intervals: {interval_set}") # ADD THIS

                if intervals_in_fingering == interval_set: # Changed to EXACT MATCH for primary chords
                    fingering_tuple = tuple(test_fingering)
                    if fingering_tuple not in generated_fingerings:
                        root_note_name_for_chord = reverse_note_map.get(potential_root_semitone, str(potential_root_semitone)) # Get root note name for chord name
                        result_chord_name = f"{root_note_name_for_chord} {chord_name}" # Correctly formatted chord name
                        result = {
                            "chord": result_chord_name, # Use the correctly formatted chord name
                            "fingering": test_fingering,
                            "intervals": list(interval_set),
                            "interval_set": interval_set  # Added new key for interval set
                        }

                        # if count_effective_fingers(test_fingering) < MAX_FINGERS:
                        #     continue
                        def detect_barres(fingering):
                            fretted = [(i, int(f)) for i, f in enumerate(fingering) if f not in ("x", "X", "0")]
                            if not fretted:
                                return []
                            frets = {}
                            for idx, fret in fretted:
                                frets.setdefault(fret, []).append(idx)
                            barres = []
                            for fret, strings in frets.items():
                                if len(strings) < 2:
                                    continue
                                if all(
                                    all(fingering[j] in ("x", "X") or int(fingering[j]) >= fret for j in range(NUM_STRINGS))
                                    for j in strings
                                ):
                                    barres.append({"fret": fret, "strings": strings})
                            return barres
                        
                        result["barres"] = detect_barres(test_fingering)

                        results.append(result)
                        generated_fingerings.add(fingering_tuple)
                        print(f"    Chord FOUND (EXACT MATCH): {result}") # ADD THIS
                        break # Stop after finding exact match for a root


    def count_fingers(fingering):
        return sum(1 for f in fingering if f not in ("x", "X", "0"))

    def is_same_chord(fingering, chord_name, string_tunings, note_map, intervals): # intervals is interval_set here
        print(f"      [is_same_chord] Checking fingering: {fingering}, chord_name: {chord_name}, intervals: {intervals}") # DEBUG
        fretted = []
        for i, f in enumerate(fingering):
            if f not in ("x", "X"):
                tuning_note = string_tunings[i].strip()
                note = (note_map[tuning_note] + int(f)) % 12
                fretted.append(note)
        print(f"      [is_same_chord] Fretted notes (semitones): {fretted}") # DEBUG
        for root in set(fretted):
            interval_set_fingering = set() # rename to avoid confusion
            for note in fretted:
                interval_set_fingering.add((note - root) % 12)
            print(f"      [is_same_chord] Potential root: {reverse_note_map.get(root)}, Interval set from fingering: {interval_set_fingering}") # DEBUG
            if interval_set_fingering == intervals: # Exact match
                print(f"      [is_same_chord] EXACT MATCH FOUND for root {reverse_note_map.get(root)}") # DEBUG
                return True
        print("      [is_same_chord] NO MATCH FOUND") # DEBUG
        return False

    def is_open_chord(fingering):
        return all(f in ("0", "x", "X") for f in fingering)


    # Final global filter pass for safety
    results = [
        r for r in results
        if is_valid_mute_config(r["fingering"]) and count_effective_fingers(r["fingering"], NUM_STRINGS) <= MAX_FINGERS
    ]

    # Group results
    grouped = {}
    for r in results:
        chord_key = r["chord"].replace(" (alt)", "") # Group alternatives with primary chords
        grouped.setdefault(chord_key, []).append(r["fingering"])

    final_results = []

    for chord_name, fingerings in grouped.items():
        checked = set()
        primary = None
        alternatives = []
        has_fretted_primary = False # Flag to track if a fretted primary has been found

        for fingering in fingerings:
            key = tuple(fingering)
            if key in checked:
                continue
            checked.add(key)

            intervals = next((r["intervals"] for r in results if r["fingering"] == list(fingering) and r["chord"] == chord_name), [])
            intervals = set(intervals)
            is_exact = is_same_chord(fingering, chord_name, string_tunings, note_map, intervals) # Check for exact match
            is_open = is_open_chord(fingering)
            is_fretted = not is_open # define fretted as not open


            if is_exact: # Prioritize exact matches
                if is_fretted: # If it's a fretted exact match, it's the best primary
                    if not has_fretted_primary: # if no fretted primary yet, set it.
                        primary = fingering
                        has_fretted_primary = True # Mark that we found a fretted primary
                elif not has_fretted_primary: # if it's an open exact match and no fretted primary yet, consider it primary for now, but can be replaced
                    if primary is None: # if no primary yet (and no fretted primary), set open as primary tentatively
                        primary = fingering
                else: # if it's an open chord and we already HAVE a fretted primary, just add as alternative.
                    alternatives.append(fingering)


            elif not is_exact: # If not an exact match, consider as alternative if primary is already set (exact match found) or if we have ANY primary set.
                if primary is not None:
                    alternatives.append(fingering)
                elif primary is None and not alternatives: # if no primary and no alternatives yet, set as primary if nothing better is found
                    primary = fingering
                else:
                    alternatives.append(fingering)


            simpler_versions = []
            if primary is not None and fingering == primary: # Only find simpler versions for the primary fingering
                for n in range(1, len(fingering)):
                    for idxs in combinations(range(len(fingering)), n):
                        test = fingering[:]
                        for i in idxs:
                            test[i] = "x"
                        if is_valid_mute_config(test) and is_same_chord(test, chord_name, string_tunings, note_map, intervals): # use intervals here
                            simpler_versions.append(list(test)) # Convert tuple to list
                alternatives.extend(simpler_versions) # Add simpler versions to alternatives


        if primary is None and alternatives: # If no primary after all checks, pick first alternative as primary (shouldn't happen often with exact match priority, but for safety)
            primary = alternatives.pop(0)

        if primary is not None: # Ensure we have a primary fingering before adding to final results
            final_results.append({
                "chord": chord_name.replace(" Triad", "").replace(" Seventh", "").replace(" Sixth", "").replace(" Ext.", ""), # Clean up chord name
                "fingering": primary,
                "alternatives": [alt for alt in set(map(tuple, alternatives)) if list(alt) != primary and count_fingers(list(alt)) <= MAX_FINGERS] # Remove duplicates and primary from alternatives and filter by max fingers
            })


    return final_results

def generate_chord_positions():
    return find_chord_fingerings(load_config())

def convert_to_tab(chord_results):
    chord_tabs = []
    for chord in chord_results:
        fretted_notes = chord.get('fingering', [])
        chord_name = chord.get('chord', 'Unknown')

        tab = list(fretted_notes)

        chord_tabs.append({
            "chord": chord_name,
            "tab": tab
        })

def main():
    config = load_config()
    fingerings = find_chord_fingerings(config)
    if not fingerings:
        print("No fingerings found. Check input data and logic.")
    else:
        print("Found", len(fingerings), "fingerings.")
    export_json(fingerings, "triad_chords") # Use utils.export_json
    print(json.dumps(fingerings, indent=2))

if __name__ == "__main__":
    main()