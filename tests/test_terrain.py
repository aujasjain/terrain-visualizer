import math
import unittest

from visualizer.landscape import Landscape


class TerrainTests(unittest.TestCase):
    def test_height_is_deterministic_and_varied(self):
        terrain = Landscape(19)
        values = [terrain.height(x, z) for x, z in ((0, 0), (10, 20), (-14, 47), (28, 60))]
        self.assertEqual(values, [terrain.height(x, z) for x, z in ((0, 0), (10, 20), (-14, 47), (28, 60))])
        self.assertGreater(max(values) - min(values), 2.0)

    def test_seed_changes_shape_and_palette(self):
        first = Landscape(1)
        second = Landscape(2)
        self.assertNotEqual(first.ground_hue, second.ground_hue)
        self.assertNotEqual(first.sky_hue, second.sky_hue)
        self.assertNotEqual(first.height(4, 9), second.height(4, 9))

    def test_flat_landscape_is_a_valid_mode(self):
        terrain = Landscape(19)
        terrain.landform = 0
        self.assertEqual(terrain.height(-1000, 500), 0.0)
        self.assertEqual(terrain.height(1000, -500), 0.0)

    def test_mesh_contains_triangles(self):
        mesh = Landscape(23).mesh(radius=12, resolution=4)
        self.assertEqual(len(mesh) % 9, 0)
        self.assertTrue(all(math.isfinite(value) for value in mesh))

    def test_floating_forms_are_seeded_and_optional(self):
        first = Landscape(19)
        second = Landscape(19)
        self.assertEqual(first.floating_objects, second.floating_objects)
        self.assertTrue(all(len(form) == 8 for form in first.floating_objects))
        self.assertTrue(all(0 <= form[-1] < 4 for form in first.floating_objects))
        self.assertEqual(len(first.object_mesh()) % 9, 0)


if __name__ == "__main__":
    unittest.main()
