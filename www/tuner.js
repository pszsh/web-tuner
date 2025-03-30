document.addEventListener('DOMContentLoaded', () => {
    // Initialize Tone.js
    Tone.start(); // Ensure audio context starts on user interaction

    const synth = new Tone.Synth().toDestination();

    const a440Input = document.getElementById('a440');
    const transposeInput = document.getElementById('transpose');
    const instrumentSelect = document.getElementById('instrument');
    const tuningSelect = document.getElementById('tuning');
    const tuningModeSelect = document.getElementById('tuning-mode'); // New tuning mode selector
    const stringsDiv = document.getElementById('strings');
    const playAllButton = document.getElementById('play-all');
    const outputDiv = document.getElementById('output');

    // Expanded tunings for multiple instruments
    const instrumentTunings = {
        "ukulele": {
            "standard": [67 + 12, 60 + 12, 64 + 12, 69 + 12],  // G5, C5, E5, A5
            "low-g": [55 + 12, 60 + 12, 64 + 12, 69 + 12],     // G4, C5, E5, A5
            "harmonic-minor": [67 + 12, 58 + 12, 62 + 12, 67 + 12], // G5, Bb5, D5, G5
            "suspended-fourth": [67 + 12, 60 + 12, 53 + 12, 60 + 12], // G5, C5, F5, C5
            "lydian": [67 + 12, 60 + 12, 64 + 12, 66 + 12], // G5, C5, E5, F#5
            "diminished": [67 + 12, 59 + 12, 62 + 12, 65 + 12], // G5, B5, D5, F5
            "augmented": [67 + 12, 61 + 12, 64 + 12, 68 + 12], // G5, C#5, E5, G#5
            "open-fifths": [67 + 12, 62 + 12, 69 + 12, 62 + 12], // G5, D5, A5, D5
            "double-unison": [67 + 12, 67 + 12, 60 + 12, 60 + 12], // G5, G5, C5, C5
            "ionian": [67 + 12, 60 + 12, 64 + 12, 69 + 12], // G C E A
            "dorian": [67 + 12, 58 + 12, 62 + 12, 69 + 12], // G Bb D A
            "mixo-dorian": [65 + 12, 58 + 12, 67 + 12, 69 + 12], // F A# G A
            "phrygian": [67 + 12, 56 + 12, 62 + 12, 69 + 12], // G Ab D A
            "mixolydian": [67 + 12, 60 + 12, 62 + 12, 69 + 12], // G C D A
            "aeolian": [67 + 12, 58 + 12, 62 + 12, 67 + 12], // G Bb D G
            "locrian": [67 + 12, 56 + 12, 60 + 12, 67 + 12] // G Ab C G
        },
        "guitar": {
            "standard": [40, 45, 50, 55, 59, 64],  // EADGBE
            "drop-d": [38, 45, 50, 55, 59, 64],   // DADGBE
            "dadgad": [38, 45, 50, 55, 57, 64],   // DADGAD
            "open-g": [38, 43, 47, 50, 55, 59],    // DGDGBD
            "open-d": [38, 43, 50, 54, 57, 64],    // DADF#AD
            "open-c": [36, 40, 43, 48, 52, 57],    // CGCGCE
            "half-step-down": [39, 43, 48, 52, 55, 60], // Eb Ab Db Gb Bb Eb
            "full-step-down": [38, 43, 48, 53, 57, 62], // D G C F A D
            "double-drop-d": [38, 43, 48, 50, 55, 59], // DADGBD
            "new-standard": [36, 40, 45, 50, 54, 59], // CGDAEG
            "nashville-high-strung": [40, 45, 50, 55, 59, 64], // EADGBE but with lighter strings
            "orkney": [36, 40, 43, 36, 40, 43], // CGDGCD
            "modal-tuning-1": [40, 45, 39, 50, 45, 64], // CGDGBE
            "modal-tuning-2": [40, 45, 37, 50, 45, 64]  // EAEAC#E
        }
    };
    let currentTuning = [];
    let currentA440 = 440;
    let currentTranspose = 0;
    let tuningMode = "equal"; // Default tuning mode

    const harmonicFrequencyRatios = {
        "C": 1.0,
        "Db": 17/16,
        "D": 9/8,
        "Eb": 19/16,
        "E": 5/4,
        "F": 21/16,
        "Gb": 11/8,
        "G": 3/2,
        "Ab": 13/8,
        "A": 5/3,
        "Bb": 7/4,
        "B": 15/8,
        "C_octave": 2.0
    };

    function updateInstrument() {
        const selectedInstrument = instrumentSelect.value;
        tuningSelect.innerHTML = ""; // Clear previous tuning options
        Object.keys(instrumentTunings[selectedInstrument]).forEach(tuning => {
            let option = document.createElement("option");
            option.value = tuning;
            option.textContent = tuning.replace(/-/g, " ").toUpperCase();
            tuningSelect.appendChild(option);
        });
        updateTuning(); // Apply default tuning for new instrument
    }

    function updateTuning() {
        const selectedInstrument = instrumentSelect.value;
        const selectedTuning = tuningSelect.value;
        currentTuning = instrumentTunings[selectedInstrument][selectedTuning];
        updateStringButtons(); // Update button labels when tuning changes
    }

    function updateStringButtons() {
        stringsDiv.innerHTML = ""; // Clear existing buttons
        currentTuning.forEach((midiNote, index) => {
            let button = document.createElement("button");
            button.classList.add("string-button");
            button.textContent = `String ${index + 1}`;
            button.addEventListener("click", () => playNote(midiNote));
            stringsDiv.appendChild(button);
        });
    }

    function calculateFrequency(midiNote, tuningMode) {
        const referenceNote = 60; // Middle C in MIDI
        const referenceFreq = currentA440 * Math.pow(2, (referenceNote - 69) / 12); // Middle C in A440

        if (tuningMode === "harmonic") {
            const noteNames = ["C", "Db", "D", "Eb", "E", "F", "Gb", "G", "Ab", "A", "Bb", "B"];
            const octave = Math.floor(midiNote / 12) - 5;
            const note = noteNames[midiNote % 12];
            return referenceFreq * harmonicFrequencyRatios[note] * Math.pow(2, octave);
        } else {
            return 440 * Math.pow(2, (midiNote - 69) / 12);
        }
    }

    function playNote(midiNote) {
        const a440Value = parseFloat(a440Input.value);
        const transposeValue = parseInt(transposeInput.value);

        if (!isNaN(a440Value)) {
            currentA440 = a440Value;
        }
        if (!isNaN(transposeValue)) {
            currentTranspose = transposeValue;
        }

        const adjustedMidiNote = midiNote + currentTranspose;
        const frequency = calculateFrequency(adjustedMidiNote, tuningMode);

        // Adjust frequency based on A440 reference (simplified - for precise tuning, more complex calculations needed)
        const referenceFrequencyRatio = currentA440 / 440;
        const adjustedFrequency = frequency * referenceFrequencyRatio;

        synth.set({ oscillator: { type: 'sine' } });
        synth.triggerAttackRelease(adjustedFrequency, "1.75s"); // Play for 2 seconds duration

        // **DEBUGGING OUTPUTS ADDED HERE**
        console.log("MIDI Note (input):", midiNote);
        console.log("Adjusted MIDI Note (transpose applied):", adjustedMidiNote);
        console.log("Calculated Frequency (before A440 adjust):", frequency);
        console.log("Final Frequency (A440 adjusted):", adjustedFrequency);

        outputDiv.textContent = `Playing: ${Tone.Frequency(adjustedFrequency).toNote()} (Freq: ${adjustedFrequency.toFixed(2)} Hz, A4 Ref: ${currentA440} Hz, Transpose: ${currentTranspose} semitones)`;
    }

    playAllButton.addEventListener('click', () => {
        let delay = 0;
        Tone.Transport.stop();
        Tone.Transport.cancel(); // Clear all scheduled events
        currentTuning.forEach((midiNote, index) => {
            Tone.Transport.scheduleOnce(time => {
                playNote(midiNote);
            }, `+${delay}`); // Small delay between notes
            delay += 0.2; // Increase delay for each note
        });
        Tone.Transport.start(); // Start Tone.Transport
    });

    instrumentSelect.addEventListener('change', updateInstrument);
    tuningSelect.addEventListener('change', updateTuning);
    tuningModeSelect.addEventListener('change', () => {
        tuningMode = tuningModeSelect.value; // Update tuning mode based on user selection
    });
    updateInstrument(); // Initialize instrument and tuning on page load

    a440Input.addEventListener('change', () => {
        outputDiv.textContent = `A4 Reference set to ${a440Input.value} Hz`;
    });

    transposeInput.addEventListener('change', () => {
        outputDiv.textContent = `Transpose set to ${transposeInput.value} semitones`;
    });
});