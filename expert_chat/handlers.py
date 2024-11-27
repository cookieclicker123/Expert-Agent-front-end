import chainlit as cl
from utils.callbacks import StreamingHandler
import sys

class ChainlitStreamHandler(StreamingHandler):
    def __init__(self):
        super().__init__()
        self.current_message = None
        self.is_synthesizing = False
        self.text = ""
        self.current_step = None
        
    async def on_llm_start(self, *args, **kwargs):
        try:
            metadata = kwargs.get('metadata', {})
            agent_name = metadata.get('agent_name')
            
            if agent_name:
                if agent_name == "meta":
                    self.is_synthesizing = True
                    self.current_message = None
                    await cl.Message(
                        content="🤖 Synthesizing final response...",
                        author="system"
                    ).send()
                else:
                    self.current_step = await cl.Step(
                        name=f"{agent_name.title()} Agent",
                        show_input=False
                    ).__aenter__()
        except Exception as e:
            print(f"Error in on_llm_start: {str(e)}")
    
    async def on_llm_new_token(self, token: str, **kwargs):
        try:
            if self.is_synthesizing:
                if self.current_message is None:
                    self.current_message = await cl.Message(
                        content="",
                        author="Assistant"
                    ).send()
                await self.current_message.stream_token(token)
            else:
                self.text += token
                if self.current_step:
                    self.current_step.output = self.text
        except Exception as e:
            print(f"Error streaming token: {str(e)}")
        
    async def on_llm_end(self, *args, **kwargs):
        try:
            if self.is_synthesizing:
                await cl.Message(
                    content="✅ Synthesis complete",
                    author="system",
                    parent_id="sidebar"
                ).send()
                self.is_synthesizing = False
            
            if self.current_step:
                await self.current_step.__aexit__(None, None, None)
                self.current_step = None
            
            self.text = ""
            
        except Exception as e:
            print(f"Error in on_llm_end: {str(e)}")
