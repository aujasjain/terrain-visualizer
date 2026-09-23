# Terrain Visualizer

A real-time procedural terrain explorer built with Python, pyglet, and OpenGL.
Each generated landscape is seeded, so the same seed produces the same terrain,
palette, and floating forms.

## Requirements

- Python 3.10 or newer
- An OpenGL-capable desktop environment

## Install

From the repository root:

```bash
python -m venv .venv
.venv/bin/python -m pip install -e .
```

On Windows, use `.venv\\Scripts\\python` instead of `.venv/bin/python`.

## Run

```bash
.venv/bin/python -m visualizer
```

Controls are shown in the application window:

- `N`: generate a new terrain
- `Space`: shift the colour palette
- `WASD` or arrow keys: move
- `Q` / `E`: change altitude
- Drag with the left mouse button: look around
- `Shift`: move faster
- `Esc`: quit

## Disclaimer

I mostly did the computational part, i,e, generating the terrain, and used AI for the OpenGL visualization part.
