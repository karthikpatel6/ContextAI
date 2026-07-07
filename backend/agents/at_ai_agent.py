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
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


load_dotenv()

llm = ChatGroq(
    model="qwen/qwen3.6-27b", 
    api_key=os.getenv("GROQ_API_KEY"),
    temperature=0.7,
)

tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

# WEB SEARCH TOOL
@tool   
def web_search(query: str) -> str:
    """Search the web for current information."""
    results = tavily_client.search(query=query, max_results=3)
    answers = results.get("results", [])
    if not answers:
        return "No results found."
    return answers[0]["content"][:500]

# EMAIL TOOL
@tool
def send_email(to: str, subject: str, body: str) -> str:
    """Send an email to a specified address with a subject and body."""
    try:
        email_address = os.getenv("EMAIL_ADDRESS")
        email_password = os.getenv("EMAIL_PASSWORD")

        msg = MIMEMultipart()
        msg["From"] = email_address
        msg["To"] = to
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(email_address, email_password)
            server.sendmail(email_address, to, msg.as_string())

        return f"Email sent successfully to {to}"

    except Exception as e:
        return f"Failed to send email: {str(e)}"

class AgentState(TypedDict):
    messages: Annotated[list, operator.add]

tools = [web_search, send_email]
llm_with_tools = llm.bind_tools(tools)

def agent_node(state: AgentState):
    messages = state["messages"]
    response = llm_with_tools.invoke(messages)
    return {"messages": [response]}

tool_node = ToolNode(tools)

def should_continue(state: AgentState):
    last_message = state["messages"][-1]
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "tools"
    return END

graph = StateGraph(AgentState)

graph.add_node("agent", agent_node)
graph.add_node("tools", tool_node)

graph.set_entry_point("agent")

graph.add_conditional_edges(
    "agent",
    should_continue,
    {"tools": "tools", END: END}
)

graph.add_edge("tools", "agent")

agent = graph.compile()

async def run_agent(query: str, chat_history: list = []) -> str:
    system = SystemMessage(content="""You are an AI assistant inside a chat app.
                           You help users with questions, web searches, and tasks.
                           Be concise and friendly. Format responses clearly.""")
    
    user_message = HumanMessage(content=query)

    result = await agent.ainvoke({
        "messages": [system, *chat_history, user_message]
    })

    last_message = result["messages"][-1]

    if hasattr(last_message, "content") and last_message.content:
        return last_message.content
    
    if isinstance(last_message.content, list):
        for block in last_message.content:
            if isinstance(block, dict) and block.get("type") == "text":
                return block.get("text", "")

    return "I couldn't generate a response. Please try again."