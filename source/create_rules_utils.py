import json
import sys
import openai
import json
import sys
import openai
import re
from typing import List, Dict
from source.io import load_markdown, save_rules_to_json

def split_markdown_into_sections(markdown_content: str, max_length: int = 3000) -> List[str]:
    """
    Split the Markdown content into sections based on headings to preserve context.
    Each section should be within the max_length to prevent exceeding token limits.
    """
    # Split by headings (assuming headings start with #)
    sections = re.split(r'(?:\n\s*)#{1,6}\s+', markdown_content)
    headings = re.findall(r'(?:\n\s*)#{1,6}\s+([^\n]+)', markdown_content)

    if not headings:
        # If no headings found, split by character count
        return [markdown_content[i:i+max_length] for i in range(0, len(markdown_content), max_length)]

    combined_sections = []
    current_section = ""
    for heading, content in zip(headings, sections[1:]):  # sections[0] is content before first heading
        section = f"# {heading}\n{content}"
        if len(current_section) + len(section) > max_length:
            if current_section:
                combined_sections.append(current_section)
                current_section = section
            else:
                # If single section is larger than max_length, split it further
                split_subsections = [section[i:i+max_length] for i in range(0, len(section), max_length)]
                combined_sections.extend(split_subsections)
        else:
            current_section += f"\n{section}"
    if current_section:
        combined_sections.append(current_section)
    return combined_sections

def format_rules(raw_response: str) -> List[Dict[str, str]]:
    """
    Parse the GPT-4 response and format it into a list of rule dictionaries.
    """
    try:
        # Attempt to extract JSON from the response
        json_start = raw_response.find('{')
        json_end = raw_response.rfind('}') + 1
        if json_start == -1 or json_end == -1:
            raise ValueError("No JSON object found in the response.")
        json_str = raw_response[json_start:json_end]
        rules = json.loads(json_str)
        
        # Validate the structure
        if isinstance(rules, dict) and 'rules' in rules:
            return rules['rules']
        else:
            raise ValueError("JSON structure is invalid. Expected a 'rules' key with a list of rule objects.")
    except Exception as e:
        print(f"Error parsing GPT-4 response: {e}")
        print("GPT-4 Response was:")
        print(raw_response)
        print("Continuing parsing next section...")

def generate_rules_from_chunk(chunk: str) -> List[Dict[str, str]]:
    """
    Use OpenAI GPT-4 to generate coding rules from a chunk of Markdown content.
    """
    prompt = f"""
You are an assistant that extracts coding guidelines from a project's README file.

Given the following Markdown content, identify and extract the coding guidelines or rules. 
Format the extracted rules into a JSON structure with the following format:

{{
    "rules": [
        {{
            "id": "1",
            "description": "First coding rule description."
        }},
        {{
            "id": "2",
            "description": "Second coding rule description."
        }}
        // Add more rules as needed
    ]
}}

Only include the "rules" key with an array of rule objects. Do not include any additional text or explanations.

Markdown Content:
{chunk}
"""
    client = openai.OpenAI()

    response = client.chat.completions.create(
        model="gpt-4o",  
        messages=[
            {"role": "system", "content": "You are a helpful assistant specialized in extracting coding guidelines."},
            {"role": "user", "content": prompt}
        ]
    )
    # check if there was an error
    if response.choices[0].message.content is None:
        print("Error: No response from GPT-4")
        sys.exit(1)
    return format_rules(response.choices[0].message.content)
    

def aggregate_rules(rules_list: List[List[Dict[str, str]]]) -> List[Dict[str, str]]:
    """
    Aggregate rules from multiple chunks, remove duplicates, and assign unique IDs.
    """
    unique_rules = {}
    for rules in rules_list:
        for rule in rules:
            description = rule.get('description', '').strip()
            if description and description not in unique_rules:
                unique_rules[description] = rule.get('suggestion', '')
    
    aggregated_rules = []
    for idx, (description, suggestion) in enumerate(unique_rules.items(), start=1):
        aggregated_rules.append({
            "id": str(idx),
            "description": description
        })
    
    return aggregated_rules

def review_rules(rules: List[Dict[str, str]]) -> List[Dict[str, str]]:
    """
    Review the rules and make sure they are good.
    """
    prompt = f"""
You are an assistant that reviews coding guidelines extracted from a project's README file.

Remove any rules that are not explicitly about written code that belongs in a codebase.

Only keep the 24 most important rules.

Coding Guidelines:
{rules}
"""
    client = openai.OpenAI()

    response = client.chat.completions.create(
        model="gpt-4",  
        messages=[
            {"role": "system", "content": "You are a helpful assistant specialized in reviewing coding guidelines."},
            {"role": "user", "content": prompt}
        ]
    )
    # check if there was an error
    if response.choices[0].message.content is None:
        print("Error: No response from GPT-4")
        sys.exit(1)
    return format_rules(response.choices[0].message.content)


def generate_rules(markdown_content: str) -> Dict[str, List[Dict[str, str]]]:
    """
    Generate rules by processing the Markdown content in chunks.
    """
    # Define maximum characters per chunk (adjust as needed)
    max_chunk_length = 3000
    chunks = split_markdown_into_sections(markdown_content, max_length=max_chunk_length)
    print(f"Total sections to process: {len(chunks)}")

    all_rules = []
    for idx, chunk in enumerate(chunks, start=1):
        print(f"Processing section {idx}/{len(chunks)}...")
        rules = generate_rules_from_chunk(chunk)
        all_rules.append(rules)
    
    aggregated_rules = aggregate_rules(all_rules)
    corrected_rules = review_rules(aggregated_rules)

    return {"rules": aggregated_rules}


