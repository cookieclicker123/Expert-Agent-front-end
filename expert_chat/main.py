import sys
from pathlib import Path
import asyncio
import signal

# Add the parent directory to the path
project_root = str(Path(__file__).parent.parent)
if project_root not in sys.path:
    sys.path.append(project_root)

import chainlit as cl
from utils.expert_system import ExpertSystem
from utils.config import Config
from expert_chat.handlers import ChainlitStreamHandler
from expert_chat.ui.components import UIComponents
from utils.memory import AgentMemoryManager


# Add model display mapping
model_display = {
    "anthropic": "Anthropic (Claude 3.5 Sonnet)",
    "groq": "Groq Mixtral 8×7B",
    "ollama": "Local (Ollama LLaMA 3.2)"
}

def init_system():
    """Initialize the expert system with Groq configuration"""
    # Default to Groq
    provider = "anthropic"
    model_name = Config.model_config.anthropic_model_name
    
    # Set configuration
    Config.model_config.provider = provider
    Config.model_config.model_name = model_name
    
    streaming_handler = ChainlitStreamHandler()
    system = ExpertSystem(callbacks=[streaming_handler])
    
    return system, provider

# Add cleanup handler
async def cleanup(signal_event=None):
    """Cleanup async resources"""
    try:
        system = cl.user_session.get("system")
        memory_manager = cl.user_session.get("memory_manager")
        
        if memory_manager:
            memory_manager.clear_all()
            
        if system and system.streaming_handler:
            # Close any open steps
            if system.streaming_handler.current_step:
                await system.streaming_handler.current_step.__aexit__(None, None, None)
            if system.streaming_handler.workflow_step:
                await system.streaming_handler.workflow_step.__aexit__(None, None, None)
            system.streaming_handler.reset_state()
    except Exception as e:
        print(f"Error during cleanup: {str(e)}")

@cl.on_chat_start
async def start():
    """Initialize chat session"""
    system, provider = init_system()
    ui = UIComponents()
    
    # Initialize memory manager
    memory_manager = AgentMemoryManager()
    
    # Create welcome message with selected model
    await cl.Message(
        content=f"""# 🚀 Financial Expert System
## Powered by {model_display[provider]}

Welcome to your AI-powered financial analysis assistant! This system combines multiple specialized agents to provide comprehensive financial insights and analysis.

### 🤖 Available Capabilities:
• 📈 Real-time Market Analysis
• 📊 Options Trading Strategies
• 🔍 Market Research & News
• 📚 Educational Resources

### 💡 Example Queries:
• "Analyze current market trends for tech stocks"
• "Explain options trading strategies for beginners"
• "What are the most volatile stocks this week?"
• "Help me understand put options with examples"

Let's begin! How can I assist you today?""",
        author="system"
    ).send()
    
    # Show initial workflow template with enhanced formatting
    await cl.Message(
        content="""```python
# 🎯 System Architecture

Type: ADVANCED FINANCIAL ANALYSIS
Complexity: MULTI-AGENT SYSTEM

🔄 Core Agents:
• 📈 Finance Agent → Real-time market data and technical analysis
• 🌐 Web Agent → Latest market news, trends, and sentiment
• 📚 PDF Agent → Documentation, guides, and educational context

🧠 Processing Strategy:
1. Query Analysis & Planning
2. Multi-Agent Information Gathering
3. Cross-Reference & Validation
4. Synthesis & Recommendation

This system combines real-time data, market research, and educational resources 
to provide comprehensive financial insights and actionable recommendations.
```""",
        author="system"
    ).send()
    
    # Store in session
    cl.user_session.set("system", system)
    cl.user_session.set("ui", ui)
    cl.user_session.set("memory_manager", memory_manager)

@cl.on_message
async def main(message: cl.Message):
    """Process messages through expert system"""
    system = cl.user_session.get("system")
    
    try:
        # Reset handler state for new query
        if isinstance(system.streaming_handler, ChainlitStreamHandler):
            system.streaming_handler.reset_state()
            
        # Create Query Analysis step (for initial plan)
        async with cl.Step(name="🔍 Query Analysis", show_input=True) as step:
            step.input = message.content
            # Process query to get initial plan
            workflow = await system.analyze_workflow(message.content)
            step.output = workflow
            
        # Process through expert system (agents will create their own steps at root level)
        await system.process_query(message.content)
                
    except Exception as e:
        await cl.Message(
            content=f"Error: {str(e)}",
            author="system"
        ).send()

@cl.on_stop
async def on_stop():
    """Handle graceful shutdown"""
    await cleanup()

# Register signal handlers
def signal_handler():
    asyncio.create_task(cleanup())
    
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)
