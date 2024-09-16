import unittest
from unittest.mock import patch, mock_open
import json
import sys
from io import StringIO

from lib.review_utils import (
    load_rules_from_json,
    format_response,
    check_diff_with_gpt,
    display_issues
)

# Sample test data for the rules JSON file
sample_rules_json = {
    "rules": [
        {"id": "1", "description": "Avoid using global variables."},
        {"id": "2", "description": "Use snake_case for variable names."}
    ]
}

# Test the functions
import unittest
from unittest.mock import patch

class TestReviewUtils(unittest.TestCase):

    @patch("builtins.open", new_callable=mock_open, read_data=json.dumps(sample_rules_json))
    def test_load_rules_from_json(self, mock_file):
        """
        Test loading rules from a JSON file.
        """
        file_path = "mock_rules.json"
        rules_text = load_rules_from_json(file_path)
        expected_rules_text = "1. Avoid using global variables.\n2. Use snake_case for variable names."
        self.assertEqual(rules_text, expected_rules_text)

    def test_format_response(self):
        """
        Test formatting of the GPT review response.
        """
        raw_response = """Rule Violated: Avoid using global variables
Line 12: Global variable 'x' is used
Suggestion: Refactor to avoid using global variables.
"""
        expected_output = [
            {
                "Rule Violated": "Rule Violated",
                "Line Number(s)": "Line 12",
                "Issue Description": "Avoid using global variables",
                "Suggestion": "Suggestion: Refactor to avoid using global variables."
            }
        ]
        formatted_response = format_response(raw_response)
        self.assertEqual(formatted_response, expected_output)

    @patch("builtins.print")
    def test_display_issues(self, mock_print):
        """
        Test the display_issues function by mocking the print function.
        """
        issues = [
            {
                "Rule Violated": "Avoid using global variables",
                "Line Number(s)": "Line 12",
                "Issue Description": "Global variable 'x' is used",
                "Suggestion": "Refactor to avoid using global variables."
            }
        ]
        display_issues(issues)
        
        mock_print.assert_any_call("Rule Violated: Avoid using global variables")
        mock_print.assert_any_call("Line Number(s): Line 12")
        mock_print.assert_any_call("Issue Description: Global variable 'x' is used")
        mock_print.assert_any_call("Suggestion: Refactor to avoid using global variables.")
        mock_print.assert_any_call('-' * 80)
    
    def test_load_rules_from_json_success(self):
        mock_json = '''
        {
            "rules": [
                {"id": "1", "description": "Avoid using global variables"},
                {"id": "2", "description": "Ensure all functions have docstrings"}
            ]
        }
        '''
        with patch('builtins.open', mock_open(read_data=mock_json)):
            rules_text = load_rules_from_json('dummy_path.json')
            expected_text = "1. Avoid using global variables\n2. Ensure all functions have docstrings"
            self.assertEqual(rules_text, expected_text)
    
    def test_load_rules_from_json_missing_rules_key(self):
        mock_json = '''
        {
            "guidelines": [
                {"id": "1", "description": "Some rule"}
            ]
        }
        '''
        with patch('builtins.open', mock_open(read_data=mock_json)):
            rules_text = load_rules_from_json('dummy_path.json')
            self.assertEqual(rules_text, "")
    
    def test_load_rules_from_json_invalid_json(self):
        mock_json = '''
        {
            "rules": [
                {"id": "1", "description": "Some rule"},
        '''
        with patch('builtins.open', mock_open(read_data=mock_json)):
            with self.assertRaises(SystemExit) as cm:
                load_rules_from_json('dummy_path.json')
            self.assertEqual(cm.exception.code, 1)
    
    def test_load_rules_from_json_empty_rules(self):
        mock_json = '''
        {
            "rules": []
        }
        '''
        with patch('builtins.open', mock_open(read_data=mock_json)):
            rules_text = load_rules_from_json('dummy_path.json')
            self.assertEqual(rules_text, "")
    
    ### Tests for format_response ###
    
    def test_format_response_single_issue(self):
        raw_response = """Rule Violated: Avoid using global variables
Line 12: Global variable 'x' is used
Suggestion: Refactor to avoid using global variables."""
        expected_output = [
            {
                "Rule Violated": "Rule Violated",
                "Issue Description": "Avoid using global variables",
                "Line Number(s)": "Line 12",
                "Suggestion": "Suggestion: Refactor to avoid using global variables."
            }
        ]
        formatted_response = format_response(raw_response)
        self.assertEqual(formatted_response, expected_output)
    
    def test_format_response_multiple_issues(self):
        raw_response = """Rule Violated: Avoid using global variables
Line 12: Global variable 'x' is used
Suggestion: Refactor to avoid using global variables.
Rule Violated: Ensure all functions have docstrings
Line 45: Function 'process_data' lacks a docstring
Suggestion: Add a docstring to describe the function's purpose."""
        expected_output = [
            {
                "Rule Violated": "Rule Violated",
                "Issue Description": "Avoid using global variables",
                "Line Number(s)": "Line 12",
                "Suggestion": "Suggestion: Refactor to avoid using global variables."
            },
            {
                "Rule Violated": "Rule Violated",
                "Issue Description": "Ensure all functions have docstrings",
                "Line Number(s)": "Line 45",
                "Suggestion": "Suggestion: Add a docstring to describe the function's purpose."
            }
        ]
        formatted_response = format_response(raw_response)
        self.assertEqual(formatted_response, expected_output)
    
    def test_format_response_no_issues(self):
        raw_response = "No issues found."
        expected_output = [{"Message": "No issues found."}]
        formatted_response = format_response(raw_response)
        self.assertEqual(formatted_response, expected_output)
    
    def test_format_response_unexpected_format(self):
        raw_response = """Some unexpected response format"""
        expected_output = [{"Message": "No issues found."}]
        formatted_response = format_response(raw_response)
        self.assertEqual(formatted_response, expected_output)
    
    ### Tests for check_diff_with_gpt ###
    
    @patch('lib.review_utils.openai.ChatCompletion.create')
    def test_check_diff_with_gpt_with_issues(self, mock_create):
        # Mocking GPT response
        mock_response = {
            'choices': [
                {
                    'message': {
                        'content': """Rule Violated: Avoid using global variables
Line 12: Global variable 'x' is used
Suggestion: Refactor to avoid using global variables."""
                    }
                }
            ]
        }
        mock_create.return_value = mock_response
        
        diff_text = "diff --git a/file.py b/file.py\n+ global x\n"
        rules = "1. Avoid using global variables\n2. Ensure all functions have docstrings"
        
        expected_output = [
            {
                "Rule Violated": "Rule Violated",
                "Issue Description": "Avoid using global variables",
                "Line Number(s)": "Line 12",
                "Suggestion": "Suggestion: Refactor to avoid using global variables."
            }
        ]
        
        formatted_response = check_diff_with_gpt(diff_text, rules)
        self.assertEqual(formatted_response, expected_output)
    
    @patch('lib.review_utils.openai.ChatCompletion.create')
    def test_check_diff_with_gpt_no_issues(self, mock_create):
        # Mocking GPT response
        mock_response = {
            'choices': [
                {
                    'message': {
                        'content': "No issues found."
                    }
                }
            ]
        }
        mock_create.return_value = mock_response
        
        diff_text = "diff --git a/file.py b/file.py\n+ def new_function():\n+     pass\n"
        rules = "1. Avoid using global variables\n2. Ensure all functions have docstrings"
        
        expected_output = [{"Message": "No issues found."}]
        
        formatted_response = check_diff_with_gpt(diff_text, rules)
        self.assertEqual(formatted_response, expected_output)
    
    @patch('lib.review_utils.openai.ChatCompletion.create')
    def test_check_diff_with_gpt_api_error(self, mock_create):
        # Simulate an API error
        mock_create.side_effect = Exception("API Error")
        
        diff_text = "diff --git a/file.py b/file.py\n+ global x\n"
        rules = "1. Avoid using global variables\n2. Ensure all functions have docstrings"
        
        with self.assertRaises(Exception) as context:
            check_diff_with_gpt(diff_text, rules)
        
        self.assertIn("API Error", str(context.exception))
    
    ### Tests for display_issues ###
    
    def test_display_issues_with_issues(self):
        issues = [
            {
                "Rule Violated": "Avoid using global variables",
                "Issue Description": "Avoid using global variables",
                "Line Number(s)": "Line 12",
                "Suggestion": "Suggestion: Refactor to avoid using global variables."
            },
            {
                "Rule Violated": "Ensure all functions have docstrings",
                "Issue Description": "Ensure all functions have docstrings",
                "Line Number(s)": "Line 45",
                "Suggestion": "Suggestion: Add a docstring to describe the function's purpose."
            }
        ]
        expected_output = (
            "Rule Violated: Avoid using global variables\n"
            "Line Number(s): Line 12\n"
            "Issue Description: Avoid using global variables\n"
            "Suggestion: Suggestion: Refactor to avoid using global variables.\n"
            "--------------------------------------------------------------------------------\n"
            "Rule Violated: Ensure all functions have docstrings\n"
            "Line Number(s): Line 45\n"
            "Issue Description: Ensure all functions have docstrings\n"
            "Suggestion: Suggestion: Add a docstring to describe the function's purpose.\n"
            "--------------------------------------------------------------------------------\n"
        )
        with patch('sys.stdout', new=StringIO()) as fake_out:
            display_issues(issues)
            self.assertEqual(fake_out.getvalue(), expected_output)
    
    def test_display_issues_no_issues(self):
        issues = [{"Message": "No issues found."}]
        expected_output = "No issues found.\n"
        with patch('sys.stdout', new=StringIO()) as fake_out:
            display_issues(issues)
            self.assertEqual(fake_out.getvalue(), expected_output)
    
    def test_display_issues_missing_fields(self):
        issues = [
            {
                "Rule Violated": "Avoid using global variables",
                # Missing 'Line Number(s)'
                "Issue Description": "Avoid using global variables"
                # Missing 'Suggestion'
            }
        ]
        expected_output = (
            "Rule Violated: Avoid using global variables\n"
            "Line Number(s): N/A\n"
            "Issue Description: Avoid using global variables\n"
            "Suggestion: N/A\n"
            "--------------------------------------------------------------------------------\n"
        )
        with patch('sys.stdout', new=StringIO()) as fake_out:
            display_issues(issues)
            self.assertEqual(fake_out.getvalue(), expected_output)
    

if __name__ == '__main__':
    unittest.main()

