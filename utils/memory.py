from langchain.memory import ConversationBufferMemory
from typing import Dict, Any

class AgentMemoryManager:
    def __init__(self):
        self.memories = {
            "meta": ConversationBufferMemory(
                return_messages=True,
                memory_key="chat_history",
                output_key="output"
            ),
            "web": ConversationBufferMemory(
                return_messages=True,
                memory_key="web_history",
                output_key="output"
            ),
            "finance": ConversationBufferMemory(
                return_messages=True,
                memory_key="finance_history",
                output_key="output"
            ),
            "pdf": ConversationBufferMemory(
                return_messages=True,
                memory_key="pdf_history",
                output_key="output"
            )
        }
        
    def get_memory(self, agent_name: str) -> Dict[str, Any]:
        """Get memory for specific agent"""
        memory = self.memories.get(agent_name)
        if memory:
            return memory.load_memory_variables({})
        return {}
        
    def save_context(self, agent_name: str, query: str, response: str):
        """Save context for specific agent"""
        try:
            memory = self.memories.get(agent_name)
            if memory:
                print(f"DEBUG: Saving memory for {agent_name}")
                print(f"DEBUG: Input: {query[:50]}...")
                print(f"DEBUG: Output: {response[:50]}...")
                memory.save_context(
                    {"input": query},
                    {"output": response}
                )
            else:
                print(f"Warning: No memory found for agent {agent_name}")
        except Exception as e:
            print(f"Error saving memory for {agent_name}: {str(e)}")
            
    def clear_all(self):
        """Clear all agent memories"""
        for memory in self.memories.values():
            memory.clear() 