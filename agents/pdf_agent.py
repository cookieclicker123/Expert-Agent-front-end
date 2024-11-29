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
            # Get memory context and relevant documents
            pdf_history = self._get_memory_context()
            context = self._get_relevant_context(query)
            
            # Format the prompt with context and history
            prompt = self.prompt.format(
                context=context,
                query=query,
                pdf_history=pdf_history
            )
            
            # Get and save response
            response = self._invoke_llm(prompt)
            self._save_to_memory(query, response)
            
            return response
            
        except Exception as e:
            return f"PDF processing error: {str(e)}"
            
    def _get_relevant_context(self, query: str) -> str:
        """Get relevant context from PDF documents using RAG"""
        try:
            return self.pdf_tool.query_documents(query)
        except Exception as e:
            raise Exception(f"Error retrieving PDF context: {str(e)}")