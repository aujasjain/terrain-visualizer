import math

import pyglet
from pyglet.gl import GL_DEPTH_TEST, GL_TRIANGLES, glClearColor, glClearDepth, glEnable
from pyglet.graphics.shader import Shader, ShaderProgram


VERTEX_SHADER = """#version 330 core
in vec3 position;

uniform vec3 u_camera;
uniform float u_yaw;
uniform float u_pitch;
uniform float u_aspect;
uniform float u_focal;
uniform float u_near;
uniform float u_far;
uniform vec2 u_world_origin;
uniform float u_phase_x;
uniform float u_phase_z;
uniform float u_scale;
uniform float u_warp;
uniform float u_detail;
uniform float u_height_scale;
uniform float u_height_bias;
uniform float u_ridge_mix;
uniform int u_landform;
uniform int u_object_mode;

out vec3 v_world;
out float v_height;
out float v_depth;

float terrain_height(float x, float z) {
    if (u_landform == 0) return 0.0;
    float warped_x = x + sin(z * u_scale * 0.7 + u_phase_z) * u_warp;
    float warped_z = z + cos(x * u_scale * 0.55 + u_phase_x) * u_warp;
    float broad = sin(warped_x * u_scale + u_phase_x) + cos(warped_z * u_scale * 0.8 - u_phase_z) * 0.75;
    float folds = sin((warped_x + warped_z) * u_detail + u_phase_x) * 0.42;
    folds += cos((warped_x - warped_z) * u_detail * 0.73) * 0.36;
    float radial = sin(length(vec2(x, z)) * u_scale * 1.8 + u_phase_z) * 0.25;
    if (u_landform == 1) return sin(warped_x * u_scale * 1.9) * cos(warped_z * u_scale * 1.4) * u_height_scale * 0.35;
    if (u_landform == 2) return abs(sin(warped_x * u_scale * 1.4 + warped_z * u_scale)) * u_height_scale * 0.65 - u_height_scale * 0.25;
    if (u_landform == 3) return (sin(warped_x * u_scale * 2.8) + cos(warped_z * u_scale * 2.1)) * u_height_scale * 0.22;
    return (broad * u_ridge_mix + folds + radial) * u_height_scale + u_height_bias;
}

void main() {
    vec3 world_position = u_object_mode == 1
        ? position
        : vec3(position.x + u_world_origin.x, terrain_height(position.x + u_world_origin.x, position.z + u_world_origin.y), position.z + u_world_origin.y);
    vec3 delta = world_position - u_camera;
    float side = delta.x * cos(u_yaw) - delta.z * sin(u_yaw);
    float depth = delta.x * sin(u_yaw) + delta.z * cos(u_yaw);
    float vertical = delta.y * cos(u_pitch) - depth * sin(u_pitch);
    float focal_y = 1.0 / tan(u_focal * 0.5);
    float focal_x = focal_y / u_aspect;

    gl_Position = vec4(side * focal_x, vertical * focal_y, 0.0, depth);
    gl_Position.z = (-((u_far + u_near) / (u_far - u_near)) * depth + (2.0 * u_far * u_near / (u_far - u_near)));
    v_world = world_position;
    v_height = world_position.y;
    v_depth = depth;
}
"""

FRAGMENT_SHADER = """#version 330 core
in vec3 v_world;
in float v_height;
in float v_depth;

uniform float u_ground_hue_from;
uniform float u_ground_hue_to;
uniform float u_ground_saturation;
uniform float u_ground_value;
uniform float u_pulse_age;
uniform vec2 u_pulse_origin;
uniform vec3 u_sky_rgb;

out vec4 fragment_color;

vec3 hsv(float h, float s, float v) {
    vec3 k = vec3(1.0, 2.0 / 3.0, 1.0 / 3.0);
    vec3 p = abs(fract(vec3(h) + k) * 6.0 - 3.0);
    return v * mix(k.xxx, clamp(p - 1.0, 0.0, 1.0), s);
}

float hue_between(float from_hue, float to_hue, float amount) {
    float delta = mod(to_hue - from_hue + 0.5, 1.0) - 0.5;
    return fract(from_hue + delta * amount);
}

void main() {
    float altitude = clamp((v_height + 10.0) / 20.0, 0.0, 1.0);
    float pulse_radius = max(u_pulse_age, 0.0) * 42.0;
    float pulse_transition = 1.0;
    if (u_pulse_age >= 0.0) {
        float pulse_radius = u_pulse_age * 42.0;
        float distance_from_origin = length(v_world.xz - u_pulse_origin);
        pulse_transition = 1.0 - smoothstep(pulse_radius - 3.0, pulse_radius + 3.0, distance_from_origin);
    }
    float base_hue = hue_between(u_ground_hue_from, u_ground_hue_to, pulse_transition);
    float hue = fract(base_hue + altitude * 0.12 + sin(v_world.x * 0.08 + v_world.z * 0.04) * 0.035);
    float saturation = u_ground_saturation;
    float brightness = clamp(u_ground_value * (0.45 + altitude * 0.55), 0.0, 1.0);
    vec3 terrain = hsv(hue, saturation, brightness);
    float fog = clamp((v_depth - 35.0) / 100.0, 0.0, 0.82);
    fragment_color = vec4(mix(terrain, u_sky_rgb, fog), 1.0);
}
"""


