import chainlit as cl
from typing import Dict

# Store message elements by agent
agent_messages = {}

async def update_agent_status(agent_name: str, status: str):
    """Update agent status in sidebar"""
    icon = "🔄" if status == "active" else "✅"
    
    if agent_name not in agent_messages:
        # Create new message for this agent
        agent_messages[agent_name] = await cl.Message(
            content=f"{icon} {agent_name.capitalize()}: {status}",
            author=agent_name,
            parent_id="sidebar"
        ).send()
    else:
        # Update existing message
        await agent_messages[agent_name].update(
            content=f"{icon} {agent_name.capitalize()}: {status}"
        )
        
        # Clear message reference if complete
        if status == "complete":
            del agent_messages[agent_name]

async def show_agent_list(agents: Dict[str, str]):
    """Display available agents in sidebar"""
    agent_list = "\n".join([f"- {name}: {purpose}" for name, purpose in agents.items()])
    await cl.Message(
        content=f"Available Agents:\n{agent_list}",
        author="system",
        parent_id="sidebar"
    ).send()
