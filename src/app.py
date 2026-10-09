
import streamlit as st
from google import genai
from config import API_KEY, MODEL_NAME

st.set_page_config(
    page_title="My AI Chatbot",
    page_icon="🤖",
    layout="centered",
)

st.title("🤖 My AI Chatbot")
st.caption("Your personal AI assistant, powered by Gemini.")

client = genai.Client(api_key=API_KEY)

SYSTEM_INSTRUCTION = (
    "You are a helpful AI assistant for beginners. "
    "Explain technical concepts in simple language. "
    "Use practical examples when helpful. "
    "Keep answers clear and organized. "
    "If you are unsure about something, say so honestly."
)

if "messages" not in st.session_state:
    st.session_state.messages = []

# Display previous messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept a new message
if prompt := st.chat_input("Ask me anything..."):
    st.session_state.messages.append(
        {"role": "user", "content": prompt}
    )

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            with st.spinner("Thinking..."):
                response = client.models.generate_content(
                    model=MODEL_NAME,
                    contents=[
                        {
                            "role": "user",
                            "parts": [
                                {
                                    "text": (
                                        SYSTEM_INSTRUCTION
                                        + "\n\nUser question: "
                                        + prompt
                                    )
                                }
                            ],
                        }
                    ],
                )

                answer = response.text or "I couldn't generate a response."
                st.markdown(answer)

            st.session_state.messages.append(
                {"role": "assistant", "content": answer}
            )

        except Exception as error:
            st.error(f"Something went wrong: {error}")
