import streamlit as st
import requests
import uuid
import concurrent.futures
from gsheet_utils import log_agent_click  # ✅ Import logging function

# Agent endpoints
CHATGPT_RPC = "http://localhost:8000/rpc"
DEEPSEEK_RPC = "http://localhost:8001/rpc"
GROQ_RPC = "http://localhost:8002/rpc"
LLAMA_RPC = "http://localhost:8003/rpc"

st.set_page_config(page_title="Multi-Agent QA", layout="wide")
st.title("🤖 Multi-Agent Q&A: ChatGPT vs DeepSeek vs Groq vs LLaMA")

query = st.text_input("🔍 Ask your question:", "")
submit = st.button("Get Answers")
show_debug = st.checkbox("Show raw server responses (for debugging)")

# Ask individual agent
def ask_agent(agent_name, rpc_url, user_query):
    task_id = str(uuid.uuid4())
    payload = {
        "jsonrpc": "2.0",
        "id": task_id,
        "method": "tasks/send",
        "params": {
            "id": task_id,
            "message": {
                "role": "user",
                "parts": [{"type": "text", "text": user_query}]
            },
            "metadata": {}
        }
    }

    try:
        resp = requests.post(rpc_url, json=payload, timeout=20)
        resp.raise_for_status()
        data = resp.json()

        if show_debug:
            st.markdown(f"### 🔍 Debug: {agent_name} raw response")
            st.json(data)

        if "error" in data:
            return None, f"{agent_name} error: {data['error'].get('message', 'Unknown error')}"

        artifacts = data.get("result", {}).get("artifacts", [])
        if not artifacts:
            return None, f"{agent_name} error: No artifacts in response"

        parts = artifacts[0].get("parts", [])
        if not parts:
            return None, f"{agent_name} error: No parts in artifacts"

        text_data = parts[0].get("text", "")
        return (text_data.get("raw", "No raw text found") if isinstance(text_data, dict) else text_data), None

    except requests.exceptions.RequestException as e:
        return None, f"{agent_name} connection error: {str(e)}"
    except Exception as e:
        return None, f"{agent_name} error: {str(e)}"

# Summarize text (first 25 words)
def summarize(text):
    if not text:
        return ""
    words = text.split()
    return " ".join(words[:25]) + ("..." if len(words) > 25 else "")

# Render answer card with logging
def render_answer(col, summary, full_text, error_msg, agent_label):
    with col:
        st.markdown(f"#### 🤖 {agent_label}")
        if error_msg:
            st.error(error_msg)
        else:
            if st.session_state.get(f"{agent_label}_expanded", False):
                st.text_area("Full Answer", full_text, height=200, key=f"{agent_label}_text")
                if st.button(f"Show Less ({agent_label})", key=f"{agent_label}_less"):
                    st.session_state[f"{agent_label}_expanded"] = False
            else:
                st.markdown(f"**Summary:** {summary}")
                if st.button(f"Read Full Answer ({agent_label})", key=f"{agent_label}_more"):
                    st.session_state[f"{agent_label}_expanded"] = True
                    log_agent_click(agent_label)  # ✅ Log the click to Google Sheets

# Main interaction
if submit and query:
    agents = [
        ("ChatGPT", CHATGPT_RPC),
        ("DeepSeek", DEEPSEEK_RPC),
        ("Groq (LLaMA3)", GROQ_RPC),
        ("LLaMA", LLAMA_RPC),
    ]

    answers = {}

    with st.spinner("⏳ Getting answers..."):
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future_to_agent = {
                executor.submit(ask_agent, name, url, query): name
                for name, url in agents
            }
            for future in concurrent.futures.as_completed(future_to_agent):
                agent_name = future_to_agent[future]
                try:
                    answer, error = future.result()
                    answers[agent_name] = (answer, error)
                except Exception as e:
                    answers[agent_name] = (None, f"{agent_name} error: {str(e)}")

    # Save answers to session_state for later access
    st.session_state.full_answers = {
        "ChatGPT": answers["ChatGPT"][0],
        "DeepSeek": answers["DeepSeek"][0],
        "Groq (LLaMA3)": answers["Groq (LLaMA3)"][0],
        "LLaMA": answers["LLaMA"][0],
    }

    st.session_state.agent_errors = {
        "ChatGPT": answers["ChatGPT"][1],
        "DeepSeek": answers["DeepSeek"][1],
        "Groq (LLaMA3)": answers["Groq (LLaMA3)"][1],
        "LLaMA": answers["LLaMA"][1],
    }

# Show responses if available
if "full_answers" in st.session_state:
    col1, col2, col3, col4 = st.columns(4)
    render_answer(
        col1,
        summarize(st.session_state.full_answers["ChatGPT"]),
        st.session_state.full_answers["ChatGPT"],
        st.session_state.agent_errors["ChatGPT"],
        "ChatGPT"
    )
    render_answer(
        col2,
        summarize(st.session_state.full_answers["DeepSeek"]),
        st.session_state.full_answers["DeepSeek"],
        st.session_state.agent_errors["DeepSeek"],
        "DeepSeek"
    )
    render_answer(
        col3,
        summarize(st.session_state.full_answers["Groq (LLaMA3)"]),
        st.session_state.full_answers["Groq (LLaMA3)"],
        st.session_state.agent_errors["Groq (LLaMA3)"],
        "Groq (LLaMA3)"
    )
    render_answer(
        col4,
        summarize(st.session_state.full_answers["LLaMA"]),
        st.session_state.full_answers["LLaMA"],
        st.session_state.agent_errors["LLaMA"],
        "LLaMA"
    )

    if all(val for val in st.session_state.full_answers.values()):
        st.markdown("### 🗳️ Which answer did you prefer?")
        preferred = st.radio(
            "Choose your preferred agent:",
            ("ChatGPT", "DeepSeek", "Groq (LLaMA3)", "LLaMA")
        )
        if st.button("Submit Preference"):
            st.success(f"✅ Thanks! You chose: {preferred}")
