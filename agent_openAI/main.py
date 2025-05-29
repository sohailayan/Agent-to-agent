import json
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Any, Dict, Literal
from azure.ai.inference import ChatCompletionsClient
from azure.ai.inference.models import SystemMessage, UserMessage
from azure.core.credentials import AzureKeyCredential

app = FastAPI(title="GitHub Models QA Agent")

# --- Serve the Agent Card ---
@app.get("/.well-known/agent.json")
async def agent_card():
    try:
        with open("agent_cards/openAI_card.json", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        return {"error": f"Failed to load agent card: {str(e)}"}

# --- JSON-RPC 2.0 request model ---
class JsonRpcRequest(BaseModel):
    jsonrpc: Literal["2.0"]
    id: str
    method: str
    params: Dict[str, Any]

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

    # --- Hardcoded token and model info ---
    endpoint = "https://models.github.ai/inference"
    model = "openai/gpt-4.1"
    token = ""  # 

    try:
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
            model=model
        )
        answer_content = response.choices[0].message.content
    except Exception as e:
        return {
            "jsonrpc": "2.0",
            "id": rpc_req.id,
            "error": {"code": -32000, "message": f"Model inference failed: {str(e)}"}
        }

    # Return result
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
