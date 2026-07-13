import streamlit as st
from langchain_core.messages import HumanMessage, SystemMessage
from backend import chatbot_app
import uuid


def generate_uuid():
    id = str(uuid.uuid4())
    return id

if 'thread_id' not in st.session_state:
    st.session_state['thread_id'] = generate_uuid()

CONFIG = {"configurable": {"thread_id": st.session_state['thread_id']}}


######################################################################################

# If there is no chat history, create a new chat thread
def get_config():
    return {
        "configurable": {
            "thread_id": st.session_state["thread_id"]
        }
    }

def reset_chat():
    thread_id = generate_uuid()
    st.session_state['thread_id'] = thread_id
    add_thread(st.session_state['thread_id'])
    st.session_state['message_history'] = []


def add_thread(thread_id, name ="New Chat"):
    if thread_id not in st.session_state['chat_thread_id']:
        st.session_state['chat_thread_id'][thread_id] = {
            "name":name
        }


def load_conversation(thread_id):
    return chatbot_app.get_state(
        config={
            "configurable":{"thread_id": thread_id}
        }
    ).values['messages']

####################################################################################


if 'message_history' not in st.session_state:
    st.session_state['message_history'] = []




if 'chat_thread_id' not in st.session_state:
    st.session_state['chat_thread_id'] = {}

add_thread(st.session_state['thread_id'])

######################################################################################

st.sidebar.title("ChatBot")
if st.sidebar.button("New Chat"):
    reset_chat()

st.sidebar.header("My Conversations")

tid = list(st.session_state['chat_thread_id'].keys())
for thread_id in reversed(tid):
    name = st.session_state['chat_thread_id'][thread_id]['name']
    if st.sidebar.button(name):
        
        st.session_state['thread_id'] = thread_id
        messages = load_conversation(thread_id)

        temp_messages = []

        for msg in messages:
            if isinstance(msg, HumanMessage):
                role = 'user'
            else:
                role = 'assistant'

            temp_messages.append({'role':role, 'content':msg.content})

        st.session_state['message_history'] = temp_messages

##########################################################################################
for message in st.session_state['message_history']:
    st.chat_message(message['role']).text(message['content'])


user_input = st.chat_input('type here')
if user_input:
    if user_input:
        current_chat = st.session_state["chat_thread_id"][st.session_state["thread_id"]]

        if current_chat["name"] == "New Chat":  
            current_chat["name"] = user_input[:30]
            
    st.session_state['message_history'].append({'role':'user', 'content':user_input})
    with st.chat_message('user'):
        st.text(user_input)

    # response = chatbot_app.invoke({'messages': st.session_state['message_history']}, config=CONFIG)
    # ai_message  = response['messages'][-1].content
    # 
    with st.chat_message('assistant'):
        # st.text(ai_message)
        ai_message = st.write_stream(
            message_chunk.content 
            for message_chunk, metadata in chatbot_app.stream(
                {'messages': [HumanMessage(content=user_input)]},
                config=get_config(),
                stream_mode='messages'
            )
        )

    st.session_state['message_history'].append({'role':'assistant', 'content':ai_message})
