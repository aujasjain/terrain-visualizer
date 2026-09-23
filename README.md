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

## How the Math Works

The seed selects the terrain's wave phases, scale, height, colours, and
landform. The same seed produces the same result.

### Terrain Height

The vertex shader calculates height from a horizontal position $(x,z)$. It
first warps the coordinates:

$$
x' = x + w \sin(0.7sz + p_z), \qquad
z' = z + w \cos(0.55sx + p_x)
$$

Here, $s$ is scale, $w$ is warp, and $p_x,p_z$ are seeded phase offsets. The
main landform combines broad waves, smaller folds, and a radial wave:

$$
h(x,z) = H\left(r\left[\sin(sx' + p_x) + 0.75\cos(0.8sz' - p_z)\right]
	+ f(x',z') + 0.25\sin(1.8s\sqrt{x^2+z^2}+p_z)\right] + b
$$

where the fold term is:

$$
f(x',z') = 0.42\sin(d(x'+z')+p_x)
		  + 0.36\cos(0.73d(x'-z'))
$$

$H$ controls height, $b$ shifts it vertically, $r$ controls the broad waves,
and $d$ controls fold detail. The other modes use simpler wave formulas; one
returns $h(x,z)=0$ for flat land.

### Mesh and Camera

Python creates a square grid and splits each cell into two triangles. The
vertices start at $y=0$; the vertex shader replaces that value with $h(x,z)$
when drawing.

The camera applies yaw and pitch, then perspective scaling:

$$
f_y = \frac{1}{\tan(\theta/2)}, \qquad f_x = \frac{f_y}{\mathrm{aspect}}
$$

where $\theta$ is the field of view and `aspect` is the window's width divided
by its height. Depth division makes distant points appear smaller.

### Colour and Depth

Terrain colour is calculated in HSV space. Height changes brightness, and
`Space` starts a hue transition. Distance fog blends the terrain toward the
sky colour:

$$
c = (1-q)c_{terrain} + q c_{sky}, \qquad
q = \operatorname{clamp}\left(\frac{depth-35}{100}, 0, 0.82\right)
$$

## Test

```bash
.venv/bin/python -m unittest discover -s tests
```

The tests cover deterministic terrain generation, supported terrain modes,
mesh validity, and seeded floating forms. They do not require an OpenGL window.
