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
    
    # Create welcome message
    await cl.Message(
        content="# 🚀 Financial Expert System\nPowered by Groq",
        author="system"
    ).send()
    
    # Initialize agents with tasks
    agents = {
        "Finance": "Real-time market data and analysis",
        "PDF": "Educational resources and documentation",
        "Web": "Current market research and news",
        "Meta": "Orchestrates other agents for comprehensive answers"
    }
    
    # Create task list
    tasks = []
    for agent, desc in agents.items():
        tasks.append(
            cl.Task(
                title=f"{agent} Agent",
                status="ready",
                description=desc
            )
        )
    
    # Send task list
    await cl.TaskList(elements=tasks).send()
    
    # Store in session
    cl.user_session.set("system", system)
    cl.user_session.set("ui", ui)
    cl.user_session.set("agents", agents)

@cl.on_message
async def main(message: cl.Message):
    """Process messages through expert system"""
    system = cl.user_session.get("system")
    ui = cl.user_session.get("ui")
    
    try:
        # First, show the workflow analysis
        workflow = {
            "query_type": "ANALYSIS",
            "complexity": "ADVANCED",
            "workflow": [
                {"agent": "finance", "reason": "To provide current market data and analysis"},
                {"agent": "web", "reason": "To gather latest market news and trends"},
                {"agent": "pdf", "reason": "To provide documentation and context"}
            ],
            "reason": "This query requires comprehensive market analysis combining real-time data with contextual information."
        }
        
        await ui.show_workflow_analysis(
            workflow["query_type"],
            workflow["complexity"],
            workflow["workflow"],
            workflow["reason"]
        )

        # Then update the task list
        tasks = [
            {"agent": "Meta", "description": "Analyzing query", "status": "running"},
            {"agent": "Finance", "description": "Gathering market data", "status": "ready"},
            {"agent": "Web", "description": "Searching current news", "status": "ready"},
            {"agent": "PDF", "description": "Finding relevant documentation", "status": "ready"}
        ]
        await ui.create_task_list(tasks)
        
        # Process through expert system
        response = await system.process_query(message.content)
        
        # Update chat history
        messages = cl.user_session.get("messages", [])
        messages.append({
            "role": "user",
            "content": message.content
        })
        await ui.update_chat_history(messages)
        
    except Exception as e:
        await cl.Message(
            content=f"Error: {str(e)}",
            author="system"
        ).send()
