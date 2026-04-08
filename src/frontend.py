
import streamlit as st
from backend import chatbot
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage


#thread creation to maintain history
CONFIG = {'configurable': {'thread_id': 'thread-1'}}

if 'message_history' not in st.session_state:
    st.session_state['message_history'] = []


for message in st.session_state['message_history']:
    if isinstance(message, HumanMessage):
        role = "user"
    elif isinstance(message, AIMessage):
        role = "assistant"

    with st.chat_message(role):
        st.text(message.content)



user_input = st.chat_input("Ask here")

if user_input:
    
    # first add the message to message_history
    st.session_state['message_history'].append(HumanMessage(content=user_input))

    with st.chat_message('user'):
        st.text(user_input)
    
    # response = chatbot.invoke(
    #     {'messages': [HumanMessage(content = user_input)]},
    #     config = CONFIG
    # )   

    # AI_message = response['messages'][-1].content


    # Streamming the AI response
    with st.chat_message('assistant'):
        AI_message = st.write_stream(
              message_chunk.content for message_chunk, metadata in chatbot.stream(
                {'messages': [HumanMessage(content=user_input)]},
                config= CONFIG,
                stream_mode= 'messages'
        )
        )


    # add AI response to message_history 
    st.session_state['message_history'].append(AIMessage(content=AI_message))

   
