"""
Command-line interface utilities for ModuLens.
"""

import argparse
from typing import Dict, Any
import sys
from colorama import init, Fore, Style

# Initialize colorama for colored terminal output
init()

def setup_cli() -> argparse.Namespace:
    """
    Set up the command-line interface for ModuLens.
    
    Returns:
        Parsed command-line arguments
    """
    parser = argparse.ArgumentParser(
        description="ModuLens: A tool for exploring and evaluating LLM moderation systems."
    )
    
    parser.add_argument(
        "--config", 
        type=str, 
        default="config.json",
        help="Path to configuration file"
    )
    
    parser.add_argument(
        "--model", 
        type=str, 
        default="gemini-2.0-flash",
        help="LLM model to use (default: gemini-2.0-flash)"
    )
    
    parser.add_argument(
        "--debug", 
        action="store_true",
        help="Start in debug mode"
    )
    
    return parser.parse_args()

def print_welcome():
    """Print welcome message and information."""
    print(f"{Fore.CYAN}======================================================{Style.RESET_ALL}")
    print(f"{Fore.CYAN}ModuLens: LLM Moderation Exploration Platform{Style.RESET_ALL}")
    print(f"{Fore.CYAN}======================================================{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}This platform is for legitimate research and educational purposes only.{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}Uses both Gemini and Cohere models for each request.{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}Use responsibly and ethically.{Style.RESET_ALL}")
    print(f"{Fore.CYAN}======================================================{Style.RESET_ALL}\n")

def get_user_input(prompt: str) -> str:
    """
    Get user input with proper handling of keyboard interrupts.
    
    Args:
        prompt: The prompt to display to the user
        
    Returns:
        str: User input
    """
    try:
        return input(f"{Fore.GREEN}{prompt}{Style.RESET_ALL}").strip()
    except KeyboardInterrupt:
        print("\nExiting ModuLens.")
        sys.exit(0)

