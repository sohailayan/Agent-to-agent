import os
import json
from dotenv import load_dotenv
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Any, Dict, Literal
from openai import OpenAI

# Load environment variables
load_dotenv()

app = FastAPI(title="Google Gemma QA Agent via OpenRouter")

# Initialize OpenRouter API
api_key = os.getenv("OPENROUTER_API_KEY")
if not api_key:
    raise ValueError("OPENROUTER_API_KEY not found in .env")

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=api_key,
)

@app.get("/.well-known/agent.json")
async def agent_card():
    """Serve the agent card JSON for Google Gemma."""
    try:
        with open("../agent_openAi/agent_cards/google_gemma_card.json", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        return {"error": f"Failed to load agent card: {str(e)}"}

class JsonRpcRequest(BaseModel):
    jsonrpc: Literal["2.0"]
    id: str
    method: str
    params: Dict[str, Any]

@app.post("/rpc")
async def rpc_handler(rpc_req: JsonRpcRequest):
    """Handle JSON-RPC requests for Google Gemma."""
    if rpc_req.method != "tasks/send":
        return {
            "jsonrpc": "2.0",
            "id": rpc_req.id,
            "error": {"code": -32601, "message": "Method not found"}
        }

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

    try:
        response = client.chat.completions.create(
            model="google/gemma-3-27b-it:free",
            messages=[
                {"role": "user", "content": user_query}
            ]
        )
        answer_text = response.choices[0].message.content

    except Exception as e:
        return {
            "jsonrpc": "2.0",
            "id": rpc_req.id,
            "error": {"code": -32000, "message": f"Inference call failed: {str(e)}"}
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
                        {"type": "text", "text": {"raw": answer_text}}
                    ],
                    "index": 0,
                    "append": False,
                    "lastChunk": True
                }
            ],
            "metadata": {}
        }
    }
