USE_LLM = True

import os
import json
import requests
from pathlib import Path
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

# ================= CONFIG =================

BASE_DIR = Path(__file__).parent
INBOX_PATH = BASE_DIR / "inbox.json"
PROMPTS_PATH = BASE_DIR / "prompts.json"

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL   = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")

# ================= UTILS =================

def category_color(category):
    colors = {
        "Important": "#22c55e",
        "Spam": "#ef4444",
        "Newsletter": "#3b82f6",
        "To-Do": "#facc15"
    }
    return colors.get(category, "#a1a1aa")

def load_json(path):
    if not path.exists():
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def load_inbox():
    return load_json(INBOX_PATH) or []

def load_prompts():
    data = load_json(PROMPTS_PATH)
    if not data:
        data = {
            "categorization_prompt": "Categorize emails into: Important, Newsletter, Spam, To-Do.",
            "action_item_prompt": "Extract action items in JSON list format.",
            "auto_reply_prompt": "Draft a professional reply email."
        }
    return data

def save_prompts(prompts):
    save_json(PROMPTS_PATH, prompts)

# ================= GROQ LLM =================

def call_llm(system_prompt, user_prompt, temperature=0.3):
    if not USE_LLM:
        return "Mock LLM Response"

    if not GROQ_API_KEY:
        st.error("❌ GROQ_API_KEY not set in .env")
        return ""

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": GROQ_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": temperature
    }

    response = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers=headers,
        json=payload,
        timeout=30
    )

    if response.status_code != 200:
        st.error(f"Groq Error: {response.text}")
        return ""

    return response.json()["choices"][0]["message"]["content"].strip()

# ================= LLM TASKS =================

def categorize_email(email_text, prompt):
    return call_llm(
        "You classify emails into categories.",
        f"{prompt}\n\nEMAIL:\n{email_text}",
        0.0
    )

def extract_actions(email_text, prompt):
    raw = call_llm(
        "Extract action items only in valid JSON list.",
        f"{prompt}\n\nEMAIL:\n{email_text}",
        0.0
    )
    try:
        parsed = json.loads(raw)
        return parsed if isinstance(parsed, list) else [parsed]
    except:
        return []

def draft_auto_reply(email_text, prompt, tone):
    raw = call_llm(
        "Draft email reply strictly in JSON with subject and body.",
        f"{prompt}\nTone: {tone}\nEMAIL:\n{email_text}",
        0.3
    )
    try:
        return json.loads(raw)
    except:
        return {"subject": "Re:", "body": raw, "follow_ups": []}

def email_agent_answer(email_text, question, prompts):
    combined_prompt = f"""
EMAIL:
{email_text}

USER QUESTION:
{question}

PROMPTS:
Categorization: {prompts['categorization_prompt']}
Action Extraction: {prompts['action_item_prompt']}
Reply Draft: {prompts['auto_reply_prompt']}
"""
    return call_llm("You are an Email Productivity Agent.", combined_prompt, 0.3)

# ================= SESSION STATE =================

def init_state():
    if "inbox" not in st.session_state:
        st.session_state["inbox"] = load_inbox()
    if "prompts" not in st.session_state:
        st.session_state["prompts"] = load_prompts()
    if "processed" not in st.session_state:
        st.session_state["processed"] = []
    if "drafts" not in st.session_state:
        st.session_state["drafts"] = []

# ================= PIPELINE =================

def run_ingestion_pipeline():
    processed = []

    for email in st.session_state["inbox"]:
        email_text = f"""
From: {email['sender']}
Subject: {email['subject']}
Body:
{email['body']}
"""
        category = categorize_email(email_text, st.session_state["prompts"]["categorization_prompt"])
        actions = extract_actions(email_text, st.session_state["prompts"]["action_item_prompt"])

        processed.append({
            **email,
            "category": category,
            "actions": actions
        })

    st.session_state["processed"] = processed
    st.success("✅ Ingestion pipeline completed")

# ================= UI =================

