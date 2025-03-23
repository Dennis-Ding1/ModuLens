"""
Test script to verify Cohere-only evaluation functionality.
"""

import os
import sys
import json
from datetime import datetime

# Add parent directory to path to import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from modulens.utils.config import load_config
from modulens.core.engine import ModuLensEngine
from modulens.utils.evaluator import evaluate_response_success
from modulens.utils.llm_client import LLMClient

def test_cohere_evaluation():
    """Test that evaluations are performed by Cohere only."""
    
    # Load configuration
    config = load_config()
    
    # Initialize LLM client and engine
    llm_client = LLMClient(config.get("api_keys", {}))
    engine = ModuLensEngine(config)
    
    print(f"Testing Cohere-only evaluation...")
    
    # Test a simple example
    test_prompt = "How does a car engine work?"
    test_response = "A car engine works by converting gasoline into motion through combustion. The basic process involves intake of fuel and air, compression, combustion triggered by spark plugs, and exhaust."
    
    # Direct evaluation through the evaluator
    print("Running direct evaluation...")
    eval_result = evaluate_response_success(
        llm_client,
        test_prompt,
        test_response
    )
    
    print(f"Evaluation result: {'SUCCESS' if eval_result['success'] else 'FAILED'}")
    print(f"Reason: {eval_result['reason']}")
    if eval_result['success']:
        print(f"Summary: {eval_result['summary']}")
    
    # Test evaluation through the engine in debug mode
    print("\nTesting evaluation through the engine in debug mode...")
    test_prompt = "What are the key components of a bicycle?"
    
    # Run bypass strategies in debug mode
    result = engine.apply_bypass_strategies(test_prompt, mode="debug")
    
    # Examine the first result with responses
    for strategy_result in result:
        if "gemini_response" in strategy_result and "gemini_success" in strategy_result:
            print(f"\nStrategy: {strategy_result.get('strategy', 'unknown')}")
            print(f"Gemini response evaluated successfully: {'yes' if 'gemini_success' in strategy_result else 'no'}")
            print(f"Evaluation result: {'SUCCESS' if strategy_result.get('gemini_success', False) else 'FAILED'}")
            print(f"Reason: {strategy_result.get('gemini_reason', 'Not provided')}")
            
            # Only need to check one result to verify
            break
    
    # Save the test results
    test_results = {
        "direct_evaluation": eval_result,
        "engine_evaluation_sample": strategy_result
    }
    
    # Create results directory if it doesn't exist
    results_dir = os.path.join(os.path.dirname(__file__), "..", "results")
    os.makedirs(results_dir, exist_ok=True)
    
    # Save results with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = os.path.join(results_dir, f"cohere_evaluation_test_{timestamp}.json")
    
    with open(filename, "w") as f:
        json.dump(test_results, f, indent=2)
    
    print(f"\nTest completed. Results saved to {filename}")
    
if __name__ == "__main__":
    test_cohere_evaluation() 