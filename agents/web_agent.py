from agents.base_agent import BaseAgent
from tools.web_tools import SerperTool
from utils.prompts import WEB_AGENT_PROMPT

class WebAgent(BaseAgent):
    def __init__(self, callbacks=None):
        super().__init__("web", callbacks)
        self.search_tool = SerperTool()
        self.prompt = WEB_AGENT_PROMPT
        
    def process(self, query: str) -> str:
        """Process web-based queries with search and analysis"""
        try:
            # Get memory context
            web_history = self._get_memory_context()
            search_results = self.search_tool.search(query)
            
            prompt = self.prompt.format(
                search_results=search_results,
                query=query,
                web_history=web_history
            )
            
            response = self._invoke_llm(prompt)
            
            # Save to memory
            self._save_to_memory(query, response)
            
            return response
            
        except Exception as e:
            return f"Error in web agent: {str(e)}" 