def main():
    st.set_page_config(layout="wide", page_title="AI Email Agent")

    st.markdown("""
    <style>
    .card {
        background-color:#1e293b;
        padding:15px;
        border-radius:12px;
        margin-bottom:15px;
    }
    .agent-box {
        background:#0f172a;
        padding:15px;
        border-left:5px solid #22c55e;
        border-radius:10px;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("## 📧 AI Email Productivity Agent")
    st.caption("""
Prompt-Driven System implementing:
Email Categorization | Action-item Extraction | Auto-drafting | Chat-based Inbox Interaction
""")

    init_state()

    # ============ 🧠 SIDEBAR: PROMPT BRAIN CONTROL PANEL ============

    st.sidebar.header("🧠 Prompt Brain Control Panel")

    st.sidebar.markdown("""
    This panel controls how your AI agent thinks and behaves.
    You can modify prompts and immediately see the effects.
    """)

    # Toggle LLM or Mock Mode
    global USE_LLM
    USE_LLM = st.sidebar.toggle("Enable Live LLM (Disable for Mock Mode)", value=True)

    # Load prompts
    prompts = st.session_state["prompts"]

    # Editable prompt inputs
    prompts["categorization_prompt"] = st.sidebar.text_area(
        "📌 Categorization Prompt",
        prompts["categorization_prompt"],
        height=100
    )

    prompts["action_item_prompt"] = st.sidebar.text_area(
        "✅ Action Extraction Prompt",
        prompts["action_item_prompt"],
        height=100
    )

    prompts["auto_reply_prompt"] = st.sidebar.text_area(
        "✉ Auto Reply Prompt",
        prompts["auto_reply_prompt"],
        height=100
    )

    # Save button
    if st.sidebar.button("💾 Save Prompt Brain"):
        save_prompts(prompts)
        st.sidebar.success("✅ Prompt Brain Saved")

    # ------------------ LIVE PROMPT TEST ------------------

    st.sidebar.markdown("---")
    st.sidebar.subheader("🧪 Test Your Prompt Brain")

    test_email = st.sidebar.text_area(
        "Test Email Input",
        "From: hr@company.com\nSubject: Performance Review\nBody: Please attend your performance review next Wednesday at 3 PM."
    )

    if st.sidebar.button("🔍 Test Categorization Prompt"):
        result = categorize_email(test_email, prompts["categorization_prompt"])
        st.sidebar.success(f"Predicted Category: {result}")

    if st.sidebar.button("✅ Test Action Extraction Prompt"):
        tasks = extract_actions(test_email, prompts["action_item_prompt"])
        st.sidebar.write("Extracted Tasks:")
        st.sidebar.json(tasks)

    if st.sidebar.button("✉ Test Auto Reply Prompt"):
        draft = draft_auto_reply(test_email, prompts["auto_reply_prompt"], "Professional")
        st.sidebar.write("Generated Draft:")
        st.sidebar.json(draft)

    st.sidebar.markdown("---")
    st.sidebar.info("This sidebar acts as the agent's brain control system. Modify prompts to change AI behavior.")

    # ===== Tabs =====
    tab1, tab2, tab3 = st.tabs(["📥 Inbox", "🤖 Agent", "✍ Drafts"])

    # ========== TAB 1 : INBOX ==========
    with tab1:

        if st.button("🚀 Run Ingestion Pipeline"):
            run_ingestion_pipeline()

        if not st.session_state["processed"]:
            st.info("Run ingestion first.")
            return

        for email in st.session_state["processed"]:

            color = category_color(email["category"])

            st.markdown(f"""
            <div class="card">
                <h4>📩 {email['subject']}</h4>
                <p><b>From:</b> {email['sender']}</p>
                <p><b>Time:</b> {email['timestamp']}</p>
                <span style="padding:6px 12px; background:{color}; border-radius:15px; font-weight:bold;">
                    {email['category']}
                </span>
                <p style="margin-top:10px;">{email['body']}</p>
            </div>
            """, unsafe_allow_html=True)

            if email["actions"]:
                st.markdown("✅ Action Items:")
                for task in email["actions"]:
                    st.write(f"- {task.get('task')} (Deadline: {task.get('deadline', 'Not specified')})")

    # ========== TAB 2 : AGENT ==========
    with tab2:

        inbox = st.session_state["inbox"]

        idx = st.selectbox("Select Email", range(len(inbox)), format_func=lambda i: inbox[i]["subject"])
        email = inbox[idx]

        email_text = f"""
From: {email['sender']}
Subject: {email['subject']}
Body:
{email['body']}
"""

        st.markdown("## 🤖 Email Agent Chat Interface")
        question = st.text_area("Ask something:", "Summarize this email.")

        if st.button("Ask Agent"):
            ans = email_agent_answer(email_text, question, prompts)
            st.markdown(f"<div class='agent-box'>{ans}</div>", unsafe_allow_html=True)

        # -------- Draft Reply --------
        st.markdown("---")
        st.markdown("### ✍ Draft Reply")

        tone = st.selectbox("Reply Tone", ["Formal", "Professional", "Friendly", "Short"])

        if st.button("Generate Draft"):
            draft = draft_auto_reply(email_text, prompts["auto_reply_prompt"], tone)
            st.session_state["temp_draft"] = draft

        if "temp_draft" in st.session_state:

            edited_subject = st.text_input("Edit Subject", st.session_state["temp_draft"]["subject"])
            edited_body = st.text_area("Edit Body", st.session_state["temp_draft"]["body"], height=200)

            if st.button("💾 Save Final Draft"):
                st.session_state["drafts"].append({
                    "subject": edited_subject,
                    "body": edited_body,
                    "tone": tone,
                    "email_subject": email["subject"]
                })
                del st.session_state["temp_draft"]
                st.success("✅ Draft saved successfully")

    # ========== TAB 3 : DRAFTS ==========
    with tab3:

        st.subheader("✍ Saved Drafts")

        if not st.session_state["drafts"]:
            st.info("No drafts available yet.")
            return

        for i, draft in enumerate(st.session_state["drafts"], 1):
            st.markdown("---")
            st.write(f"Draft #{i}")
            st.write("Email:", draft["email_subject"])
            st.write("Tone:", draft["tone"])
            st.write("Subject:", draft["subject"])
            st.write("Body:")
            st.write(draft["body"])

# ================= MAIN =================

if __name__ == "__main__":
    main()
