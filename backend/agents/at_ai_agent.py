import os
import re
from pathlib import Path
from dotenv import dotenv_values, load_dotenv
from langchain_groq import ChatGroq
from langchain_core.tools import tool
from tavily import TavilyClient
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import SecretStr
from typing import TypedDict, Annotated
import operator
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


BACKEND_ROOT = Path(__file__).resolve().parent.parent
ENV_PATH = BACKEND_ROOT / ".env"

load_dotenv(ENV_PATH, override=False)


def _load_email_config() -> tuple[str, str]:
    load_dotenv(ENV_PATH, override=False)
    env_values = dotenv_values(ENV_PATH)

    email_address = str(os.getenv("EMAIL_ADDRESS") or env_values.get("EMAIL_ADDRESS", "")).strip()
    email_password = str(os.getenv("EMAIL_PASSWORD") or env_values.get("EMAIL_PASSWORD", "")).strip()

    if not email_address or not email_password:
        raise ValueError(
            "Email credentials are not configured. Add EMAIL_ADDRESS and EMAIL_PASSWORD to backend/.env."
        )

    return email_address, email_password


def _build_direct_email_action(query: str) -> tuple[str, str, str] | None:
    normalized_query = query.strip().lower()
    if "send email" not in normalized_query and "send an email" not in normalized_query and "email" not in normalized_query:
        return None

    email_matches = re.findall(r"[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}", query, flags=re.IGNORECASE)
    if not email_matches:
        return None

    recipient = email_matches[0]
    subject = "Generated content"
    body = (
        "Hi,\n\n"
        "This is a generated message from ContextAI.\n\n"
        "Regards,\n"
        "ContextAI"
    )

    if "generate" in normalized_query or "generate something" in normalized_query:
        body = (
            "Hi,\n\n"
            "Here is a generated message from ContextAI for your request.\n\n"
            "Regards,\n"
            "ContextAI"
        )

    return recipient, subject, body


groq_api_key = os.getenv("GROQ_API_KEY") or dotenv_values(ENV_PATH).get("GROQ_API_KEY")
llm = ChatGroq(
    model="qwen/qwen3.6-27b",
    api_key=SecretStr(groq_api_key) if groq_api_key else None,
    temperature=0.7,
)

tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY") or dotenv_values(ENV_PATH).get("TAVILY_API_KEY", ""))


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
        email_address, email_password = _load_email_config()

        msg = MIMEMultipart()
        msg["From"] = email_address
        msg["To"] = to
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        smtp_host = str(os.getenv("SMTP_HOST") or dotenv_values(ENV_PATH).get("SMTP_HOST", "smtp.gmail.com"))
        smtp_port = int(str(os.getenv("SMTP_PORT") or dotenv_values(ENV_PATH).get("SMTP_PORT", "587")))

        with smtplib.SMTP(smtp_host, smtp_port) as server:
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
    {"tools": "tools", END: END},
)

graph.add_edge("tools", "agent")

agent = graph.compile()


async def run_agent_stream(query: str, callback) -> str:
    """Stream agent response token by token via callback."""
    direct_email_action = _build_direct_email_action(query)
    if direct_email_action:
        recipient, subject, body = direct_email_action
        email_sender = getattr(send_email, "func", None)
        result = email_sender(recipient, subject, body) if callable(email_sender) else send_email.invoke({"to": recipient, "subject": subject, "body": body})
        result_text = str(result)
        await callback(result_text)
        return result_text

    system = SystemMessage(
        content="""You are an AI assistant inside a chat app.
You help users with questions, web searches, and tasks.
If the user asks you to send an email, use the send_email tool with a clear recipient, subject, and message body.
Be concise and friendly. Format responses clearly."""
    )

    user_message = HumanMessage(content=query)

    full_response = ""
    async for chunk in llm.astream([system, user_message]):
        token = chunk.content
        if isinstance(token, str) and token:
            full_response += token
            await callback(token)

    return full_response


async def run_agent(query: str, chat_history: list | None = None) -> str:
    direct_email_action = _build_direct_email_action(query)
    if direct_email_action:
        recipient, subject, body = direct_email_action
        email_sender = getattr(send_email, "func", None)
        result = email_sender(recipient, subject, body) if callable(email_sender) else send_email.invoke({"to": recipient, "subject": subject, "body": body})
        return str(result)

    system = SystemMessage(
        content="""You are an AI assistant inside a chat app.
You help users with questions, web searches, and tasks.
If the user asks you to send an email, use the send_email tool with a clear recipient, subject, and message body.
Be concise and friendly. Format responses clearly."""
    )

    user_message = HumanMessage(content=query)
    history = chat_history or []

    result = await agent.ainvoke({
        "messages": [system, *history, user_message]
    })

    last_message = result["messages"][-1]

    if hasattr(last_message, "content") and last_message.content:
        if isinstance(last_message.content, str):
            return last_message.content
        if isinstance(last_message.content, list):
            for block in last_message.content:
                if isinstance(block, dict) and block.get("type") == "text":
                    return block.get("text", "")

    return "I couldn't generate a response. Please try again."