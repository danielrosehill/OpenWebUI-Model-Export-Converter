#!/usr/bin/env python3
"""
Script to extract model information from OpenWebUI JSON export and convert it to multiple formats:
- CSV: Name, description, system prompt
- Simplified JSON: Only essential fields
- Markdown: Formatted with model names as headers
- TXT: Plain text version of the markdown format

The script looks for input.json in the input directory and creates a timestamped
output folder with all the converted files.
"""

import json
import csv
import os
import sys
from datetime import datetime

def create_output_directory():
    """
    Create a timestamped output directory in the format ddmmyy_hhmm
    
    Returns:
        str: Path to the created output directory
    """
    # Get current timestamp in the format ddmmyy_hhmm
    timestamp = datetime.now().strftime("%d%m%y_%H%M")
    
    # Define base directory (relative to the repository root)
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    output_dir = os.path.join(base_dir, "outputs", timestamp)
    
    # Create the output directory
    os.makedirs(output_dir, exist_ok=True)
    print(f"Created output directory: {output_dir}")
    
    return output_dir

def extract_model_data(input_file):
    """
    Extract model data from the input JSON file
    
    Args:
        input_file (str): Path to the input JSON file
        
    Returns:
        list: List of dictionaries containing model data
    """
    try:
        # Read the JSON file
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Check if data is a list
        if not isinstance(data, list):
            print(f"Error: Expected a JSON array, but got {type(data).__name__}")
            return None
        
        # Extract the required fields for each model
        models = []
        for model in data:
            model_data = {
                "name": model.get("name", "").strip(),
                "description": "",
                "system_prompt": "",
                "link": f"openwebui://model/{model.get('id', '')}"
            }
            
            # Extract description and system prompt from nested structure
            if "info" in model and isinstance(model["info"], dict):
                info = model["info"]
                
                # Get description from meta if it exists
                if "meta" in info and isinstance(info["meta"], dict):
                    model_data["description"] = info["meta"].get("description", "")
                
                # Get system prompt from params if it exists
                if "params" in info and isinstance(info["params"], dict):
                    model_data["system_prompt"] = info["params"].get("system", "")
            
            models.append(model_data)
        
        print(f"Successfully extracted data for {len(models)} models")
        return models
    
    except json.JSONDecodeError:
        print(f"Error: {input_file} is not a valid JSON file")
        return None
    except Exception as e:
        print(f"Error extracting model data: {str(e)}")
        return None

def save_as_csv(models, output_file):
    """
    Save model data as CSV
    
    Args:
        models (list): List of model data dictionaries
        output_file (str): Path to the output CSV file
    """
    try:
        with open(output_file, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            
            # Write header
            writer.writerow(['name', 'description', 'system_prompt', 'link'])
            
            # Write data rows
            for model in models:
                writer.writerow([
                    model["name"],
                    model["description"],
                    model["system_prompt"],
                    model["link"]
                ])
        
        print(f"Successfully saved CSV to {output_file}")
        return True
    except Exception as e:
        print(f"Error saving CSV: {str(e)}")
        return False

def save_as_simplified_json(models, output_file):
    """
    Save model data as simplified JSON
    
    Args:
        models (list): List of model data dictionaries
        output_file (str): Path to the output JSON file
    """
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(models, f, indent=2)
        
        print(f"Successfully saved simplified JSON to {output_file}")
        return True
    except Exception as e:
        print(f"Error saving simplified JSON: {str(e)}")
        return False

def save_as_markdown(models, output_file):
    """
    Save model data as Markdown with model names as headers
    
    Args:
        models (list): List of model data dictionaries
        output_file (str): Path to the output Markdown file
    """
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("# OpenWebUI Models\n\n")
            
            for model in models:
                # Write model name as header
                f.write(f"## {model['name']}\n\n")
                
                # Write description
                if model["description"]:
                    f.write(f"{model['description']}\n\n")
                
                # Write link
                f.write(f"**Link**: [{model['name']}]({model['link']})\n\n")
                
                # Add separator between models
                f.write("---\n\n")
        
        print(f"Successfully saved Markdown to {output_file}")
        return True
    except Exception as e:
        print(f"Error saving Markdown: {str(e)}")
        return False

def save_as_txt(models, output_file):
    """
    Save model data as plain text
    
    Args:
        models (list): List of model data dictionaries
        output_file (str): Path to the output text file
    """
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("OPENWEBUI MODELS\n\n")
            
            for model in models:
                # Write model name
                f.write(f"{model['name']}\n")
                f.write("=" * len(model['name']) + "\n\n")
                
                # Write description
                if model["description"]:
                    f.write(f"{model['description']}\n\n")
                
                # Write link
                f.write(f"Link: {model['link']}\n\n")
                
                # Add separator between models
                f.write("-" * 50 + "\n\n")
        
        print(f"Successfully saved text file to {output_file}")
        return True
    except Exception as e:
        print(f"Error saving text file: {str(e)}")
        return False

def main():
    # Define input file path (hardcoded as per requirements)
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    input_file = os.path.join(base_dir, "input", "input.json")
    
    # Check if input file exists
    if not os.path.isfile(input_file):
        print(f"Error: Input file not found at {input_file}")
        print("Please place your JSON file as 'input.json' in the input directory")
        return 1
    
    # Create timestamped output directory
    output_dir = create_output_directory()
    
    # Extract model data
    models = extract_model_data(input_file)
    if not models:
        return 1
    
    # Save data in different formats
    success = True
    success &= save_as_csv(models, os.path.join(output_dir, "models.csv"))
    success &= save_as_simplified_json(models, os.path.join(output_dir, "models.json"))
    success &= save_as_markdown(models, os.path.join(output_dir, "models.md"))
    success &= save_as_txt(models, os.path.join(output_dir, "models.txt"))
    
    if success:
        print(f"\nConversion complete. All output files saved to: {output_dir}")
        return 0
    else:
        print("\nConversion completed with errors. Check the logs above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
