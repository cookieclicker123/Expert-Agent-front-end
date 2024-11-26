import chainlit as cl
from typing import Dict, List, Optional
from dataclasses import dataclass

@dataclass
class ProcessStep:
    name: str
    status: str
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
                "ready": "⚪️",
                "running": "🔄",
                "done": "✅",
                "failed": "❌"
            }.get(step.status, "⏺️")
            
            details = f"\n  *{step.details}*" if step.details else ""
            steps_content += f"{icon} **{step.name}**{details}\n"
        
        await cl.Message(
            content=steps_content,
            parent_id="process_steps"
        ).send()

    @staticmethod
    async def update_sidebar_agents(agents: Dict[str, str], active_agent: Optional[str] = None) -> None:
        """Updates sidebar using Chainlit's native elements"""
        sidebar_elements = []
        
        for name, description in agents.items():
            status = "running" if name == active_agent else "ready"
            element = cl.Text(
                name=name,
                content=description,
                display="inline",
                size="small"
            )
            sidebar_elements.append(element)
        
        await cl.Message(elements=sidebar_elements).send()

    @staticmethod
    async def show_synthesis_header() -> None:
        """Shows synthesis phase header"""
        await cl.Message(
            content="🤖 **Synthesizing Response**\n\n---",
            parent_id="synthesis"
        ).send()

    @staticmethod
    async def show_workflow_analysis(
        query_type: str,
        complexity: str,
        workflow: List[dict],
        reason: str
    ) -> None:
        """Display workflow analysis using Chainlit's native elements"""
        # Create the workflow text
        workflow_text = f"""QUERY_TYPE: {query_type}
COMPLEXITY: {complexity}

WORKFLOW:
{chr(10).join(f'• {step["agent"]} -> {step["reason"]}' for step in workflow)}

REASON: {reason}"""
        
        # Send as a message with code block
        await cl.Message(
            content=f"```python\n{workflow_text}\n```",
            author="system"
        ).send()

    @staticmethod
    async def create_task_list(tasks: List[dict]) -> None:
        """Create task list using Chainlit's native TaskList"""
        task_elements = []
        
        for task in tasks:
            element = cl.Task(
                title=task["agent"],
                status=task["status"],
                description=task["description"]
            )
            task_elements.append(element)
            
        await cl.TaskList(elements=task_elements).send()

    @staticmethod
    async def update_chat_history(messages: List[dict]) -> None:
        """Update right sidebar chat history"""
        content = "### Chat History\n\n"
        for msg in messages:
            content += f"**{msg['role']}**: {msg['content'][:50]}...\n\n"
        
        await cl.Message(
            content=content,
            parent_id="chat_history"
        ).send() 