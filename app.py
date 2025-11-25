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

# ================= LLM =================

def call_llm(system_prompt, user_prompt, temperature=0.3):
    if not USE_LLM:
        return "Mock LLM Response"

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

    return response.json()["choices"][0]["message"]["content"].strip()

# ================= SUMMARY FUNCTION =================

def summarize_email(email_text):
    return call_llm(
        "You summarize emails clearly and briefly.",
        f"""
Summarize this email in 2-3 short sentences.
ONLY summary. Do NOT classify or extract action items.

EMAIL:
{email_text}
""",
        0.2
    )

# ================= LLM TASKS =================

def categorize_email(email_text, prompt):
    return call_llm(
        "You classify emails into categories.",
        f"{prompt}\n\nEMAIL:\n{email_text}", 0.0
    )

def extract_actions(email_text, prompt):
    raw = call_llm(
        "Extract ONLY action items in valid JSON list format.",
        f"{prompt}\n\nEMAIL:\n{email_text}", 0.0
    )
    try:
        return json.loads(raw)
    except:
        return []

def draft_auto_reply(email_text, prompt, tone):
    raw = call_llm(
        "Draft email reply strictly in JSON with subject and body.",
        f"{prompt}\nTone: {tone}\nEMAIL:\n{email_text}", 0.3
    )
    try:
        return json.loads(raw)
    except:
        return {"subject": "Re:", "body": raw}

# ================= AGENT CHAT =================

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

# ================= STATE =================

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

    init_state()

    st.title("📧 AI Email Productivity Agent")

    tab1, tab2, tab3 = st.tabs(["📥 Inbox", "🤖 Agent", "✍ Drafts"])

    # ✅ INBOX TAB
    with tab1:

        st.subheader("📥 Raw Emails")

        for email in st.session_state["inbox"]:
            st.markdown("----")
            st.markdown(f"**From:** {email['sender']}")
            st.markdown(f"**Subject:** {email['subject']}")
            st.markdown(f"**Time:** {email['timestamp']}")
            st.write(email["body"])

        st.markdown("---")

        if st.button("🚀 Run Ingestion Pipeline"):
            run_ingestion_pipeline()

        if st.session_state["processed"]:
            st.subheader("✅ Processed Emails")

            for email in st.session_state["processed"]:
                st.markdown("---")
                st.markdown(f"**Subject:** {email['subject']}")
                st.write("Category:", email["category"])
                st.write("Actions:", email["actions"])

    # ✅ AGENT TAB
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

        st.subheader("🤖 Email Agent")

        col1, col2 = st.columns(2)

        with col1:
            if st.button("📝 Summarize Email"):
                summary = summarize_email(email_text)
                st.success(summary)

        with col2:
            question = st.text_input("Ask custom question:")
            if st.button("💬 Ask Agent"):
                answer = email_agent_answer(email_text, question, st.session_state["prompts"])
                st.info(answer)

        st.markdown("---")
        st.subheader("✍ Draft Reply")

        tone = st.selectbox("Tone", ["Formal", "Professional", "Friendly", "Short"])

        if st.button("Generate Draft"):
            st.session_state["temp_draft"] = draft_auto_reply(email_text, st.session_state["prompts"]["auto_reply_prompt"], tone)

        if "temp_draft" in st.session_state:
            subject = st.text_input("Subject", st.session_state["temp_draft"]["subject"])
            body = st.text_area("Body", st.session_state["temp_draft"]["body"], height=150)

            if st.button("💾 Save Draft"):
                st.session_state["drafts"].append({
                    "subject": subject,
                    "body": body,
                    "email": email["subject"]
                })
                del st.session_state["temp_draft"]
                st.success("Draft saved!")

    # ✅ DRAFTS TAB
    with tab3:

        st.subheader("✍ Saved Drafts")

        if not st.session_state["drafts"]:
            st.info("No drafts available yet")

        for draft in st.session_state["drafts"]:
            st.markdown("---")
            st.write("Original Email:", draft["email"])
            st.write("Subject:", draft["subject"])
            st.write("Body:")
            st.write(draft["body"])

if __name__ == "__main__":
    main()
