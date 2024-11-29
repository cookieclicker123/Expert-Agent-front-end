from typing import List
import json
from agents.base_agent import BaseAgent
from agents.registry import AgentRegistry
from utils.prompts import META_AGENT_PROMPT, SYNTHESIS_PROMPT
from utils.workpad import Workpad
import chainlit as cl

class MetaAgent(BaseAgent):
    def __init__(self, callbacks=None):
        super().__init__("meta", callbacks)
        self.registry = AgentRegistry()
        self.prompt = META_AGENT_PROMPT
        self.synthesis_prompt = SYNTHESIS_PROMPT
        self.workpad = Workpad()
        
    async def process(self, query: str) -> str:
        """Process query through appropriate agents"""
        try:
            # Get all relevant memories
            memory_manager = cl.user_session.get("memory_manager")
            meta_memory = memory_manager.get_memory("meta")
            
            required_agents = self._analyze_query(query)
            self.workpad.clear()
            
            # Process each agent
            for agent_name in required_agents:
                agent = self.registry.get_agent(agent_name)
                if agent:
                    # Manually trigger start callback
                    if self.callbacks and hasattr(self.callbacks[0], 'on_llm_start'):
                        await self.callbacks[0].on_llm_start(
                            serialized={},
                            prompts=[query],
                            metadata={"agent_name": agent_name}
                        )
                    
                    response = agent.process(query)
                    self.workpad.write(agent_name, response)
                    
                    # Manually trigger end callback
                    if self.callbacks and hasattr(self.callbacks[0], 'on_llm_end'):
                        await self.callbacks[0].on_llm_end()
            
            # Synthesis with manual callbacks
            if self.callbacks and hasattr(self.callbacks[0], 'on_llm_start'):
                await self.callbacks[0].on_llm_start(
                    serialized={},
                    prompts=[query],
                    metadata={"agent_name": "meta"}
                )
            
            # Synthesis with memory
            synthesis_response = self._synthesize_with_memory(
                query,
                meta_memory.get("chat_history", "")
            )
            
            # End callback for synthesis
            if self.callbacks and hasattr(self.callbacks[0], 'on_llm_end'):
                await self.callbacks[0].on_llm_end()
            
            # Save to memory
            memory_manager.save_context("meta", query, synthesis_response)
            return synthesis_response
                
        except Exception as e:
            print(f"Error in workflow: {str(e)}")
            return str(e)

    def _synthesize_from_workpad(self, query: str) -> str:
        """Synthesize final response from workpad content"""
        try:
            content = self.workpad.get_all_content()
            if not content:
                return "No valid information gathered from agents."
                
            # Format content for synthesis
            formatted_content = []
            for agent, response in content.items():
                formatted_content.append(f"""
Information from {agent}:
{response}
""")
            
            # Create synthesis prompt
            synthesis_prompt = self.synthesis_prompt.format(
                query=query,
                agent_responses="\n".join(formatted_content)
            )
            
            # Get synthesis
            return self._invoke_llm(synthesis_prompt)
            
        except Exception as e:
            return f"Synthesis failed: {str(e)}"
        
    def _analyze_workflow(self, query: str) -> List[dict]:
        try:
            meta_memory = self._get_memory_context()
            analysis_prompt = self.prompt.format(
                query=query,
                available_agents=self.registry.list_agents(),
                meta_history=meta_memory
            )
            
            response = self._invoke_llm(analysis_prompt)
            workflow = []
            
            if "WORKFLOW:" in response:
                workflow_text = response.split("WORKFLOW:")[1]
                if "REASON:" in workflow_text:
                    workflow_text = workflow_text.split("REASON:")[0]
                
                lines = [line.strip() for line in workflow_text.split('\n') if line.strip()]
                for line in lines:
                    if "->" in line:
                        parts = line.split("->")
                        agent = parts[0].strip().lstrip('-')
                        reason = parts[1].split("-")[0].strip()
                        if agent in self.registry.list_agents():
                            workflow.append({
                                "agent": agent,
                                "reason": reason
                            })
            
            return workflow or [{"agent": "web", "reason": "fallback"}]
                
        except Exception as e:
            print(f"Workflow analysis failed: {str(e)}")
            return [{"agent": "web", "reason": "error fallback"}]

    def _analyze_query(self, query: str) -> List[str]:
        """Extract required agents from workflow analysis"""
        try:
            workflow = self._analyze_workflow(query)
            required_agents = []
            
            # Extract agents from workflow and validate them
            for step in workflow:
                agent = step.get("agent")
                if agent and agent in self.registry.list_agents():
                    if agent not in required_agents:
                        required_agents.append(agent)
            
            # If no valid agents found, use web as fallback
            if not required_agents:
                print("No valid agents found in workflow, falling back to web")
                return ["web"]
            
            print(f"Selected agents from workflow: {required_agents}")
            return required_agents
            
        except Exception as e:
            print(f"Workflow analysis failed: {str(e)}, falling back to web")
            return ["web"]

    def _synthesize_with_memory(self, query: str, history: str) -> str:
        """Synthesize response with conversation history"""
        content = self.workpad.get_all_content()
        
        synthesis_prompt = self.synthesis_prompt.format(
            query=query,
            agent_responses=json.dumps(content, indent=2),
            chat_history=history
        )
        
        return self._invoke_llm(synthesis_prompt)
