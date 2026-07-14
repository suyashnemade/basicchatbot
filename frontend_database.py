import streamlit as st
from langchain_core.messages import HumanMessage, SystemMessage
from backend_database import chatbot_app, retreve_all_thread
import uuid

#-----------------------------utiliy functions----------------------------------------#
def generate_uuid():
    id = str(uuid.uuid4())
    return id

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
            "configurable":{
                "thread_id": thread_id
            }
        }
    ).values['messages']



#---------------------------------------------------------------------------------------#

CONFIG = {"configurable": {"thread_id": st.session_state['thread_id']}}

if 'message_history' not in st.session_state:
    st.session_state['message_history'] = []

if 'thread_id' not in st.session_state:
    st.session_state['thread_id'] = generate_uuid()


if 'chat_thread_id' not in st.session_state:
    st.session_state['chat_thread_id'] = retreve_all_thread()
add_thread(st.session_state['thread_id'])




#----------------------------SIDEBAR-------------------------------------#



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



#----------------------------CHAT WINDOW-------------------------------------#


for message in st.session_state['message_history']:
    st.chat_message(message['role']).text(message['content'])


user_input = st.chat_input('type here')
if user_input:
    if user_input:
        current_chat = st.session_state["chat_thread_id"][st.session_state["thread_id"]]

        if current_chat["name"] == "New Chat":  
            current_chat["name"] = user_input[:30]
            
    st.session_state['message_history'].append(
        {
            'role':'user', 
            'content':user_input
        }
    )

    with st.chat_message('user'):
        st.text(user_input)

    with st.chat_message('assistant'):
        ai_message = st.write_stream(
            message_chunk.content 
            for message_chunk, metadata in chatbot_app.stream(
                {
                    'messages': [HumanMessage(content=user_input)]
                },
                config=get_config(),
                stream_mode='messages'
            )
        )

    st.session_state['message_history'].append({'role':'assistant', 'content':ai_message})
