from agents.base_agent import BaseAgent
from tools.finance_tools import VantageFinanceTool
from utils.prompts import FINANCE_AGENT_PROMPT
import json
import re
from typing import List

class FinanceAgent(BaseAgent):
    def __init__(self, callbacks=None):
        super().__init__("finance", callbacks)
        self.finance_tool = VantageFinanceTool()
        self.prompt = FINANCE_AGENT_PROMPT
        
    def process(self, query: str) -> str:
        """Process financial queries with comprehensive analysis"""
        try:
            symbols = self._extract_symbols(query)
            market_data = {symbol: self.finance_tool.get_stock_data(symbol) for symbol in symbols}
            
            prompt = self.prompt.format(
                market_data=json.dumps(market_data, indent=2),
                query=query
            )
            
            return self._invoke_llm(prompt)
            
        except Exception as e:
            return self._format_error_response(str(e))
            
    def _extract_symbols(self, query: str) -> List[str]:
        """Extract stock symbols with strict formatting requirements"""
        symbols = set()
        
        # Primary check: Look for properly formatted symbols in parentheses
        parens_pattern = r'\(([A-Z]{1,4})\)'  # 1-4 capital letters in parentheses
        parens_symbols = set(re.findall(parens_pattern, query))
        if parens_symbols:
            symbols.update(parens_symbols)
            return list(symbols)  # Return early if we find properly formatted symbols
            
        # Secondary check: Look for standalone capital letters that match stock pattern
        # Only if no parenthesized symbols were found
        standalone_pattern = r'\b[A-Z]{1,4}\b'  # 1-4 capital letters as whole word
        standalone_matches = set(re.findall(standalone_pattern, query))
        
        # Only process standalone matches if they look like stock symbols
        # (optional LLM validation could be added here if needed)
        for match in standalone_matches:
            if self._looks_like_stock_symbol(match):
                symbols.add(match)
        
        if not symbols:
            raise Exception(
                "No valid stock symbols found. Please use format (AAPL) or AAPL. "
                "Examples: (MSFT), (GOOGL), AAPL, TSLA"
            )
        
        return list(symbols)
        
    def _looks_like_stock_symbol(self, text: str) -> bool:
        """
        Stricter validation for potential stock symbols
        Helps avoid matching random capital words
        """
        if not (1 <= len(text) <= 4 and text.isalpha() and text.isupper()):
            return False
            
        # Additional checks that might help identify stock symbols
        # Avoid common word patterns
        if text.endswith('S'):  # Plural words
            return False
        if len(text) == 1:  # Single letters are rarely stocks
            return False
        if all(c == text[0] for c in text):  # Repeated letters (e.g., 'AAA')
            return False
            
        return True
        
    def _format_error_response(self, error_msg: str) -> str:
        """Format error messages consistently"""
        return json.dumps({
            "error": {
                "message": error_msg,
                "agent": self.name
            }
        }, indent=2) 