# 📧 Prompt-Driven Email Productivity Agent

An intelligent, prompt-driven AI system that processes a mock email inbox and automates key productivity tasks using a Large Language Model (LLM) and a Streamlit-based UI.

---

## 🎯 Project Objective

Build an intelligent Email Productivity Agent capable of:

- 📥 Email Categorization  
- ✅ Action-Item Extraction  
- ✍ Auto-Drafting Replies  
- 🤖 Chat-Based Inbox Interaction  
- 🧠 Prompt-Driven Agent Behavior  

The system allows users to modify prompts (the **Agent Brain**) to dynamically control how the AI behaves.

---

## 🚀 Features

### 1. Email Categorization
Automatically classifies emails into:
- Important
- To-Do
- Newsletter
- Spam

### 2. Action Item Extraction
Extracts tasks mentioned in emails and converts them into structured JSON.

### 3. AI Reply Drafting
Generates professional reply drafts with adjustable tone:
- Formal
- Professional
- Friendly
- Short

### 4. Email Agent Chat
Users can interact with the agent using natural language questions like:
- “Give a short summary of this email”
- “Categorize this email”
- “What actions do I need to take?”

### 5. Prompt Brain (Interactive Sidebar)
Users can modify the agent’s behavior by editing:
- Categorization Prompt  
- Action Extraction Prompt  
- Auto Reply Prompt  

Changes instantly affect the AI’s logic.

---

## 🧠 Technology Stack

- **Frontend**: Streamlit  
- **Backend**: Python  
- **LLM API**: Groq API  
- **Data**: Mock Email Inbox (`inbox.json`)  
- **Configuration**: `.env` file  

---

## 📁 Project Structure

```plaintext
email-agent/
│
├── app.py               # Main application
├── inbox.json           # Mock inbox dataset
├── prompts.json         # Prompt brain storage
├── requirements.txt     # Project dependencies
├── .env                 # API keys (not uploaded)
└── README.md            # Project documentation
```

---

## ⚙️ Installation & Setup Guide

Follow these steps to run the project on your machine.
- Step 1: Clone the Repository
```bash
git clone https://github.com/Pragni24/email-agent
cd email-agent
```
- Step 2: Create a Virtual Environment

This keeps your project dependencies isolated.
On Windows:
```bash
python -m venv venv
venv\Scripts\activate
```

On macOS / Linux:
```
python3 -m venv venv
source venv/bin/activate
```
- Step 3: Install Required Python Packages
```bash
pip install -r requirements.txt
```

- Step 4: Configure Environment Variables

Create a file named .env in the root folder of your project and add:
```bash
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=llama-3.1-8b-instant
```
⚠ Important: Do NOT upload your .env file to GitHub.

- Step 5: Run the Application

Start the Streamlit app using:
```bash
streamlit run app.py
```
Now open your browser and go to:
```bash
http://localhost:8501
```
You should now see your Email Productivity Agent UI running.
