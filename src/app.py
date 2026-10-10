
import streamlit as st
from google import genai
from config import API_KEY, MODEL_NAME
from chat_history import initialize_database, save_message, load_messages

st.set_page_config(
    page_title="My AI Chatbot",
    page_icon="🤖",
    layout="centered",
)

st.title("🤖 My AI Chatbot")
st.caption("Your personal AI assistant, powered by Gemini.")

client = genai.Client(api_key=API_KEY)
initialize_database()


SYSTEM_INSTRUCTION = (
    "You are a helpful AI assistant for beginners. "
    "Explain technical concepts in simple language. "
    "Use practical examples when helpful. "
    "Keep answers clear and organized. "
    "If you are unsure about something, say so honestly."
)

if "messages" not in st.session_state:
    st.session_state.messages = load_messages()

# Display previous messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


# Accept a new message

# Accept a new message


if prompt := st.chat_input("Ask me anything..."):
    user_message = {"role": "user", "content": prompt}

    # Save the user's message
    save_message("user", prompt)
    st.session_state.messages.append(user_message)

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            conversation = [
                {
                    "role": "user",
                    "parts": [{"text": SYSTEM_INSTRUCTION}],
                }
            ]

            for message in st.session_state.messages:
                conversation.append(
                    {
                        "role": (
                            "model"
                            if message["role"] == "assistant"
                            else "user"
                        ),
                        "parts": [{"text": message["content"]}],
                    }
                )

            with st.spinner("Thinking..."):
                response = client.models.generate_content(
                    model=MODEL_NAME,
                    contents=conversation,
                )

                answer = (
                    response.text
                    or "I couldn't generate a response."
                )

                st.markdown(answer)

            # Save the assistant's response
            save_message("assistant", answer)
            st.session_state.messages.append(
                {"role": "assistant", "content": answer}
            )

        except Exception as error:
            st.error(f"Something went wrong: {error}")
            st.session_state.messages.pop()
