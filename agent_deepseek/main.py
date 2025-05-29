import os
import json
from dotenv import load_dotenv
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Any, Dict, Literal
from azure.ai.inference import ChatCompletionsClient
from azure.ai.inference.models import SystemMessage, UserMessage
from azure.core.credentials import AzureKeyCredential
from starlette.concurrency import run_in_threadpool

# --- Load environment variables ---
load_dotenv()

app = FastAPI(title="DeepSeek QA Agent via Azure Inference")

# --- Serve the Agent Card ---
@app.get("/.well-known/agent.json")
async def agent_card():
    try:
        with open("agent_cards/deepseek_card.json", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        return {"error": f"Failed to load agent card: {str(e)}"}

# --- JSON-RPC 2.0 request model ---
class JsonRpcRequest(BaseModel):
    jsonrpc: Literal["2.0"]
    id: str
    method: str
    params: Dict[str, Any]

# --- Synchronous inference call wrapped in a threadpool ---
def sync_infer(user_query: str, token: str) -> str:
    endpoint = "https://models.github.ai/inference"
    model = "deepseek/DeepSeek-V3-0324"
    token = ""

    client = ChatCompletionsClient(
        endpoint=endpoint,
        credential=AzureKeyCredential(token),
    )

    response = client.complete(
        messages=[
            SystemMessage("You are a helpful assistant."),
            UserMessage(user_query),
        ],
        temperature=1.0,
        top_p=1.0,
        max_tokens=1000,
        model=model
    )
    return response.choices[0].message.content

# --- RPC handler ---
@app.post("/rpc")
async def rpc_handler(rpc_req: JsonRpcRequest):
    if rpc_req.method != "tasks/send":
        return {
            "jsonrpc": "2.0",
            "id": rpc_req.id,
            "error": {"code": -32601, "message": "Method not found"}
        }

    # Extract user query
    message = rpc_req.params.get("message", {})
    user_query = ""
    for part in message.get("parts", []):
        if part.get("type") == "text":
            user_query = part.get("text", "")
            break

    if not user_query:
        return {
            "jsonrpc": "2.0",
            "id": rpc_req.id,
            "error": {"code": -32602, "message": "No valid text part found in message"}
        }

    token = ""
    if not token:
        return {
            "jsonrpc": "2.0",
            "id": rpc_req.id,
            "error": {"code": -32001, "message": "Missing GITHUB_TOKEN in environment variables"}
        }

    try:
        # Run blocking call in a threadpool
        answer_content = await run_in_threadpool(sync_infer, user_query, token)
    except Exception as e:
        return {
            "jsonrpc": "2.0",
            "id": rpc_req.id,
            "error": {"code": -32000, "message": f"Model inference failed: {str(e)}"}
        }

    return {
        "jsonrpc": "2.0",
        "id": rpc_req.id,
        "result": {
            "id": rpc_req.params.get("id"),
            "sessionId": None,
            "status": {"state": "completed"},
            "artifacts": [
                {
                    "parts": [
                        {"type": "text", "text": {"raw": answer_content}}
                    ],
                    "index": 0,
                    "append": False,
                    "lastChunk": True
                }
            ],
            "metadata": {}
        }
    }