def print_result(result: Dict[str, Any], mode: str = "user"):
    """
    Print the result of a bypass attempt in a user-friendly format.
    
    Args:
        result: The result dictionary
        mode: The mode ('user' or 'debug')
    """
    if mode == "user":
        if result.get("success", False):
            print(f"\n{Fore.GREEN}Success!{Style.RESET_ALL} Using strategy: {result.get('strategy_used', 'unknown')}")
            print(f"\n{Fore.YELLOW}Original Prompt:{Style.RESET_ALL} {result.get('original_prompt', '')}")
            
            # Print the strategy prompt
            if "strategy_prompt" in result:
                print(f"\n{Fore.CYAN}Strategy Prompt:{Style.RESET_ALL}")
                print(result.get("strategy_prompt", ""))
                
            # Print individual model responses
            if "gemini_response" in result:
                print(f"\n{Fore.MAGENTA}Gemini ({result.get('gemini_model', 'unknown')}) Response:{Style.RESET_ALL}")
                print(result.get("gemini_response", ""))
                
            if "cohere_response" in result:
                print(f"\n{Fore.BLUE}Cohere ({result.get('cohere_model', 'unknown')}) Response:{Style.RESET_ALL}")
                print(result.get("cohere_response", ""))
                
            # Print combined response if available
            if "response" in result and not ("gemini_response" in result or "cohere_response" in result):
                print(f"\n{Fore.GREEN}Response:{Style.RESET_ALL}")
                print(result.get("response", ""))
                
        else:
            print(f"\n{Fore.RED}Failure{Style.RESET_ALL}")
            print(f"\n{Fore.YELLOW}Message:{Style.RESET_ALL} {result.get('message', 'Unknown error')}")
            
            if "attempted_strategies" in result:
                print(f"\n{Fore.CYAN}Attempted Strategies:{Style.RESET_ALL}")
                for strategy in result.get("attempted_strategies", []):
                    print(f"  - {strategy}")
    
    else:  # Debug mode
        print(f"\n{Fore.YELLOW}Strategy Results:{Style.RESET_ALL}")
        
        # Print model summary
        model_summary = result.get("model_summary", {})
        if model_summary:
            print(f"\n{Fore.CYAN}Model Summary:{Style.RESET_ALL}")
            # Rating counts only
            print(f"  {Fore.CYAN}Gemini Ratings:{Style.RESET_ALL}")
            print(f"    Useful: {model_summary.get('gemini_useful_count', 0)}")
            print(f"    Alternative: {model_summary.get('gemini_alternative_count', 0)}")
            print(f"    Unrelated: {model_summary.get('gemini_unrelated_count', 0)}")
            print(f"  {Fore.CYAN}Cohere Ratings:{Style.RESET_ALL}")
            print(f"    Useful: {model_summary.get('cohere_useful_count', 0)}")
            print(f"    Alternative: {model_summary.get('cohere_alternative_count', 0)}")
            print(f"    Unrelated: {model_summary.get('cohere_unrelated_count', 0)}")
            print(f"  {Fore.CYAN}Evaluation performed by:{Style.RESET_ALL} {model_summary.get('evaluation_performed_by', 'unknown')}")
        
        # Print individual strategy results
        for idx, strategy in enumerate(result.get("strategy_attempts", [])):
            strategy_name = strategy.get("strategy", "unknown")
            success = strategy.get("success", False)
            moderation_blocked = strategy.get("moderation_blocked", True)
            
            # Print strategy header with success/failure indicator
            moderation_status = f"{Fore.GREEN}PASSED MODERATION{Style.RESET_ALL}" if not moderation_blocked else f"{Fore.RED}BLOCKED BY MODERATION{Style.RESET_ALL}"
            response_status = f"{Fore.GREEN}SUCCESS{Style.RESET_ALL}" if success else f"{Fore.RED}FAILED{Style.RESET_ALL}"
            print(f"\n{idx+1}. {strategy_name} - Moderation: {moderation_status} | Response: {response_status}")
            
            # Print transformed prompt
            print(f"   {Fore.YELLOW}Transformed Prompt:{Style.RESET_ALL}")
            print(f"   {strategy.get('transformed_prompt', '')[:100]}...")
            
            # Print moderation flags if available
            if "moderation_flags" in strategy:
                print(f"   {Fore.YELLOW}Moderation Flags:{Style.RESET_ALL}")
                for flag, value in strategy.get("moderation_flags", {}).items():
                    print(f"   - {flag}: {value}")
            
            # Print Gemini evaluation if available
            if "gemini_Rating" in strategy:
                eval_by = strategy.get("gemini_evaluation_by", "unknown")
                gemini_rating = strategy.get("gemini_Rating", "Unknown")
                
                # Set color based on rating
                rating_color = Fore.GREEN if gemini_rating == "Useful" else Fore.YELLOW if gemini_rating == "Alternative" else Fore.RED
                
                print(f"\n   {Fore.MAGENTA}Gemini ({strategy.get('gemini_model', 'unknown')}) Evaluation:{Style.RESET_ALL}")
                print(f"   Evaluated by: {eval_by}")
                print(f"   Rating: {rating_color}{gemini_rating}{Style.RESET_ALL}")
                print(f"   Reason: {strategy.get('gemini_Reason', 'Not provided')}")
                
                # Print response preview
                if "gemini_response" in strategy:
                    response = strategy.get("gemini_response", "")
                    print(f"   {Fore.MAGENTA}Response Preview:{Style.RESET_ALL} {response[:150]}...")
            
            # Print Cohere evaluation if available
            if "cohere_Rating" in strategy:
                eval_by = strategy.get("cohere_evaluation_by", "unknown")
                cohere_rating = strategy.get("cohere_Rating", "Unknown")
                
                # Set color based on rating
                rating_color = Fore.GREEN if cohere_rating == "Useful" else Fore.YELLOW if cohere_rating == "Alternative" else Fore.RED
                
                print(f"\n   {Fore.BLUE}Cohere ({strategy.get('cohere_model', 'unknown')}) Evaluation:{Style.RESET_ALL}")
                print(f"   Evaluated by: {eval_by}")
                print(f"   Rating: {rating_color}{cohere_rating}{Style.RESET_ALL}")
                print(f"   Reason: {strategy.get('cohere_Reason', 'Not provided')}")
                
                # Print response preview
                if "cohere_response" in strategy:
                    response = strategy.get("cohere_response", "")
                    print(f"   {Fore.BLUE}Response Preview:{Style.RESET_ALL} {response[:150]}...")
        
        # Print metrics
        metrics = result.get("metrics", {})
        if metrics:
            print(f"\n{Fore.YELLOW}Metrics:{Style.RESET_ALL}")
            print(f"   Success Rate: {metrics.get('response_success_rate', 0) * 100:.1f}%")
            print(f"   Total Attempts: {metrics.get('total_attempts', 0)}")
            print(f"   Successful Attempts: {metrics.get('response_successful_attempts', 0)}")
            print(f"   Useful Ratings: {metrics.get('gemini_useful_ratings', 0) + metrics.get('cohere_useful_ratings', 0)}")
            print(f"   Alternative Ratings: {metrics.get('gemini_alternative_ratings', 0) + metrics.get('cohere_alternative_ratings', 0)}")
            print(f"   Unrelated Ratings: {metrics.get('gemini_unrelated_ratings', 0) + metrics.get('cohere_unrelated_ratings', 0)}")
        
    print(f"\n{Fore.CYAN}=========================={Style.RESET_ALL}\n") 