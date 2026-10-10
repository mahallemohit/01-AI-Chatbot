
import streamlit as st
from google import genai
from config import API_KEY, MODEL_NAME
from chat_history import (
    initialize_database,
    create_conversation,
    list_conversations,
    save_message,
    load_messages,
)

st.set_page_config(
    page_title="My AI Chatbot",
    page_icon="🤖",
    layout="centered",
)

initialize_database()
client = genai.Client(api_key=API_KEY)

SYSTEM_INSTRUCTION = (
    "You are a helpful AI assistant for beginners. "
    "Explain technical concepts in simple language. "
    "Use practical examples when helpful. "
    "Keep answers clear and organized. "
    "If you are unsure about something, say so honestly."
)

st.title("🤖 My AI Chatbot")
st.caption("Your personal AI assistant, powered by Gemini.")

# Create a conversation when the app is opened for the first time.
if "conversation_id" not in st.session_state:
    conversations = list_conversations()

    if conversations:
        st.session_state.conversation_id = conversations[0]["id"]
    else:
        st.session_state.conversation_id = create_conversation()

    st.session_state.messages = load_messages(
        st.session_state.conversation_id
    )

# Sidebar: create and select conversations.
with st.sidebar:
    st.header("Chat History")

    if st.button("➕ New Chat", use_container_width=True):
        st.session_state.conversation_id = create_conversation()
        st.session_state.messages = []
        st.rerun()

    conversations = list_conversations()

    if conversations:
        conversation_ids = [c["id"] for c in conversations]
        conversation_titles = {
            c["id"]: c["title"] for c in conversations
        }

        current_id = st.session_state.conversation_id

        if current_id in conversation_ids:
            selected_id = st.selectbox(
                "Previous conversations",
                options=conversation_ids,
                index=conversation_ids.index(current_id),
                format_func=lambda cid: conversation_titles[cid],
            )

            if selected_id != current_id:
                st.session_state.conversation_id = selected_id
                st.session_state.messages = load_messages(selected_id)
                st.rerun()

# Display messages from the selected conversation.
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Handle a new message.
if prompt := st.chat_input("Ask me anything..."):
    conversation_id = st.session_state.conversation_id

    save_message(conversation_id, "user", prompt)
    st.session_state.messages.append(
        {"role": "user", "content": prompt}
    )

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

            save_message(conversation_id, "assistant", answer)
            st.session_state.messages.append(
                {"role": "assistant", "content": answer}
            )

            # Give a new conversation a useful title.
            conversations = list_conversations()
            current_title = next(
                (
                    c["title"]
                    for c in conversations
                    if c["id"] == conversation_id
                ),
                "New Chat",
            )

            if current_title == "New Chat":
                title = prompt[:40].strip() or "New Chat"

                import sqlite3
                from chat_history import DB_PATH

                with sqlite3.connect(DB_PATH) as connection:
                    connection.execute(
                        "UPDATE conversations SET title = ? WHERE id = ?",
                        (title, conversation_id),
                    )

        except Exception as error:
            st.error(f"Something went wrong: {error}")
            st.session_state.messages.pop()
