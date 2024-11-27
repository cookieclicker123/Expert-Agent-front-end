import sys
from pathlib import Path
import argparse

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

# Add model display mapping
model_display = {
    "anthropic": "Anthropic (Claude 3.5 Sonnet)",
    "groq": "Groq Mixtral 8×7B",
    "ollama": "Local (Ollama LLaMA 3.2)"
}

def select_model():
    """Prompt user to select model provider"""
    print("\n🤖 Available Models:")
    print("1. Anthropic (Claude 3.5 Sonnet)")
    print("2. Groq (Mixtral 8x7B)")
    print("3. Local (Ollama LLaMA 3.2)")
    
    while True:
        choice = input("\nSelect model (1-3): ").strip()
        if choice == "1":
            return "anthropic", Config.model_config.anthropic_model_name
        elif choice == "2":
            return "groq", Config.model_config.groq_model_name
        elif choice == "3":
            return "ollama", Config.model_config.model_name
        else:
            print("Invalid choice. Please select 1-3.")

def init_system():
    """Initialize the expert system with selected model configuration"""
    provider, model_name = select_model()
    
    Config.model_config.provider = provider
    Config.model_config.model_name = model_name
    
    streaming_handler = ChainlitStreamHandler()
    system = ExpertSystem(callbacks=[streaming_handler])
    
    return system, provider

@cl.on_chat_start
async def start():
    """Initialize chat session"""
    # Initialize components with selected model
    system, provider = init_system()
    ui = UIComponents()
    
    # Create welcome message with selected model (using global model_display)
    await cl.Message(
        content=f"# 🚀 Financial Expert System\nPowered by {model_display[provider]}",
        author="system"
    ).send()
    
    # Show initial workflow template
    await cl.Message(
        content="""```python
Type: ANALYSIS
Complexity: ADVANCED

Planned Steps:
• Finance Agent → To provide current market data and analysis
• Web Agent → To gather latest market news and trends
• Pdf Agent → To provide documentation and context

Strategy:
This query requires comprehensive market analysis combining real-time data with contextual information.
```""",
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
    
    try:
        # Create Query Analysis step (for initial plan)
        async with cl.Step(name="Query Analysis", show_input=True) as step:
            step.input = message.content
            # Process query to get initial plan
            workflow = await system.analyze_workflow(message.content)
            step.output = workflow
            
        # Process through expert system (agents will create their own steps at root level)
        response = await system.process_query(message.content)
                
    except Exception as e:
        await cl.Message(
            content=f"Error: {str(e)}",
            author="system"
        ).send()
