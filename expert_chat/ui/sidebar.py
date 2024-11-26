import chainlit as cl
from typing import Dict, Optional
from .components import UIComponents, ProcessStep

class Sidebar:
    def __init__(self):
        self.ui = UIComponents()
        self.active_agent = None
        self.agent_steps: Dict[str, ProcessStep] = {}
        
    async def initialize(self, agents: Dict[str, str]) -> None:
        """Initialize sidebar with system status and available agents"""
        # Create header
        await cl.Message(
            content="### System Status",
            parent_id="sidebar"
        ).send()
        
        # Initialize agent steps
        for agent_name in agents:
            self.agent_steps[agent_name] = ProcessStep(
                name=agent_name,
                status="pending",
                icon="⚪️"
            )
        
        # Show initial state
        await self.ui.update_sidebar_agents(agents)
        await self.ui.show_process_steps(list(self.agent_steps.values()))
        
    async def update_agent_status(self, agent_name: str, status: str, details: Optional[str] = None) -> None:
        """Update agent status and refresh sidebar"""
        if agent_name in self.agent_steps:
            # Update step status
            self.agent_steps[agent_name].status = status
            self.agent_steps[agent_name].details = details
            
            # Update active agent
            self.active_agent = agent_name if status == "running" else None
            
            # Refresh UI
            await self.ui.show_process_steps(list(self.agent_steps.values()))
            await self.ui.update_sidebar_agents(
                cl.user_session.get("agents", {}),
                self.active_agent
            )
