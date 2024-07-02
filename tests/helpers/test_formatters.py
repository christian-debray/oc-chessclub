import unittest
from app.helpers.text_ui import format_table


class TestFormatTable(unittest.TestCase):
    """Test the format_table helper."""

    def test_format_table(self):
        lines_data = [
            ["Header 1", "Header 2\nlinespan"],
            ["Lorem\nipsum", "dolor sit amet,"],
            ["consectetur", "adipiscing\nelit"],
        ]

        expected_lines = [
            "+--------------+------------------+",
            "|  Header 1    |  Header 2        |",
            "|              |  linespan        |",
            "+--------------+------------------+",
            "|  Lorem       |  dolor sit amet, |",
            "|  ipsum       |                  |",
            "+--------------+------------------+",
            "|  consectetur |  adipiscing      |",
            "|              |  elit            |",
            "+--------------+------------------+",
        ]
        expected_str = "\n".join(expected_lines)
        table_str = format_table(
            table_data=lines_data, pad_left=2, pad_right=1, cell_sep="|", line_sep="-"
        )
        self.assertEqual(table_str, expected_str)
