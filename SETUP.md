# Gmail AI Assistant — Setup Guide

This guide explains how to install, configure, run, authenticate, and troubleshoot the Gmail AI Assistant locally on Windows.

The recommended setup uses:

- Python
- FastAPI + Uvicorn
- React + Vite
- Gmail API + Google OAuth 2.0
- Ollama with `llama3.1:8b`
- Chroma for the local knowledge base

---

## 1. Prerequisites

Install the following before starting.

### Python

Recommended:

```text
Python 3.10+
```

Check:

```cmd
python --version
```

### Node.js and npm

Check:

```cmd
node --version
npm --version
```

### Git

Check:

```cmd
git --version
```

### Ollama

If using the default LLM provider, install Ollama and verify:

```cmd
ollama --version
```

Then download the configured model:

```cmd
ollama pull llama3.1:8b
```

Make sure the Ollama service is running before using AI features.

---

# 2. Clone the Repository

Open Windows CMD or PowerShell:

```cmd
git clone https://github.com/YOUR-USERNAME/Gmail-AI-Assistant.git
cd Gmail-AI-Assistant
```

Replace `YOUR-USERNAME` with your GitHub username.

---

# 3. Backend Setup

## Step 1 — Create a virtual environment

From the project root:

```cmd
python -m venv venv
```

Activate it in Windows CMD:

```cmd
venv\Scripts\activate
```

You should see something similar to:

```text
(venv) C:\...\Gmail-AI-Assistant>
```

---

## Step 2 — Upgrade pip

```cmd
python -m pip install --upgrade pip
```

---

## Step 3 — Install Python dependencies

```cmd
pip install -r requirements.txt
```

The main dependencies include:

- FastAPI
- Uvicorn
- Google API client libraries
- Google OAuth
- LangChain
- LangChain Chroma
- LangChain Ollama
- LangChain Google GenAI
- Pydantic
- Supabase
- Cryptography
- Pytest

---

# 4. Google Cloud / Gmail API Setup

Gmail access requires a Google Cloud project and OAuth credentials.

## Step 1 — Create a Google Cloud project

Open Google Cloud Console and create a new project.

Suggested project name:

```text
Gmail AI Assistant
```

---

## Step 2 — Enable Gmail API

In Google Cloud Console:

```text
APIs & Services
    ↓
Library
    ↓
Gmail API
    ↓
Enable
```

---

## Step 3 — Configure OAuth consent screen

Go to:

```text
APIs & Services
    ↓
OAuth consent screen
```

Configure the application information.

For local development, configure the appropriate test users if your OAuth application is in testing mode.

---

## Step 4 — Create OAuth credentials

Go to:

```text
APIs & Services
    ↓
Credentials
    ↓
Create Credentials
    ↓
OAuth client ID
```

Create an OAuth client suitable for the local web application flow.

Download the JSON credentials file.

---

# 5. Add `credentials.json`

Rename the downloaded Google OAuth JSON file to:

```text
credentials.json
```

Place it in the project root.

Correct:

```text
Gmail-AI-Assistant/
│
├── credentials.json
├── app/
├── frontend/
├── requirements.txt
└── ...
```

Incorrect:

```text
Gmail-AI-Assistant/
└── app/
    └── credentials.json
```

The current backend searches for:

```text
credentials.json
```

in the project root.

### Important

Never commit this file to GitHub.

The repository `.gitignore` already contains:

```gitignore
credentials.json
```

---

# 6. Configure Google OAuth Redirect URI

The application uses this callback:

```text
http://localhost:8000/auth/callback
```

Add the exact URL to the OAuth client's authorized redirect URIs.

The application also redirects to the frontend after successful authentication:

```text
http://localhost:5173/?auth=success
```

For local development, make sure the frontend is running on port `5173`.

---

# 7. Configure Environment Variables

Create a file named:

```text
.env
```

in the project root.

Example:

```env
LLM_PROVIDER=ollama

GOOGLE_API_KEY=

SUPABASE_URL=
SUPABASE_ANON_KEY=
```

### What each variable does

#### `LLM_PROVIDER`

Selects the LLM implementation.

Default:

```env
LLM_PROVIDER=ollama
```

Available provider values in the current factory:

```text
ollama
gemini
openai
```

However, the current OpenAI adapter is not fully implemented.

---

## 8. Ollama Setup

Ollama is the default provider.

The application currently expects:

```text
llama3.1:8b
```

Pull it:

```cmd
ollama pull llama3.1:8b
```

Verify the model:

```cmd
ollama list
```

You should see:

```text
llama3.1:8b
```

Then keep Ollama running and start the backend.

---

# 9. Optional Gemini Setup

To use Gemini instead of Ollama:

```env
LLM_PROVIDER=gemini
GOOGLE_API_KEY=YOUR_GEMINI_API_KEY
```

