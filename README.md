# Gmail AI Assistant

An AI-powered Gmail assistant that combines **Gmail API**, **FastAPI**, **React/Vite**, **LangChain**, **Ollama/Gemini**, and a **Chroma-based knowledge base** to help users understand and respond to emails.

The project provides a web interface where authenticated Gmail users can view unread emails, chat with an AI assistant, generate reply suggestions, send replies, and build a knowledge base from sent emails.

> **Project status:** This repository is intended primarily for local development and demonstration. Review the security and production notes before deploying it publicly.

---

## Features

- 🔐 **Google Gmail OAuth authentication**
  - Uses Google OAuth 2.0 with Gmail scopes.
  - Supports offline access and stores the resulting token locally.
  - Can optionally persist the serialized token in Supabase.

- 📩 **Unread email dashboard**
  - Retrieves unread Gmail messages through the Gmail API.
  - Displays sender, subject, date, body/snippet, and message ID.

- 🤖 **AI email assistance**
  - Generate AI-powered reply suggestions.
  - Chat with the assistant through a dedicated API endpoint.
  - Modular LLM adapter architecture.

- 🧠 **Multiple LLM provider structure**
  - **Ollama** — default provider in the current configuration.
  - **Gemini** — supported when `GOOGLE_API_KEY` is configured.
  - **OpenAI** — adapter exists, but the current OpenAI adapter is not fully configured and should not be treated as production-ready.

- 📚 **Knowledge Base / RAG**
  - Uses Chroma for persistent local vector storage.
  - Can build a knowledge base from sent emails.
  - Recent sent-email synchronization runs periodically after backend startup.

- ✉️ **Send Gmail replies**
  - Sends generated or manually edited replies through the Gmail API.

- ⚛️ **Modern frontend**
  - React 19
  - Vite
  - Tailwind CSS
  - Responsive dark interface

---

## Tech Stack

### Backend

| Technology | Purpose |
|---|---|
| Python | Backend language |
| FastAPI | REST API framework |
| Uvicorn | ASGI development server |
| Gmail API | Read and send Gmail messages |
| Google OAuth | Gmail authentication |
| LangChain | LLM/RAG orchestration |
| Ollama | Local LLM provider |
| Gemini | Optional cloud LLM provider |
| Chroma | Local vector database |
| Supabase | Optional cloud token persistence |
| Pydantic | Request/data validation |
| Cryptography | Encryption-related functionality |

### Frontend

| Technology | Purpose |
|---|---|
| React | UI |
| Vite | Frontend tooling/dev server |
| Tailwind CSS | Styling |
| JavaScript/JSX | Frontend implementation |

---

## Project Architecture

```text
Gmail-AI-Assistant-main/
│
├── app/
│   ├── api/
│   │   └── routes/
│   │       ├── auth.py
│   │       ├── chat.py
│   │       └── email.py
│   │
│   ├── core/
│   │   ├── config.py
│   │   └── llm_factory.py
│   │
│   ├── llm/
│   │   ├── adapters/
│   │   │   ├── base.py
│   │   │   ├── ollama.py
│   │   │   ├── gemini.py
│   │   │   └── openai.py
│   │   ├── classifier.py
│   │   ├── prompts.py
│   │   ├── reply_generator.py
│   │   └── summarizer.py
│   │
│   ├── schemas/
│   ├── services/
│   │   ├── gmail_client.py
│   │   ├── chat_service.py
│   │   ├── rag_service.py
│   │   ├── sent_email_service.py
│   │   ├── auto_reply.py
│   │   ├── intent_detector.py
│   │   ├── sentiment_analyzer.py
│   │   └── encryption.py
│   │
│   └── main.py
│
├── data/
│   └── chroma_db/
│
├── frontend/
│   ├── src/
│   ├── public/
│   ├── package.json
│   └── vite.config.js
│
├── tests/
├── requirements.txt
├── .gitignore
├── README.md
└── SETUP.md
```

---

## How the Application Works

