import sys
from pathlib import Path

# Add the parent directory to the path
project_root = str(Path(__file__).parent.parent)
if project_root not in sys.path:
    sys.path.append(project_root)

import chainlit as cl
from typing import Dict
from utils.expert_system import ExpertSystem
from utils.config import Config
from expert_chat.handlers import ChainlitStreamHandler
from expert_chat.ui.sidebar import update_agent_status, show_agent_list

# Initialize system with Groq for Chainlit interface
def init_system():
    """Initialize the expert system with Groq configuration"""
    Config.model_config.provider = "groq"
    Config.model_config.model_name = Config.model_config.groq_model_name
    streaming_handler = ChainlitStreamHandler()
    return ExpertSystem(callbacks=[streaming_handler])

@cl.on_chat_start
async def start():
    """Initialize chat session"""
    # Initialize system
    system = init_system()
    
    # Welcome message with model info
    model_info = f"{Config.model_config.groq_display_name}"
    await cl.Message(
        content=f"Welcome to the Financial Expert System! Using {model_info} for analysis."
    ).send()
    
    # Show available agents in sidebar
    agents = {
        "Finance": "Real-time market data and analysis",
        "PDF": "Educational resources and documentation",
        "Web": "Current market research and news",
        "Meta": "Orchestrates other agents for comprehensive answers"
    }
    await show_agent_list(agents)
    
    # Store system in user session
    cl.user_session.set("system", system)

@cl.on_message
async def main(message: cl.Message):
    """Process messages through expert system"""
    system = cl.user_session.get("system")
    
    try:
        # Process through expert system - streaming handler will manage output
        response = system.process_query(message.content)
        
        # Only send additional message if there's an error
        if response:
            await cl.Message(content=response).send()
            
    except Exception as e:
        await cl.Message(
            content=f"Error processing query: {str(e)}",
            author="system"
        ).send()
