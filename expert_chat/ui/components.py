import chainlit as cl
from typing import Dict, List, Optional
from dataclasses import dataclass

@dataclass
class ProcessStep:
    name: str
    status: str  # "pending", "running", "complete", "error"
    icon: str
    details: Optional[str] = None

class UIComponents:
    """Manages UI components and their states"""
    
    @staticmethod
    async def create_expandable_section(
        title: str,
        content: str,
        expanded: bool = False,
        icon: str = "📊"
    ) -> None:
        """Creates an expandable section with title and content"""
        elements = []
        
        # Create header element
        header = cl.Message(
            content=f"{icon} **{title}**"
        )
        elements.append(header)
        
        # Create content element if not expanded
        if not expanded:
            content_msg = cl.Message(
                content=content,
                author="system"  # Using author to differentiate content
            )
            elements.append(content_msg)
        
        # Send all elements
        for element in elements:
            await element.send()

    @staticmethod
    async def show_process_steps(steps: List[ProcessStep]) -> None:
        """Shows process steps with status indicators"""
        steps_content = ""
        for step in steps:
            icon = {
                "pending": "⏳",
                "running": "🔄",
                "complete": "✅",
                "error": "❌"
            }.get(step.status, "⏺️")
            
            details = f"\n  *{step.details}*" if step.details else ""
            steps_content += f"{icon} **{step.name}**{details}\n"
        
        await cl.Message(
            content=steps_content,
            parent_id="process_steps"
        ).send()

    @staticmethod
    async def update_sidebar_agents(agents: Dict[str, str], active_agent: Optional[str] = None) -> None:
        """Updates sidebar with agent status"""
        content = "### Active Agents\n\n"
        for name, description in agents.items():
            icon = "🔵" if name == active_agent else "⚪️"
            content += f"{icon} **{name}**\n  *{description}*\n\n"
        
        await cl.Message(
            content=content,
            parent_id="sidebar"
        ).send()

    @staticmethod
    async def show_synthesis_header() -> None:
        """Shows synthesis phase header"""
        await cl.Message(
            content="🤖 **Synthesizing Response**\n\n---",
            parent_id="synthesis"
        ).send() 