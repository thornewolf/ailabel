gemini code example
```
import google.generativeai as genai
from dotenv import load_dotenv
import os

load_dotenv()
genai.configure(api_key=os.environ["GEMINI_API_KEY"])


def evaluate_math_expression(expression: str) -> str:
    print(f"Evaluating math expression: {expression}")
    return str(eval(expression))


def main():
    model = genai.GenerativeModel(
        "gemini-2.0-flash-exp", tools=[evaluate_math_expression]
    )
    chat = model.start_chat(enable_automatic_function_calling=True)

    response = chat.send_message("What's 1+1?")
    print(response.text)


if __name__ == "__main__":
    main()

```