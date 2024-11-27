from agents.meta_agent import MetaAgent
from agents.pdf_agent import PDFAgent
from agents.finance_agent import FinanceAgent
from agents.web_agent import WebAgent
import json
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
        
    async def process_query(self, query: str) -> str:
        """Process a query through the meta agent"""
        try:
            print("\nProcessing query...\n")
            response = await self.meta_agent.process(query)
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
        
    async def analyze_workflow(self, query: str) -> str:
        """Analyze query and return formatted workflow plan"""
        try:
            # Get workflow from meta agent
            workflow = self.meta_agent._analyze_workflow(query)
            
            # Format for display
            workflow_str = """Type: ANALYSIS
Complexity: ADVANCED

Planned Steps:"""
            
            for step in workflow:
                workflow_str += f"\n• {step['agent'].title()} Agent → {step['reason']}"
            
            workflow_str += "\n\nStrategy:\nThis query requires comprehensive analysis using specialized agents."
            
            return workflow_str
            
        except Exception as e:
            print(f"Error in analyze_workflow: {str(e)}")
            return f"Error analyzing workflow: {str(e)}" 