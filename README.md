## Multi-Agent Q&A System

A Streamlit-based web app that compares answers from multiple AI agents (ChatGPT, DeepSeek, Grok, and LLaMA) in real time. Users can view summaries, read full responses, and vote on their preferred agent. Agent preferences are logged to a Google Sheet for analysis.

## Project Structure
```
Multi-Agent-QA/
├── Agent_DeepSeek/
│   ├── AgentCard/
│   │   └── DeepSeekCard.py
│   └── main.py
│
├── Agent_Grok/
│   └── main.py
│
├── Agent_LLaMA/
│   └── main.py
│
├── Agent_OpenAI/
│   ├── AgentCard/
│   │   ├── GrokCard.py
│   │   ├── LamaCard.py
│   │   └── OpenAICard.py
│   └── main.py
│
├── Hosting/
│   ├── app.py              # Streamlit frontend
│   ├── credentials.json    # GCP service account key
│   └── gsheet_utils.py     # Google Sheets logging logic
```
## Working
Ask a question in the Streamlit UI (app.py).

The system sends your query to four agents: ChatGPT, DeepSeek, Grok, and LLaMA.

Each agent returns a response. Summaries are shown on the interface.

Click "Read Full Answer" to view complete responses.

Each click logs an event to Google Sheets using gsheet_utils.py.

Users can vote for their preferred answer to help collect preference analytics.

Getting Started
Prerequisites
Python 3.9+

Google Cloud Project with a Service Account key

Four local or hosted agents running JSON-RPC interfaces

Install Requirements

-pip install -r requirements.txt
-Google Sheets Logging Setup
-Create a Google Sheet named: Agent click logs

Add headers in the first row:

Agent Name | Count
Download your credentials.json from Google Cloud Console with Sheets and Drive API access.

Place it inside the Hosting/ folder.

▶️ Running the App
Ensure each agent is running on the following ports:

Agent	Port
ChatGPT	8000
DeepSeek	8001
Grok	8002
LLaMA	8003

Run the app:

cd Hosting
streamlit run app.py

🧠 Agents Overview
Agent	Uses Card?	Main File Location
ChatGPT	Yes	Agent_OpenAI/AgentCard/
DeepSeek	Yes	Agent_DeepSeek/AgentCard/
Grok	Yes	Agent_Grok/main.py
LLaMA	Yes	Agent_LLaMA/main.py

🗃️ Google Sheets Logging Logic
Logging is handled via gsheet_utils.py. When a user expands an agent's answer:

It opens the Google Sheet.

Increments the click count for the selected agent.

Adds a new row if the agent does not yet exist in the sheet.

📊 Use Case
This system is designed to:

Compare the performance and quality of multiple language models.

Collect human preference data.

Provide a single interface for multi-agent responses.

Enable easy experimentation with different LLM backends.


---

## Why This System is Only Partially A2A

This project currently implements a multi-agent architecture where all agents communicate only with the main orchestrator (the Streamlit app). Agents do not communicate or delegate tasks to each other directly. The following limitations prevent it from being a fully Agent2Agent (A2A) system:

- Centralized orchestration: All communication is routed through the orchestrator, not directly between agents.
- No agent discovery: Agents are hardcoded and do not use dynamic discovery mechanisms such as agent cards (`/.well-known/agent.json`).
- No standardized A2A task schema: The system uses custom or JSON-RPC interfaces, not the A2A protocol’s standardized `/run` endpoint and message format.
- No task delegation or chaining: Agents cannot delegate sub-tasks to other agents or collaborate on multi-step workflows.

## How to Make This System Fully A2A-Compliant

To achieve full A2A compliance, consider the following steps:

1. Implement the A2A protocol’s `/run` endpoint for all agents, using the standardized JSON schema for tasks and responses as described in the [A2A protocol specification](https://google.github.io/A2A/).
2. Publish agent cards for each agent by serving a `/.well-known/agent.json` file that describes the agent’s capabilities, endpoints, and metadata. This enables dynamic discovery by other agents.
3. Enable agent-to-agent communication by allowing agents to send tasks directly to other agents’ `/run` endpoints, not just respond to the orchestrator. This supports true delegation and collaboration.
4. Implement task delegation and chaining so agents can break down complex tasks, delegate sub-tasks to specialist agents, and aggregate responses for the final output.
5. Support multi-turn interactions and status updates, as described in the A2A protocol, to enable more complex workflows and better tracking of task progress.

By following these steps, you can evolve this project from a centralized, orchestrator-driven setup to a fully decentralized, collaborative A2A agent network.

For more details, refer to the [A2A protocol specification](https://google.github.io/A2A/) and related implementation guides.


"# Agent-to-agent" 
