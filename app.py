#!/usr/bin/env python3
"""
Main entry point for ModuLens.
"""

import os
import sys
import json
from modulens.main import main
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Check if config exists and has required API keys
if not os.path.exists("config.json"):
    # Create minimal config file if it doesn't exist
    gemini_key = os.environ.get("MODULENS_GEMINI_API_KEY") or input("Enter your Gemini API key: ").strip()
    cohere_key = os.environ.get("MODULENS_COHERE_API_KEY") or input("Enter your Cohere API key: ").strip()
    
    if not gemini_key and not cohere_key:
        print("Error: You must provide at least one API key (Gemini or Cohere)")
        sys.exit(1)
    
    config = {
        "api_keys": {"openai": "", "anthropic": "", "gemini": gemini_key, "cohere": cohere_key},
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
        "logging": {"enabled": True, "log_dir": "logs", "level": "INFO"}
    }
    
    with open("config.json", "w") as f:
        json.dump(config, f, indent=4)
    
    print(f"Created configuration file with API keys")

# Run the main application
if __name__ == "__main__":
    main() 