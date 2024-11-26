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
from expert_chat.ui.sidebar import Sidebar
from expert_chat.ui.components import UIComponents
from expert_chat.ui.elements import AnalysisElement, SynthesisElement, ContentFormatter

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
    # Initialize components
    system = init_system()
    ui = UIComponents()
    sidebar = Sidebar()
    
    # Welcome message with enhanced formatting
    await ui.create_expandable_section(
        title="Financial Expert System",
        content=f"""Using {Config.model_config.groq_display_name} for analysis
        
**Capabilities:**
• Market Analysis and Research
• Options Trading Strategies
• Portfolio Management
• Real-time Data Analysis

Type your query to begin!""",
        expanded=True,
        icon="🚀"
    )
    
    # Initialize sidebar with agents
    agents = {
        "Finance": "Real-time market data and analysis",
        "PDF": "Educational resources and documentation",
        "Web": "Current market research and news",
        "Meta": "Orchestrates other agents for comprehensive answers"
    }
    await sidebar.initialize(agents)
    
    # Store in session for access
    cl.user_session.set("system", system)
    cl.user_session.set("ui", ui)
    cl.user_session.set("sidebar", sidebar)
    cl.user_session.set("agents", agents)

@cl.on_message
async def main(message: cl.Message):
    """Process messages through expert system"""
    system = cl.user_session.get("system")
    ui = cl.user_session.get("ui")
    sidebar = cl.user_session.get("sidebar")
    
    try:
        # Show processing status
        await ui.create_expandable_section(
            title="Processing Query",
            content=f"```{message.content}```",
            expanded=False,
            icon="⚡"
        )
        
        # Process through expert system
        response = await system.process_query(message.content)
        
        # Only send additional message if there's an error
        if response:
            await ui.create_expandable_section(
                title="Error",
                content=response,
                expanded=True,
                icon="❌"
            )
            
    except Exception as e:
        await ui.create_expandable_section(
            title="System Error",
            content=f"```\n{str(e)}\n```",
            expanded=True,
            icon="⚠️"
        )
