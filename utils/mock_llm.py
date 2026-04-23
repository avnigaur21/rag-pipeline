"""
mock_llm.py – A simulated LLM layer.

This module simulates natural language generation by applying heuristic text wrapping
and conversational phrasing. It allows the system to run locally without API keys,
while maintaining an architecture where a real LLM can easily be plugged in later.
"""

import random

class MockLLM:
    def __init__(self):
        # In a real implementation, we would initialize the API client here.
        pass

    def generate_response(self, prompt: str, context: str = None, intent: str = "general") -> str:
        """
        Simulate an LLM response based on the intent and provided context.
        
        Args:
            prompt: The user's input or structured prompt.
            context: Formatted context from RAG retrieval.
            intent: The intent category to guide the mock response style.
            
        Returns:
            A natural-sounding response string.
        """
        if intent in ["pricing", "policies"] and context:
            intros = [
                "Here's what I found for you:\n\n",
                "Absolutely! Let me break down the details:\n\n",
                "I can certainly help with that. Here is the info you requested:\n\n"
            ]
            outros = [
                "\n\nDoes this sound like what you're looking for?",
                "\n\nLet me know if you have any specific questions about these details!",
                "\n\nWould you like to get started or learn more?"
            ]
            return f"{random.choice(intros)}{context}{random.choice(outros)}"
            
        elif intent == "general" and context:
             intros = [
                 "Based on our knowledge base, here is the information:\n\n",
                 "I found some relevant information for you:\n\n",
                 "Here's what you need to know:\n\n"
             ]
             return f"{random.choice(intros)}{context}"
             
        elif intent == "greeting":
            greetings = [
                "Hello! 👋 Welcome to AutoStream. I'm here to answer your questions about our video editing plans or help you get started. What's on your mind?",
                "Hi there! 👋 How can I help you with AutoStream today? I know all about our pricing, features, and policies.",
                "Hey! 👋 Welcome. Are you looking to learn about our features, or perhaps ready to choose a plan?"
            ]
            return random.choice(greetings)

        # Fallback / Catch-all
        fallbacks = [
            "I'm still learning! I'm best at answering questions about AutoStream's plans, pricing, and policies. Could you try asking about those?",
            "I'm not completely sure about that. I specialize in helping creators find the right AutoStream plan. Want to hear about our Pro plan?",
            "Hmm, I might not have the answer to that just yet. Can I help you with pricing or support information instead?"
        ]
        return random.choice(fallbacks)
