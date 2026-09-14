# Couples Therapy Multi-Agent System

A simple multi-agent couples therapy simulation built with **Python, AutoGen, Groq, and Cloudflare Workers**.

The project simulates a therapy session between a woman and a man, while a therapist agent manages the conversation, analyzes both perspectives, and generates a final session report.

## 🤖 Agents

The project contains exactly **3 agents**:

### 1. Woman Agent
Role-plays the woman based on her profile, personality, communication style, and relationship concerns.

### 2. Man Agent
Role-plays the man based on his profile, personality, communication style, and relationship concerns.

### 3. Therapist Agent
Manages the therapy session, analyzes what both partners say, asks follow-up questions, identifies communication patterns, and generates the final therapy report.

There is **no separate Report Agent**. The Therapist Agent produces the final report itself.

## 🏗️ Project Structure

```text
couple_therapy/
├── main.py
├── prompts.py
├── profiles.py
├── requirements.txt
├── .env
├── test_agent.py
└── gateway.py
```

## 🔄 How It Works

The application uses a controlled turn-based conversation:

```text
          ┌──────────────┐
          │  Therapist   │
          └──────┬───────┘
                 │
                 ▼
          ┌──────────────┐
          │     Sara     │
          │    Woman     │
          └──────┬───────┘
                 │
                 ▼
          ┌──────────────┐
          │     Reza     │
          │     Man      │
          └──────┬───────┘
                 │
                 ▼
          ┌──────────────┐
          │  Therapist   │
          │   Analysis   │
          └──────┬───────┘
                 │
                 ▼
          Final Session Report
```

The application intentionally uses direct agent calls instead of `RoundRobinGroupChat`. This keeps the orchestration simple and avoids tool-choice compatibility issues with the selected GPT-OSS models.

## 🧠 Models

The default configuration uses:

- **Woman:** `openai/gpt-oss-20b`
- **Man:** `openai/gpt-oss-20b`
- **Therapist:** `openai/gpt-oss-120b`

Each agent can use its own Groq API key.

## 🔐 Environment Variables

Create a `.env` file in the project root:

```env
GATEWAY_URL=https://your-worker.workers.dev
GATEWAY_API_KEY=your_gateway_key

WOMAN_GROQ_API_KEY=gsk_...
MAN_GROQ_API_KEY=gsk_...
THERAPIST_GROQ_API_KEY=gsk_...

WOMAN_MODEL=openai/gpt-oss-20b
MAN_MODEL=openai/gpt-oss-20b
THERAPIST_MODEL=openai/gpt-oss-120b
```

**Never commit your real API keys to GitHub.**

Add `.env` to `.gitignore`:

```gitignore
.env
__pycache__/
*.pyc
```

## ☁️ Gateway

The project can route model requests through a Cloudflare Worker gateway.

The gateway:

1. Receives OpenAI-compatible chat completion requests.
2. Authenticates the request using `GATEWAY_API_KEY`.
3. Receives the agent-specific Groq key through the request header.
4. Forwards the request to Groq.
5. Returns the Groq response to AutoGen.

This allows the three agents to use separate Groq API keys while sharing the same gateway.

## 📦 Installation

Clone the repository:

```bash
git clone https://github.com/YOUR_USERNAME/couple-therapy.git
cd couple-therapy
```

Create and activate a virtual environment if desired:

```bash
python -m venv .venv
```

Windows:

```powershell
.venv\Scriptsctivate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## ▶️ Run

Start the application with:

```bash
python main.py
```

You should see the conversation between:

```text
[Woman - Sara]
...

[Man - Reza]
...

[Therapist]
...

[Woman - Sara]
...

[Man - Reza]
...

[THERAPIST - FINAL REPORT]
...
SESSION_COMPLETE
```

## 🧪 Test an Agent

The project also includes `test_agent.py` for testing an individual agent and verifying the connection to the model gateway.

Run:

```bash
python test_agent.py
```

## 🛠️ Technologies

- Python
- AutoGen AgentChat
- AutoGen OpenAI-compatible model client
- Groq API
- GPT-OSS models
- Cloudflare Workers
- python-dotenv

## ⚠️ Disclaimer

This project is an **AI simulation/demo** for educational and technical purposes.

The generated therapy conversation and report are not a substitute for professional mental-health or couples counseling.




