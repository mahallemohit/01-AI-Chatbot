
import os
import time
from dotenv import load_dotenv
from google import genai

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key or api_key == "your_api_key_here":
    raise ValueError("Please configure GEMINI_API_KEY in your .env file.")

client = genai.Client(api_key=api_key)


def ask_gemini(message):
    for attempt in range(3):
        try:
            response = client.models.generate_content(
                model="gemini-3.5-flash-lite",
                contents=message,
            )
            return response.text

        except Exception as error:
            error_message = str(error)

            temporary_error = any(
                code in error_message
                for code in ["503", "429", "500", "502", "504"]
            )

            if temporary_error and attempt < 2:
                wait_seconds = 2 ** (attempt + 1)
                print(
                    f"Temporary API error. "
                    f"Retrying in {wait_seconds} seconds..."
                )
                time.sleep(wait_seconds)
            else:
                print(f"API request failed: {error}")
                return None


print("=== My AI Chatbot ===")
print("Type 'exit' to quit.\n")

while True:
    user_message = input("You: ").strip()

    if user_message.lower() == "exit":
        print("Goodbye!")
        break

    if not user_message:
        continue

    answer = ask_gemini(user_message)

    if answer:
        print(f"\nAI: {answer}\n")
