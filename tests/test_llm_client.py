"""
Test script for the LLM client functionality.
"""

import unittest
import os
import json
from unittest.mock import patch, MagicMock
import sys

# Add the parent directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from modulens.utils.llm_client import LLMClient

class TestLLMClient(unittest.TestCase):
    """Test cases for the LLM client."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create API keys for testing
        self.test_api_keys = {
            "openai": "test_openai_key",
            "anthropic": "test_anthropic_key",
            "gemini": "test_gemini_key",
            "cohere": "test_cohere_key"
        }
        
        # Mock environment for tests
        self.mock_environment()
        
    def mock_environment(self):
        """Set up the mocked environment for testing."""
        # Create patches for the external libraries
        self.openai_patch = patch('modulens.utils.llm_client.OpenAI')
        self.anthropic_patch = patch('modulens.utils.llm_client.anthropic')
        self.genai_patch = patch('modulens.utils.llm_client.genai')
        self.cohere_patch = patch('modulens.utils.llm_client.cohere')
        
        # Start the patches
        self.mock_openai = self.openai_patch.start()
        self.mock_anthropic = self.anthropic_patch.start()
        self.mock_genai = self.genai_patch.start()
        self.mock_cohere = self.cohere_patch.start()
        
        # Set up availability flags
        self.openai_available_patch = patch('modulens.utils.llm_client.OPENAI_AVAILABLE', True)
        self.anthropic_available_patch = patch('modulens.utils.llm_client.ANTHROPIC_AVAILABLE', True)
        self.gemini_available_patch = patch('modulens.utils.llm_client.GEMINI_AVAILABLE', True)
        self.cohere_available_patch = patch('modulens.utils.llm_client.COHERE_AVAILABLE', True)
        
        # Start availability flag patches
        self.openai_available_patch.start()
        self.anthropic_available_patch.start()
        self.gemini_available_patch.start()
        self.cohere_available_patch.start()
        
        # Set up Gemini mock
        self.mock_gen_model = MagicMock()
        self.mock_gen_model.generate_content.return_value.text = "Gemini response"
        self.mock_genai.GenerativeModel.return_value = self.mock_gen_model
        
        # Set up Cohere mock
        self.mock_cohere_client = MagicMock()
        self.mock_cohere_client.chat.return_value.text = "Cohere response"
        self.mock_cohere.Client.return_value = self.mock_cohere_client
        
    def tearDown(self):
        """Tear down test fixtures."""
        # Stop all the patches
        self.openai_patch.stop()
        self.anthropic_patch.stop()
        self.genai_patch.stop()
        self.cohere_patch.stop()
        self.openai_available_patch.stop()
        self.anthropic_available_patch.stop()
        self.gemini_available_patch.stop()
        self.cohere_available_patch.stop()
    
    def test_init(self):
        """Test client initialization."""
        client = LLMClient(self.test_api_keys)
        
        # Check that clients were initialized
        self.mock_genai.configure.assert_called_once_with(api_key=self.test_api_keys["gemini"])
        self.mock_cohere.Client.assert_called_once_with(api_key=self.test_api_keys["cohere"])
        self.mock_openai.assert_called_once_with(api_key=self.test_api_keys["openai"])
        self.mock_anthropic.Anthropic.assert_called_once_with(api_key=self.test_api_keys["anthropic"])
        
        # Check client attributes
        self.assertEqual(client.default_model, "gemini-2.0-flash")
        self.assertIn("command", client.fallback_models)
        self.assertIn("command-r", client.fallback_models)
        
    def test_get_completion_with_gemini_primary(self):
        """Test getting a completion from Gemini primary model."""
        client = LLMClient(self.test_api_keys)
        
        # Test with default model (should be gemini-2.0-flash)
        result = client.get_completion("Test prompt")
        
        # Verify Gemini was called with the right model
        self.mock_genai.GenerativeModel.assert_called_with("gemini-2.0-flash")
        self.mock_gen_model.generate_content.assert_called_once()
        self.assertEqual(result, "Gemini response")
        
    def test_get_completion_with_cohere_primary(self):
        """Test getting a completion from Cohere primary model."""
        client = LLMClient(self.test_api_keys)
        
        # Test with Cohere model
        result = client.get_completion("Test prompt", model="command")
        
        # Verify Cohere was called
        self.mock_cohere_client.chat.assert_called_once()
        self.assertEqual(result, "Cohere response")
        
    def test_fallback_behavior(self):
        """Test fallback behavior when primary model fails."""
        client = LLMClient(self.test_api_keys)
        
        # Make Gemini fail
        self.mock_gen_model.generate_content.side_effect = Exception("Model error")
        
        # Set successful response for Cohere
        self.mock_cohere_client.chat.return_value.text = "Fallback response"
        
        # Test completion with fallback
        result = client.get_completion("Test prompt")
        
        # Gemini should have been tried first and failed
        self.mock_genai.GenerativeModel.assert_called_with("gemini-2.0-flash")
        self.mock_gen_model.generate_content.assert_called_once()
        
        # Then Cohere should have been tried
        self.mock_cohere_client.chat.assert_called_once()
        
        # Should get Cohere's response
        self.assertEqual(result, "Fallback response")
        
    def test_moderation_check(self):
        """Test the moderation check functionality."""
        client = LLMClient(self.test_api_keys)
        
        # Mock the model response for fallback moderation (since OpenAI is disabled)
        self.mock_gen_model.generate_content.return_value.text = json.dumps({
            "is_blocked": False,
            "reason": None
        })
        
        # Test moderation
        result = client.check_moderation("Test prompt")
        
        # Verify result structure
        self.assertFalse(result["is_blocked"])
        self.assertIn("flags", result)
        
        # Now test blocked content
        self.mock_gen_model.generate_content.return_value.text = json.dumps({
            "is_blocked": True,
            "reason": "Policy violation"
        })
        
        result = client.check_moderation("Harmful prompt")
        self.assertTrue(result["is_blocked"])
        self.assertEqual(result["reason"], "Policy violation")
        
if __name__ == '__main__':
    unittest.main() 