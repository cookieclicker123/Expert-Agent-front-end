from agents.meta_agent import MetaAgent
from agents.pdf_agent import PDFAgent
from agents.finance_agent import FinanceAgent
from agents.web_agent import WebAgent
import json
from utils.config import Config
from utils.callbacks import StreamingHandler

class ExpertSystem:
    def __init__(self, callbacks=None):
        print("Loading Expert System...")
        # Initialize streaming handler if not provided
        self.streaming_handler = callbacks[0] if callbacks else StreamingHandler()
        
        # Initialize meta agent with streaming
        self.meta_agent = MetaAgent(callbacks=[self.streaming_handler])
        
        # Initialize and register available agents
        self._initialize_agents()
        
    def _initialize_agents(self):
        """Initialize and register all available agents"""
        print("Initializing PDF agent...")
        pdf_agent = PDFAgent(callbacks=[self.streaming_handler])
        print("Initializing Finance agent...")
        finance_agent = FinanceAgent(callbacks=[self.streaming_handler])
        print("Initializing Web agent...")
        web_agent = WebAgent(callbacks=[self.streaming_handler])
        
        # Register all agents
        self.meta_agent.registry.register("pdf", pdf_agent)
        self.meta_agent.registry.register("finance", finance_agent)
        self.meta_agent.registry.register("web", web_agent)
        
    def process_query(self, query: str) -> str:
        """Process a query through the meta agent"""
        try:
            print("\nProcessing query...\n")
            response = self.meta_agent.process(query)
            print("\n")
            return ""  # Return empty as streaming handles output
        except Exception as e:
            error_msg = str(e)
            print(f"Error in process_query: {error_msg}")
            return self._format_error(error_msg)
            
    def _format_error(self, error_msg: str) -> str:
        """Format error messages"""
        return json.dumps({
            "error": {
                "message": error_msg,
                "type": "system_error"
            }
        }, indent=2) 