```text
                 ┌─────────────────────┐
                 │   React + Vite UI   │
                 │   localhost:5173    │
                 └──────────┬──────────┘
                            │ HTTP
                            ▼
                 ┌─────────────────────┐
                 │   FastAPI Backend   │
                 │   localhost:8000    │
                 └──────┬──────┬───────┘
                        │      │
             ┌──────────┘      └─────────────┐
             ▼                               ▼
      ┌─────────────┐                 ┌─────────────┐
      │ Gmail API   │                 │ LLM Layer   │
      │ OAuth 2.0   │                 │ Ollama /    │
      └─────────────┘                 │ Gemini      │
                                      └──────┬──────┘
                                             │
                                             ▼
                                      ┌─────────────┐
                                      │ Chroma RAG  │
                                      │ Knowledge   │
                                      │ Base        │
                                      └─────────────┘
```

---

## Main API Endpoints

The backend currently exposes endpoints including:

| Method | Endpoint | Purpose |
|---|---|---|
| `GET` | `/` | Backend health/message |
| `GET` | `/auth/url` | Generate Google authorization URL |
| `GET` | `/auth/login` | Start Google OAuth login |
| `GET` | `/auth/callback` | OAuth callback |
| `POST` | `/chat/query` | Send a chat query to the assistant |
| `POST` | `/email/generate-reply` | Generate reply suggestions |
| `POST` | `/email/send` | Send a Gmail reply |
| `POST` | `/kb/build` | Start sent-email knowledge-base build |
| `GET` | `/emails/unread` | Retrieve unread Gmail messages |

You can also open the FastAPI documentation after starting the backend:

```text
http://localhost:8000/docs
```

---

## Requirements

Before starting, install:

- **Python 3.10+**
- **Node.js 18+** recommended
- **npm**
- A **Google Cloud project**
- Gmail API enabled in Google Cloud
- Google OAuth client credentials
- **Ollama** if using the default local LLM provider

Optional:

- Google Gemini API key
- Supabase project

For the exact setup procedure, see **[SETUP.md](SETUP.md)**.

---

## Quick Start

### 1. Clone the repository

```bash
git clone https://github.com/YOUR-USERNAME/Gmail-AI-Assistant.git
cd Gmail-AI-Assistant
```

### 2. Create and activate a Python virtual environment

Windows CMD:

```cmd
python -m venv venv
venv\Scripts\activate
```

### 3. Install backend dependencies

```cmd
pip install -r requirements.txt
```

### 4. Configure Google OAuth

Create/download the Google OAuth client credentials and place:

```text
credentials.json
```

in the **project root**:

```text
Gmail-AI-Assistant/
├── credentials.json
├── app/
├── frontend/
└── ...
```

Do **not** commit this file to GitHub.

### 5. Configure the LLM

The current default provider is:

```text
LLM_PROVIDER=ollama
```

For Ollama, install Ollama and pull the configured model:

```cmd
ollama pull llama3.1:8b
```

### 6. Start the backend

```cmd
uvicorn app.main:app --reload
```

Backend:

```text
http://localhost:8000
```

API documentation:

```text
http://localhost:8000/docs
```

### 7. Start the frontend

Open another terminal:

```cmd
cd frontend
npm install
npm run dev
```

Frontend:

```text
http://localhost:5173
```

### 8. Authenticate with Gmail

Open:

```text
http://localhost:8000/auth/login
```

Complete the Google consent flow. After successful authentication, the application redirects back to the frontend.

---

## Environment Variables

Create a `.env` file in the project root when using environment-based configuration.

Example:

```env
# LLM provider: ollama or gemini
LLM_PROVIDER=ollama

# Required only when using Gemini
GOOGLE_API_KEY=

# Optional Supabase token storage
SUPABASE_URL=
SUPABASE_ANON_KEY=
```

### Provider notes

#### Ollama

The current configuration uses:

```text
LLM_PROVIDER=ollama
```

and:

```text
llama3.1:8b
```

The Ollama service must be running locally.

#### Gemini

Set:

```env
LLM_PROVIDER=gemini
GOOGLE_API_KEY=your_google_ai_api_key
```

The configured Gemini model is:

```text
gemini-flash-lite-latest
```

#### OpenAI

An OpenAI adapter is present in the source tree, but the current adapter raises `NotImplementedError`. Additional configuration/code changes are required before using OpenAI as the active provider.

---

## Google OAuth Configuration

The backend expects the OAuth callback:

```text
http://localhost:8000/auth/callback
```

