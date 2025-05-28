Multi-Agent Q&A System
A Streamlit-based web app that compares answers from multiple AI agents (ChatGPT, DeepSeek, Grok, and LLaMA) in real time. Users can view summaries, read full responses, and vote on their preferred agent. Agent preferences are logged to a Google Sheet for analysis.

📂 Project Structure
bash
Copy
Edit
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
⚙️ How It Works
Ask a question in the Streamlit UI (app.py).

The system sends your query to 4 agents (ChatGPT, DeepSeek, Grok, and LLaMA).

Each agent returns a response, and a summary of each answer is shown.

Click "Read Full Answer" to expand and see the complete response.

When you expand any agent's response, it logs your click to a Google Sheet via gsheet_utils.py.

At the end, you can vote for your preferred answer, helping us collect preference analytics.

🚀 Getting Started
Prerequisites
Python 3.9+

Google Cloud Project with a Service Account key

Four local or hosted agents running JSON-RPC interfaces

Install Requirements
bash
Copy
Edit
pip install -r requirements.txt
Setup Google Sheets Logging
Create a Google Sheet named: Agent click logs

Add headers in the first row:

mathematica
Copy
Edit
Agent Name | Count
Download your credentials.json from Google Cloud Console (Service Account with Sheets and Drive API enabled).

Place it inside the Hosting/ folder.

▶️ Running the App
Ensure each agent is running at the respective ports:

Agent	Port
ChatGPT	8000
DeepSeek	8001
Grok	8002
LLaMA	8003

Then run:

bash
Copy
Edit
cd Hosting
streamlit run app.py
🧠 Agents Overview
Agent	Uses Card?	Main File Location
ChatGPT	✅	Agent_OpenAI/AgentCard/
DeepSeek	✅	Agent_DeepSeek/AgentCard/
Grok	❌	Agent_Grok/main.py
LLaMA	❌	Agent_LLaMA/main.py

🗃️ Google Sheets Logging Logic
The logging is handled in gsheet_utils.py. When a user expands an agent's answer, it:

Opens the Google Sheet.

Increments the click count for that agent.

Adds a new row if the agent isn’t already listed.

📊 Use Case
This system helps compare the performance and quality of different language models by:

Collecting human preference data.

Offering a single interface for multi-agent responses.

Allowing easy experimentation across multiple LLM backends.

🔐 Security Note
Ensure credentials.json is never exposed publicly. Add it to your .gitignore.

📌 TODO (Optional Enhancements)
Add support for asynchronous WebSocket-based agents.

Store full answer logs in Google Sheets.

Add feedback comments for why users preferred a response.

Visualize preference analytics using Streamlit or Google Sheets Charts.

👨‍💻 Author
Built with ❤️ for evaluating and improving agent performance across LLMs.

Certainly! Here’s a clear, markdown-friendly section you can copy directly into your GitHub README to explain why your system is only partially A2A and how to make it fully A2A-compliant:

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

---
Answer from Perplexity: pplx.ai/share

"# Agent-to-agent" 
