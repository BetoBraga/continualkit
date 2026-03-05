import unittest

from continualkit.eval import compute_forgetting


class TestComputeForgetting(unittest.TestCase):
    def test_average_forgetting(self):
        before = {"a": 0.9, "b": 0.8}
        after = {"a": 0.8, "b": 0.8}
        self.assertAlmostEqual(compute_forgetting(before, after), 0.05, places=3)

    def test_no_forgetting(self):
        before = {"a": 0.9}
        after = {"a": 0.9}
        self.assertEqual(compute_forgetting(before, after), 0.0)

    def test_improvement(self):
        before = {"a": 0.9}
        after = {"a": 1.0}
        self.assertEqual(compute_forgetting(before, after), 0.0)

    def test_different_keys(self):
        before = {"a": 0.9}
        after = {"b": 0.8}
        with self.assertRaises(ValueError):
            compute_forgetting(before, after)

    def test_empty_dicts(self):
        before = {}
        after = {}
        with self.assertRaises(ValueError):
            compute_forgetting(before, after)
