"""
Configuration utilities for ModuLens.
"""

import json
import os
from typing import Dict, Any
import sys
from dotenv import load_dotenv

def load_config(config_path: str = "config.json") -> Dict[str, Any]:
    """
    Load configuration from file and environment variables.
    
    Args:
        config_path: Path to configuration file
        
    Returns:
        Dict of configuration settings
    """
    # Default configuration
    config = {
        "api_keys": {
            "openai": "",
            "anthropic": "",
            "gemini": "",
            "cohere": ""
        },
        "models": {
            "gemini_primary": "gemini-2.0-flash",
            "cohere_primary": "command",
            "alternatives": ["command-r", "command-light", "gemini-1.5-flash"]
        },
        "strategies": {
            "caesar_cipher": {"enabled": True},
            "tense_transformation": {"enabled": True},
            "chain_of_thought": {"enabled": True},
            "code_completion": {"enabled": True},
            "text_continuation": {"enabled": True}
        },
        "logging": {
            "enabled": True,
            "log_dir": "logs",
            "level": "INFO"
        }
    }
    
    # Load environment variables
    load_dotenv()
    
    # Try to load configuration from file
    try:
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                file_config = json.load(f)
                # Update config with file values
                _deep_update(config, file_config)
    except Exception as e:
        print(f"Warning: Could not load configuration from {config_path}: {str(e)}")
    
    # Override with environment variables
    for provider in config["api_keys"]:
        env_var = f"MODULENS_{provider.upper()}_API_KEY"
        if os.environ.get(env_var):
            config["api_keys"][provider] = os.environ.get(env_var)
    
    # If there are missing API keys and no sample config exists, create one
    if not os.path.exists(config_path) and not any(config["api_keys"].values()):
        _create_sample_config(config_path)
        print(f"Created sample configuration file at {config_path}")
        print("Please edit this file with your API keys and other settings.")
    
    # Validate configuration - need at least one provider's API key
    if not any(config["api_keys"].values()):
        print("Error: No API keys configured. Please set at least one API key in config file or environment variables.")
        print("Required environment variables: MODULENS_GEMINI_API_KEY or MODULENS_COHERE_API_KEY")
        sys.exit(1)
    
    return config

def _deep_update(original: Dict[str, Any], update: Dict[str, Any]) -> Dict[str, Any]:
    """
    Deep update a nested dictionary.
    
    Args:
        original: Original dictionary to update
        update: Dictionary with new values
        
    Returns:
        Updated dictionary
    """
    for key, value in update.items():
        if key in original and isinstance(original[key], dict) and isinstance(value, dict):
            _deep_update(original[key], value)
        else:
            original[key] = value
    return original

def _create_sample_config(config_path: str) -> None:
    """
    Create a sample configuration file.
    
    Args:
        config_path: Path to write the sample configuration
    """
    sample_config = {
        "api_keys": {
            "openai": "",
            "anthropic": "",
            "gemini": "YOUR_GEMINI_API_KEY_HERE",
            "cohere": "YOUR_COHERE_API_KEY_HERE"
        },
        "models": {
            "gemini_primary": "gemini-2.0-flash",
            "cohere_primary": "command",
            "alternatives": ["command-r", "command-light", "gemini-1.5-flash"]
        },
        "strategies": {
            "caesar_cipher": {"enabled": True},
            "tense_transformation": {"enabled": True},
            "chain_of_thought": {"enabled": True},
            "code_completion": {"enabled": True},
            "text_continuation": {"enabled": True}
        },
        "logging": {
            "enabled": True,
            "log_dir": "logs",
            "level": "INFO"
        }
    }
    
    try:
        os.makedirs(os.path.dirname(config_path) or '.', exist_ok=True)
        with open(config_path, 'w') as f:
            json.dump(sample_config, f, indent=4)
    except Exception as e:
        print(f"Warning: Could not create sample configuration file: {str(e)}") 