# Multi-Agent Financial Advisor with Front End

![GitHub](https://img.shields.io/github/license/cookieclicker123/Expert-Agent)
![Python](https://img.shields.io/badge/python-3.11%2B-blue)
![LangChain](https://img.shields.io/badge/🦜_LangChain-Latest-green)
![Chainlit](https://img.shields.io/badge/Chainlit-Latest-purple)
![Groq](https://img.shields.io/badge/Groq-Latest-orange)
![Claude](https://img.shields.io/badge/Claude-3.5_Sonnet-blue)

![System Overview](images/front-end.jpg "Multi-Agent System with Front End")

## Table of Contents
- [Overview](#overview)
- [System Architecture](#system-architecture)
- [New Features](#new-features-in-part-2)
- [Model Insights](#model-insights)
- [Testing Insights](#testing-insights)
- [Quick Start](#quick-start-tutorial)
- [Configuration](#model-configuration)
- [Common Issues](#common-issues)
- [Future Directions](#future-directions)

## System Architecture

```mermaid
graph TD
    User[User Query] --> MetaAgent[Meta Agent]
    
    subgraph AgentSelection[Agent Selection & Workflow]
        MetaAgent --> Analysis[Query Analysis]
        Analysis --> Selection[Agent Selection]
        Selection --> Workpad[Workpad]
        Memory[Conversation Memory] --> MetaAgent
    end
    
    subgraph AgentProcessing[Agent Processing]
        Workpad --> PDFAgent[PDF Agent]
        Workpad --> WebAgent[Web Agent]
        Workpad --> FinanceAgent[Finance Agent]
        
        PDFAgent --> FAISS[FAISS Index]
        WebAgent --> Serper[Serper API]
        FinanceAgent --> AlphaVantage[Alpha Vantage API]
        
        FAISS --> AgentResponse1[Agent Response]
        Serper --> AgentResponse2[Agent Response]
        AlphaVantage --> AgentResponse3[Agent Response]
    end
    
    subgraph ResponseSynthesis[Response Synthesis]
        AgentResponse1 --> Workpad
        AgentResponse2 --> Workpad
        AgentResponse3 --> Workpad
        
        Workpad --> SynthesisCheck{Sufficient Info?}
        SynthesisCheck -->|Yes| FinalSynthesis[Final Synthesis]
        SynthesisCheck -->|No| MetaAgent
        
        FinalSynthesis --> Response[Final Response]
        Memory --> FinalSynthesis
    end
    
    Response --> User
    Response --> Memory
    
    style SynthesisCheck fill:#ff9900,stroke:#333,stroke-width:2px
    style Workpad fill:#90EE90,stroke:#333,stroke-width:2px
    style MetaAgent fill:#ADD8E6,stroke:#333,stroke-width:2px
    style Memory fill:#FFB6C1,stroke:#333,stroke-width:2px
```


The system follows an enhanced workflow with memory persistence:

1. **Query Processing with Context**
   - User query is received by MetaAgent
   - Conversation memory provides context from previous interactions
   - MetaAgent analyzes query and selects appropriate agents
   - Selected agents are registered in Workpad

2. **Asynchronous Agent Execution**
   - Each selected agent processes the query using specialized tools:
     - PDF Agent: FAISS vector store for document analysis
     - Web Agent: Serper API with citation requirements
     - Finance Agent: Alpha Vantage API with ticker validation
   - Agent responses are asynchronously written to Workpad

3. **Context-Aware Synthesis Loop**
   - MetaAgent checks if gathered information is sufficient
   - Previous conversation context influences synthesis
   - If YES: Proceeds to final synthesis with memory integration
   - If NO: Returns to agent selection for additional information
   - Process repeats until sufficient information is gathered

4. **Enhanced Response Generation**
   - Final synthesis combines all agent responses with conversation history
   - Response is stored in memory for future context
   - Coherent response delivered through Chainlit UI

## Overview

This repository is part of a multi-phase project aimed at building a sophisticated, production-ready financial advisory system using multi-agent architecture. This phase introduces a robust front-end interface and several enhancements over the initial setup. For the basic setup instructions without the front end, please refer to [Part 1 of this project](https://github.com/cookieclicker123/Expert-Agent).

## New Features in Part 2

- **Conversation Memory**: Enables context retention across interactions.
- **API Enablement**: Supports local, Groq, and Anthropic APIs by simply changing configurations in `main.py`.
- **Chainlit Front End**: A user-friendly interface perfect for live demonstrations.
- **Improved Web Agent**: Now includes detailed citation requirements.
- **Enhanced Meta Prompt**: Better discernment of requirements and agent needs.
- **Refined Finance Prompt**: Only invoked by explicit ticker symbols, avoiding false triggers.
- **Asynchronous Processing Framework**: Demonstrates increased architectural sophistication.
- **PDF Tool**: Now functional, allowing easy addition of multiple files to improve invocation likelihood.

This phase represents a significant system revamp, addressing the lack of software formality and sophistication in Part 1. It introduces more robust agents with real-time information access, conversation persistence, and a demonstration of building a front end asynchronously.

## Model Insights

### Anthropic with Claude 3.5 Sonnet
- Demonstrates superior agent orchestration and synthesis capabilities
- Ideal for complex agentic tasks
- Robust error handling and rich technical information processing

### Local LLaMA 3.2 3B Model
- Struggles with complex synthesis tasks
- Better suited for smaller jobs like domain expertise and information retrieval
- Shows limitations in agent orchestration capabilities

### Groq with Mixtral 8x7B (~50B parameters)
- Significant improvements in consistency and structure
- Known tokenization issues with date processing
- Efficient for business optimization with proper engineering
- Cost-effective alternative for less demanding computations

### Claude
- First-in-class agent orchestration
- Impeccable planning and answer generation
- Robust to small errors and inconsistencies
- Ideal for advanced agentic tasks and future developments

## Testing Insights

Through robust testing, we've identified that:
- Micro models (3B parameters) struggle with knowledge synthesis
- Mid-size models (~50B parameters) show significant improvement but have specific limitations
- Large models (hundreds of billions of parameters) remain advantageous for complex business optimization
- Test-driven development is crucial for understanding model capabilities

## Future Directions

As we move into Part 3 (Knowledge Base) and Part 4 (Embodied Agents with Computer Vision), these insights will guide us in:
- Developing knowledge graph implementations
- Creating computer vision-based automation
- Optimizing model selection for specific tasks
- Building more sophisticated agent architectures

## Quick Start Tutorial

1. **Setup**: Follow the setup instructions in [Part 1](https://github.com/cookieclicker123/Expert-Agent)

2. **Run the Front End**:
```bash
python expert_chat/main.py
```

3. **Model Configuration**: 
- Models are defined in `utils/config.py`
- Add environment variable for Anthropic API
- Default model in `expert_chat/main.py` is Anthropic
- Change provider and model_name variables for different models

## Environment Setup

```bash
# Add to your .env file
ANTHROPIC_API_KEY=your_key_here
```

## Model Selection

In `expert_chat/main.py`:
```python
# Change these variables for different models
provider = "anthropic"  # Options: "local", "groq", "anthropic"
model_name = "claude-3-sonnet-20240229"
```