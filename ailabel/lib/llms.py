"""LLM integration with Google's Gemini models.

This module provides helper functions for interacting with Google's Gemini models,
including configuration and specialized functions for generating structured outputs.

The module:
1. Configures the Gemini API client using credentials from environment variables
2. Defines available models as an enumeration
3. Provides functions for generating JSON responses and other content

Usage:
    # Generate a JSON response
    result = generate_json("What is the weather?", system_instruction="Return weather data as JSON")
    print(result["temperature"])
"""

import os
from typing import Callable, Dict, Any
import json
import functools
import dotenv
from enum import Enum
import google.generativeai as genai
from google.generativeai.types import GenerationConfig, ContentDict


# Load API key from environment variables
dotenv.load_dotenv(".env.secret")
dotenv.load_dotenv()

# Configure the Gemini API client
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"), transport="rest")


class Models(str, Enum):
    """Available Gemini model versions.
    
    This enum represents the available Gemini model versions that can be used.
    The values correspond to the model identifiers used by the Google Generative AI API.
    """
    GEMINI_1_5_FLASH = "models/gemini-1.5-flash"
    GEMINI_1_5_FLASH_8B = "models/gemini-1.5-flash-8b"
    GEMINI_2_0_FLASH_EXP = "models/gemini-2.0-flash-exp"
    GEMINI_2_0_FLASH = "models/gemini-2.0-flash"
    GEMINI_2_0 = "models/gemini-2.0"


# Predefined tools and configurations
TOOL_SEARCH_RETRIEVAL: Dict[str, Dict[str, Any]] = {"google_search_retrieval": {}}
JSON_CONFIG: GenerationConfig = genai.GenerationConfig(response_mime_type="application/json", temperature=0.0)


@functools.cache
def get_gemini(system_instruction: str | None = None) -> genai.GenerativeModel:
    """Get a configured Gemini model instance.
    
    Creates a GenerativeModel instance with the specified system instruction.
    Results are cached, so calling this function multiple times with the same
    system_instruction will return the same model instance.
    
    Args:
        system_instruction: Optional system instruction to guide the model's behavior
        
    Returns:
        A configured GenerativeModel instance
    """
    return genai.GenerativeModel(
        Models.GEMINI_1_5_FLASH,
        system_instruction=system_instruction,
    )


def generate_json(
    prompt: str, 
    history: list[ContentDict] | None = None, 
    system_instruction: str | None = None
) -> Dict[str, Any]:
    """Generate a JSON response from the model.
    
    Sends a prompt to the model and returns the parsed JSON response.
    Optionally uses conversation history and system instructions.
    
    Args:
        prompt: The prompt to send to the model
        history: Optional conversation history for context
        system_instruction: Optional system instruction to guide the model's behavior
        
    Returns:
        The parsed JSON response from the model
        
    Raises:
        ValueError: If the response cannot be parsed as JSON
    """
    model = get_gemini(system_instruction=system_instruction)
    if history:
        response = model.generate_content(
            history + [{"role": "user", "parts": [prompt]}], generation_config=JSON_CONFIG
        )
    else:
        response = model.generate_content(prompt, generation_config=JSON_CONFIG)
    return json.loads(response.text)


# Unused functions kept for future reference
if False:
    def generate_content(prompt: str, system_instruction: str | None = None) -> genai.types.GenerateContentResponse:
        """Generate a free-form response from the model.
        
        Args:
            prompt: The prompt to send to the model
            system_instruction: Optional system instruction to guide the model's behavior
            
        Returns:
            The raw model response
        """
        model = get_gemini(system_instruction=system_instruction)
        return model.generate_content(prompt)

    def get_chat_with_tools(
        tools: list[Callable], 
        system_instruction: str | None = None, 
        enable_automatic_function_calling: bool = True
    ) -> genai.ChatSession:
        """Create a chat session with function-calling tools.
        
        Args:
            tools: List of callable tools to provide to the model
            system_instruction: Optional system instruction for the chat
            enable_automatic_function_calling: Whether to allow automatic function calling
            
        Returns:
            A configured chat session
        """
        model = genai.GenerativeModel(
            Models.GEMINI_1_5_FLASH,
            system_instruction=system_instruction,
            tools=tools,
        )
        return model.start_chat(enable_automatic_function_calling=enable_automatic_function_calling)

    def get_chat_with_search(system_instruction: str | None = None) -> genai.ChatSession:
        """Create a chat session with web search capability.
        
        Args:
            system_instruction: Optional system instruction for the chat
            
        Returns:
            A configured chat session with search capability
        """
        model = genai.GenerativeModel(
            Models.GEMINI_1_5_FLASH,
            system_instruction=system_instruction,
            tools=TOOL_SEARCH_RETRIEVAL,
        )
        return model.start_chat()
