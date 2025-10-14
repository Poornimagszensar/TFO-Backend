from typing import TypedDict, Annotated, List
from langgraph.graph import StateGraph, START, END
from langchain_ollama import ChatOllama
from langchain_core.messages import BaseMessage, HumanMessage
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver

class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    agent: str

llm = ChatOllama(model="llama3.2:latest")

def knowledge_agent(state: ChatState) -> ChatState:
    # take user query from state
    messages = state['messages']
    # sending it to llm
    response = llm.invoke(messages)
    # response store into state
    return {'messages': [response], "agent": "Knowledge Agent"}

def math_agent(state: ChatState) -> ChatState:
    # take user query from state
    messages = state['messages']
    # sending it to llm
    response = llm.invoke(messages)
    # response store into state
    return {'messages': [response], "agent": "Math Agent"}

def router_node(state: ChatState):
    last_message = state['messages'][-1].content

    if any(char.isdigit() for char in last_message) or "math" in last_message.lower():
        return "math_agent"
    else :
        return "knowledge_agent"

check_pointer = MemorySaver()

graph = StateGraph(ChatState)
graph.add_node("router_node", router_node)
graph.add_node("knowledge_agent", knowledge_agent)
graph.add_node("math_agent", math_agent)

graph.add_conditional_edges(START, router_node)
graph.add_edge("knowledge_agent", END)
graph.add_edge("math_agent", END)

workflow = graph.compile(checkpointer=check_pointer)