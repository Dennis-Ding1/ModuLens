"""
Core engine for ModuLens that manages prompt rewriting strategies and LLM interactions.
"""

from typing import Dict, List, Any, Optional
import time
import random
import os
import json
from datetime import datetime

from modulens.strategies.base import BaseStrategy
from modulens.strategies.original import OriginalStrategy
from modulens.strategies.caesar_cipher import CaesarCipherStrategy
from modulens.strategies.tense_transformation import TenseTransformationStrategy
from modulens.strategies.chain_of_thought import ChainOfThoughtStrategy
from modulens.strategies.code_completion import CodeCompletionStrategy
from modulens.strategies.text_continuation import TextContinuationStrategy
from modulens.utils.llm_client import LLMClient
from modulens.utils.logger import Logger
from modulens.utils.evaluator import evaluate_response_success


class ModuLensEngine:
    """
    Core engine that orchestrates the ModuLens functionality.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the ModuLens engine with configuration.
        
        Args:
            config: Configuration dictionary for the engine
        """
        self.config = config
        self.logger = Logger()
        self.llm_client = LLMClient(config.get("api_keys", {}))
        
        # Initialize strategies with OriginalStrategy as the first strategy
        self.strategies = [
            OriginalStrategy(),
            CaesarCipherStrategy(),
            TenseTransformationStrategy(),
            ChainOfThoughtStrategy(),
            CodeCompletionStrategy(),
            TextContinuationStrategy()
        ]
        
        # Get primary models from config
        self.gemini_primary = config.get("models", {}).get("gemini_primary", "gemini-2.0-flash")
        self.cohere_primary = config.get("models", {}).get("cohere_primary", "command")
        
        # Get alternative models from config
        self.gemini_alternatives = [model for model in config.get("models", {}).get("alternatives", []) 
                                   if model.startswith("gemini")]
        self.cohere_alternatives = [model for model in config.get("models", {}).get("alternatives", []) 
                                   if model.startswith("command") or model.startswith("co.")]
        
        # Complete model lists including primary models
        self.gemini_models = [self.gemini_primary] + self.gemini_alternatives
        self.cohere_models = [self.cohere_primary] + self.cohere_alternatives
    
    def evaluate_original_prompt(self, prompt: str) -> Dict[str, Any]:
        """
        Test if the original prompt is blocked by the LLM's moderation and get responses if not blocked.
        
        Args:
            prompt: The user's original prompt
            
        Returns:
            Dict with results of the moderation check and model responses if not blocked
        """
        try:
            # Check moderation
            mod_result = self.llm_client.check_moderation(prompt)
            is_blocked = mod_result.get("is_blocked", False)
            
            result = {
                "prompt": prompt,
                "is_blocked": is_blocked,
                "moderation_flags": mod_result.get("flags", {}),
                "strategy": "original",
                "timestamp": time.time()
            }
            
            # If not blocked, get responses from both models
            if not is_blocked:
                try:
                    # Use the OriginalStrategy's get_response method
                    original_response = self.strategies[0].get_response(
                        self.llm_client, 
                        prompt, 
                        self.gemini_primary, 
                        self.cohere_primary
                    )
                    
                    # Update result with response data
                    result.update({
                        k: v for k, v in original_response.items() 
                        if k not in ['strategy', 'prompt', 'is_blocked']
                    })
                except Exception as e:
                    self.logger.error(f"Error getting responses for original prompt: {str(e)}")
                    result["error"] = str(e)
            
            return result
        except Exception as e:
            self.logger.error(f"Error checking moderation: {str(e)}")
            return {
                "prompt": prompt,
                "is_blocked": True,
                "error": str(e),
                "strategy": "original",
                "timestamp": time.time()
            }
    
    def apply_bypass_strategies(self, prompt: str, mode: str = "user") -> List[Dict[str, Any]]:
        """
        Apply available bypass strategies to find one that works.
        
        Args:
            prompt: The original user prompt
            mode: Operating mode ('user' or 'debug')
            
        Returns:
            List of results from all attempted strategies
        """
        results = []
        
        # Try original prompt first to see if it's blocked
        original_result = self.evaluate_original_prompt(prompt)
        
        # Evaluate responses for original prompt if they exist
        if "gemini_response" in original_result:
            # Note: Using Cohere for evaluation regardless of the model parameter
            gemini_eval = evaluate_response_success(
                self.llm_client,
                prompt,
                original_result["gemini_response"]
                # No model parameter - will use Cohere by default
            )
            original_result["gemini_Rating"] = gemini_eval["Rating"]
            original_result["gemini_Reason"] = gemini_eval["Reason"]
            original_result["gemini_evaluation_by"] = "cohere-command"
            
        if "cohere_response" in original_result:
            cohere_eval = evaluate_response_success(
                self.llm_client,
                prompt,
                original_result["cohere_response"]
            )
            original_result["cohere_Rating"] = cohere_eval["Rating"]
            original_result["cohere_Reason"] = cohere_eval["Reason"]
            original_result["cohere_evaluation_by"] = "cohere-command"
            
        # Set overall success flag based on any model's "Useful" Rating
        original_result["response_success"] = (
            original_result.get("gemini_Rating", "") == "Useful" or 
            original_result.get("cohere_Rating", "") == "Useful"
        )
        
        results.append(original_result)
        
        # In user mode, if original is not blocked, return immediately
        if not original_result.get("is_blocked", True) and mode == "user":
            # Original prompt already includes responses from evaluate_original_prompt
            self._save_results(results, mode)
            return results
        
        # Apply each strategy starting from index 1 (skip OriginalStrategy) and check if it bypasses moderation
        for strategy in self.strategies[1:]:
            try:
                # Apply strategy to transform the prompt
                transformed_prompt = strategy.apply(prompt)
                
                # Check if transformed prompt passes moderation
                mod_result = self.llm_client.check_moderation(transformed_prompt)
                
                # If the prompt is blocked, note it but continue with responses in debug mode
                is_blocked = mod_result.get("is_blocked", True)
                
                strategy_result = {
                    "prompt": transformed_prompt,
                    "original_prompt": prompt,
                    "is_blocked": is_blocked,
                    "moderation_flags": mod_result.get("flags", {}),
                    "strategy": strategy.name,
                    "timestamp": time.time()
                }
                
                # In debug mode, always get responses from both models
                if mode == "debug":
                    # Use the strategy's get_response method to get responses
                    response_result = strategy.get_response(
                        self.llm_client, 
                        transformed_prompt, 
                        self.gemini_primary, 
                        self.cohere_primary
                    )
                    
                    # Update strategy result with response data
                    strategy_result.update({
                        k: v for k, v in response_result.items() 
                        if k not in ["strategy", "prompt", "is_blocked"]
                    })
                    
                    # Evaluate the responses
                    if "gemini_response" in strategy_result:
                        gemini_eval = evaluate_response_success(
                            self.llm_client,
                            prompt,
                            strategy_result["gemini_response"]
                        )
                        strategy_result["gemini_Rating"] = gemini_eval["Rating"]
                        strategy_result["gemini_Reason"] = gemini_eval["Reason"]
                        strategy_result["gemini_evaluation_by"] = "cohere-command"
                        
                    if "cohere_response" in strategy_result:
                        cohere_eval = evaluate_response_success(
                            self.llm_client,
                            prompt,
                            strategy_result["cohere_response"]
                        )
                        strategy_result["cohere_Rating"] = cohere_eval["Rating"]
                        strategy_result["cohere_Reason"] = cohere_eval["Reason"]
                        strategy_result["cohere_evaluation_by"] = "cohere-command"
                        
                    # Set overall success flag based on any model's Rating being "Useful"
                    strategy_result["response_success"] = (
                        strategy_result.get("gemini_Rating", "") == "Useful" or 
                        strategy_result.get("cohere_Rating", "") == "Useful"
                    )
                    
                elif mode == "user" and not is_blocked:
                    # In user mode, only get responses if moderation check passes
                    # Use the strategy's get_response method to get responses
                    response_result = strategy.get_response(
                        self.llm_client, 
                        transformed_prompt, 
                        self.gemini_primary, 
                        self.cohere_primary
                    )
                    
                    # Update strategy result with response data
                    strategy_result.update({
                        k: v for k, v in response_result.items() 
                        if k not in ["strategy", "prompt", "is_blocked"]
                    })
                    
                    # Evaluate the responses
                    if "gemini_response" in strategy_result:
                        gemini_eval = evaluate_response_success(
                            self.llm_client,
                            prompt,
                            strategy_result["gemini_response"]
                        )
                        strategy_result["gemini_Rating"] = gemini_eval["Rating"]
                        strategy_result["gemini_Reason"] = gemini_eval["Reason"]
                        strategy_result["gemini_evaluation_by"] = "cohere-command"
                        
                    if "cohere_response" in strategy_result:
                        cohere_eval = evaluate_response_success(
                            self.llm_client,
                            prompt,
                            strategy_result["cohere_response"]
                        )
                        strategy_result["cohere_Rating"] = cohere_eval["Rating"]
                        strategy_result["cohere_Reason"] = cohere_eval["Reason"]
                        strategy_result["cohere_evaluation_by"] = "cohere-command"
                        
                    # Set overall success flag based on any model's Rating being "Useful"
                    strategy_result["response_success"] = (
                        strategy_result.get("gemini_Rating", "") == "Useful" or 
                        strategy_result.get("cohere_Rating", "") == "Useful"
                    )
                
                results.append(strategy_result)
                
                # In user mode, we can return after first successful bypass
                if mode == "user" and not strategy_result.get("is_blocked", True) and "response" in strategy_result:
                    break
                    
            except Exception as e:
                self.logger.error(f"Error with strategy {strategy.name}: {str(e)}")
                results.append({
                    "prompt": prompt,
                    "is_blocked": True,
                    "error": str(e),
                    "strategy": strategy.name,
                    "timestamp": time.time()
                })
        
        # Save results to a JSON file in the results directory
        self._save_results(results, mode)
        
        return results
    
    def _save_results(self, results: List[Dict[str, Any]], mode: str) -> None:
        """
        Save results to a JSON file in the results directory.
        
        Args:
            results: List of results to save
            mode: Operating mode ('user' or 'debug')
        """
        try:
            # Create results directory if it doesn't exist
            os.makedirs("results", exist_ok=True)
            
            # Create a timestamped filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"results/{mode}_mode_{timestamp}.json"
            
            # Write results to file
            with open(filename, "w") as f:
                json.dump(results, f, indent=2)
                
            self.logger.info(f"Results saved to {filename}")
        except Exception as e:
            self.logger.error(f"Error saving results: {str(e)}")
    
    def get_metrics(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calculate metrics based on the results of bypass attempts.
        
        Args:
            results: List of results from bypass attempts
            
        Returns:
            Dict of metrics
        """
        total_attempts = len(results)
        
        # Moderation bypass metrics
        moderation_successful_attempts = sum(1 for r in results if not r.get("is_blocked", True))
        
        # Response evaluation success metrics based on Rating
        response_successful_attempts = sum(1 for r in results if r.get("response_success", False))
        
        # Count responses by model
        gemini_responses = sum(1 for r in results if "gemini_response" in r)
        cohere_responses = sum(1 for r in results if "cohere_response" in r)
        
        # Count ratings by model
        gemini_useful_ratings = sum(1 for r in results if r.get("gemini_Rating", "") == "Useful")
        gemini_alternative_ratings = sum(1 for r in results if r.get("gemini_Rating", "") == "Alternative")
        gemini_unrelated_ratings = sum(1 for r in results if r.get("gemini_Rating", "") == "Unrelated")
        
        cohere_useful_ratings = sum(1 for r in results if r.get("cohere_Rating", "") == "Useful")
        cohere_alternative_ratings = sum(1 for r in results if r.get("cohere_Rating", "") == "Alternative")
        cohere_unrelated_ratings = sum(1 for r in results if r.get("cohere_Rating", "") == "Unrelated")
        
        return {
            "total_attempts": total_attempts,
            # Moderation metrics
            "moderation_successful_attempts": moderation_successful_attempts,
            "moderation_success_rate": moderation_successful_attempts / total_attempts if total_attempts > 0 else 0,
            "moderation_successful_strategies": [r.get("strategy") for r in results if not r.get("is_blocked", True)],
            
            # Response evaluation metrics
            "response_successful_attempts": response_successful_attempts,
            "response_success_rate": response_successful_attempts / total_attempts if total_attempts > 0 else 0,
            "response_successful_strategies": [r.get("strategy") for r in results if r.get("response_success", False)],
            
            # Model stats
            "gemini_responses": gemini_responses,
            "cohere_responses": cohere_responses,
            
            # Rating stats
            "gemini_useful_ratings": gemini_useful_ratings,
            "gemini_alternative_ratings": gemini_alternative_ratings,
            "gemini_unrelated_ratings": gemini_unrelated_ratings,
            "cohere_useful_ratings": cohere_useful_ratings,
            "cohere_alternative_ratings": cohere_alternative_ratings,
            "cohere_unrelated_ratings": cohere_unrelated_ratings,
            "evaluation_performed_by": "cohere-command",
            
            # Strategy information
            "strategies_attempted": [r.get("strategy") for r in results]
        } 