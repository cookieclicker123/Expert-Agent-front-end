from abc import ABC, abstractmethod
from langchain_ollama import OllamaLLM
from langchain_groq import ChatGroq
from langchain_anthropic import ChatAnthropic
from langchain.schema.messages import HumanMessage
from utils.config import Config
import chainlit as cl

class BaseAgent(ABC):
    def __init__(self, name: str, callbacks=None):
        self.name = name
        self.callbacks = callbacks or []
        self.llm = self._initialize_llm()
        
    def _initialize_llm(self):
        if Config.model_config.provider == "anthropic":
            return ChatAnthropic(
                api_key=Config.model_config.anthropic_api_key,
                model_name=Config.model_config.anthropic_model_name,
                callbacks=self.callbacks,
                streaming=True
            )
        elif Config.model_config.provider == "groq":
            return ChatGroq(
                api_key=Config.model_config.groq_api_key,
                model_name=Config.model_config.groq_model_name,
                callbacks=self.callbacks,
                streaming=True
            )
        elif Config.model_config.provider == "ollama":
            return OllamaLLM(
                model=Config.model_config.model_name,
                callbacks=self.callbacks
            )
        else:
            raise ValueError(f"Unknown provider: {Config.model_config.provider}")
        
    def _invoke_llm(self, prompt: str) -> str:
        """Invoke LLM with consistent callbacks"""
        try:
            if Config.model_config.provider in ["groq", "anthropic"]:
                for callback in self.callbacks:
                    if hasattr(callback, 'on_llm_start'):
                        callback.on_llm_start(metadata={'agent_name': self.name})
                    
                response = self.llm.invoke(
                    [HumanMessage(content=prompt)]
                )
                return response.content
            else:
                return self.llm.invoke(prompt)
            
        except Exception as e:
            print(f"\nError invoking LLM: {str(e)}")
            return f"Error: {str(e)}"
    
    def _get_memory_context(self) -> str:
        """Get memory context for this agent"""
        try:
            memory_manager = cl.user_session.get("memory_manager")
            if memory_manager:
                memory_vars = memory_manager.get_memory(self.name)
                history_key = f"{self.name}_history"
                if self.name == "meta":
                    history_key = "chat_history"
                    
                if history_key in memory_vars:
                    return memory_vars[history_key]
                print(f"Warning: No history found for key {history_key}")
            return ""
        except Exception as e:
            print(f"Error getting memory: {str(e)}")
            return ""
        
    def _save_to_memory(self, query: str, response: str):
        """Save interaction to agent memory"""
        try:
            memory_manager = cl.user_session.get("memory_manager")
            if memory_manager:
                memory_manager.save_context(self.name, query, response)
        except Exception as e:
            print(f"Error saving memory: {str(e)}")
    
    @abstractmethod
    def process(self, query: str) -> str:
        pass