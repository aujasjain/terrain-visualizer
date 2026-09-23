import math
import random


class Landscape:
    def __init__(self, seed: int):
        rng = random.Random(seed)
        self.seed = seed
        self.phase_x = rng.random() * math.tau
        self.phase_z = rng.random() * math.tau
        self.scale = rng.uniform(0.025, 0.18)
        self.warp = rng.uniform(0.0, 18.0)
        self.detail = rng.uniform(0.05, 0.5)
        self.height_scale = rng.uniform(0.0, 24.0)
        self.height_bias = rng.uniform(-8.0, 8.0)
        self.ridge_mix = rng.uniform(0.1, 1.8)
        self.landform = rng.randrange(5)
        self.ground_hue = rng.random()
        self.sky_hue = (self.ground_hue + rng.uniform(0.08, 0.92)) % 1.0
        self.sky_saturation = rng.uniform(0.2, 1.0)
        self.sky_value = rng.uniform(0.3, 0.95)
        self.ground_saturation = rng.uniform(0.45, 1.0)
        self.ground_value = rng.uniform(0.45, 0.95)
        self.permanent_hue_shift = 0.0
        self.floating_objects = []
        if rng.random() < 0.68:
            for _ in range(rng.randint(4, 16)):
                self.floating_objects.append(
                    (
                        rng.uniform(-150.0, 150.0),
                        rng.uniform(8.0, 34.0),
                        rng.uniform(-150.0, 150.0),
                        rng.uniform(1.0, 8.0),
                        rng.uniform(1.0, 8.0),
                        rng.uniform(3.0, 42.0),
                        rng.uniform(0.0, math.tau),
                        rng.randrange(4),
                    )
                )

    def height(self, x: float, z: float) -> float:
        if self.landform == 0:
            return 0.0
        warped_x = x + math.sin(z * self.scale * 0.7 + self.phase_z) * self.warp
        warped_z = z + math.cos(x * self.scale * 0.55 + self.phase_x) * self.warp
        broad = math.sin(warped_x * self.scale + self.phase_x)
        broad += math.cos(warped_z * self.scale * 0.8 - self.phase_z) * 0.75
        folds = math.sin((warped_x + warped_z) * self.detail + self.phase_x) * 0.42
        folds += math.cos((warped_x - warped_z) * self.detail * 0.73) * 0.36
        radial = math.sin(math.hypot(x, z) * self.scale * 1.8 + self.phase_z) * 0.25
        if self.landform == 1:
            return math.sin(warped_x * self.scale * 1.9) * math.cos(warped_z * self.scale * 1.4) * self.height_scale * 0.35
        if self.landform == 2:
            return abs(math.sin(warped_x * self.scale * 1.4 + warped_z * self.scale)) * self.height_scale * 0.65 - self.height_scale * 0.25
        if self.landform == 3:
            return (math.sin(warped_x * self.scale * 2.8) + math.cos(warped_z * self.scale * 2.1)) * self.height_scale * 0.22
        return (broad * self.ridge_mix + folds + radial) * self.height_scale + self.height_bias

    def mesh(self, radius: float = 220.0, resolution: int = 150) -> list[float]:
        vertices = []
        step = radius * 2 / resolution
        for ix in range(resolution):
            x0 = -radius + ix * step
            x1 = x0 + step
            for iz in range(resolution):
                z0 = -radius + iz * step
                z1 = z0 + step
                a = (x0, 0.0, z0)
                b = (x1, 0.0, z0)
                c = (x1, 0.0, z1)
                d = (x0, 0.0, z1)
                vertices.extend((*a, *b, *c, *a, *c, *d))
        return vertices

    def object_mesh(self) -> list[float]:
        vertices = []
        for x, y, z, width, depth, height, _phase, shape in self.floating_objects:
            if shape == 1:
                top = (x, y + height / 2, z)
                bottom = (x, y - height / 2, z)
                corners = ((x - width / 2, y, z - depth / 2), (x + width / 2, y, z - depth / 2), (x + width / 2, y, z + depth / 2), (x - width / 2, y, z + depth / 2))
                faces = ((top, corners[0], corners[1]), (top, corners[1], corners[2]), (top, corners[2], corners[3]), (top, corners[3], corners[0]), (bottom, corners[1], corners[0]), (bottom, corners[2], corners[1]), (bottom, corners[3], corners[2]), (bottom, corners[0], corners[3]))
                for face in faces:
                    for point in face:
                        vertices.extend(point)
                continue
            x0, x1 = x - width / 2, x + width / 2
            y0, y1 = y - height / 2, y + height / 2
            z0, z1 = z - depth / 2, z + depth / 2
            if shape == 2:
                top_width, top_depth = width * 0.28, depth * 0.28
                corners = ((x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0), (x - top_width / 2, y1 + height * 0.35, z - top_depth / 2), (x + top_width / 2, y1 + height * 0.35, z - top_depth / 2), (x + top_width / 2, y1 + height * 0.35, z + top_depth / 2), (x - top_width / 2, y1 + height * 0.35, z + top_depth / 2))
                faces = ((0, 1, 5), (0, 5, 4), (1, 2, 6), (1, 6, 5), (2, 3, 7), (2, 7, 6), (3, 0, 4), (3, 4, 7), (4, 5, 6), (4, 6, 7))
            elif shape == 3:
                corners = ((x0, y0, z0), (x1, y0, z0), (x1, y0, z1), (x0, y0, z1), (x, y1, z))
                faces = ((0, 1, 4), (1, 2, 4), (2, 3, 4), (3, 0, 4), (0, 3, 2), (0, 2, 1))
            else:
                corners = ((x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0), (x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1))
                faces = ((0, 1, 2), (0, 2, 3), (4, 6, 5), (4, 7, 6), (0, 4, 5), (0, 5, 1), (3, 2, 6), (3, 6, 7), (1, 5, 6), (1, 6, 2), (0, 3, 7), (0, 7, 4))
            for face in faces:
                for index in face:
                    vertices.extend(corners[index] if isinstance(index, int) else index)
        return vertices
