"""
Base class for all ModuLens bypassing strategies.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class BaseStrategy(ABC):
    """
    Abstract base class for all prompt modification strategies.
    All strategy implementations must inherit from this class.
    """
    
    @property
    @abstractmethod
    def name(self) -> str:
        """
        Returns the name of the strategy.
        
        Returns:
            str: Name of the strategy
        """
        pass
    
    @property
    @abstractmethod
    def description(self) -> str:
        """
        Returns a description of the strategy.
        
        Returns:
            str: Description of how the strategy works
        """
        pass
    
    @abstractmethod
    def apply(self, prompt: str) -> str:
        """
        Apply the strategy to transform the prompt.
        
        Args:
            prompt: The original prompt to transform
            
        Returns:
            str: The transformed prompt
        """
        pass
    
    def get_response(self, llm_client, transformed_prompt: str, 
                     gemini_model: str, cohere_model: str) -> Dict[str, Any]:
        """
        Get responses from LLM models for the transformed prompt.
        
        Args:
            llm_client: The LLM client instance
            transformed_prompt: The transformed prompt to send to the models
            gemini_model: The Gemini model to use
            cohere_model: The Cohere model to use
            
        Returns:
            Dict with the responses from both models and related information
        """
        result = {
            "strategy": self.name,
            "prompt": transformed_prompt,
            "is_blocked": False,
        }
        
        # Try to get Gemini response
        try:
            gemini_response = llm_client.get_completion(transformed_prompt, model=gemini_model)
            result["gemini_response"] = gemini_response
            result["gemini_model"] = gemini_model
        except Exception as e:
            result["gemini_error"] = str(e)
            
        # Try to get Cohere response
        try:
            cohere_response = llm_client.get_completion(transformed_prompt, model=cohere_model)
            result["cohere_response"] = cohere_response
            result["cohere_model"] = cohere_model
        except Exception as e:
            result["cohere_error"] = str(e)
            
        # Combine responses if both were obtained
        if result.get("gemini_response") and result.get("cohere_response"):
            result["response"] = (
                f"Gemini ({gemini_model}) response:\n{result['gemini_response']}\n\n"
                f"Cohere ({cohere_model}) response:\n{result['cohere_response']}"
            )
            
        return result 