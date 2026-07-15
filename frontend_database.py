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


def add_thread(thread_id, name =None):
    if name is None:
        name =f"Chat {thread_id[:8]}"
    if thread_id not in st.session_state['chat_thread_id']:
        st.session_state['chat_thread_id'][thread_id] = {
            "name": name
        }


def load_conversation(thread_id):
    state = chatbot_app.get_state(
        config={
            "configurable":{
                "thread_id": thread_id
            }
        }
    ).values.get('messages',[])
    return state



#---------------------------------------------------------------------------------------#



if 'message_history' not in st.session_state:
    st.session_state['message_history'] = []

if 'thread_id' not in st.session_state:
    st.session_state['thread_id'] = generate_uuid()

# CONFIG = {"configurable": {"thread_id": st.session_state['thread_id']}}


if 'chat_thread_id' not in st.session_state:
    raw_threads = retreve_all_thread()
    for thread_id in raw_threads:
        try:
            messages = load_conversation(thread_id)
            if messages:
                for msg in messages:
                    if isinstance(msg, HumanMessage) or (hasattr(msg, 'type') and msg.type == 'human'):
                        raw_threads[thread_id]['name'] = msg.content[:30]
                        break
                else:
                    raw_threads[thread_id]['name'] = messages[0].content[:30]
            else:
                raw_threads[thread_id]['name'] = f"Chat {thread_id[:8]}"
        except Exception:
            raw_threads[thread_id]['name'] = f"Chat {thread_id[:8]}"
    st.session_state['chat_thread_id'] = raw_threads
add_thread(st.session_state['thread_id'])




#----------------------------SIDEBAR-------------------------------------#



st.sidebar.title("ChatBot")
if st.sidebar.button("New Chat"):
    reset_chat()
    st.rerun()



st.sidebar.header("My Conversations")

tid = list(st.session_state['chat_thread_id'].keys())

for thread_id in reversed(tid):
    name = st.session_state['chat_thread_id'][thread_id]['name']
    if st.sidebar.button(name, key=f"thread_{thread_id}"):
        
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
        st.rerun()



#----------------------------CHAT WINDOW-------------------------------------#


for message in st.session_state['message_history']:
    st.chat_message(message['role']).text(message['content'])


user_input = st.chat_input('type here')
if user_input:
    current_chat = st.session_state["chat_thread_id"][st.session_state["thread_id"]]

    if current_chat["name"] == "New Chat" or current_chat["name"] == f"Chat {st.session_state['thread_id'][:8]}":  
        current_chat["name"] = user_input[:30]
            
    st.session_state['message_history'].append(
        {
            'role':'user', 
            'content':user_input
        }
    )

    CONFIG = {
        "configurable": {"thread_id": st.session_state['thread_id']},
        "metadata":{
            "thread_id": st.session_state["thread_id"],
            "name": st.session_state['chat_thread_id'][st.session_state['thread_id']]['name']
        },
        "run_name": "chat_turn"
    }

    with st.chat_message('user'):
        st.text(user_input)

    with st.chat_message('assistant'):
        ai_message = st.write_stream(
            message_chunk.content 
            for message_chunk, metadata in chatbot_app.stream(
                {
                    'messages': [HumanMessage(content=user_input)]
                },
                config=CONFIG,
                stream_mode='messages'
            )
        )

    st.session_state['message_history'].append({'role':'assistant', 'content':ai_message})
    st.rerun()
