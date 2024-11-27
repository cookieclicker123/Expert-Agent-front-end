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
    async def show_workflow_analysis(
        query_type: str,
        complexity: str,
        workflow: List[dict],
        reason: str
    ) -> None:
        """Display workflow analysis with enhanced formatting"""
        # Create the workflow text with better formatting
        workflow_text = f"""# 🔍 Workflow Analysis

## Query Details
🎯 Type: `{query_type}`
📊 Complexity: `{complexity}`

## 🔄 Planned Steps
{chr(10).join(f'• 🤖 {step["agent"].title()} Agent → {step["reason"]}' for step in workflow)}

## 💡 Strategy
{reason}"""
        
        # Send as a message with code block
        await cl.Message(
            content=f"```python\n{workflow_text}\n```",
            author="system"
        ).send()

    @staticmethod
    async def create_task_list(tasks: List[dict]) -> None:
        """Create task list with enhanced headers"""
        await cl.Message(
            content="# 📋 Task Pipeline",
            author="system"
        ).send()
        
        task_elements = []
        for task in tasks:
            element = cl.Task(
                title=f"🤖 {task['agent']} Agent",
                status=task["status"],
                description=task["description"]
            )
            task_elements.append(element)
            
        await cl.TaskList(elements=task_elements).send()

    @staticmethod
    async def show_source_evaluation(content: str) -> None:
        """Display source evaluation with enhanced header"""
        await cl.Message(
            content=f"""# 📚 Source Evaluation & Analysis
            
{content}""",
            author="system"
        ).send()

    @staticmethod
    async def show_synthesis_header() -> None:
        """Shows enhanced synthesis phase header"""
        await cl.Message(
            content="""# 🧠 Final Synthesis & Strategy
            
Synthesizing comprehensive analysis and recommendations...""",
            author="system"
        ).send()

    @staticmethod
    async def update_chat_history(messages: List[dict]) -> None:
        """Update chat history with better formatting"""
        content = "# 📝 Chat History\n\n"
        for msg in messages:
            role_icon = "👤" if msg['role'] == "user" else "🤖"
            content += f"**{role_icon} {msg['role'].title()}**: {msg['content'][:50]}...\n\n"
        
        await cl.Message(
            content=content,
            author="system"
        ).send() 