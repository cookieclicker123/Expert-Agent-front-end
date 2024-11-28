from agents.base_agent import BaseAgent
from utils.prompts import PDF_AGENT_PROMPT
from tools.pdf_tools import PDFTool

class PDFAgent(BaseAgent):
    def __init__(self, callbacks=None):
        super().__init__("pdf", callbacks)
        self.prompt = PDF_AGENT_PROMPT
        self.pdf_tool = PDFTool()  # Initialize the PDF tool
        
    def process(self, query: str) -> str:
        """Process PDF-related queries"""
        try:
            # Get relevant context using the PDF tool
            context = self._get_relevant_context(query)
            
            # Format the prompt with the retrieved context
            prompt = self.prompt.format(
                context=context,
                query=query
            )
            return self._invoke_llm(prompt)
        except Exception as e:
            return f"PDF processing error: {str(e)}"
            
    def _get_relevant_context(self, query: str) -> str:
        """Get relevant context from PDF documents using RAG"""
        try:
            return self.pdf_tool.query_documents(query)
        except Exception as e:
            raise Exception(f"Error retrieving PDF context: {str(e)}")