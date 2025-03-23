"""
Test script to verify the improved JSON extraction from LLM responses.
"""

import os
import sys
import json
from datetime import datetime

# Add parent directory to path to import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from modulens.utils.config import load_config
from modulens.utils.llm_client import LLMClient
from modulens.utils.evaluator import extract_json_from_text, evaluate_response_success

def test_json_extraction():
    """Test the extraction of JSON from LLM responses."""
    
    # Sample responses that might be returned by an LLM
    test_cases = [
        # Clean JSON
        '{"success": true, "reason": "The response is detailed", "summary": "Good explanation"}',
        
        # JSON with text before and after
        'Here is my evaluation: {"success": true, "reason": "Good answer", "summary": "Clear explanation"} Hope that helps!',
        
        # JSON in markdown code block
        '```json\n{"success": false, "reason": "Incomplete answer", "summary": null}\n```',
        
        # Messy JSON with newlines and spacing issues
        'Evaluation result:\n{\n  "success" : false,\n  "reason":"Missing key details",\n  "summary":null\n}',
        
        # Invalid JSON (missing quotes)
        '{"success": true, reason: "Good answer", "summary": "Clear details"}',
        
        # No JSON at all
        'The response successfully answers the question with detailed information.'
    ]
    
    results = []
    
    print("Testing JSON extraction from LLM responses...\n")
    
    for i, test_case in enumerate(test_cases):
        print(f"Test case {i+1}:")
        print(f"Input: {test_case[:50]}{'...' if len(test_case) > 50 else ''}")
        
        # Try to extract JSON
        extracted = extract_json_from_text(test_case)
        print(f"Extracted: {extracted}")
        
        # Try to parse the extracted JSON
        valid_json = False
        parsed = None
        try:
            if extracted:
                parsed = json.loads(extracted)
                valid_json = True
                print(f"Valid JSON: Yes - {parsed}")
            else:
                print("Valid JSON: No - Nothing extracted")
        except json.JSONDecodeError:
            print("Valid JSON: No - Extraction failed to produce valid JSON")
        
        results.append({
            "input": test_case,
            "extracted": extracted,
            "valid_json": valid_json,
            "parsed": parsed
        })
        print()
    
    # Now test the complete evaluation function with a real LLM
    print("\nTesting full evaluation with Cohere...")
    
    # Load configuration and initialize LLM client
    config = load_config()
    llm_client = LLMClient(config.get("api_keys", {}))
    
    test_prompt = "What are the main components of a computer?"
    test_response = "The main components of a computer include the CPU (Central Processing Unit), RAM (Random Access Memory), storage devices like HDD or SSD, motherboard, power supply, and input/output devices like keyboard, mouse, and monitor."
    
    try:
        # Evaluate the response
        eval_result = evaluate_response_success(llm_client, test_prompt, test_response)
        print(f"Evaluation result: {json.dumps(eval_result, indent=2)}")
        
        # Add to results
        results.append({
            "type": "live_evaluation",
            "prompt": test_prompt,
            "response": test_response,
            "evaluation": eval_result
        })
    except Exception as e:
        print(f"Error during live evaluation: {str(e)}")
        results.append({
            "type": "live_evaluation",
            "error": str(e)
        })
    
    # Save results to file
    results_dir = os.path.join(os.path.dirname(__file__), "..", "results")
    os.makedirs(results_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = os.path.join(results_dir, f"json_extraction_test_{timestamp}.json")
    
    with open(filename, "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\nTest completed. Results saved to {filename}")

if __name__ == "__main__":
    test_json_extraction() 