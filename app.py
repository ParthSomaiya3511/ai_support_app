# app.py

import os
import streamlit as st
from dotenv import load_dotenv
from ai_agent import SupportAgent
from ticket_manager import TicketManager
from docs_store import DOCUMENTATION

load_dotenv()

st.set_page_config(
    page_title="AI Customer Support Desk",
    layout="wide",
    initial_sidebar_state="expanded"
)

if "messages" not in st.session_state:
    st.session_state.messages = []
if "tickets" not in st.session_state:
    st.session_state.tickets = []

# Fetch active key or fall back to our Free Mock Key
env_api_key = os.getenv("ANTHROPIC_API_KEY", "sk-ant-free-mock-key-12345")

with st.sidebar:
    st.title("⚙️ Support Hub Controls")
    
    # Input field pre-filled with the free testing key
    api_key_input = st.text_input(
        "Anthropic Claude API Key", 
        value=env_api_key,
        type="password",
        help="Use 'sk-ant-free-mock-key-12345' to test the logic for free."
    )
    
    if api_key_input == "sk-ant-free-mock-key-12345":
        st.success("🟢 Running in Free Mode")
    else:
        st.info("🔵 Running with Live API Key")

    st.divider()
    st.subheader("📚 Available Documentation")
    for category, content in DOCUMENTATION.items():
        with st.expander(category.replace("_", " ").title()):
            st.write(content)

st.title("🤖 AI Customer Support Automation")
st.write("An implementation of automated AI sorting, knowledge look-up, and ticketing systems.")

tab1, tab2 = st.tabs(["💬 Customer Chat Portal", "📋 Agent Ticket Dashboard"])

with tab1:
    st.subheader("How can we assist you today?")
    
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if user_query := st.chat_input("Type your question or request here..."):
        st.session_state.messages.append({"role": "user", "content": user_query})
        with st.chat_message("user"):
            st.markdown(user_query)

        try:
            agent = SupportAgent(api_key=api_key_input)
            
            with st.spinner("Analyzing request..."):
                agent_output = agent.process_message(user_query, st.session_state.messages[:-1])
                
            response_text = agent_output.get("response", "No response parsed.")
            action = agent_output.get("action", "REPLY")
            
            if agent_output.get("ticket_needed") or action in ["CREATE_TICKET", "ESCALATE"]:
                summary = agent_output.get("ticket_summary") or user_query
                priority = agent_output.get("ticket_priority") or "Medium"
                
                new_ticket = TicketManager.create_ticket(
                    customer_name="Anonymous Guest User",
                    email="customer@example.com",
                    issue_summary=summary,
                    priority=priority
                )
                st.session_state.tickets.append(new_ticket)
                response_text += f"\n\n*(Ticket {new_ticket['ticket_id']} has been successfully filed and escalated to our human support desk).* "

            st.session_state.messages.append({"role": "assistant", "content": response_text})
            with st.chat_message("assistant"):
                st.markdown(response_text)
        except Exception as e:
            st.error(f"Error handling request: {str(e)}")

with tab2:
    st.subheader("🎫 Human Agent Escalation Queue")
    
    if not st.session_state.tickets:
        st.info("No escalated tickets active in queue.")
    else:
        for ticket in st.session_state.tickets:
            with st.container(border=True):
                col1, col2, col3 = st.columns([1, 3, 1])
                with col1:
                    st.write(f"**Ticket ID:** `{ticket['ticket_id']}`")
                    st.write(f"**Priority:** {ticket['priority']}")
                with col2:
                    st.write(f"**Subject:** {ticket['issue_summary']}")
                    st.write(f"**Timestamp:** {ticket['created_at']}")
                with col3:
                    st.write(f"**Status:** {ticket['status']}")
                    if st.button("Resolve Ticket", key=ticket['ticket_id']):
                        st.session_state.tickets.remove(ticket)
                        st.success(f"Ticket {ticket['ticket_id']} marked as resolved.")
                        st.rerun()