"""
LLM client utilities for ModuLens to interact with various AI models.
"""

import os
from typing import Dict, Any, Optional, List
import random
import time
import json

# Import LLM clients conditionally
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except (ImportError, TypeError):
    OPENAI_AVAILABLE = False

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

try:
    import cohere
    COHERE_AVAILABLE = True
except ImportError:
    COHERE_AVAILABLE = False

class LLMClient:
    """
    Client for interacting with language models from different providers.
    """
    
    def __init__(self, api_keys: Dict[str, str], 
                 default_model: str = "gemini-2.0-flash",
                 fallback_models: Optional[List[str]] = None):
        """
        Initialize the LLM client with API keys.
        
        Args:
            api_keys: Dictionary of API keys by provider
            default_model: Name of the default model to use
            fallback_models: List of fallback models to try if default fails
        """
        self.api_keys = api_keys
        self.default_model = default_model
        self.fallback_models = fallback_models or ["command", "command-r"]
        
        # Initialize clients for different providers, but only if keys are provided
        self.openai_client = None
        self.anthropic_client = None
        self.gemini_client = None
        self.cohere_client = None
        
        # Only initialize active clients - prioritizing Gemini and Cohere
        if api_keys.get("gemini") and GEMINI_AVAILABLE:
            try:
                genai.configure(api_key=api_keys["gemini"])
                self.gemini_client = genai
                print("Gemini client initialized successfully")
            except Exception as e:
                print(f"Warning: Could not initialize Gemini client: {str(e)}")
            
        # Initialize Cohere client
        if api_keys.get("cohere") and COHERE_AVAILABLE:
            try:
                self.cohere_client = cohere.Client(api_key=api_keys["cohere"])
                print("Cohere client initialized successfully")
            except Exception as e:
                print(f"Warning: Could not initialize Cohere client: {str(e)}")
                
        # Keep OpenAI and Anthropic available but inactive by default 
        if api_keys.get("openai") and OPENAI_AVAILABLE:
            try:
                self.openai_client = OpenAI(api_key=api_keys["openai"])
                print("OpenAI client initialized (not active by default)")
            except Exception as e:
                print(f"Warning: Could not initialize OpenAI client: {str(e)}")
                
        if api_keys.get("anthropic") and ANTHROPIC_AVAILABLE:
            try:
                self.anthropic_client = anthropic.Anthropic(api_key=api_keys["anthropic"])
                print("Anthropic client initialized (not active by default)")
            except Exception as e:
                print(f"Warning: Could not initialize Anthropic client: {str(e)}")
    
    def check_moderation(self, prompt: str) -> Dict[str, Any]:
        """
        Check if a prompt would be blocked by content moderation.
        
        Args:
            prompt: The prompt to check
            
        Returns:
            Dict with moderation check results
        """
        try:
            # Use OpenAI's moderation endpoint if available, but only if explicitly configured
            if self.openai_client and False:  # Disabled for now
                moderation = self.openai_client.moderations.create(input=prompt)
                result = moderation.results[0].model_dump()
                
                # Convert to a more usable format
                return {
                    "is_blocked": result["flagged"],
                    "flags": {
                        category: score > 0.5
                        for category, score in result["category_scores"].items()
                    },
                    "scores": result["category_scores"]
                }
            # Fallback to manual check with model if no OpenAI moderation API
            else:
                # This is a simplified approach using Gemini or Cohere
                fallback_check = self.get_completion(
                    "You are a content moderation system. Analyze the following content and respond only with "
                    "a JSON object containing 'is_blocked' (boolean) and 'reason' (string if blocked, null if not).\n\n"
                    f"Content to analyze: {prompt}"
                )
                
                # Try to parse the response as JSON
                try:
                    result = json.loads(fallback_check)
                    return {
                        "is_blocked": result.get("is_blocked", False),
                        "flags": {"manual_check": result.get("is_blocked", False)},
                        "reason": result.get("reason")
                    }
                except:
                    # If we can't parse the JSON, assume it's not blocked
                    return {
                        "is_blocked": False,
                        "flags": {},
                        "reason": "Failed to parse moderation response"
                    }
                
        except Exception as e:
            # If there's an error, assume it's blocked to be safe
            return {
                "is_blocked": True,
                "flags": {"error": True},
                "error": str(e)
            }
    
    def get_completion(self, prompt: str, 
                       model: Optional[str] = None,
                       max_tokens: int = 1000,
                       temperature: float = 0.7) -> str:
        """
        Get a completion from an LLM for the given prompt.
        
        Args:
            prompt: The prompt to send to the model
            model: The model to use (defaults to self.default_model)
            max_tokens: Maximum tokens in the response
            temperature: Creativity parameter (0-1)
            
        Returns:
            str: The model's response
        """
        model = model or self.default_model
        
        # Helper function to handle retries and fallbacks
        def _try_completion_with_model(model_name: str) -> Optional[str]:
            # Prioritize Gemini and Cohere models
            if model_name.startswith("gemini") and self.gemini_client:
                try:
                    model = self.gemini_client.GenerativeModel(model_name)
                    response = model.generate_content(prompt, 
                                                     generation_config=genai.types.GenerationConfig(
                                                        temperature=temperature,
                                                        max_output_tokens=max_tokens
                                                     ))
                    return response.text
                except Exception as e:
                    print(f"Error with Gemini model {model_name}: {str(e)}")
                    return None
                    
            elif (model_name.startswith("command") or 
                  model_name == "cohere" or 
                  model_name.startswith("co.")) and self.cohere_client:
                try:
                    # Determine specific Cohere model
                    cohere_model = model_name
                    if model_name == "cohere":
                        cohere_model = "command"  # Default to command model
                        
                    response = self.cohere_client.chat(
                        message=prompt,
                        model=cohere_model,
                        max_tokens=max_tokens,
                        temperature=temperature
                    )
                    return response.text
                except Exception as e:
                    print(f"Error with Cohere model {model_name}: {str(e)}")
                    return None
                    
            # These models are available but not used by default
            elif model_name.startswith("gpt") and self.openai_client:
                try:
                    response = self.openai_client.chat.completions.create(
                        model=model_name,
                        messages=[{"role": "user", "content": prompt}],
                        max_tokens=max_tokens,
                        temperature=temperature
                    )
                    return response.choices[0].message.content
                except Exception as e:
                    print(f"Error with OpenAI model {model_name}: {str(e)}")
                    return None
                    
            elif model_name.startswith("claude") and self.anthropic_client:
                try:
                    response = self.anthropic_client.messages.create(
                        model=model_name,
                        max_tokens=max_tokens,
                        temperature=temperature,
                        messages=[{"role": "user", "content": prompt}]
                    )
                    return response.content[0].text
                except Exception as e:
                    print(f"Error with Anthropic model {model_name}: {str(e)}")
                    return None
            
            return None
        
        # Try with the specified/default model
        result = _try_completion_with_model(model)
        if result:
            return result
        
        # If that fails, try fallback models
        for fallback_model in self.fallback_models:
            # Skip if it's the same as the one that just failed
            if fallback_model == model:
                continue
                
            print(f"Trying fallback model: {fallback_model}")
            result = _try_completion_with_model(fallback_model)
            if result:
                return result
                
        raise Exception("All models failed to generate a completion") 