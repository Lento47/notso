import io
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from notso import cli


class CliTests(unittest.TestCase):
    def test_index_and_search_commands(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            index_path = Path(temp_dir) / "index.json"

            index_stdout = io.StringIO()
            with redirect_stdout(index_stdout):
                exit_code = cli.main(["index", "--output", str(index_path)])
            self.assertEqual(exit_code, 0)
            self.assertTrue(index_path.exists())

            search_stdout = io.StringIO()
            with redirect_stdout(search_stdout):
                exit_code = cli.main(
                    [
                        "search",
                        "search engine",
                        "--index",
                        str(index_path),
                        "--top-k",
                        "2",
                    ]
                )
            self.assertEqual(exit_code, 0)
            output = search_stdout.getvalue()
            self.assertIn("1.", output)
            self.assertIn("[", output)


if __name__ == "__main__":
    unittest.main()
