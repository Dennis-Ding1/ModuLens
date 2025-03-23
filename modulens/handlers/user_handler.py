"""
Handler for User Mode in ModuLens.
"""

from typing import Dict, Any

def process_user_mode(engine, prompt: str) -> Dict[str, Any]:
    """
    Process a user prompt in User Mode.
    In this mode, we try all bypass strategies and return the first successful response
    using both Gemini and Cohere models.
    
    Args:
        engine: The ModuLens engine instance
        prompt: The user's prompt
        
    Returns:
        Dict containing results with the successful response and strategy
    """
    # Apply bypass strategies to the prompt
    results = engine.apply_bypass_strategies(prompt, mode="user")
    
    # Find the first successful result (non-blocked with a response)
    successful_result = next(
        (r for r in results if not r.get("is_blocked", True) and "response" in r), 
        None
    )
    
    # If we found a successful result, return it
    if successful_result:
        # Extract individual model responses
        gemini_response = successful_result.get("gemini_response", "")
        cohere_response = successful_result.get("cohere_response", "")
        gemini_model = successful_result.get("gemini_model", "unknown")
        cohere_model = successful_result.get("cohere_model", "unknown")
        
        # Determine which model gave the better response
        gemini_success = successful_result.get("gemini_success", False)
        cohere_success = successful_result.get("cohere_success", False)
        
        # Choose the best model based on success flags
        best_model = "gemini" if gemini_success else "cohere" if cohere_success else "gemini"
        
        # Prepare the combined result
        return {
            "success": True,
            "original_prompt": prompt,
            "response": successful_result.get("response", ""),
            "gemini_response": gemini_response,
            "cohere_response": cohere_response,
            "gemini_model": gemini_model,
            "cohere_model": cohere_model,
            "strategy_used": successful_result.get("strategy", "unknown"),
            "strategy_prompt": successful_result.get("prompt", ""),
            "message": f"Successfully bypassed moderation using the {successful_result.get('strategy', 'unknown')} strategy.",
            "best_strategy": successful_result,
            "best_model": best_model
        }
    
    # If all strategies failed, return an error
    return {
        "success": False,
        "original_prompt": prompt,
        "message": "All bypass strategies failed. The content may be against ethical guidelines or the strategies need improvement.",
        "attempted_strategies": [r.get("strategy") for r in results if r.get("strategy") != "original"],
        "best_strategy": None,
        "best_model": None
    } 