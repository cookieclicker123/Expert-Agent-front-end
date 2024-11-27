from dataclasses import dataclass
from typing import List

@dataclass
class AnalysisElement:
    query_type: str
    complexity: str
    workflow: List[str]
    reason: str

@dataclass
class SynthesisElement:
    title: str
    sections: List[dict]  # {title: str, content: str, collapsed: bool}
    
class ContentFormatter:
    """Formats content for UI display"""
    
    @staticmethod
    def format_analysis(analysis: AnalysisElement) -> str:
        return f"""
**Query Analysis**
Type: `{analysis.query_type}`
Complexity: `{analysis.complexity}`

**Workflow**
{chr(10).join(f"• {step}" for step in analysis.workflow)}

**Reasoning**
{analysis.reason}
"""

    @staticmethod
    def format_synthesis(synthesis: SynthesisElement) -> str:
        formatted = f"# {synthesis.title}\n\n"
        for section in synthesis.sections:
            formatted += f"### {section['title']}\n{section['content']}\n\n"
        return formatted