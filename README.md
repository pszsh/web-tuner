# web-tuner

A neat little tool for custom tuning string instruments.

## Setup

```bash
python -m venv venv
source venv/bin/activate  # or 'venv\Scripts\activate' on Windows
pip install -r requirements.txt
```

## Configuration

Edit the `config.json` file to customize your chord generation:

- **Strings**: Add/remove strings and use sharps (`#`), flats (`b`), or a mix.
- **max_fingers**: Set the maximum number of fingers allowed per chord. (Note: Not always respected yet.)
- **max_frets**: Controls how far up the neck to search for chords.

> **Warning**: Even on a powerful computer, setting `max_frets` higher than `5` can slow things down *a lot*. You've been warned!

---

Run
```bash
python main.py > output.txt
```
it will be much slower if you don't output it to a file instead of the shell, but if you want to see the debugging messages, just run the command normally. That's all, playable chord shapes from any tuning you put into the config will be generated.
View them by opening chords.html, which will be generated into www/
