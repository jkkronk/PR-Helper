import argparse
import sys
from source.review_utils import load_rules_from_json, check_diff_with_gpt, display_issues
from source.git_helpers import git_diff_branch

def main():
    parser = argparse.ArgumentParser(description='Pre-check git diffs against coding guidelines.')
    parser.add_argument('--branch', type=str, default='origin/main', help='Branch to compare against (default: main)')
    parser.add_argument('--rules', type=str, default='data/example_rules.json', help='Path to the JSON file containing coding guidelines')
    args = parser.parse_args()

    # Load rules from JSON file
    rules = load_rules_from_json(args.rules)

    diff_text = git_diff_branch(branch=args.branch)
    if not diff_text.strip():
        print("No staged changes to check.")
        sys.exit(0)

    print(f"Checking code against guidelines using branch '{args.branch}'...\n")

    issues = check_diff_with_gpt(diff_text, rules)
    display_issues(issues)

    if "Message" not in issues[0] or issues[0]["Message"] != "No issues found.":
        sys.exit(1)

if __name__ == "__main__":
    main()
