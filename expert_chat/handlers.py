import chainlit as cl
from utils.callbacks import StreamingHandler
import sys

class ChainlitStreamHandler(StreamingHandler):
    """Extends StreamingHandler to stream tokens to Chainlit UI"""
    
    def __init__(self):
        super().__init__()
        self.current_message = None
        self.is_synthesizing = False
        
    async def on_llm_start(self, agent_name: str = None, metadata: dict = None, *args, **kwargs):
        """Display agent activation in sidebar"""
        try:
            # Get agent name from metadata if not directly provided
            agent_name = agent_name or (metadata or {}).get("agent_name")
            
            if agent_name:
                if agent_name == "meta":
                    self.is_synthesizing = True
                    self.current_message = None  # Reset message for synthesis
                    await cl.Message(
                        content="🤖 Synthesizing final response...",
                        author="system",
                        parent_id="sidebar"
                    ).send()
                else:
                    await cl.Message(
                        content=f"🔄 Activating {agent_name} agent",
                        author=agent_name,
                        parent_id="sidebar"
                    ).send()
        except Exception as e:
            print(f"Error in on_llm_start: {str(e)}")
    
    async def on_llm_new_token(self, token: str, **kwargs):
        """Stream tokens to main chat"""
        try:
            # Initialize message if needed
            if self.current_message is None:
                self.current_message = await cl.Message(
                    content="",
                    author="Assistant" if self.is_synthesizing else None
                ).send()
            
            # Stream token and update internal state
            await self.current_message.stream_token(token)
            self.text += token
            
        except Exception as e:
            print(f"Error streaming token: {str(e)}")
        
    async def on_llm_end(self, *args, **kwargs):
        """Clean up after streaming"""
        try:
            if self.is_synthesizing:
                await cl.Message(
                    content="✅ Synthesis complete",
                    author="system",
                    parent_id="sidebar"
                ).send()
                self.is_synthesizing = False
            
            self.current_message = None
            self.text = ""
            
        except Exception as e:
            print(f"Error in on_llm_end: {str(e)}")
