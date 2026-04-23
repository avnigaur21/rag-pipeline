# AutoStream AI Agent

> A conversational AI agent that qualifies social media leads for AutoStream — an automated video editing SaaS for content creators.

---

## Quick Start

### 1. Clone / download the project

```bash
git clone https://github.com/avnigaur21/rag-pipeline.git
cd rag-pipeline
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

You must provide a Gemini API key. Create a `.env` file in the root directory and add:
```bash
GEMINI_API_KEY=your-api-key
```

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

## Architecture

### Framework

The agent is built with **LangGraph** to provide explicit, robust control over the conversational workflow using a directed graph (`StateGraph`). It uses **Gemini 2.5 Flash** for natural language generation. This hybrid approach guarantees deterministic routing for lead-capture sequences while remaining highly conversational during product inquiries.

### State Management

State is managed via LangGraph's `AgentState` and persisted across the session using `langgraph.checkpoint.memory.MemorySaver`. The state tracks the conversational history buffer, the active user intent, and any collected lead data (`name`, `email`, `platform`).

### Retrieval-Augmented Generation (RAG)

When a pricing inquiry is detected, the graph routes to the RAG node. It fetches precise details from a local `knowledge.json` via keyword matching, and injects it into Gemini's context window.

---

## WhatsApp Integration

To deploy this agent on WhatsApp using Webhooks:

1. **Webhook Setup**: Register an HTTPS webhook URL (e.g., using FastAPI) with Meta's Cloud API or Twilio.
2. **Backend Handler**: When a WhatsApp message arrives, the webhook triggers your server.
3. **Session Persistence**: Instead of the in-memory `MemorySaver`, use `langgraph.checkpoint.postgres` or Redis to store the LangGraph checkpointer state, keyed by the user's WhatsApp phone number.
4. **Execution**: Pass the incoming message to `graph.invoke(..., config={"configurable": {"thread_id": phone_number}})`.
5. **Sending Replies**: Take the resulting `AIMessage` and POST it back via the WhatsApp Business API.
