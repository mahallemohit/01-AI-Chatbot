import time
from google import genai
from config import API_KEY, MODEL_NAME

client = genai.Client(api_key=API_KEY)



def send_message(chat, message):
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
