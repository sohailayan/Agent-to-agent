import os
import json
from dotenv import load_dotenv
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Any, Dict, Literal
from azure.ai.inference import ChatCompletionsClient
from azure.ai.inference.models import SystemMessage, UserMessage
from azure.core.credentials import AzureKeyCredential

# --- Load environment variables from .env ---
load_dotenv()

app = FastAPI(title="LLaMA Answer Agent")

# --- Serve the Agent Card ---
@app.get("/.well-known/agent.json")
async def agent_card():
    try:
        with open("../agent_openAI/agent_cards/llama_card.json", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        return {"error": f"Failed to load agent card: {str(e)}"}

# --- JSON-RPC 2.0 request model ---
class JsonRpcRequest(BaseModel):
    jsonrpc: Literal["2.0"]
    id: str
    method: str
    params: Dict[str, Any]

# --- RPC endpoint for handling user queries ---
@app.post("/rpc")
async def rpc_handler(rpc_req: JsonRpcRequest):
    if rpc_req.method != "tasks/send":
        return {
            "jsonrpc": "2.0",
            "id": rpc_req.id,
            "error": {"code": -32601, "message": "Method not found"}
        }

    # Extract user query from the request
    message = rpc_req.params.get("message", {})
    user_query = next(
        (part.get("text", "") for part in message.get("parts", []) if part.get("type") == "text"),
        ""
    )

    if not user_query:
        return {
            "jsonrpc": "2.0",
            "id": rpc_req.id,
            "error": {"code": -32602, "message": "No valid text part found in message"}
        }

    # GitHub Inference Setup for LLaMA model
    endpoint = "https://models.github.ai/inference"
    model = "meta/Llama-4-Scout-17B-16E-Instruct"
    token = ""

    if not token:
        return {
            "jsonrpc": "2.0",
            "id": rpc_req.id,
            "error": {"code": -32001, "message": "Missing GitHub token in environment"}
        }

    # Call the LLaMA model using GitHub inference API
    try:
        client = ChatCompletionsClient(
            endpoint=endpoint,
            credential=AzureKeyCredential(token),
        )
        response = client.complete(
            messages=[
                SystemMessage("You are a helpful, honest assistant."),
                UserMessage(user_query),
            ],
            temperature=0.8,
            top_p=0.1,
            max_tokens=2048,
            model=model
        )
        print("hello",response)
        answer_content = response.choices[0].message.content
    except Exception as e:
        return {
            "jsonrpc": "2.0",
            "id": rpc_req.id,
            "error": {"code": -32000, "message": f"LLM call failed: {str(e)}"}
        }

    # Format and return the response
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