The configured Gemini model is:

```text
gemini-flash-lite-latest
```

Do not publish your API key.

---

# 10. OpenAI Provider Note

The project contains:

```text
app/llm/adapters/openai.py
```

but the current implementation intentionally raises:

```text
NotImplementedError
```

Therefore, do not select:

```env
LLM_PROVIDER=openai
```

unless you have completed the OpenAI adapter implementation.

---

# 11. Optional Supabase Setup

Supabase is optional.

Without Supabase, the application uses local token storage.

With Supabase configured:

```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your_supabase_anon_key
```

the Gmail OAuth token is also stored in Supabase.

The current code expects a table named:

```text
user_tokens
```

with fields used by the application:

```text
email
auth_token
```

The logical user key currently used by the code is:

```text
primary_user
```

### Security warning

Do not expose your Supabase service credentials or other privileged secrets. Review the database policies before using Supabase in production.

---

# 12. Start the Backend

From the project root:

```cmd
venv\Scripts\activate
```

Then:

```cmd
uvicorn app.main:app --reload
```

Expected backend address:

```text
http://localhost:8000
```

FastAPI Swagger documentation:

```text
http://localhost:8000/docs
```

Alternative ReDoc documentation:

```text
http://localhost:8000/redoc
```

---

# 13. Start the Frontend

Open a second CMD window.

Go to the project:

```cmd
cd Gmail-AI-Assistant
```

Then:

```cmd
cd frontend
```

Install packages:

```cmd
npm install
```

Start Vite:

```cmd
npm run dev
```

The frontend should be available at:

```text
http://localhost:5173
```

---

# 14. Authenticate Gmail

Once both backend and frontend are running, open:

```text
http://localhost:8000/auth/login
```

The backend redirects you to Google.

Sign in and approve the requested Gmail permissions.

After successful authentication, Google redirects to:

```text
http://localhost:8000/auth/callback
```

The application saves the OAuth credentials and redirects to:

```text
http://localhost:5173/?auth=success
```

---

# 15. Gmail Permissions

The application currently requests:

```text
gmail.readonly
gmail.send
gmail.modify
```

These permissions are used for:

- Reading Gmail messages
- Sending replies
- Performing Gmail modifications required by the application

Only grant access to a Google account you are comfortable using with the project.

---

# 16. Verify the Backend

Open:

```text
http://localhost:8000/
```

Expected response:

```json
{
  "message": "Gmail AI Assistant Backend Running (Modular)"
}
```

Then open:

```text
http://localhost:8000/docs
```

You should see the available API endpoints.

---

# 17. Useful API Tests

## Check unread emails

After authentication:

```text
GET http://localhost:8000/emails/unread
```

This endpoint requires Gmail authentication.

---

## Generate a reply

```text
POST http://localhost:8000/email/generate-reply
```

Example JSON:

```json
{
  "email_text": "Could you please send the project report?",
  "sender": "example@example.com"
}
```

---

## Send a reply

```text
POST http://localhost:8000/email/send
```

Example JSON:

```json
{
  "email_id": "GMAIL_MESSAGE_ID",
  "reply_body": "Sure, I will send the project report shortly."
}
```

---

## Chat with the assistant

```text
POST http://localhost:8000/chat/query
```

Example:

```json
{
  "query": "Summarize my recent email activity."
}
```

---

# 18. Knowledge Base

The project uses Chroma for persistent local vector storage.

Directory:

```text
data/chroma_db/
```

The application can build the sent-email knowledge base through:

```text
POST /kb/build
```

The backend also runs a background process after startup that:

1. Checks the knowledge base.
2. Builds it when necessary.
3. Periodically synchronizes recent sent emails.

The current synchronization interval is approximately:

```text
5 minutes
```

---

# 19. Run Tests

From the project root:

```cmd
pytest
```

For more detailed output:

```cmd
pytest -v
```

---

# 20. Frontend Commands

Inside:

```text
frontend/
```

### Development

```cmd
npm run dev
```

### Production build

```cmd
npm run build
```

### Preview production build

```cmd
npm run preview
```

### Lint

```cmd
npm run lint
```

---

# 21. Recommended Folder Structure After Setup

```text
Gmail-AI-Assistant/
│
├── .env
├── credentials.json
├── requirements.txt
│
├── app/
│   ├── api/
│   ├── core/
│   ├── llm/
│   ├── schemas/
│   ├── services/
│   └── main.py
│
├── data/
│   └── chroma_db/
│
├── frontend/
│   ├── node_modules/
│   ├── src/
│   ├── package.json
│   └── ...
│
├── tests/
├── README.md
└── SETUP.md
```

The following files/directories are local and should not be pushed:

```text
.env
credentials.json
token.pickle
data/chroma_db/
frontend/node_modules/
frontend/dist/
```

---

