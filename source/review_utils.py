import json
import sys
import openai
import os 
from openai import OpenAI
import re
from source.io import load_rules_from_json


def format_response(raw_response):
    issues = []
    issue = {}
    for line in raw_response.splitlines():
        line = line.strip()
        if not line:
            continue  # Skip empty lines
        # Use regex to split at the first colon
        match = re.match(r'^(Rule Violated|Line Number\(s\)|Issue Description|Suggestion):\s*(.*)', line, re.IGNORECASE)
        if match:
            key, value = match.groups()
            key = key.lower()
            if key == 'rule violated':
                if issue:
                    issues.append(issue)
                    issue = {}
                issue['Rule Violated'] = value
            elif key == 'line number(s)':
                issue['Line Number(s)'] = value
            elif key == 'issue description':
                issue['Issue Description'] = value
            elif key == 'suggestion':
                issue['Suggestion'] = value
    if issue:
        issues.append(issue)
    
    if not issues:
        return [{"Message": "No issues found."}]
    
    return issues

def check_diff_with_gpt(diff_text, rules):
    """
    Use OpenAI GPT-4 to check the diff against the rules.
    """
    prompt = f"""
You are a code reviewer who ensures code changes adhere to the following guidelines:

{rules}

Please review the following git diff and report any violations of the guidelines. Be specific about the issues and reference the relevant line numbers if possible.

Structure your response with:
Rule Violated: <Rule description>
Line Number(s): <Line numbers where the violation occurs>
Issue Description: <Description of the issue>
Suggestion: <Suggestion on how to fix it (optional)>

Git diff:
{diff_text}

If there are no issues, respond with 'No issues found.'
"""
    client = OpenAI()

    response = client.chat.completions.create(
        model="gpt-4",  
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ]
    )
    # check if there was an error
    if response.choices[0].message.content is None:
        print("Error: No response from GPT-4")
        sys.exit(1)
    return format_response(response.choices[0].message.content)

def display_issues(issues):
    """
    Display issues in a structured format.
    """
    if "Message" in issues[0] and issues[0]["Message"] == "No issues found.":
        print("No issues found.")
    else:
        for issue in issues:
            print(f"Rule Violated: {issue.get('Rule Violated', 'N/A')}")
            print(f"Line Number(s): {issue.get('Line Number(s)', 'N/A')}")
            print(f"Issue Description: {issue.get('Issue Description', 'N/A')}")
            print(f"Suggestion: {issue.get('Suggestion', 'N/A')}")
            print('-' * 80)