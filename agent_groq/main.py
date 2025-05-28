import os
import json
from dotenv import load_dotenv
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Any, Dict, Literal
from groq import Groq

# --- Load environment variables ---
load_dotenv()

app = FastAPI(title="Groq Chat Agent")

# --- Serve the Agent Card ---
@app.get("/.well-known/agent.json")
async def agent_card():
    try:
        with open("../agent_openAi/agent_cards/groq_card.json", encoding="utf-8") as f:
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

    groq_key = os.getenv("GROQ_API_KEY")
    if not groq_key:
        return {
            "jsonrpc": "2.0",
            "id": rpc_req.id,
            "error": {"code": -32001, "message": "Missing GROQ_API_KEY in environment variables"}
        }

    try:
        client = Groq(api_key=groq_key)
        response = client.chat.completions.create(
            model="llama3-70b-8192",  # Or another available Groq model
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": user_query},
            ],
            temperature=0.7,
            top_p=1.0,
        )
        answer_content = response.choices[0].message.content
    except Exception as e:
        return {
            "jsonrpc": "2.0",
            "id": rpc_req.id,
            "error": {"code": -32000, "message": f"Groq inference failed: {str(e)}"}
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
