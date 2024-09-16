import argparse
import json
import sys
import openai
import os
import re
from source.io import load_markdown, save_rules_to_json
from source.create_rules_utils import generate_rules

def main():
    parser = argparse.ArgumentParser(description='Generate rules.json from a README Markdown file using GPT-4.')
    parser.add_argument('--input', type=str, required=True, help='Path to the input Markdown file (e.g., README.md)')
    parser.add_argument('--output', type=str, default='rules.json', help='Path to the output JSON file (default: rules.json)')
    args = parser.parse_args()

    # Check OpenAI API key
    if not os.getenv("OPENAI_API_KEY"):
        print("Error: The OPENAI_API_KEY environment variable is not set.")
        sys.exit(1)

    # Load Markdown content
    markdown_content = load_markdown(args.input)

    # Generate rules using GPT-4
    rules = generate_rules(markdown_content)

    # Save rules to JSON file
    save_rules_to_json(rules, args.output)

if __name__ == "__main__":
    main()
