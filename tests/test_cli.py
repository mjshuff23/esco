from __future__ import annotations

import unittest
from contextlib import redirect_stdout
from io import StringIO

from tests import bootstrap  # noqa: F401

from esco_cli import main


class CliTests(unittest.TestCase):
    def test_one_shot_cli_renders_structured_output(self) -> None:
        buffer = StringIO()
        with redirect_stdout(buffer):
            exit_code = main(["What phase is ESCO in right now?", "--limit", "2"])

        output = buffer.getvalue()
        self.assertEqual(exit_code, 0)
        self.assertIn("Route:", output)
        self.assertIn("Policy:", output)
        self.assertIn("Answer:", output)


if __name__ == "__main__":
    unittest.main()
