import os
from typing import Callable
import json
import functools
import dotenv
from enum import Enum
import google.generativeai as genai


dotenv.load_dotenv(".env.secret")
dotenv.load_dotenv()

genai.configure(api_key=os.environ.get("GEMINI_API_KEY"), transport="rest")


class Models(str, Enum):
    GEMINI_1_5_FLASH = "models/gemini-1.5-flash"
    GEMINI_1_5_FLASH_8B = "models/gemini-1.5-flash-8b"
    GEMINI_2_0_FLASH_EXP = "models/gemini-2.0-flash-exp"
    GEMINI_2_0_FLASH = "models/gemini-2.0-flash"
    GEMINI_2_0 = "models/gemini-2.0"


TOOL_SEARCH_RETRIEVAL = {"google_search_retrieval": {}}
JSON_CONFIG = genai.GenerationConfig(response_mime_type="application/json", temperature=0.0)


@functools.cache
def get_gemini(system_instruction: str | None = None):
    return genai.GenerativeModel(
        Models.GEMINI_1_5_FLASH,
        system_instruction=system_instruction,
    )


def generate_json(
    prompt: str, history: list[genai.types.ContentDict] | None = None, system_instruction: str | None = None
):
    model = get_gemini(system_instruction=system_instruction)
    if history:
        response = model.generate_content(
            history + [{"role": "user", "parts": [prompt]}], generation_config=JSON_CONFIG
        )
    else:
        response = model.generate_content(prompt, generation_config=JSON_CONFIG)
    return json.loads(response.text)


if False:
    # Unused for now
    def generate_content(prompt: str, system_instruction: str | None = None):
        model = get_gemini(system_instruction=system_instruction)
        return model.generate_content(prompt)

    def get_chat_with_tools(
        tools: list[Callable], system_instruction: str | None = None, enable_automatic_function_calling: bool = True
    ):
        model = genai.GenerativeModel(
            Models.GEMINI_1_5_FLASH,
            system_instruction=system_instruction,
            tools=tools,
        )
        return model.start_chat(enable_automatic_function_calling=enable_automatic_function_calling)

    def get_chat_with_search(system_instruction: str | None = None):
        model = genai.GenerativeModel(
            Models.GEMINI_1_5_FLASH,
            system_instruction=system_instruction,
            tools=TOOL_SEARCH_RETRIEVAL,
        )
        return model.start_chat()
