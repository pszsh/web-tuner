document.addEventListener("DOMContentLoaded", () => {
  const container = document.getElementById("chord-container");

  // Create controls
  const controls = document.createElement("div");
  controls.style.marginBottom = "1rem";

  const sortRoot = document.createElement("select");
  sortRoot.innerHTML = `
    <option value="">Sort by Root</option>
    <option value="asc">Root A-Z</option>
    <option value="desc">Root Z-A</option>
  `;

  const sortType = document.createElement("select");
  sortType.innerHTML = `
    <option value="">Sort by Type</option>
    <option value="asc">Type A-Z</option>
    <option value="desc">Type Z-A</option>
  `;

  const themeSelect = document.createElement("select");
  themeSelect.innerHTML = `
    <option value="light">ðŸŒž Light</option>
    <option value="default">ðŸŽ¸ Default Theme</option>
    <option value="solarized">ðŸŒ… Solarized</option>
    <option value="tomorrow-amoled">ðŸŒŒ Tomorrow AMOLED</option>
    <option value="darcula">ðŸ§› Darcula</option>
  `;
  controls.appendChild(themeSelect);

  // Create theme <link> tag if not exists
  let themeLink = document.getElementById("theme-stylesheet");
  if (!themeLink) {
    themeLink = document.createElement("link");
    themeLink.rel = "stylesheet";
    themeLink.id = "theme-stylesheet";
    document.head.appendChild(themeLink);
  }

  themeSelect.addEventListener("change", () => {
    const theme = themeSelect.value;
    themeLink.href = `chords-${theme}.css`;
  });

  // Load default
  themeLink.href = "chords-light.css";

  controls.appendChild(sortRoot);
  controls.appendChild(sortType);
  document.body.insertBefore(controls, container);

  function getChordElements() {
    return Array.from(container.getElementsByClassName("chord-card"));
  }

  function extractChordInfo(el) {
    const title = el.querySelector("h2").textContent.trim();
    const [root, ...typeParts] = title.split(" ");
    return {
      root,
      type: typeParts.join(" "),
      element: el
    };
  }

  function sortAndRender(by = "root", order = "asc") {
    const chords = getChordElements().map(extractChordInfo);
    chords.sort((a, b) => {
      const valA = by === "root" ? a.root : a.type;
      const valB = by === "root" ? b.root : b.type;
      return order === "asc"
        ? valA.localeCompare(valB)
        : valB.localeCompare(valA);
    });

    chords.forEach(({ element }) => {
      element.style.transition = 'transform 0.2s ease, opacity 0.3s ease';
      element.style.opacity = '0.9';
      element.style.transform = 'scale(1.01)';
      container.appendChild(element);
      setTimeout(() => {
        element.style.transform = 'scale(1.0)';
        element.style.opacity = '1.0';
      }, 300);
    });
  }

  sortRoot.addEventListener("change", () => {
    if (sortRoot.value) sortAndRender("root", sortRoot.value);
  });

  sortType.addEventListener("change", () => {
    if (sortType.value) sortAndRender("type", sortType.value);
  });

  function renderFretboards() {
    const fretboards = document.querySelectorAll(".fretboard");
    fretboards.forEach(fb => {
      const fingering = JSON.parse(fb.dataset.fingering);
      const maxFret = parseInt(document.getElementById("chord-container").dataset.maxFret, 10);
      const numStrings = parseInt(document.getElementById("chord-container").dataset.numStrings, 10);

      const wrapper = document.createElement("div");
      wrapper.className = "fretboard";

      fb.innerHTML = ""; // Clear existing content
      fb.style.display = "inline-block";
      fb.style.marginBottom = "1rem";

      const fretMatrix = [];
      const fretCounts = {};
      fingering.forEach(f => {
        if (!isNaN(f)) {
          fretCounts[f] = (fretCounts[f] || 0) + 1;
        }
      });

      const entries = Object.entries(fretCounts)
        .filter(([fret, count]) => count >= 2)
        .map(([f, c]) => parseInt(f));

      let barreFretNum = null;
      for (const f of entries.sort((a, b) => a - b)) {
        const allBefore = fingering.every(x => x === "x" || isNaN(x) || parseInt(x) >= f);
        if (allBefore) {
          barreFretNum = f;
          break;
        }
      }

      for (let s = 0; s < numStrings; s++) {
        const stringRow = [];

        for (let f = 1; f <= maxFret; f++) {
          const fret = document.createElement("div");
          fret.className = "fret";
          fret.dataset.row = s;
          fret.dataset.col = f;

          const fretValue = fingering[s];
          const numericFret = parseInt(fretValue, 10);
          if (fretValue === "x" && f === 1) {
            fret.setAttribute('muted', '');
            fret.textContent = "x";
          } else if (fretValue !== "x" && numericFret === f) {
            fret.dataset.dot = "true";
            if (barreFretNum !== null && numericFret === barreFretNum) {
              fret.classList.add("barre");
            }
          }

          stringRow.push(fret);
        }
        fretMatrix.push(stringRow);
      }

      const barreCols = [];
      if (barreFretNum !== null) {
        for (let s = 0; s < numStrings; s++) {
          if (parseInt(fingering[s]) === barreFretNum) {
            barreCols.push(s);
          }
        }
      }

      for (let s = numStrings - 1; s >= 0; s--) {
        const stringRow = document.createElement("div");
        stringRow.className = "fret-row";
        for (let f = 1; f <= maxFret; f++) {
          const fret = fretMatrix[s][f - 1];
          if (fret) {
            stringRow.appendChild(fret);
          }
        }
        wrapper.appendChild(stringRow);
      }

      fb.appendChild(wrapper); // Append before computing barre line

      if (barreFretNum !== null && barreCols.length >= 2) {
        const start = Math.min(...barreCols);
        const end = Math.max(...barreCols);

        const line = document.createElement("div");
        line.className = "barre-line";

        requestAnimationFrame(() => {
          let totalDotCenter = 0;
          let dotCount = 0;

          for (let s = start; s <= end; s++) { // Iterate through all barre strings
              const dotFret = fretMatrix[s][barreFretNum - 1];
              if (dotFret) { // Ensure fret exists (should always exist in barre scenario)
                  const rect = dotFret.getBoundingClientRect();
                  totalDotCenter += (rect.left + rect.right) / 2;
                  dotCount++;
              }
          }
          const avgDotCenter = totalDotCenter / dotCount;
          const parentRect = wrapper.getBoundingClientRect();
          const dotCenter = avgDotCenter - parentRect.left;


          const firstDot = fretMatrix[start][barreFretNum - 1];
          const lastDot  = fretMatrix[end][barreFretNum - 1];
          const rect1 = firstDot.getBoundingClientRect();
          const rect2 = lastDot.getBoundingClientRect();

          const top = Math.min(rect1.top, rect2.top) - parentRect.top;
          const bottom = Math.max(rect1.bottom, rect2.bottom) - parentRect.top;
          const height = bottom - top;


          line.style.top = `${Math.round(top)}px`;
          line.style.height = `${Math.round(height)}px`;
          line.style.left = `${Math.round(dotCenter)}px`;


          // Add finger number (1)
          line.textContent = "|";

          wrapper.appendChild(line);
        });
      }
    });
  }

  renderFretboards();
});