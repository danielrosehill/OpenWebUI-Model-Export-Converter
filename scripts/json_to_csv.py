#!/usr/bin/env python3
import json
import csv
import os
import sys
from datetime import datetime

def convert_json_to_csv(input_file, output_file):
    """
    Convert JSON array to CSV with columns: name, description, system prompt
    
    Args:
        input_file (str): Path to the input JSON file
        output_file (str): Path to the output CSV file
    """
    try:
        # Read the JSON file
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Check if data is a list
        if not isinstance(data, list):
            print(f"Error: Expected a JSON array, but got {type(data).__name__}")
            return False
        
        # Create output directory if it doesn't exist
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        # Write to CSV
        with open(output_file, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            
            # Write header
            writer.writerow(['name', 'description', 'system_prompt'])
            
            # Process each model in the array
            for model in data:
                name = model.get('name', '')
                
                # Extract description and system prompt from nested structure
                description = ''
                system_prompt = ''
                
                # Check if 'info' and 'meta' exist
                if 'info' in model and isinstance(model['info'], dict):
                    info = model['info']
                    
                    # Get description from meta if it exists
                    if 'meta' in info and isinstance(info['meta'], dict):
                        description = info['meta'].get('description', '')
                    
                    # Get system prompt from params if it exists
                    if 'params' in info and isinstance(info['params'], dict):
                        system_prompt = info['params'].get('system', '')
                
                # Write the row
                writer.writerow([name, description, system_prompt])
        
        print(f"Successfully converted {input_file} to {output_file}")
        return True
    
    except json.JSONDecodeError:
        print(f"Error: {input_file} is not a valid JSON file")
        return False
    except Exception as e:
        print(f"Error: {str(e)}")
        return False

def main():
    # Get current timestamp
    timestamp = datetime.now().strftime("%y%m%d_%H%M%S")
    
    # Define input and output paths
    workspace_dir = os.path.dirname(os.path.abspath(__file__))
    input_file = os.path.join(workspace_dir, "workspace", "input", "input.json")
    output_file = os.path.join(workspace_dir, "workspace", "output", f"{timestamp}_models.csv")
    
    # Check if input file exists
    if not os.path.isfile(input_file):
        print(f"Error: Input file not found at {input_file}")
        print("Please place your JSON file as 'input.json' in the workspace/input directory")
        return 1
    
    # Convert JSON to CSV
    if convert_json_to_csv(input_file, output_file):
        print(f"Conversion complete. Output saved to: {output_file}")
        return 0
    else:
        return 1

if __name__ == "__main__":
    sys.exit(main())
