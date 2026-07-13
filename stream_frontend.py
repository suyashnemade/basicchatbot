import streamlit as st
from langchain_core.messages import HumanMessage, SystemMessage
from backend import chatbot_app

CONFIG = {"configurable": {"thread_id": "t1"}}

if 'message_history' not in st.session_state:
    st.session_state['message_history'] = []

for message in st.session_state['message_history']:
    st.chat_message(message['role']).text(message['content'])


user_input = st.chat_input('type here')
if user_input:
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
                config=CONFIG,
                stream_mode='messages'
            )
        )

    st.session_state['message_history'].append({'role':'assistant', 'content':ai_message})
