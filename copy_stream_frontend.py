import uuid

import streamlit as st
from langchain_core.messages import HumanMessage
from backend import chatbot_app


# -------------------- Utility Functions -------------------- #

def generate_uuid():
    return str(uuid.uuid4())


def get_config():
    return {
        "configurable": {
            "thread_id": st.session_state["thread_id"]
        }
    }


def add_thread(thread_id, name="New Chat"):
    if thread_id not in st.session_state["chat_threads"]:
        st.session_state["chat_threads"][thread_id] = {
            "name": name
        }


def reset_chat():
    new_thread = generate_uuid()
    st.session_state["thread_id"] = new_thread
    add_thread(new_thread)
    st.session_state["message_history"] = []


def load_conversation(thread_id):
    state = chatbot_app.get_state(
        config={
            "configurable": {
                "thread_id": thread_id
            }
        }
    )

    if not state.values:
        return []

    return state.values.get("messages", [])


# -------------------- Session State -------------------- #

if "thread_id" not in st.session_state:
    st.session_state["thread_id"] = generate_uuid()

if "message_history" not in st.session_state:
    st.session_state["message_history"] = []

if "chat_threads" not in st.session_state:
    st.session_state["chat_threads"] = {}

add_thread(st.session_state["thread_id"])


# -------------------- Sidebar -------------------- #

st.sidebar.title("🤖 ChatBot")

if st.sidebar.button("➕ New Chat"):
    reset_chat()
    st.rerun()

st.sidebar.header("My Conversations")

thread_ids = list(st.session_state["chat_threads"].keys())

for thread_id in reversed(thread_ids):

    chat_name = st.session_state["chat_threads"][thread_id]["name"]

    if st.sidebar.button(chat_name, key=thread_id):

        st.session_state["thread_id"] = thread_id

        messages = load_conversation(thread_id)

        history = []

        for msg in messages:

            role = "user" if isinstance(msg, HumanMessage) else "assistant"

            history.append(
                {
                    "role": role,
                    "content": msg.content,
                }
            )

        st.session_state["message_history"] = history
        st.rerun()


# -------------------- Chat Window -------------------- #

for message in st.session_state["message_history"]:
    with st.chat_message(message["role"]):
        st.write(message["content"])


user_input = st.chat_input("Type your message...")

if user_input:

    # Give the chat a name from the first prompt
    current_chat = st.session_state["chat_threads"][st.session_state["thread_id"]]

    if current_chat["name"] == "New Chat":
        current_chat["name"] = user_input[:30]

    # Display user message
    st.session_state["message_history"].append(
        {
            "role": "user",
            "content": user_input,
        }
    )

    with st.chat_message("user"):
        st.write(user_input)

    # Stream assistant response
    with st.chat_message("assistant"):

        ai_message = st.write_stream(
            chunk.content
            for chunk, metadata in chatbot_app.stream(
                {
                    "messages": [
                        HumanMessage(content=user_input)
                    ]
                },
                config=get_config(),
                stream_mode="messages",
            )
        )

    st.session_state["message_history"].append(
        {
            "role": "assistant",
            "content": ai_message,
        }
    )

    st.rerun()