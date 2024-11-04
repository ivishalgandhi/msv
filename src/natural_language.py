# src/natural_language.py
from dataclasses import dataclass
from typing import List, Optional, Dict
try:
    from openai import OpenAI
except ImportError:
    raise ImportError(
        "The openai package is required for natural language features. "
        "Install it with: pip install openai>=1.0.0"
    )
import json
from dotenv import load_dotenv
import os
import tomli
from pathlib import Path

@dataclass
class MergeRequest:
    source_file: str
    destination_file: str
    match_column: str
    columns_to_copy: List[str]
    ignore_case: bool = False
    join_type: str = 'left'
    output_file: Optional[str] = None
    source_sheet: Optional[str] = None
    dest_sheet: Optional[str] = None
    output_sheet: Optional[str] = None

def setup_openai_functions() -> List[Dict]:
    """Define the OpenAI function schema for file merging operations"""
    return [{
        "name": "merge_files",
        "description": "Merge data from source file into destination file",
        "parameters": {
            "type": "object",
            "properties": {
                "source_file": {
                    "type": "string",
                    "description": "Path to source CSV or Excel file"
                },
                "destination_file": {
                    "type": "string",
                    "description": "Path to destination CSV or Excel file"
                },
                "match_column": {
                    "type": "string",
                    "description": "Column name to match between files"
                },
                "columns_to_copy": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of columns to copy from source"
                },
                "ignore_case": {
                    "type": "boolean",
                    "description": "Whether to ignore case when matching"
                },
                "join_type": {
                    "type": "string",
                    "enum": ["left", "right", "outer", "inner", "left_outer", "right_outer"],
                    "description": "Type of join operation"
                },
                "output_file": {
                    "type": "string",
                    "description": "Optional output file path"
                },
                "source_sheet": {
                    "type": "string",
                    "description": "Sheet name for source Excel file"
                },
                "dest_sheet": {
                    "type": "string",
                    "description": "Sheet name for destination Excel file"
                },
                "output_sheet": {
                    "type": "string",
                    "description": "Sheet name for output Excel file"
                }
            },
            "required": ["source_file", "destination_file", "match_column", "columns_to_copy"]
        }
    }]

def get_ai_config():
    """Load AI configuration from config.toml"""
    # Search for config.toml in multiple locations
    config_locations = [
        Path.cwd() / "config.toml",  # Current working directory
        Path(__file__).parent.parent / "config.toml",  # Project root
        Path.home() / ".config" / "msv" / "config.toml",  # User config directory
        Path("/etc/msv/config.toml"),  # System config directory
    ]
    
    for config_path in config_locations:
        if config_path.exists():
            try:
                with open(config_path, "rb") as f:
                    config = tomli.load(f)
                    provider = config.get("default", {}).get("provider", "openai")
                    if provider not in config:
                        raise ValueError(f"Provider '{provider}' not found in config")
                    return config[provider]
            except Exception as e:
                print(f"Warning: Error reading {config_path}: {e}")
                continue
    
    raise ValueError(
        "config.toml not found. Create it from config.toml.example "
        "in one of these locations:\n" + 
        "\n".join(f"- {p}" for p in config_locations)
    )

def process_natural_language(query: str, api_key: Optional[str] = None) -> MergeRequest:
    """Process natural language query using OpenAI function calling"""
    if not api_key:
        config = get_ai_config()
        if config:
            api_key = config["api_key"]
            model = config["model"]
            base_url = config["url"]
        else:
            raise ValueError("AI configuration not found in config.toml")
    
    client = OpenAI(
        api_key=api_key,
        base_url=base_url
    )
    
    response = client.chat.completions.create(
        model=model,  # Use model from config
        messages=[{
            "role": "user",
            "content": query
        }],
        functions=setup_openai_functions(),
        function_call={"name": "merge_files"}
    )

    function_args = json.loads(response.choices[0].message.function_call.arguments)
    
    return MergeRequest(
        source_file=function_args["source_file"],
        destination_file=function_args["destination_file"],
        match_column=function_args["match_column"],
        columns_to_copy=function_args["columns_to_copy"],
        ignore_case=function_args.get("ignore_case", False),
        join_type=function_args.get("join_type", "left"),
        output_file=function_args.get("output_file"),
        source_sheet=function_args.get("source_sheet"),
        dest_sheet=function_args.get("dest_sheet"),
        output_sheet=function_args.get("output_sheet")
    )