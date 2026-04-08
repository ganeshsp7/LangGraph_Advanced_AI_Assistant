from langgraph.graph import StateGraph, START, END
from langchain_core.messages import BaseMessage
from langchain_ollama import ChatOllama
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import InMemorySaver

from typing import TypedDict, Annotated
from dotenv import load_dotenv



#************************** Define StateGraph ************************************

class ChatState(TypedDict):
    messages : Annotated[list[BaseMessage], add_messages]

#************************** Define Nodes *****************************************

def chat_node(state: ChatState): 
    messages = state['messages']
    llm = ChatOllama(model="llama3.1:8b")
    response = llm.invoke(messages)
    return {"messages": [response]}


#************************** Build Graph *****************************************

graph = StateGraph(ChatState)
graph.add_node("chat_node",chat_node)

graph.add_edge(START, "chat_node")
graph.add_edge("chat_node",END)


#************************** Check Pointer *****************************************
checkpointer = InMemorySaver()

#************************** compile Graph with checkpointer ************************

chatbot =graph.compile(checkpointer=checkpointer)