import chainlit as cl
from utils.callbacks import StreamingHandler

class ChainlitStreamHandler(StreamingHandler):
    def reset_state(self):
        """Reset all state variables between queries"""
        self.current_message = None
        self.is_synthesizing = False
        self.text = ""
        self.current_step = None
        self.workflow_step = None
        
    async def on_llm_start(self, *args, **kwargs):
        try:
            metadata = kwargs.get('metadata', {})
            agent_name = metadata.get('agent_name')
            
            if agent_name:
                if agent_name == "meta":
                    # Close any existing steps before synthesis
                    if self.current_step:
                        await self.current_step.__aexit__(None, None, None)
                        self.current_step = None
                    if self.workflow_step:
                        await self.workflow_step.__aexit__(None, None, None)
                        self.workflow_step = None
                        
                    self.is_synthesizing = True
                    await cl.Message(
                        content="# 📊 Synthesizing Final Analysis...",
                        author="system"
                    ).send()
                else:
                    # Create new root-level step for each agent
                    agent_icons = {
                        "web": "🌐",
                        "finance": "📈",
                        "pdf": "📚"
                    }
                    agent_icon = agent_icons.get(agent_name, "🤖")
                    
                    self.current_step = await cl.Step(
                        name=f"{agent_icon} {agent_name.title()} Agent Processing",
                        show_input=False
                    ).__aenter__()
                    
        except Exception as e:
            print(f"Error in on_llm_start: {str(e)}")
            await self.reset_state()
    
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
                if self.current_message:
                    await self.current_message.update()
                
                await cl.Message(
                    content="# ✨ Analysis Complete!",
                    author="system",
                    language="markdown"
                ).send()
                self.is_synthesizing = False
            
            # Always close current step if it exists
            if self.current_step:
                await self.current_step.__aexit__(None, None, None)
                self.current_step = None
            
            self.text = ""
            
        except Exception as e:
            print(f"Error in on_llm_end: {str(e)}")
            await self.reset_state()
