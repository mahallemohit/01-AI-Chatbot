import time
from google import genai
from config import API_KEY, MODEL_NAME

client = genai.Client(api_key=API_KEY)




def send_message(chat, message):
    for attempt in range(3):
        try:
            response = chat.send_message_stream(message)

            print("\nAI: ", end="", flush=True)
            full_response = ""

            for chunk in response:
                if chunk.text:
                    print(chunk.text, end="", flush=True)
                    full_response += chunk.text

            print("\n")
            return full_response

        except Exception as error:
            error_message = str(error)

            temporary_error = any(
                code in error_message
                for code in ["429", "500", "502", "503", "504"]
            )

            if temporary_error and attempt < 2:
                wait_seconds = 2 ** (attempt + 1)

                print(
                    f"\nTemporary API error. "
                    f"Retrying in {wait_seconds} seconds..."
                )

                time.sleep(wait_seconds)

            else:
                print(f"\nAPI request failed: {error}")
                return None



chat = client.chats.create(
    model=MODEL_NAME,
    config={
        "system_instruction": (
            "You are a helpful AI assistant for beginners. "
            "Explain technical concepts in simple language. "
            "Use practical examples when helpful. "
            "Keep answers clear and organized. "
            "If you are unsure about something, say so honestly."
        )
    },
)

print("=== My AI Chatbot ===")
print("Type /help to see commands.")
print("Type 'exit' to quit.\n")

while True:
    user_message = input("You: ").strip()

    if not user_message:
        continue

    if user_message.lower() == "exit":
        print("Goodbye!")
        break

    if user_message.lower() == "/help":
        print("\nAvailable commands:")
        print("  /help  - Show available commands")
        print("  /clear - Start a fresh conversation")
        print("  exit   - Quit the chatbot\n")
        continue

    if user_message.lower() == "/clear":
        chat = client.chats.create(
            model=MODEL_NAME,
            config={
                "system_instruction": (
                    "You are a helpful AI assistant for beginners. "
                    "Explain technical concepts in simple language. "
                    "Use practical examples when helpful. "
                    "Keep answers clear and organized. "
                    "If you are unsure about something, say so honestly."
                )
            },
        )
        print("Conversation cleared. Let's start fresh!\n")
        continue

    send_message(chat, user_message)



print("=== My AI Chatbot ===")
print("I can remember our conversation while this session runs.")
print("Type 'exit' to quit.\n")

while True:
    user_message = input("You: ").strip()

    if user_message.lower() == "exit":
        print("Goodbye!")
        break

    if not user_message:
        continue

    answer = send_message(chat, user_message)

    if answer:
        print(f"\nAI: {answer}\n")
