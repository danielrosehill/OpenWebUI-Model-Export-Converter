#!/usr/bin/env python3
"""
Script to simplify JSON data by extracting only the name, system prompt, and description fields.
"""

import json
import argparse
import os
from datetime import datetime

def simplify_json(input_file, output_file, filter_personal=True):
    """
    Extract only the name, system prompt, and description from each item in a JSON array.
    
    Args:
        input_file (str): Path to the input JSON file
        output_file (str): Path to the output JSON file
        filter_personal (bool): Whether to filter out entries with personal information
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Read the input JSON file
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if not isinstance(data, list):
            print(f"Error: Expected a JSON array, but got {type(data).__name__}")
            return False
        
        # Personal terms to filter out if filter_personal is True
        personal_terms = ["Daniel", "Rosehill", "daniel", "rosehill"]
        
        # Simplify each item in the array
        simplified_data = []
        skipped = 0
        
        for i, item in enumerate(data):
            # Check if we should skip this item due to personal information
            if filter_personal and contains_personal_info(item, personal_terms):
                skipped += 1
                print(f"Skipped item {i+1} (contains personal info)")
                continue
            
            # Extract the required fields
            simplified_item = {
                "name": item.get("name", "")
            }
            
            # Extract description and system prompt from nested structure
            if "info" in item and isinstance(item["info"], dict):
                info = item["info"]
                
                # Get system prompt from params if it exists
                if "params" in info and isinstance(info["params"], dict):
                    simplified_item["system_prompt"] = info["params"].get("system", "")
                else:
                    simplified_item["system_prompt"] = ""
                
                # Get description from meta if it exists
                if "meta" in info and isinstance(info["meta"], dict):
                    simplified_item["description"] = info["meta"].get("description", "")
                else:
                    simplified_item["description"] = ""
            else:
                simplified_item["system_prompt"] = ""
                simplified_item["description"] = ""
            
            simplified_data.append(simplified_item)
            print(f"Simplified item {i+1}")
        
        # Create output directory if it doesn't exist
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        # Write simplified data to output file
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(simplified_data, f, indent=2)
        
        print(f"Successfully simplified {len(simplified_data)} items to {output_file}")
        if filter_personal:
            print(f"Skipped {skipped} items containing personal information")
        
        return True
    
    except Exception as e:
        print(f"Error: {str(e)}")
        return False

def contains_personal_info(obj, personal_terms):
    """
    Check if an object contains personal information.
    
    Args:
        obj: The object to check
        personal_terms: List of personal terms to filter out
    
    Returns:
        True if personal info is found, False otherwise
    """
    if isinstance(obj, dict):
        # Check all values in the dictionary
        for key, value in obj.items():
            if isinstance(value, (dict, list)):
                if contains_personal_info(value, personal_terms):
                    return True
            elif isinstance(value, str):
                for term in personal_terms:
                    if term in value:
                        return True
    elif isinstance(obj, list):
        # Check all items in the list
        for item in obj:
            if contains_personal_info(item, personal_terms):
                return True
    elif isinstance(obj, str):
        # Check if the string contains any personal terms
        for term in personal_terms:
            if term in obj:
                return True
    
    return False

def main():
    parser = argparse.ArgumentParser(description='Simplify JSON data by extracting only name, system prompt, and description')
    parser.add_argument('--input', '-i', default='workspace/input/input.json', 
                        help='Path to input JSON file')
    parser.add_argument('--output', '-o', 
                        help='Path to output JSON file (default: simplified_data_YYMMDD_HHMMSS.json)')
    parser.add_argument('--filter', '-f', action='store_true', default=True,
                        help='Filter out entries with personal information (default: True)')
    parser.add_argument('--no-filter', dest='filter', action='store_false',
                        help='Do not filter out entries with personal information')
    
    args = parser.parse_args()
    
    # Generate default output filename if not provided
    if not args.output:
        timestamp = datetime.now().strftime("%y%m%d_%H%M%S")
        args.output = f"workspace/output/simplified_data_{timestamp}.json"
    
    # Simplify JSON
    simplify_json(args.input, args.output, args.filter)

if __name__ == "__main__":
    main()
