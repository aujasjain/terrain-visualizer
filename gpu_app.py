import math
import random

import pyglet
from pyglet.gl import GL_DEPTH_TEST, glDisable, glEnable
from pyglet import shapes
from pyglet.window import key, mouse

from .gpu_renderer import GPURenderer
from .landscape import Landscape


class ProceduralTerrainApp(pyglet.window.Window):
    def __init__(self):
        super().__init__(width=1280, height=760, caption="Procedural Terrain", resizable=True, vsync=True)
        self.keys = key.KeyStateHandler()
        self.push_handlers(self.keys)
        self.landscape = Landscape(19)
        self.renderer = GPURenderer(self, self.landscape)
        self.camera = [0.0, 12.0, -22.0]
        self.yaw = 0.0
        self.pitch = -0.08
        self.pulse_age = -1.0
        self.pulse_origin = [0.0, 30.0]
        self.hue_shift_from = 0.0
        self.hue_shift_to = 0.0
        self.controls = pyglet.text.Label(
            "N: NEW TERRAIN     SPACE: SHIFT COLOUR     WASD/ARROWS: MOVE     Q/E: ALTITUDE     DRAG: LOOK     SHIFT: FAST",
            x=22,
            y=13,
            color=(255, 255, 255, 255),
            font_name="Menlo",
            font_size=13,
        )
        self.controls_shadow = pyglet.text.Label(
            self.controls.text,
            x=23,
            y=12,
            color=(0, 0, 0, 220),
            font_name="Menlo",
            font_size=13,
        )
        self.hud_background = shapes.Rectangle(0, 0, self.width, 68, color=(0, 0, 0))
        self.hud_background.opacity = 190
        pyglet.clock.schedule_interval(self.update, 1 / 60)

    def on_resize(self, width, height):
        self.hud_background.width = width
        return super().on_resize(width, height)

    def on_key_press(self, symbol, modifiers):
        if symbol == key.ESCAPE:
            self.close()
        elif symbol == key.N:
            self.new_landscape()
        elif symbol == key.SPACE:
            self.hue_shift_from = self.hue_shift_to
            self.hue_shift_to = (self.hue_shift_to + 0.37) % 1.0
            self.landscape.permanent_hue_shift = self.hue_shift_to
            self.pulse_age = 0.0
            self.pulse_origin = [self.camera[0] + 30.0 * math.sin(self.yaw), self.camera[2] + 30.0 * math.cos(self.yaw)]

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        if buttons & mouse.LEFT:
            self.yaw += dx * 0.004
            self.pitch = max(-1.1, min(1.1, self.pitch + dy * 0.003))

    def new_landscape(self):
        self.landscape = Landscape(random.randrange(1, 2_000_000_000))
        self.renderer.landscape = self.landscape
        self.renderer.rebuild()
        self.pulse_age = -1.0
        self.hue_shift_from = 0.0
        self.hue_shift_to = 0.0

    def update(self, dt):
        dt = min(dt, 0.05)
        speed = 28.0 if self.keys[key.LSHIFT] or self.keys[key.RSHIFT] else 12.0
        forward = int(self.keys[key.W] or self.keys[key.UP]) - int(self.keys[key.S] or self.keys[key.DOWN])
        strafe = int(self.keys[key.D] or self.keys[key.RIGHT]) - int(self.keys[key.A] or self.keys[key.LEFT])
        if forward or strafe:
            length = max(1.0, (forward * forward + strafe * strafe) ** 0.5)
            forward /= length
            strafe /= length
            self.camera[0] += (math.sin(self.yaw) * forward + math.cos(self.yaw) * strafe) * speed * dt
            self.camera[2] += (math.cos(self.yaw) * forward - math.sin(self.yaw) * strafe) * speed * dt
        self.camera[1] += (int(self.keys[key.E]) - int(self.keys[key.Q])) * speed * dt
        if self.pulse_age >= 0:
            self.pulse_age += dt
            if self.pulse_age > 2.5:
                self.pulse_age = -1.0
                self.hue_shift_from = self.hue_shift_to

    def on_draw(self):
        self.renderer.draw(
            self.camera,
            self.yaw,
            self.pitch,
            self.pulse_age,
            self.pulse_origin,
            self.hue_shift_from,
            self.hue_shift_to,
        )
        glDisable(GL_DEPTH_TEST)
        self.hud_background.draw()
        self.controls_shadow.draw()
        self.controls.draw()
        glEnable(GL_DEPTH_TEST)


def main():
    ProceduralTerrainApp()
    pyglet.app.run()


if __name__ == "__main__":
    main()
