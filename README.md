
# 📧 Prompt-Driven Email Productivity Agent

An intelligent, prompt-driven AI system that processes a mock email inbox and automates productivity tasks using a Large Language Model (LLM) with a Streamlit-based UI.

---

## 🎯 Project Objective

This project implements an **Email Productivity Agent** capable of:

- 📥 Email Categorization  
- ✅ Action-Item Extraction  
- ✍ Auto-Drafting Replies  
- 🤖 Chat-Based Inbox Interaction  
- 🧠 Prompt-Driven Agent Behavior  

All LLM actions are controlled using editable **Agent Prompts**, making the system dynamic and customizable.

A Streamlit-based user interface is used for seamless interaction.

---

## 🧠 Technology Stack

- **Frontend**: Streamlit  
- **Backend**: Python  
- **LLM Provider**: Groq API  
- **Data Source**: Mock Inbox (`inbox.json`)  
- **Prompt Storage**: `prompts.json`

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

## ⚙️ Setup Instructions

### Step 1: Clone the Repository

```bash
git clone https://github.com/Pragni24/email-agent
cd email-agent
```

---

### Step 2: Create a Virtual Environment

**Windows:**

```bash
python -m venv venv
venv\Scripts\activate
```

**Mac/Linux:**

```bash
python3 -m venv venv
source venv/bin/activate
```

---

### Step 3: Install Dependencies

Ensure your `requirements.txt` contains:

```
streamlit
requests
python-dotenv
```

Then install:

```bash
pip install -r requirements.txt
```

---

### Step 4: Configure Environment Variables

Create a file called `.env` in your project root and add:

```bash
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=llama-3.1-8b-instant
```

⚠️ **Important:** Do NOT upload your `.env` file to GitHub.

---

## ▶ How to Run the UI and Backend

Run the application using:

```bash
streamlit run app.py
```

Open in your browser:

```
http://localhost:8501
```

This runs both the UI and backend logic together.

---

## 📥 How to Load the Mock Inbox

The mock inbox is stored in:

```
inbox.json
```

The app automatically loads it at startup.

Each email follows this format:

```json
{
  "id": 1,
  "sender": "manager@company.com",
  "subject": "Project update",
  "timestamp": "2025-11-20T09:30:00",
  "body": "Email content here..."
}
```

To add emails, edit `inbox.json` before running the app.

---

## 🧠 How to Configure Prompts

Prompts are stored in:

```
prompts.json
```

They control:

* Email categorization
* Action item extraction
* Auto reply generation

These prompts can be edited inside the UI.
Changes are saved automatically.

---

## 💬 Usage Examples

### Example 1: Categorize Email

After running ingestion:

```
Category: Important
```

---

### Example 2: Extract Action Items

Input:

> "Please send the report by Friday and schedule a meeting."

Output:

```json
[
  "Send report by Friday",
  "Schedule a meeting"
]
```

---

### Example 3: Auto Reply Draft

Tone: Professional

```json
{
  "subject": "Re: Project Update",
  "body": "Hi, I will share the report by Friday as requested...",
  "follow_ups": []
}
```

---

### Example 4: Chat with the Email Agent

Available quick prompts:

* Categorize this email
* Extract action items
* Summarize this email

Summary prompt only gives a short overall description.

---

## 🚀 Deployment

You can deploy the app using:

* Streamlit Cloud
* Render
* Railway

Make sure your repo includes:

✅ app.py
✅ inbox.json
✅ prompts.json
✅ requirements.txt

And your API key is set in deployment environment variables.

---

