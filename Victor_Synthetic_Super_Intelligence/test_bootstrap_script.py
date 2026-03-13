import os
import importlib
import unittest

import bootstrap


class TestBootstrap(unittest.TestCase):
    def test_smoke_allows_missing(self):
        summary, ok = bootstrap.smoke_check(allow_missing=True)
        self.assertIn("numpy", summary)
        self.assertTrue(ok)


if __name__ == "__main__":
    unittest.main()
