#!/usr/bin/env python3
"""
GUI application for exporting OpenWebUI model data with customizable field selection
and output format options.
"""

import json
import csv
import os
import sys
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from datetime import datetime
import threading
import yaml
import xml.dom.minidom
import pandas as pd
import traceback

class ExportApp:
    def __init__(self, root):
        self.root = root
        self.root.title("OpenWebUI Model Export Utility")
        self.root.geometry("800x700")
        self.root.minsize(700, 600)
        
        # Set app icon if available
        try:
            self.root.iconbitmap("icon.ico")
        except:
            pass
        
        # Variables
        self.input_file_var = tk.StringVar(value="")
        self.output_dir_var = tk.StringVar(value="")
        self.export_format_var = tk.StringVar(value="csv")
        self.filter_personal_var = tk.BooleanVar(value=True)
        self.progress_var = tk.DoubleVar(value=0.0)
        self.status_var = tk.StringVar(value="Ready")
        
        # Field selection variables and structure
        self.field_vars = {}
        self.field_structure = {
            "Primary Fields": [
                {"name": "name", "display": "Name", "default": True},
                {"name": "info.meta.description", "display": "Description", "default": True},
                {"name": "info.params.system", "display": "System Prompt", "default": True},
            ],
            "Basic": [
                {"name": "id", "display": "Model ID", "default": False},
                {"name": "object", "display": "Object Type", "default": False},
                {"name": "created", "display": "Creation Timestamp", "default": False},
                {"name": "owned_by", "display": "Owner", "default": False},
            ],
            "Info": [
                {"name": "info.id", "display": "Info ID", "default": False},
                {"name": "info.base_model_id", "display": "Base Model", "default": True},
                {"name": "info.name", "display": "Info Name", "default": False},
                {"name": "info.is_active", "display": "Is Active", "default": False},
                {"name": "info.created_at", "display": "Info Created At", "default": False},
                {"name": "info.updated_at", "display": "Info Updated At", "default": False},
            ],
            "Meta": [
                {"name": "info.meta.profile_image_url", "display": "Profile Image URL", "default": False},
                {"name": "info.meta.capabilities.usage", "display": "Usage Capability", "default": False},
                {"name": "info.meta.capabilities.vision", "display": "Vision Capability", "default": False},
                {"name": "info.meta.capabilities.citations", "display": "Citations Capability", "default": False},
                {"name": "info.meta.tags", "display": "Tags", "default": False},
            ],
            "Other": [
                {"name": "preset", "display": "Is Preset", "default": False},
                {"name": "actions", "display": "Actions", "default": False},
            ]
        }
        
        # Create UI
        self.create_ui()
        
        # Initialize field checkboxes
        self.initialize_field_checkboxes()
    
    def create_ui(self):
        """Create the user interface"""
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Main tab
        main_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(main_frame, text="Export")
        
        # About tab
        about_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(about_frame, text="About")
        
        # Create about tab content
        self.create_about_tab(about_frame)
        
        # File selection frame
        file_frame = ttk.LabelFrame(main_frame, text="File Selection", padding="10")
        file_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Input file selection
        ttk.Label(file_frame, text="Input JSON File:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Entry(file_frame, textvariable=self.input_file_var, width=50).grid(row=0, column=1, sticky=tk.EW, padx=5, pady=5)
        ttk.Button(file_frame, text="Browse...", command=self.browse_input_file).grid(row=0, column=2, padx=5, pady=5)
        
        # Output directory selection
        ttk.Label(file_frame, text="Output Directory:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Entry(file_frame, textvariable=self.output_dir_var, width=50).grid(row=1, column=1, sticky=tk.EW, padx=5, pady=5)
        ttk.Button(file_frame, text="Browse...", command=self.browse_output_dir).grid(row=1, column=2, padx=5, pady=5)
        
        # Export options frame
        options_frame = ttk.LabelFrame(main_frame, text="Export Options", padding="10")
        options_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Export format selection
        ttk.Label(options_frame, text="Export Format:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        formats = [
            ("CSV (.csv)", "csv"),
            ("JSON (.json)", "json"),
            ("Excel (.xlsx)", "excel"),
            ("YAML (.yaml)", "yaml"),
            ("XML (.xml)", "xml"),
            ("Markdown Table (.md)", "markdown"),
            ("All Formats", "all")
        ]
        format_frame = ttk.Frame(options_frame)
        format_frame.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        for i, (text, value) in enumerate(formats):
            ttk.Radiobutton(format_frame, text=text, value=value, variable=self.export_format_var).grid(row=i//3, column=i%3, sticky=tk.W, padx=10)
        
        # Filter personal info option
        ttk.Checkbutton(options_frame, text="Filter out personal information", variable=self.filter_personal_var).grid(row=1, column=0, columnspan=2, sticky=tk.W, padx=5, pady=5)
        
        # Field selection frame with scrollbar
        fields_container = ttk.LabelFrame(main_frame, text="Select Fields to Export", padding="10")
        fields_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Add a canvas with scrollbar for the fields
        canvas = tk.Canvas(fields_container)
        scrollbar = ttk.Scrollbar(fields_container, orient="vertical", command=canvas.yview)
        self.fields_frame = ttk.Frame(canvas)
        
        canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Create a window in the canvas for the fields frame
        canvas_window = canvas.create_window((0, 0), window=self.fields_frame, anchor="nw")
        
        # Configure the canvas to resize with the window
        def configure_canvas(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
            canvas.itemconfig(canvas_window, width=event.width-5)
        
        self.fields_frame.bind("<Configure>", configure_canvas)
        canvas.bind("<Configure>", lambda e: canvas.itemconfig(canvas_window, width=e.width-5))
        
        # Button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, padx=5, pady=10)
        
        # Select/Deselect All buttons
        select_frame = ttk.Frame(button_frame)
        select_frame.pack(side=tk.LEFT, padx=5)
        ttk.Button(select_frame, text="Select All", command=self.select_all_fields).pack(side=tk.LEFT, padx=5)
        ttk.Button(select_frame, text="Deselect All", command=self.deselect_all_fields).pack(side=tk.LEFT, padx=5)
        ttk.Button(select_frame, text="Reset to Default", command=self.reset_to_default).pack(side=tk.LEFT, padx=5)
        
        # Export button
        ttk.Button(button_frame, text="Export", command=self.start_export, style="Accent.TButton").pack(side=tk.RIGHT, padx=5)
        
        # Progress bar and status
        progress_frame = ttk.Frame(main_frame)
        progress_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(progress_frame, textvariable=self.status_var).pack(anchor=tk.W, padx=5)
        
        # Set default values
        self.output_dir_var.set(os.path.join(os.path.dirname(os.path.abspath(__file__)), "workspace", "output"))
        
        # Try to find a default input file
        default_input = os.path.join(os.path.dirname(os.path.abspath(__file__)), "workspace", "input", "input.json")
        if os.path.exists(default_input):
            self.input_file_var.set(default_input)
    
    def create_about_tab(self, about_frame):
        """Create the about tab content"""
        # Create a label with the about text
        about_text = "OpenWebUI Model Export Utility\n\n"
        about_text += "Version: 1.0\n"
        about_text += "Author: [Your Name]\n"
        about_text += "License: MIT License\n"
        about_text += "\n"
        about_text += "This utility allows you to export OpenWebUI model data with customizable field selection and output format options."
        
        ttk.Label(about_frame, text=about_text, wraplength=600, justify=tk.LEFT).pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    def initialize_field_checkboxes(self):
        """Initialize the field selection checkboxes"""
        # Clear any existing widgets
        for widget in self.fields_frame.winfo_children():
            widget.destroy()
        
        # Create checkboxes for each field category
        row = 0
        for category, fields in self.field_structure.items():
            # Category label
            category_frame = ttk.LabelFrame(self.fields_frame, text=category)
            category_frame.grid(row=row, column=0, sticky=tk.EW, padx=5, pady=5)
            
            # Create a grid of checkboxes
            for i, field in enumerate(fields):
                field_key = field["name"]
                if field_key not in self.field_vars:
                    self.field_vars[field_key] = tk.BooleanVar(value=field["default"])
                
                checkbox = ttk.Checkbutton(
                    category_frame, 
                    text=field["display"], 
                    variable=self.field_vars[field_key]
                )
                checkbox.grid(row=i//3, column=i%3, sticky=tk.W, padx=10, pady=2)
            
            row += 1
    
    def browse_input_file(self):
        """Open file dialog to select input JSON file"""
        filename = filedialog.askopenfilename(
            title="Select Input JSON File",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if filename:
            self.input_file_var.set(filename)
    
    def browse_output_dir(self):
        """Open directory dialog to select output directory"""
        directory = filedialog.askdirectory(title="Select Output Directory")
        if directory:
            self.output_dir_var.set(directory)
    
    def select_all_fields(self):
        """Select all field checkboxes"""
        for var in self.field_vars.values():
            var.set(True)
    
    def deselect_all_fields(self):
        """Deselect all field checkboxes"""
        for var in self.field_vars.values():
            var.set(False)
    
    def reset_to_default(self):
        """Reset field selection to default values"""
        for category, fields in self.field_structure.items():
            for field in fields:
                self.field_vars[field["name"]].set(field["default"])
    
    def start_export(self):
        """Start the export process in a separate thread"""
        # Validate input
        if not self.input_file_var.get():
            messagebox.showerror("Error", "Please select an input JSON file")
            return
        
        if not self.output_dir_var.get():
            messagebox.showerror("Error", "Please select an output directory")
            return
        
        if not os.path.exists(self.input_file_var.get()):
            messagebox.showerror("Error", "Input file does not exist")
            return
        
        if not os.path.exists(self.output_dir_var.get()):
            try:
                os.makedirs(self.output_dir_var.get())
            except Exception as e:
                messagebox.showerror("Error", f"Could not create output directory: {str(e)}")
                return
        
        # Check if at least one field is selected
        if not any(var.get() for var in self.field_vars.values()):
            messagebox.showerror("Error", "Please select at least one field to export")
            return
        
        # Start export in a separate thread
        self.progress_var.set(0)
        self.status_var.set("Starting export...")
        
        export_thread = threading.Thread(target=self.perform_export)
        export_thread.daemon = True
        export_thread.start()
    
    def perform_export(self):
        """Perform the actual export operation"""
        try:
            # Get selected fields
            selected_fields = [field for field, var in self.field_vars.items() if var.get()]
            
            # Generate output filename with timestamp
            timestamp = datetime.now().strftime("%y%m%d_%H%M%S")
            format_ext = {
                "csv": ".csv",
                "json": ".json",
                "excel": ".xlsx",
                "yaml": ".yaml",
                "xml": ".xml",
                "markdown": ".md"
            }
            
            # Read input JSON
            self.update_status("Reading input file...", 5)
            with open(self.input_file_var.get(), 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if not isinstance(data, list):
                raise ValueError(f"Expected a JSON array, but got {type(data).__name__}")
            
            # Filter personal information if requested
            if self.filter_personal_var.get():
                self.update_status("Filtering personal information...", 10)
                personal_terms = ["Daniel", "Rosehill", "daniel", "rosehill"]
                filtered_data = []
                total_items = len(data)
                
                for i, item in enumerate(data):
                    if not self.contains_personal_info(item, personal_terms):
                        filtered_data.append(item)
                    self.update_status(f"Filtering: {i+1}/{total_items}", 10 + (i+1) * 20 / total_items)
                
                data = filtered_data
            
            # Extract selected fields
            self.update_status("Extracting selected fields...", 30)
            extracted_data = []
            total_items = len(data)
            
            for i, item in enumerate(data):
                extracted_item = {}
                for field in selected_fields:
                    # Handle nested fields (e.g., "info.meta.description")
                    field_parts = field.split('.')
                    value = item
                    
                    try:
                        for part in field_parts:
                            value = value.get(part, "")
                    except (AttributeError, TypeError):
                        value = ""
                    
                    extracted_item[field] = value
                
                extracted_data.append(extracted_item)
                self.update_status(f"Extracting: {i+1}/{total_items}", 30 + (i+1) * 40 / total_items)
            
            # Create individual markdown files for each model
            self.update_status("Creating individual model markdown files...", 65)
            individual_configs_dir = os.path.join(self.output_dir_var.get(), f"export_{timestamp}", "individual-configs")
            os.makedirs(individual_configs_dir, exist_ok=True)
            
            # Create individual markdown files
            for i, item in enumerate(extracted_data):
                model_name = item.get("name", "Unknown Model")
                description = item.get("info.meta.description", "")
                system_prompt = item.get("info.params.system", "")
                
                # Create a computer-friendly filename
                filename = model_name.lower().replace(" ", "-").replace("/", "-").replace("\\", "-")
                filename = ''.join(c for c in filename if c.isalnum() or c in ['-', '_'])
                filename = f"{filename}.md"
                
                # Write the markdown file
                with open(os.path.join(individual_configs_dir, filename), 'w', encoding='utf-8') as f:
                    f.write(f"## {model_name}\n\n")
                    f.write("## Description\n\n")
                    f.write(f"{description}\n\n")
                    f.write("## System Prompt\n\n")
                    f.write(f"{system_prompt}\n")
                
                self.update_status(f"Creating individual files: {i+1}/{len(extracted_data)}", 65 + (i+1) * 5 / len(extracted_data))
            
            # Export to selected format(s)
            export_format = self.export_format_var.get()
            
            if export_format == "all":
                # Export to all formats
                formats = ["csv", "json", "excel", "yaml", "xml", "markdown"]
                total_formats = len(formats)
                
                for i, fmt in enumerate(formats):
                    progress_base = 70 + (i * (30 / total_formats))
                    progress_next = 70 + ((i + 1) * (30 / total_formats))
                    
                    self.update_status(f"Exporting to {fmt.upper()} ({i+1}/{total_formats})...", progress_base)
                    output_path = os.path.join(self.output_dir_var.get(), f"export_{timestamp}{format_ext[fmt]}")
                    
                    if fmt == "csv":
                        self.export_to_csv(extracted_data, output_path)
                    elif fmt == "json":
                        self.export_to_json(extracted_data, output_path)
                    elif fmt == "excel":
                        self.export_to_excel(extracted_data, output_path)
                    elif fmt == "yaml":
                        self.export_to_yaml(extracted_data, output_path)
                    elif fmt == "xml":
                        self.export_to_xml(extracted_data, output_path)
                    elif fmt == "markdown":
                        self.export_to_markdown(extracted_data, output_path)
                    
                    self.update_status(f"Exported to {fmt.upper()} ({i+1}/{total_formats})", progress_next)
                
                self.update_status(f"Export completed successfully to all formats", 100)
                
                # Show success message with all filenames
                success_message = "Export completed successfully to all formats!\n\nOutput files:"
                for fmt in formats:
                    success_message += f"\n- export_{timestamp}{format_ext[fmt]}"
                
                success_message += f"\n\nIndividual model markdown files created in:\n- export_{timestamp}/individual-configs/"
                
                self.root.after(0, lambda: messagebox.showinfo("Success", success_message))
            else:
                # Export to a single format
                output_path = os.path.join(self.output_dir_var.get(), f"export_{timestamp}{format_ext[export_format]}")
                self.update_status(f"Exporting to {export_format.upper()}...", 70)
                
                if export_format == "csv":
                    self.export_to_csv(extracted_data, output_path)
                elif export_format == "json":
                    self.export_to_json(extracted_data, output_path)
                elif export_format == "excel":
                    self.export_to_excel(extracted_data, output_path)
                elif export_format == "yaml":
                    self.export_to_yaml(extracted_data, output_path)
                elif export_format == "xml":
                    self.export_to_xml(extracted_data, output_path)
                elif export_format == "markdown":
                    self.export_to_markdown(extracted_data, output_path)
                
                self.update_status(f"Export completed successfully: {os.path.basename(output_path)}", 100)
                
                # Show success message
                self.root.after(0, lambda: messagebox.showinfo("Success", f"Export completed successfully!\n\nOutput file: {os.path.basename(output_path)}\n\nIndividual model markdown files created in:\n- export_{timestamp}/individual-configs/"))
            
        except Exception as e:
            error_message = f"Error during export: {str(e)}\n\n{traceback.format_exc()}"
            self.update_status(f"Error: {str(e)}", 0)
            self.root.after(0, lambda: messagebox.showerror("Error", error_message))
    
    def update_status(self, message, progress):
        """Update status message and progress bar"""
        self.root.after(0, lambda: self.status_var.set(message))
        self.root.after(0, lambda: self.progress_var.set(progress))
    
    def contains_personal_info(self, obj, personal_terms):
        """Check if an object contains personal information"""
        if isinstance(obj, dict):
            for key, value in obj.items():
                if isinstance(value, (dict, list)):
                    if self.contains_personal_info(value, personal_terms):
                        return True
                elif isinstance(value, str):
                    for term in personal_terms:
                        if term in value:
                            return True
        elif isinstance(obj, list):
            for item in obj:
                if self.contains_personal_info(item, personal_terms):
                    return True
        elif isinstance(obj, str):
            for term in personal_terms:
                if term in obj:
                    return True
        return False
    
    def export_to_csv(self, data, output_path):
        """Export data to CSV format"""
        if not data:
            raise ValueError("No data to export")
        
        # Define the primary fields in the desired order
        primary_fields = ["name", "info.meta.description", "info.params.system"]
        
        # Get all unique keys from all items
        all_keys = set()
        for item in data:
            all_keys.update(item.keys())
        
        # Sort keys with primary fields first, then others alphabetically
        fieldnames = []
        
        # Add primary fields first (if they exist in the data)
        for field in primary_fields:
            if field in all_keys:
                fieldnames.append(field)
                all_keys.remove(field)
        
        # Add remaining fields alphabetically
        fieldnames.extend(sorted(all_keys))
        
        # Rename the headers to be more user-friendly
        header_mapping = {
            "name": "name",
            "info.meta.description": "description",
            "info.params.system": "system_prompt"
        }
        
        with open(output_path, 'w', encoding='utf-8', newline='') as f:
            # Use custom header names for the CSV
            writer = csv.writer(f)
            
            # Write header row with friendly names
            header_row = []
            for field in fieldnames:
                header_row.append(header_mapping.get(field, field))
            
            writer.writerow(header_row)
            
            # Write data rows
            for item in data:
                row = []
                for field in fieldnames:
                    row.append(item.get(field, ""))
                writer.writerow(row)
    
    def export_to_excel(self, data, output_path):
        """Export data to Excel format"""
        if not data:
            raise ValueError("No data to export")
            
        # Define the primary fields in the desired order
        primary_fields = ["name", "info.meta.description", "info.params.system"]
        
        # Get all unique keys from all items
        all_keys = set()
        for item in data:
            all_keys.update(item.keys())
        
        # Sort keys with primary fields first, then others alphabetically
        fieldnames = []
        
        # Add primary fields first (if they exist in the data)
        for field in primary_fields:
            if field in all_keys:
                fieldnames.append(field)
                all_keys.remove(field)
        
        # Add remaining fields alphabetically
        fieldnames.extend(sorted(all_keys))
        
        # Rename the headers to be more user-friendly
        header_mapping = {
            "name": "name",
            "info.meta.description": "description",
            "info.params.system": "system_prompt"
        }
        
        # Create a DataFrame with ordered columns
        df = pd.DataFrame(data)
        
        # Reorder columns based on fieldnames
        ordered_columns = [col for col in fieldnames if col in df.columns]
        df = df[ordered_columns]
        
        # Rename columns
        rename_dict = {col: header_mapping.get(col, col) for col in df.columns}
        df = df.rename(columns=rename_dict)
        
        # Export to Excel
        df.to_excel(output_path, index=False)
    
    def export_to_json(self, data, output_path):
        """Export data to JSON format"""
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
    
    def export_to_yaml(self, data, output_path):
        """Export data to YAML format"""
        with open(output_path, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False)
    
    def export_to_xml(self, data, output_path):
        """Export data to XML format"""
        doc = xml.dom.minidom.getDOMImplementation().createDocument(None, "models", None)
        root = doc.documentElement
        
        for item in data:
            model_elem = doc.createElement("model")
            root.appendChild(model_elem)
            
            for key, value in item.items():
                # Handle nested keys
                if '.' in key:
                    parts = key.split('.')
                    current_elem = model_elem
                    
                    # Create nested elements for each part except the last
                    for i, part in enumerate(parts[:-1]):
                        # Check if this element already exists
                        existing = None
                        for child in current_elem.childNodes:
                            if child.nodeName == part:
                                existing = child
                                break
                        
                        if existing is None:
                            new_elem = doc.createElement(part)
                            current_elem.appendChild(new_elem)
                            current_elem = new_elem
                        else:
                            current_elem = existing
                    
                    # Add the value to the last element
                    field_elem = doc.createElement(parts[-1])
                    text = doc.createTextNode(str(value) if value is not None else "")
                    field_elem.appendChild(text)
                    current_elem.appendChild(field_elem)
                else:
                    # Simple key
                    field_elem = doc.createElement(key)
                    text = doc.createTextNode(str(value) if value is not None else "")
                    field_elem.appendChild(text)
                    model_elem.appendChild(field_elem)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(doc.toprettyxml(indent="  "))
    
    def export_to_markdown(self, data, output_path):
        """Export data to Markdown table format"""
        if not data:
            raise ValueError("No data to export")
        
        # Define the primary fields in the desired order
        primary_fields = ["name", "info.meta.description", "info.params.system"]
        
        # Get all unique keys from all items
        all_keys = set()
        for item in data:
            all_keys.update(item.keys())
        
        # Sort keys with primary fields first, then others alphabetically
        headers = []
        
        # Add primary fields first (if they exist in the data)
        for field in primary_fields:
            if field in all_keys:
                headers.append(field)
                all_keys.remove(field)
        
        # Add remaining fields alphabetically
        headers.extend(sorted(all_keys))
        
        # Rename the headers to be more user-friendly
        header_mapping = {
            "name": "name",
            "info.meta.description": "description",
            "info.params.system": "system_prompt"
        }
        
        # Create markdown table
        with open(output_path, 'w', encoding='utf-8') as f:
            # Write table header
            f.write("# OpenWebUI Model Export\n\n")
            f.write("Generated on: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "\n\n")
            
            # Write table headers with friendly names
            header_row = []
            for field in headers:
                header_row.append(header_mapping.get(field, field))
            
            f.write("| " + " | ".join(header_row) + " |\n")
            f.write("| " + " | ".join(["---"] * len(headers)) + " |\n")
            
            # Write table rows
            for item in data:
                row = []
                for header in headers:
                    value = item.get(header, "")
                    # Escape pipe characters and newlines for markdown
                    if isinstance(value, str):
                        value = value.replace("|", "\\|").replace("\n", "<br>")
                    row.append(str(value) if value is not None else "")
                
                f.write("| " + " | ".join(row) + " |\n")

def main():
    root = tk.Tk()
    
    # Apply a modern theme if available
    try:
        from ttkthemes import ThemedStyle
        style = ThemedStyle(root)
        style.set_theme("arc")  # Use a modern theme
    except ImportError:
        style = ttk.Style()
        style.configure("Accent.TButton", font=("TkDefaultFont", 10, "bold"))
    
    app = ExportApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
