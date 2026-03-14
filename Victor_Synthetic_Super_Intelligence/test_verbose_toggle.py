import importlib
import os
import unittest
from unittest import mock
import logging

import victor_runtime.logging_utils as logging_utils_module
import victor_runtime.core.runtime as runtime_module


class TestVerboseToggle(unittest.TestCase):
    def setUp(self):
        importlib.reload(logging_utils_module)
        importlib.reload(runtime_module)

    def test_verbose_env_true(self):
        with mock.patch.dict(os.environ, {"VICTOR_VERBOSE_LOG": "1"}):
            importlib.reload(logging_utils_module)
            mod = importlib.reload(runtime_module)
            self.assertTrue(logging_utils_module.VERBOSE_LOGGING)
            self.assertEqual(mod.logger.getEffectiveLevel(), logging.DEBUG)

    def test_verbose_env_false_default(self):
        with mock.patch.dict(os.environ, {}, clear=True):
            importlib.reload(logging_utils_module)
            mod = importlib.reload(runtime_module)
            self.assertFalse(logging_utils_module.VERBOSE_LOGGING)
            self.assertEqual(mod.logger.getEffectiveLevel(), logging.INFO)


if __name__ == "__main__":
    unittest.main()
