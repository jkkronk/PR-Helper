# test_rules_module.py
import unittest
from unittest.mock import mock_open, patch, MagicMock
import sys
import json

# Import the functions to be tested
from source.io import load_rules_from_json, load_markdown, save_rules_to_json

class TestRulesModule(unittest.TestCase):

    # Tests for load_rules_from_json
    @patch('builtins.open', new_callable=mock_open, read_data='{"rules": [{"id": "1", "description": "Rule one"}, {"id": "2", "description": "Rule two"}]}')
    def test_load_rules_from_json_success(self, mock_file):
        expected_output = "1. Rule one\n2. Rule two"
        result = load_rules_from_json('dummy_path.json')
        self.assertEqual(result, expected_output)
        mock_file.assert_called_once_with('dummy_path.json', 'r')

    @patch('builtins.open', new_callable=mock_open, read_data='{"invalid_key": []}')
    def test_load_rules_from_json_missing_rules(self, mock_file):
        expected_output = ""
        result = load_rules_from_json('dummy_path.json')
        self.assertEqual(result, expected_output)
        mock_file.assert_called_once_with('dummy_path.json', 'r')

    @patch('builtins.open', new_callable=mock_open, read_data='Invalid JSON')
    @patch('sys.exit')
    def test_load_rules_from_json_invalid_json(self, mock_exit, mock_file):
        with patch('builtins.print') as mock_print:
            load_rules_from_json('dummy_path.json')
            mock_file.assert_called_once_with('dummy_path.json', 'r')
            mock_print.assert_called_once()
            mock_exit.assert_called_once_with(1)

    @patch('builtins.open', side_effect=FileNotFoundError("File not found"))
    @patch('sys.exit')
    def test_load_rules_from_json_file_not_found(self, mock_exit, mock_file):
        with patch('builtins.print') as mock_print:
            load_rules_from_json('non_existent.json')
            mock_file.assert_called_once_with('non_existent.json', 'r')
            mock_print.assert_called_once()
            mock_exit.assert_called_once_with(1)

    # Tests for load_markdown
    @patch('builtins.open', new_callable=mock_open, read_data='# Sample Markdown Content')
    def test_load_markdown_success(self, mock_file):
        expected_output = '# Sample Markdown Content'
        result = load_markdown('dummy_markdown.md')
        self.assertEqual(result, expected_output)
        mock_file.assert_called_once_with('dummy_markdown.md', 'r', encoding='utf-8')

    @patch('builtins.open', side_effect=FileNotFoundError("File not found"))
    @patch('sys.exit')
    def test_load_markdown_file_not_found(self, mock_exit, mock_file):
        with patch('builtins.print') as mock_print:
            load_markdown('non_existent.md')
            mock_file.assert_called_once_with('non_existent.md', 'r', encoding='utf-8')
            mock_print.assert_called_once()
            mock_exit.assert_called_once_with(1)

    @patch('builtins.open', side_effect=IOError("Read error"))
    @patch('sys.exit')
    def test_load_markdown_read_error(self, mock_exit, mock_file):
        with patch('builtins.print') as mock_print:
            load_markdown('error_markdown.md')
            mock_file.assert_called_once_with('error_markdown.md', 'r', encoding='utf-8')
            mock_print.assert_called_once()
            mock_exit.assert_called_once_with(1)

    @patch('builtins.open', side_effect=IOError("Write error"))
    @patch('sys.exit')
    def test_save_rules_to_json_write_error(self, mock_exit, mock_file):
        rules = {
            "rules": [
                {"id": "1", "description": "Rule one"},
                {"id": "2", "description": "Rule two"}
            ]
        }
        with patch('builtins.print') as mock_print:
            save_rules_to_json(rules, 'output.json')
            mock_file.assert_called_once_with('output.json', 'w', encoding='utf-8')
            mock_print.assert_called_once()
            mock_exit.assert_called_once_with(1)

if __name__ == '__main__':
    unittest.main()
