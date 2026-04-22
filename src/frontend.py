import streamlit as st
from backend import chatbot
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage


# -----------------------------
# THREAD CONFIGURATION
# -----------------------------
# Used to maintain a consistent conversation thread (memory across messages)
CONFIG = {'configurable': {'thread_id': 'thread-1'}}


# -----------------------------
# SESSION STATE INITIALIZATION
# -----------------------------
# Initialize message history in session state if not already present
if 'message_history' not in st.session_state:
    st.session_state['message_history'] = []


# -----------------------------
# DISPLAY CHAT HISTORY
# -----------------------------
# Loop through stored messages and render them in the chat UI
for message in st.session_state['message_history']:
    
    # Identify role based on message type
    if isinstance(message, HumanMessage):
        role = "user"
    elif isinstance(message, AIMessage):
        role = "assistant"

    # Display message in appropriate chat bubble
    with st.chat_message(role):
        st.text(message.content)


# -----------------------------
# USER INPUT FIELD
# -----------------------------
# Input box for user to type messages
user_input = st.chat_input("Ask here")


# -----------------------------
# HANDLE USER INPUT
# -----------------------------
if user_input:
    
    # Add user message to session history
    st.session_state['message_history'].append(
        HumanMessage(content=user_input)
    )

    # Display user message immediately in UI
    with st.chat_message('user'):
        st.text(user_input)
    

    # -----------------------------
    # (OPTIONAL) NON-STREAMING RESPONSE
    # -----------------------------
    # This block is commented out but shows how to get a full response at once
    #
    # response = chatbot.invoke(
    #     {'messages': [HumanMessage(content=user_input)]},
    #     config = CONFIG
    # )   
    #
    # AI_message = response['messages'][-1].content


    # -----------------------------
    # STREAMING AI RESPONSE
    # -----------------------------
    # Stream response token-by-token for better UX
    with st.chat_message('assistant'):
        AI_message = st.write_stream(
            # Generator expression to stream message chunks
            message_chunk.content
            for message_chunk, metadata in chatbot.stream(
                {'messages': [HumanMessage(content=user_input)]},
                config=CONFIG,
                stream_mode='messages'
            )
        )


    # -----------------------------
    # STORE AI RESPONSE
    # -----------------------------
    # Save AI response back into session history
    st.session_state['message_history'].append(
        AIMessage(content=AI_message)
    )