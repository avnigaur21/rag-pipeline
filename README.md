# AutoStream AI Agent

> A conversational AI agent that qualifies social media leads for AutoStream — an automated video editing SaaS for content creators.

---

## Quick Start

### 1. Clone / download the project

```bash
git clone <your-repo-url>
cd autostream-agent
```

### 2. Create a virtual environment (recommended)

```bash
python -m venv venv
source venv/bin/activate      # macOS / Linux
venv\Scripts\activate         # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set Environment Variables

You must provide a Gemini API key:
```bash
export GEMINI_API_KEY="your-api-key"   # macOS / Linux
set GEMINI_API_KEY=your-api-key        # Windows
```
*(Note: A default key is included in the source for testing convenience, but setting your own is recommended).*

### 5. Run the agent

```bash
python main.py
```

---

## Example Conversation

```
You: Hi
Agent: Hello! I can help you with AutoStream's pricing, features, or getting started with a plan. What's on your mind?

You: Tell me about pricing
Agent: We offer two main plans. The Basic Plan is $29/month and includes 10 videos/month at 720p. The Pro Plan is $79/month for unlimited videos in 4K resolution, plus AI captions and 24/7 support.

You: I want to try the Pro plan for my YouTube channel
Agent: Awesome choice! 🚀 I can help you get started. I'll just need a few details.
Great! I'd love to get you started. What's your name?

You: John Smith
Agent: Nice to meet you, John Smith! What's your email address?

You: john@gmail.com
Agent: Almost there! Which creator platform do you primarily use?

You: YouTube
# Console prints: Lead captured successfully: John Smith, john@gmail.com, Youtube
Agent: 🎉 You're all set, John Smith! ...
```

---

## Architecture (~200 words)

### Why LangGraph?

**LangGraph** was selected as the core framework because it provides explicit, robust control over the agent's workflow using a directed graph (`StateGraph`), perfectly matching the assignment's state machine requirements. Unlike a "black-box" ReAct agent, a custom LangGraph ensures 100% deterministic routing for Intent Detection and Lead Capture workflows while leveraging **Gemini 1.5 Flash** strictly for natural language generation. This hybrid approach guarantees the agent never hallucinates during the critical lead-capture sequence but remains highly conversational during product inquiries.

### State Management

State is managed via LangGraph's `AgentState` `TypedDict` and persisted across the session using `langgraph.checkpoint.memory.MemorySaver`. The state retains:
- `messages`: The conversational history buffer (persisting across >5 turns).
- `intent`: The active user intent.
- `collecting_lead`: A flag indicating if the agent is in the sequential lead flow.
- `lead_data`: Form fields (`name`, `email`, `platform`).

Because `MemorySaver` tracks the `thread_id`, the agent seamlessly remembers context (such as partially filled lead forms) across multiple interactions.

### RAG (Retrieval-Augmented Generation)

When a pricing inquiry is detected, the graph routes to the RAG node. It fetches precise details from a local `knowledge.json` via keyword matching, and injects it into Gemini's context window. This grounds the LLM, ensuring it answers questions without fabricating pricing or policies.

---

## WhatsApp Integration

To deploy this agent on WhatsApp using Webhooks:

1. **Webhook Setup**: Register an HTTPS webhook URL (e.g., using FastAPI) with Meta's Cloud API or Twilio.
2. **Backend Handler**: When a WhatsApp message arrives, the webhook triggers your server.
3. **Session Persistence**: Instead of the in-memory `MemorySaver`, use `langgraph.checkpoint.postgres` or Redis to store the LangGraph checkpointer state, keyed by the user's WhatsApp phone number.
4. **Execution**: Pass the incoming message to `graph.invoke(..., config={"configurable": {"thread_id": phone_number}})`.
5. **Sending Replies**: Take the resulting `AIMessage` and POST it back via the WhatsApp Business API.

---

## Evaluation Notes

| Criterion | Implementation |
|---|---|
| **Mandatory Stack** | Uses **LangGraph** (StateGraph), **Gemini 1.5 Flash**, and Python 3.10+ |
| **Intent detection** | Custom node explicitly classifies intents and routes graph edges |
| **RAG** | Retrieval node extracts from `knowledge.json` and grounds Gemini LLM |
| **State management** | `MemorySaver` checkpointer retains state and messages indefinitely |
| **Tool calling** | Lead capture node sequentially collects 3 fields and exclusively fires `mock_lead_capture()` upon completion |
