#!/usr/bin/env python3
"""
ModuLens: A platform to explore, evaluate, and responsibly bypass LLM moderation systems.
"""

import os
import sys
from typing import Dict, List, Optional

from modulens.core.auth import authenticate_user
from modulens.core.engine import ModuLensEngine
from modulens.handlers.user_handler import process_user_mode
from modulens.handlers.debug_handler import process_debug_mode
from modulens.utils.cli import setup_cli, get_user_input, print_welcome, print_result
from modulens.utils.config import load_config

def main():
    """Main entry point for the ModuLens application."""
    print_welcome()
    
    # Parse command line arguments
    args = setup_cli()
    
    # Load configuration
    config = load_config(args.config)
    
    # If model was specified in command line, override config
    if args.model:
        config["models"]["primary"] = args.model
    
    # Authentication step (simplified for now)
    if not authenticate_user():
        print("Authentication failed. Access denied.")
        sys.exit(1)
    
    print("User authenticated successfully! Welcome to ModuLens.")
    
    # Initialize the ModuLens engine
    engine = ModuLensEngine(config)
    
    # If debug flag was set, start in debug mode by default
    default_mode = "2" if args.debug else None
    
    while True:
        # Get user input (prompt and mode)
        user_prompt = get_user_input("Enter your prompt (or 'exit' to quit): ")
        if user_prompt.lower() in ["exit", "quit", "q"]:
            print("Thank you for using ModuLens. Goodbye!")
            break
        
        # Determine which model to use
        available_models = [config["models"]["primary"]] + config["models"]["alternatives"]
        active_providers = [
            ("OpenAI", bool(config["api_keys"]["openai"])),
            ("Anthropic", bool(config["api_keys"]["anthropic"])),
            ("Gemini", bool(config["api_keys"]["gemini"])),
            ("Cohere", bool(config["api_keys"]["cohere"]))
        ]
        
        print(f"\nUsing model: {config['models']['primary']}")
        print("Available providers:", ", ".join(p[0] for p in active_providers if p[1]))
            
        # Select mode
        print("\nSelect mode:")
        print("1. User Mode - Get a response with automatic bypass")
        print("2. Debug Mode - View all attempted strategies and results")
        
        mode_choice = default_mode or get_user_input("Choose mode (1/2): ")
        
        # Process based on mode
        if mode_choice == "1":
            result = process_user_mode(engine, user_prompt)
            print_result(result, mode="user")
        elif mode_choice == "2":
            result = process_debug_mode(engine, user_prompt)
            print_result(result, mode="debug")
        else:
            print("Invalid mode selection. Please try again.")

if __name__ == "__main__":
    main() 