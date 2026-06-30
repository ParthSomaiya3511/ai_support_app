# ai_agent.py

import os
import json
import anthropic
from dotenv import load_dotenv
from docs_store import get_all_docs, DOCUMENTATION

load_dotenv()

class SupportAgent:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY", "")
        self.model = "claude-3-5-sonnet-20241022"
        
        # Check if mock key is explicitly used
        self.is_mock = (self.api_key == "sk-ant-free-mock-key-12345" or not self.api_key)
        
        if not self.is_mock:
            self.client = anthropic.Anthropic(api_key=self.api_key)

    def process_message(self, user_message: str, chat_history: list) -> dict:
        # If mock key is used, run the local simulator
        if self.is_mock:
            return self._generate_mock_response(user_message)
            
        # Try to make a live call
        formatted_history = []
        for msg in chat_history:
            role = "user" if msg["role"] == "user" else "assistant"
            content = msg["content"]
            if isinstance(content, dict):
                content = content.get("response", "")
            formatted_history.append({"role": role, "content": content})

        formatted_history.append({"role": "user", "content": user_message})
        docs_context = get_all_docs()

        system_prompt = f"""You are an AI customer support assistant.
        
Reference Documentation:
{docs_context}

You must respond exclusively in valid JSON format.

Expected JSON Structure:
{{
  "action": "REPLY" | "CREATE_TICKET" | "ESCALATE",
  "response": "Your response to the customer.",
  "ticket_needed": true | false,
  "ticket_priority": "Low" | "Medium" | "High" | null,
  "ticket_summary": "Summary of the issue if creating a ticket."
}}
"""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=800,
                system=system_prompt,
                messages=formatted_history
            )
            raw_content = response.content[0].text.strip()
            
            if raw_content.startswith("```json"):
                raw_content = raw_content[7:]
            if raw_content.endswith("```"):
                raw_content = raw_content[:-3]
            raw_content = raw_content.strip()

            return json.loads(raw_content)

        except Exception as e:
            err_msg = str(e)
            # AUTO-RECOVERY: If the real API key has no credits, catch the error and run mock mode
            if "credit balance is too low" in err_msg:
                return self._generate_mock_response(user_message, automatic_fallback=True)
                
            return {
                "action": "REPLY",
                "response": f"An error occurred: {err_msg}.",
                "ticket_needed": False,
                "ticket_priority": None,
                "ticket_summary": None
            }

    def _generate_mock_response(self, message: str, automatic_fallback: bool = False) -> dict:
        """Simulates the Claude model output locally for testing without cost."""
        msg_lower = message.lower()
        prefix = "[Free Mode Active]" if not automatic_fallback else "[Auto-Fallback: Real API Key Out of Credits]"
        
        if "refund" in msg_lower or "money back" in msg_lower:
            return {
                "action": "REPLY",
                "response": f"{prefix} {DOCUMENTATION['refund_policy']}",
                "ticket_needed": False,
                "ticket_priority": None,
                "ticket_summary": None
            }
        elif "ship" in msg_lower or "delivery" in msg_lower:
            return {
                "action": "REPLY",
                "response": f"{prefix} {DOCUMENTATION['shipping_details']}",
                "ticket_needed": False,
                "ticket_priority": None,
                "ticket_summary": None
            }
        elif "reset" in msg_lower or "password" in msg_lower:
            return {
                "action": "REPLY",
                "response": f"{prefix} {DOCUMENTATION['account_reset']}",
                "ticket_needed": False,
                "ticket_priority": None,
                "ticket_summary": None
            }
        elif "pricing" in msg_lower or "cost" in msg_lower:
            return {
                "action": "REPLY",
                "response": f"{prefix} {DOCUMENTATION['pricing_plans']}",
                "ticket_needed": False,
                "ticket_priority": None,
                "ticket_summary": None
            }
        elif "human" in msg_lower or "agent" in msg_lower or "ticket" in msg_lower or "broken" in msg_lower:
            return {
                "action": "CREATE_TICKET",
                "response": f"{prefix} I've initiated a support ticket for this issue so a human agent can follow up.",
                "ticket_needed": True,
                "ticket_priority": "High",
                "ticket_summary": f"Escalated issue: '{message}'"
            }
        else:
            return {
                "action": "REPLY",
                "response": f"{prefix} Try asking about 'refunds', 'shipping details', 'password reset', or ask to 'speak to an agent' to test ticketing.",
                "ticket_needed": False,
                "ticket_priority": None,
                "ticket_summary": None
            }