import pytest
import json
from unittest.mock import patch, MagicMock

from ailabel.lib.llms import (
    get_gemini,
    generate_json,
    Models
)


def test_models_enum():
    """Test the Models enum."""
    assert Models.GEMINI_2_0 == "models/gemini-2.0"
    assert Models.GEMINI_2_0_FLASH == "models/gemini-2.0-flash"
    assert Models.GEMINI_2_0_FLASH_8B == "models/gemini-2.0-flash-8b"


@patch("ailabel.lib.llms.genai.GenerativeModel")
def test_get_gemini(mock_generative_model):
    """Test the get_gemini function."""
    # Set up mock
    mock_model = MagicMock()
    mock_generative_model.return_value = mock_model
    
    # Call with no system instruction
    model = get_gemini()
    assert model == mock_model
    mock_generative_model.assert_called_once_with(
        Models.GEMINI_2_0_FLASH,
        system_instruction=None
    )
    
    # Reset mock
    mock_generative_model.reset_mock()
    
    # Call with system instruction
    system_instruction = "You are a helpful assistant."
    model = get_gemini(system_instruction=system_instruction)
    assert model == mock_model
    mock_generative_model.assert_called_once_with(
        Models.GEMINI_2_0_FLASH,
        system_instruction=system_instruction
    )
    
    # Test caching (the function is decorated with @functools.cache)
    # If we call get_gemini again with the same system_instruction,
    # the mock shouldn't be called again
    mock_generative_model.reset_mock()
    model = get_gemini(system_instruction=system_instruction)
    assert model == mock_model
    mock_generative_model.assert_not_called()


@patch("ailabel.lib.llms.get_gemini")
def test_generate_json_with_prompt_only(mock_get_gemini):
    """Test the generate_json function with only a prompt."""
    # Set up mocks
    mock_model = MagicMock()
    mock_response = MagicMock()
    mock_response.text = '{"result": "success"}'
    mock_model.generate_content.return_value = mock_response
    mock_get_gemini.return_value = mock_model
    
    # Call the function
    prompt = "Generate a JSON response"
    result = generate_json(prompt)
    
    # Verify the result
    assert result == {"result": "success"}
    
    # Verify the mock calls
    mock_get_gemini.assert_called_once_with(system_instruction=None)
    mock_model.generate_content.assert_called_once()
    # Check that we're using the JSON generation config
    assert mock_model.generate_content.call_args[1]["generation_config"].response_mime_type == "application/json"
    assert mock_model.generate_content.call_args[1]["generation_config"].temperature == 0.0


@patch("ailabel.lib.llms.get_gemini")
def test_generate_json_with_history(mock_get_gemini):
    """Test the generate_json function with history."""
    # Set up mocks
    mock_model = MagicMock()
    mock_response = MagicMock()
    mock_response.text = '{"result": "with history"}'
    mock_model.generate_content.return_value = mock_response
    mock_get_gemini.return_value = mock_model
    
    # Call the function with history
    prompt = "Generate a JSON response"
    history = [
        {"role": "user", "parts": ["How are you?"]},
        {"role": "assistant", "parts": ["I'm doing well, thank you!"]}
    ]
    system_instruction = "You are a helpful assistant."
    
    result = generate_json(prompt, history=history, system_instruction=system_instruction)
    
    # Verify the result
    assert result == {"result": "with history"}
    
    # Verify the mock calls
    mock_get_gemini.assert_called_once_with(system_instruction=system_instruction)
    mock_model.generate_content.assert_called_once()
    
    # Check that history + new prompt is passed correctly
    call_args = mock_model.generate_content.call_args[0][0]
    assert len(call_args) == 3  # 2 from history + 1 new
    assert call_args[0] == history[0]
    assert call_args[1] == history[1]
    assert call_args[2] == {"role": "user", "parts": [prompt]}