"""
main.py – AutoStream Conversational AI Agent (LangGraph + Gemini)

This file fulfills the strict Mandatory Stack requirements:
- Framework: LangGraph
- LLM: Gemini 1.5 Flash
- State Management: MemorySaver (checkpointer)
"""

import os
import sys

# Ensure UTF-8 output on Windows consoles
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        pass

from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from dotenv import load_dotenv

load_dotenv() # Load from .env

# ── Force API Key ──
# If the user has a broken system-wide GOOGLE_API_KEY, it overrides GEMINI_API_KEY in LangChain.
# We must delete it from the runtime environment to force the correct key to be used.
if "GEMINI_API_KEY" in os.environ:
    os.environ["GOOGLE_API_KEY"] = os.environ["GEMINI_API_KEY"]
    
from langchain_google_genai import ChatGoogleGenerativeAI

from utils.intent import classify_intent
from utils.rag import retrieve, get_all_pricing
from utils.lead import try_collect_field, is_lead_complete, mock_lead_capture, get_next_lead_prompt

# Use gemini-2.5-flash since gemini-1.5-flash is deprecated and removed
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.3)

# ── 1. State Definition ──
class AgentState(TypedDict):
    messages: Annotated[list, add_messages]
    intent: str
    collecting_lead: bool
    lead_data: dict
    lead_captured: bool

# ── 2. Nodes ──

def intent_node(state: AgentState):
    """Classifies the intent of the last user message."""
    last_msg = state["messages"][-1].content
    
    # Bypass intent if we are mid-lead collection
    if state.get("collecting_lead") and not state.get("lead_captured"):
        return {"intent": "continue_lead"}
        
    intent = classify_intent(last_msg)
    return {"intent": intent}

def RAG_node(state: AgentState):
    """Handles pricing and product inquiries using Local RAG."""
    last_msg = state["messages"][-1].content
    kb_result = retrieve(last_msg)
    
    if not kb_result:
        kb_result = get_all_pricing()
        
    prompt = f"""
User asked: {last_msg}

Here is the retrieved product information from our knowledge base:
{kb_result}

Based ONLY on the retrieved info, answer the user clearly, conversationally, and accurately.
"""
    response = llm.invoke([SystemMessage(content=prompt)])
    return {"messages": [AIMessage(content=response.content)]}

def greeting_node(state: AgentState):
    """Handles casual greetings."""
    prompt = "A user just said hello. Greet them warmly and tell them you can help with AutoStream's pricing, features, or signing up for a plan. Keep it concise."
    response = llm.invoke([SystemMessage(content=prompt), state["messages"][-1]])
    return {"messages": [AIMessage(content=response.content)]}

def lead_capture_node(state: AgentState):
    """Handles the sequential collection of lead data and triggers Tool Execution."""
    last_msg = state["messages"][-1].content
    lead_data = state.get("lead_data", {"name": None, "email": None, "platform": None})
    
    # Start of lead collection
    if not state.get("collecting_lead"):
        prompt = get_next_lead_prompt(lead_data)
        intro = "Awesome choice! 🚀 I can help you get started. I'll just need a few details."
        return {
            "collecting_lead": True,
            "lead_data": lead_data,
            "messages": [AIMessage(content=f"{intro}\n\n{prompt}")]
        }
        
    # Process user input for the missing field
    updated_lead_data, error = try_collect_field(last_msg, lead_data)
    
    if error:
        return {"lead_data": updated_lead_data, "messages": [AIMessage(content=error)]}
        
    # Check if we have collected all 3 required fields
    if is_lead_complete(updated_lead_data):
        # ── Tool Execution ──
        success_msg = mock_lead_capture(
            updated_lead_data["name"], 
            updated_lead_data["email"], 
            updated_lead_data["platform"]
        )
        return {
            "lead_captured": True,
            "collecting_lead": False,
            "lead_data": updated_lead_data,
            "messages": [AIMessage(content=success_msg)]
        }
    else:
        prompt = get_next_lead_prompt(updated_lead_data)
        return {"lead_data": updated_lead_data, "messages": [AIMessage(content=prompt)]}

def general_node(state: AgentState):
    """Fallback for general queries."""
    last_msg = state["messages"][-1].content
    kb_result = retrieve(last_msg)
    
    if kb_result:
        prompt = f"User asked: {last_msg}\nRelevant info: {kb_result}\nAnswer helpfully."
    else:
        prompt = "You are an AI assistant for AutoStream. Answer the user helpfully."
        
    response = llm.invoke([SystemMessage(content=prompt), state["messages"][-1]])
    return {"messages": [AIMessage(content=response.content)]}

# ── 3. Routing Logic ──
def route_intent(state: AgentState):
    intent = state["intent"]
    if intent == "continue_lead":
        return "lead_capture"
    elif intent == "greeting":
        return "greeting"
    elif intent == "pricing":
        return "rag"
    elif intent == "high_intent":
        return "lead_capture"
    else:
        return "general"

# ── 4. Build LangGraph ──
builder = StateGraph(AgentState)

builder.add_node("intent_identifier", intent_node)
builder.add_node("greeting", greeting_node)
builder.add_node("rag", RAG_node)
builder.add_node("lead_capture", lead_capture_node)
builder.add_node("general", general_node)

# Flow: User Message -> Intent Identifier -> Routing -> Specific Node -> END
builder.add_edge(START, "intent_identifier")
builder.add_conditional_edges(
    "intent_identifier",
    route_intent,
    {
        "greeting": "greeting",
        "rag": "rag",
        "lead_capture": "lead_capture",
        "general": "general"
    }
)

builder.add_edge("greeting", END)
builder.add_edge("rag", END)
builder.add_edge("lead_capture", END)
builder.add_edge("general", END)

# Must retain memory across 5-6 conversation turns -> MemorySaver
memory = MemorySaver()
graph = builder.compile(checkpointer=memory)

# ── CLI Runner ──

BANNER = """
╔══════════════════════════════════════════════════════╗
║         AutoStream AI Agent  –  Powered by Inflx     ║
║    Automated Video Editing for Content Creators 🎬   ║
╚══════════════════════════════════════════════════════╝
Type 'quit' or 'exit' to end the session.
"""

def main():
    print(BANNER)
    # Thread ID for LangGraph memory tracking
    config = {"configurable": {"thread_id": "session_1"}}
    
    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nAgent: Goodbye! 👋")
            break

        if not user_input:
            continue

        if user_input.lower() in ("quit", "exit", "bye", "goodbye"):
            print("Agent: Thanks for chatting! Have a great day. 👋")
            break

        # Execute LangGraph Pipeline
        try:
            result = graph.invoke(
                {"messages": [HumanMessage(content=user_input)]},
                config=config
            )
            # Output the final response generated by the agent node
            ai_response = result["messages"][-1].content
            print(f"\nAgent: {ai_response}\n")
        except Exception as e:
            if "404" in str(e) or "API_KEY" in str(e) or "403" in str(e) or "401" in str(e) or "API key" in str(e):
                print("\n[Error] Gemini API key is missing or invalid.")
                print("Please export a valid GEMINI_API_KEY environment variable to use the agent.\n")
            else:
                print(f"\n[Error] An unexpected error occurred: {e}\n")

if __name__ == "__main__":
    main()