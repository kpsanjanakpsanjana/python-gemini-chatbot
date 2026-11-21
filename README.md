# Gemini AI Conversational Chatbot

A fast, low-latency AI chatbot running directly in your terminal, powered by the official Google Gen AI SDK (`google-genai`) and Google's Gemini models.

---

## Features

- **Conversational AI:** Ask any question, debug code, brainstorm ideas, or have natural discussions.
- **Fast Streaming Responses:** Tokens stream to your terminal in real-time as Gemini generates them.
- **Multi-Turn Context Memory:** Automatically remembers prior context in the same session.
- **Optimized Sliding Window:** Automatically retains the most recent 10 messages (5 exchanges) to keep API calls snappy and efficient.
- **Resilient & Safe:** Gracefully handles rate limits, network drops, and timeouts without crashing the chat session.
- **Secure by Default:** Uses `.env` and `python-dotenv` for API key management, keeping credentials private.

---

## Getting Started

### 1. Prerequisites
- Python 3.10+ installed on your system.
- A free Gemini API key from [Google AI Studio](https://aistudio.google.com/).

### 2. Installation
Clone the repository and install dependencies:
```bash
git clone <your-repo-url>
cd pythonBOT
pip install -r requirements.txt
```

### 3. Configure Your API Key
Copy the example environment file:
```bash
copy .env.example .env
```
Open `.env` and add your Gemini API key:
```env
GEMINI_API_KEY=your_actual_gemini_api_key_here
```

### 4. Run the Chatbot
Launch the chatbot in your terminal:
```bash
python BOT.py
```
*(On Windows, you can also run or double-click `run_bot.bat`).*

---

## In-Chat Commands

| Command | Action |
|---|---|
| `exit` / `quit` / `bye` | Closes the chatbot cleanly |
| `clear` / `reset` / `new` | Clears conversation history and starts a fresh topic |
| `help` | Displays the help and commands menu |

---

## Security

Your `.env` file containing your `GEMINI_API_KEY` is excluded via `.gitignore` and is never committed or pushed to Git.
