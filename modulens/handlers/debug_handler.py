"""
Handler for Debug Mode in ModuLens.
"""

from typing import Dict, Any, List

def process_debug_mode(engine, prompt: str) -> Dict[str, Any]:
    """
    Process a user prompt in Debug Mode.
    In this mode, we apply all strategies and return detailed information about each attempt,
    including responses from both Gemini and Cohere models for each strategy.
    All responses are evaluated by Cohere for effectiveness.
    
    Args:
        engine: The ModuLens engine instance
        prompt: The user's prompt
        
    Returns:
        Dict containing results of all strategy attempts and metrics
    """
    # Apply all bypass strategies and collect results
    results = engine.apply_bypass_strategies(prompt, mode="debug")
    
    # Calculate metrics
    metrics = engine.get_metrics(results)
    
    # Create a summary of each strategy attempt using evaluation data that's already present
    strategy_summaries = []
    for result in results:
        strategy_name = result.get("strategy", "unknown")
        is_blocked = result.get("is_blocked", True)
        transformed_prompt = result.get("prompt", "")
        
        summary = {
            "strategy": strategy_name,
            "moderation_blocked": is_blocked,  # Original moderation block status
            "transformed_prompt": transformed_prompt,
            "success": result.get("response_success", False),  # Overall success from evaluations
            "evaluated_by": "cohere-command"  # Indicate that Cohere performed the evaluation
        }
        
        # Include moderation flags if available
        if "moderation_flags" in result:
            summary["moderation_flags"] = result["moderation_flags"]
            
        # Include Gemini information and evaluation if available
        if "gemini_response" in result:
            summary["gemini_response"] = result["gemini_response"]
            summary["gemini_model"] = result.get("gemini_model", "unknown")
            summary["gemini_Rating"] = result.get("gemini_Rating", "Unknown")
            summary["gemini_Reason"] = result.get("gemini_Reason", "No evaluation")
            summary["gemini_evaluation_by"] = "cohere-command"  # Indicate Cohere evaluated this
            
        # Include Cohere information and evaluation if available
        if "cohere_response" in result:
            summary["cohere_response"] = result["cohere_response"]
            summary["cohere_model"] = result.get("cohere_model", "unknown")
            summary["cohere_Rating"] = result.get("cohere_Rating", "Unknown")
            summary["cohere_Reason"] = result.get("cohere_Reason", "No evaluation")
            summary["cohere_evaluation_by"] = "cohere-command"  # Indicate Cohere evaluated this
            
        # Include combined response if available
        if "response" in result:
            summary["combined_response"] = result["response"]
            
        # Include Gemini error if present
        if "gemini_error" in result:
            summary["gemini_error"] = result["gemini_error"]
            
        # Include Cohere error if present
        if "cohere_error" in result:
            summary["cohere_error"] = result["cohere_error"]
            
        # Include generic error information if present
        if "error" in result:
            summary["error"] = result["error"]
            
        strategy_summaries.append(summary)
    
    # Find the successful strategies based on "Useful" Rating
    successful_strategies = [
        r.get("strategy") for r in strategy_summaries 
        if (r.get("gemini_Rating", "") == "Useful" or 
            r.get("cohere_Rating", "") == "Useful") and 
        r.get("strategy") != "original"
    ]
    
    # Create a summary of model ratings
    model_summary = {
        # Rating count fields
        "gemini_useful_count": metrics.get("gemini_useful_ratings", 0),
        "gemini_alternative_count": metrics.get("gemini_alternative_ratings", 0),
        "gemini_unrelated_count": metrics.get("gemini_unrelated_ratings", 0),
        "cohere_useful_count": metrics.get("cohere_useful_ratings", 0),
        "cohere_alternative_count": metrics.get("cohere_alternative_ratings", 0),
        "cohere_unrelated_count": metrics.get("cohere_unrelated_ratings", 0),
        "total_strategies": len(results) - 1,  # Subtract 1 to exclude the original prompt test
        "evaluation_performed_by": "cohere-command"  # Indicate Cohere performed all evaluations
    }
    
    # Sort strategy summaries in the desired order
    # Define the order of strategies
    strategy_order = [
        "original", 
        "text_continuation", "TextContinuationStrategy",
        "code_completion", "CodeCompletionStrategy",
        "tense_transformation", "TenseTransformationStrategy",
        "caesar_cipher", "CaesarCipherStrategy",
        "chain_of_thought", "ChainOfThoughtStrategy"
    ]
    
    # Create a dictionary to assign priority values
    strategy_priorities = {strategy: idx for idx, strategy in enumerate(strategy_order)}
    
    # Sort the strategy summaries based on the order defined
    sorted_summaries = sorted(
        strategy_summaries,
        key=lambda x: strategy_priorities.get(x.get("strategy", ""), 999)  # Default to high value if not found
    )
    
    return {
        "success": len(successful_strategies) > 0,
        "original_prompt": prompt,
        "strategy_attempts": sorted_summaries,  # Use sorted summaries
        "metrics": metrics,
        "model_summary": model_summary,
        "successful_strategies": successful_strategies,
        "message": f"{len(successful_strategies)} of {len(results) - 1} strategies succeeded." if successful_strategies else "All strategies failed.",
        "evaluation_performed_by": "cohere-command"  # Indicate Cohere performed all evaluations
    } 