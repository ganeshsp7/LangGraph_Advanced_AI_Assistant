import streamlit as st
from backend import chatbot
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from uuid import uuid4


# -----------------------------
# Utility Functions
# -----------------------------

# Generate thread ID for conversation
def generate_thread_id():
    thread_id = uuid4()
    return thread_id

# Reset chat by clearing message history and generating a new thread ID
def reset_chat():
    thread_id = generate_thread_id()
    st.session_state['thread_id'] = thread_id
    add_thread(st.session_state['thread_id'])
    st.session_state['message_history'] = []

# Add a new thread to the list of chat threads in session state with a unique ID and a default title based on the thread ID
def add_thread(thread_id):
    if not any(thread_id == thread['id'] for thread in st.session_state['chat_threads']):
        st.session_state['chat_threads'].append(
            {
                'id': thread_id,
                'title': str(thread_id)[:16]  # Display only first 16 characters for readability
            }
        )

# Load conversation history for a given thread ID and update session state
def load_conversation(thread_id):
    """
    Load conversation history for a given thread from LangGraph.

    Notes:
    - `chatbot.get_state()` returns a StateSnapshot object, NOT a dictionary.
    - Actual data is stored inside `state.values`, which is a dict.
    - Messages are accessed via `state.values['messages']`.
    - Always use `.get('messages', [])` to avoid KeyError if no messages exist.
    - The extracted messages must be a list of HumanMessage / AIMessage objects
      to work correctly with Streamlit chat rendering.

    Args:
        thread_id (str): Unique identifier for the conversation thread.

    Side Effects:
        Updates `st.session_state['message_history']` with the loaded messages.
    """
    messages = chatbot.get_state({'configurable': {'thread_id': thread_id}})
    st.session_state['message_history'] = messages.values.get('messages', [])
   


# -----------------------------
# SESSION STATE INITIALIZATION
# -----------------------------
# Initialize message history in session state if not already present
if 'message_history' not in st.session_state:
    st.session_state['message_history'] = []

# Initialize thread ID in session state if not already present
if 'thread_id' not in st.session_state:
    st.session_state['thread_id'] = generate_thread_id()

if 'chat_threads' not in st.session_state:
    st.session_state['chat_threads'] = []

add_thread(st.session_state['thread_id'])

# -----------------------------
# THREAD CONFIGURATION
# -----------------------------
# Used to maintain a consistent conversation thread (memory across messages)
CONFIG = {'configurable': {'thread_id': st.session_state['thread_id']}}


# -----------------------------
# SIDEBAR UI
# -----------------------------
# Create a title in the sidebar (left panel in Streamlit UI)
st.sidebar.title("LangGraph Chatbot")


# Add a button in the sidebar to start a new conversation
st.sidebar.button("New Conversation", on_click=reset_chat)


# Add a section header in the sidebar 
st.sidebar.header("My Conversation")



# Display list of conversation threads in the sidebar
for thread in st.session_state['chat_threads'][::-1]:
    if st.sidebar.button(thread["title"]):
        st.session_state['thread_id'] = thread['id']
        load_conversation(thread['id'])   


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
        with st.spinner("Generating response..."):
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

    # -----------------------------
    # UPDATE THREAD TITLE (FIRST AI RESPONSE)
    # -----------------------------
    threads = st.session_state['chat_threads']

    for t in threads:
        if t['id'] == st.session_state['thread_id'] and t['title'] == str(st.session_state['thread_id'])[:16]: 
            # Take first 16 characters of AI response
            t['title'] = AI_message[:16]
            break