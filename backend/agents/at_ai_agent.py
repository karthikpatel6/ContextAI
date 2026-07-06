import os
from dotenv import load_dotenv
#from langchain.chat_models import ChatGroq
from langchain_groq import ChatGroq
from langchain_core.tools import tool
from tavily import TavilyClient
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langchain_core.messages import HumanMessage, SystemMessage
from typing import TypedDict, Annotated
import operator


load_dotenv()

llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    api_key=os.getenv("GROQ_API_KEY"),
    temperature=0.7,
)

tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

@tool
def web_search(query: str) -> str:
    """Search the web for current information."""
    results = tavily_client.search(query=query, max_results=3)
    answers = results.get("results", [])
    if not answers:
        return "No results found."
    return answers[0]["content"][:500]

class AgentState(TypedDict):
    messages: Annotated[list, operator.add]

tools = [web_search]
llm_with_tools = llm.bind_tools(tools)

def agent_node(state: AgentState):
    messages = state["messages"]
    response = llm_with_tools.invoke(messages)
    return {"messages": [response]}

tool_node = ToolNode(tools)