import unittest

import guided_setup


class TestGuidedSetupArgs(unittest.TestCase):
    def test_parse_args_auto_and_launch(self):
        args = guided_setup.parse_args(["--auto", "--launch-runtime"])
        self.assertTrue(args.auto)
        self.assertTrue(args.launch_runtime)
        self.assertFalse(args.skip_smoke)

    def test_parse_args_skip_smoke(self):
        args = guided_setup.parse_args(["--skip-smoke"])
        self.assertFalse(args.auto)
        self.assertFalse(args.launch_runtime)
        self.assertTrue(args.skip_smoke)


if __name__ == "__main__":
    unittest.main()