The frontend URL used after successful authentication is:

```text
http://localhost:5173/
```

In Google Cloud Console, configure the OAuth client accordingly.

The Gmail scopes currently requested are:

```text
https://www.googleapis.com/auth/gmail.readonly
https://www.googleapis.com/auth/gmail.send
https://www.googleapis.com/auth/gmail.modify
```

These permissions allow the application to read Gmail messages, send mail, and modify Gmail data.

---

## Authentication Storage

The application can store Gmail OAuth credentials in two ways:

1. **Local fallback**
   - `token.pickle`

2. **Optional Supabase storage**
   - Enabled when both `SUPABASE_URL` and `SUPABASE_ANON_KEY` are available.
   - The application uses a `user_tokens` table and the logical key `primary_user`.

If Supabase is configured, the code attempts cloud storage first and falls back to the local token file.

---

## RAG / Knowledge Base

The application uses Chroma for local persistent vector storage.

The configured location is:

```text
data/chroma_db/
```

The backend can build a knowledge base from sent emails through:

```http
POST /kb/build
```

The startup process also checks/builds the knowledge base and periodically synchronizes recent sent emails.

The current background synchronization interval is approximately **5 minutes**.

---

## Testing

The repository contains tests under:

```text
tests/
```

Run:

```cmd
pytest
```

---

## GitHub Security Checklist

Before pushing the project to GitHub, verify that the following are **not** committed:

```text
credentials.json
token.pickle
.env
data/chroma_db/
frontend/node_modules/
frontend/dist/
```

The project's `.gitignore` already excludes these sensitive/local files.

If a secret was accidentally committed in an earlier Git commit, simply deleting the file in a later commit is **not enough**. Rotate/revoke the exposed credential and clean the Git history.

---

## Troubleshooting

### `credentials.json not found`

Make sure the file exists here:

```text
Gmail-AI-Assistant/
└── credentials.json
```

and that the filename is exactly:

```text
credentials.json
```

### Google OAuth callback error

Check that the Google OAuth client has the exact redirect URI:

```text
http://localhost:8000/auth/callback
```

Then start the login process again from:

```text
http://localhost:8000/auth/login
```

### `401 Not authenticated`

Authenticate with Google first. The Gmail endpoints require a valid OAuth token.

### Ollama connection/model error

Make sure Ollama is running and the configured model exists:

```cmd
ollama pull llama3.1:8b
```

Then restart the FastAPI server.

### Gemini API key error

If using Gemini, verify:

```env
LLM_PROVIDER=gemini
GOOGLE_API_KEY=your_key
```

### Frontend cannot connect to backend

Make sure both servers are running:

```text
Backend  → http://localhost:8000
Frontend → http://localhost:5173
```

---

## Development Commands

### Backend

```cmd
venv\Scripts\activate
uvicorn app.main:app --reload
```

### Frontend

```cmd
cd frontend
npm install
npm run dev
```

### Frontend production build

```cmd
npm run build
```

### Frontend lint

```cmd
npm run lint
```

### Python tests

```cmd
pytest
```

---

## Important Production Considerations

Before deploying publicly, consider improving:

- OAuth state/verifier storage using secure server-side sessions instead of an in-memory dictionary.
- Secret and credential management.
- CORS configuration instead of allowing all origins.
- Authentication/authorization for API endpoints.
- Multi-user token isolation.
- Encryption and secure handling of OAuth tokens.
- Secure HTTPS deployment.
- Database-backed persistent sessions.
- Input validation and rate limiting.
- Logging and monitoring.
- Removal/review of debug endpoints and development scripts.
- Production-grade background job scheduling.

---

## Contributing

1. Fork the repository.
2. Create a feature branch:

```bash
git checkout -b feature/your-feature
```

3. Make your changes.
4. Run tests/linting.
5. Commit your changes:

```bash
git add .
git commit -m "feat: describe your change"
```

6. Push the branch:

```bash
git push origin feature/your-feature
```

7. Open a Pull Request.

---

## License

No license file is currently included in the project.

If you plan to make the repository public, add an appropriate `LICENSE` file before publishing.

---

## Author

**Tanmay Panchal**

Gmail AI Assistant — AI-powered Gmail management, email understanding, reply generation, and knowledge-base assistance.