class GPURenderer:
    def __init__(self, window, landscape):
        self.window = window
        self.landscape = landscape
        self.program = ShaderProgram(Shader(VERTEX_SHADER, "vertex"), Shader(FRAGMENT_SHADER, "fragment"))
        self.vertex_list = None
        self.object_list = None
        self.rebuild()
        glEnable(GL_DEPTH_TEST)
        glClearDepth(1.0)

    def rebuild(self):
        if self.vertex_list is not None:
            self.vertex_list.delete()
        vertices = self.landscape.mesh()
        self.vertex_list = self.program.vertex_list(len(vertices) // 3, GL_TRIANGLES, position=("f", vertices))
        object_vertices = self.landscape.object_mesh()
        self.object_list = self.program.vertex_list(len(object_vertices) // 3, GL_TRIANGLES, position=("f", object_vertices)) if object_vertices else None

    def draw(self, camera, yaw, pitch, pulse_age, pulse_origin, hue_shift_from, hue_shift_to):
        if pulse_age < 0:
            sky_shift = hue_shift_to
        else:
            progress = max(0.0, min(1.0, pulse_age / 2.5))
            progress = progress * progress * (3.0 - 2.0 * progress)
            hue_delta = (hue_shift_to - hue_shift_from + 0.5) % 1.0 - 0.5
            sky_shift = (hue_shift_from + hue_delta * progress) % 1.0
        sky_hue = (self.landscape.sky_hue + sky_shift) % 1.0
        sky = self._hsv_to_rgb(sky_hue, self.landscape.sky_saturation, self.landscape.sky_value)
        glClearColor(*sky, 1.0)
        self.window.clear()
        self.program.use()
        self.program["u_camera"] = (camera[0], camera[1], camera[2])
        self.program["u_yaw"] = yaw
        self.program["u_pitch"] = pitch
        self.program["u_aspect"] = self.window.width / max(1, self.window.height)
        self.program["u_focal"] = math.radians(72.0)
        self.program["u_near"] = 0.1
        self.program["u_far"] = 260.0
        origin_x = math.floor(camera[0] / 80.0) * 80.0
        origin_z = math.floor(camera[2] / 80.0) * 80.0
        self.program["u_world_origin"] = (origin_x, origin_z)
        self.program["u_phase_x"] = self.landscape.phase_x
        self.program["u_phase_z"] = self.landscape.phase_z
        self.program["u_scale"] = self.landscape.scale
        self.program["u_warp"] = self.landscape.warp
        self.program["u_detail"] = self.landscape.detail
        self.program["u_height_scale"] = self.landscape.height_scale
        self.program["u_height_bias"] = self.landscape.height_bias
        self.program["u_ridge_mix"] = self.landscape.ridge_mix
        self.program["u_landform"] = self.landscape.landform
        self.program["u_object_mode"] = 0
        self.program["u_ground_hue_from"] = (self.landscape.ground_hue + hue_shift_from) % 1.0
        self.program["u_ground_hue_to"] = (self.landscape.ground_hue + hue_shift_to) % 1.0
        self.program["u_ground_saturation"] = self.landscape.ground_saturation
        self.program["u_ground_value"] = self.landscape.ground_value
        self.program["u_pulse_age"] = pulse_age
        self.program["u_pulse_origin"] = pulse_origin
        self.program["u_sky_rgb"] = sky
        self.vertex_list.draw(GL_TRIANGLES)
        if self.object_list is not None:
            self.program["u_object_mode"] = 1
            self.object_list.draw(GL_TRIANGLES)
            self.program["u_object_mode"] = 0
        self.program.stop()

    @staticmethod
    def _hsv_to_rgb(hue, saturation, value):
        import colorsys
        return colorsys.hsv_to_rgb(hue % 1.0, saturation, value)
