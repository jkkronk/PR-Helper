import json
import sys

def load_rules_from_json(file_path):
    """
    Load coding guidelines from a JSON file.

    Rules should be an array of objects with the following structure:
    {
        "id": "1",
        "description": "Rule 1 description"
    }
    """
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
            rules_list = data.get('rules', [])
            rules_text = '\n'.join(f"{rule['id']}. {rule['description']}" for rule in rules_list)
            return rules_text
    except Exception as e:
        print(f"Error loading rules from JSON: {e}")
        sys.exit(1)

def load_markdown(file_path):
    """
    Load content from a Markdown file.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"Error reading Markdown file: {e}")
        sys.exit(1)


def save_rules_to_json(rules, output_path):
    """
    Save the rules dictionary to a JSON file.
    """
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(rules, f, indent=4)
        print(f"Rules successfully saved to {output_path}")
    except Exception as e:
        print(f"Error writing to JSON file: {e}")
        sys.exit(1)
