"""
OriginalStrategy class for handling original prompts without modifications.
"""

from modulens.strategies.base import BaseStrategy

class OriginalStrategy(BaseStrategy):
    """
    A strategy that does not modify the original prompt.
    Used as a baseline for comparison with actual bypass strategies.
    """
    
    @property
    def name(self) -> str:
        """
        Returns the name of the strategy.
        
        Returns:
            str: Name of the strategy
        """
        return "original"
    
    @property
    def description(self) -> str:
        """
        Returns a description of the strategy.
        
        Returns:
            str: Description of how the strategy works
        """
        return "Original prompt without any modifications, used as a baseline."
    
    def apply(self, prompt: str) -> str:
        """
        Apply the strategy to transform the prompt.
        For OriginalStrategy, just return the prompt unchanged.
        
        Args:
            prompt: The original prompt to use
            
        Returns:
            str: The unchanged prompt
        """
        return prompt 