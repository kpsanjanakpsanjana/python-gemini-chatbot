"""
AI-Powered Conversational Chatbot using Google Gemini API
Optimized for high-speed, low-latency streaming responses with google-genai SDK
"""

import os
import sys

# Ensure UTF-8 output encoding across Windows consoles to prevent UnicodeEncodeError with emojis
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
if hasattr(sys.stdin, "reconfigure"):
    try:
        sys.stdin.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

try:
    from google import genai
    from google.genai import types, errors
except ImportError:
    print("=" * 65)
    print("❌ ERROR: 'google-genai' package is not installed.")
    print("=" * 65)
    print("Please install the required packages by running:")
    print("    pip install google-genai python-dotenv")
    print("=" * 65)
    sys.exit(1)

DEFAULT_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite").strip() or "gemini-3.5-flash-lite"
FALLBACK_MODEL = "gemini-3.1-flash-lite"

REQUEST_TIMEOUT_SECONDS = 90.0

# Limit conversation history to the most recent 10 messages (5 user-assistant exchanges)
MAX_HISTORY_MESSAGES = 10

# Streamlined, concise system instruction to reduce prefill token processing time
SYSTEM_INSTRUCTION = (
    "You are a helpful, fast, and concise AI conversational assistant. "
    "Provide clear, direct, and well-structured answers without unnecessary filler."
)


def print_banner():
    """Prints a friendly welcome banner and instructions."""
    print("=" * 65)
    print("   ⚡ Gemini AI Fast Conversational Assistant   ")
    print("=" * 65)
    print("Ask me anything! Fast streaming responses & memory enabled.")
    print("\nSpecial commands:")
    print("  • Type 'exit', 'quit', or 'bye' to end the session.")
    print("  • Type 'clear' or 'reset'       to start a fresh conversation.")
    print("  • Type 'help'                   to view this menu again.")
    print("=" * 65)
    print()


def check_api_key():
    """Checks for the presence of GEMINI_API_KEY and provides guidance if missing."""
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if not api_key or api_key == "your_gemini_api_key_here":
        print("\n" + "=" * 65)
        print("⚠️  GEMINI API KEY IS MISSING OR NOT CONFIGURED")
        print("=" * 65)
        print("To use this AI chatbot, you need a free Gemini API key:\n")
        print("  1. Go to Google AI Studio: https://aistudio.google.com/")
        print("  2. Click 'Get API key' and generate a new key (free).")
        print("  3. Open the '.env' file in this project folder:")
        env_path = os.path.abspath(".env")
        print(f"     {env_path}")
        print("  4. Add your key on the line:")
        print("     GEMINI_API_KEY=your_actual_key_here")
        print("\nAfter saving the file, restart the chatbot.")
        print("=" * 65 + "\n")
        return None
    return api_key


def trim_chat_history(chat, max_messages=MAX_HISTORY_MESSAGES):
    """
    Trims conversation history to keep only the most recent N messages (5 exchanges).
    Ensures the history begins with a user turn so the conversation alternates cleanly.
    """
    for attr in ("_curated_history", "_comprehensive_history"):
        history = getattr(chat, attr, None)
        if history and len(history) > max_messages:
            trimmed = history[-max_messages:]
            # Ensure the first message in the trimmed window starts with a user turn
            while trimmed and getattr(trimmed[0], "role", "") != "user":
                trimmed = trimmed[1:]
            setattr(chat, attr, trimmed)


def create_chat_session(client, model_name=DEFAULT_MODEL):
    """Initializes a new multi-turn chat session with optimized configuration."""
    config = types.GenerateContentConfig(
        system_instruction=SYSTEM_INSTRUCTION,
        temperature=0.7,
        max_output_tokens=1024,
    )
    chat = client.chats.create(model=model_name, config=config)
    return chat, model_name


def send_prompt(chat, client, current_model, user_input):
    """
    Sends user prompt with real-time streaming, falling back to fallback model or non-streaming if needed.
    Returns (response_text, updated_chat, model_used).
    """
    try:
        response_stream = chat.send_message_stream(user_input)
        has_text = False
        full_text = []
        for chunk in response_stream:
            chunk_text = getattr(chunk, "text", "") or ""
            if chunk_text:
                print(chunk_text, end="", flush=True)
                full_text.append(chunk_text)
                has_text = True
        if not has_text:
            print("[Empty response from model]", end="")
        print("\n")
        trim_chat_history(chat, MAX_HISTORY_MESSAGES)
        return "".join(full_text), chat, current_model

    except errors.ClientError as e:
        if getattr(e, "code", None) == 404 and current_model != FALLBACK_MODEL:
            print(f"\n⚠️ Model '{current_model}' unavailable, switching to '{FALLBACK_MODEL}'...\n")
            new_chat, current_model = create_chat_session(client, FALLBACK_MODEL)
            return send_prompt(new_chat, client, current_model, user_input)
        raise e

    except Exception as e:
        err_str = str(e).lower()
        if any(term in err_str for term in ("readtimeout", "stream", "chunked")):
            try:
                resp = chat.send_message(user_input)
                text = getattr(resp, "text", "") or ""
                print(text)
                print("\n")
                trim_chat_history(chat, MAX_HISTORY_MESSAGES)
                return text, chat, current_model
            except Exception:
                raise e
        raise e


def chatbot():
    """Main interactive chat loop."""
    print_banner()

    api_key = check_api_key()
    if not api_key:
        return

    # Initialize Gemini client with configured HTTP timeout in milliseconds (90 seconds = 90,000 ms)
    try:
        timeout_ms = int(REQUEST_TIMEOUT_SECONDS * 1000)
        http_opts = types.HttpOptions(timeout=timeout_ms)
        client = genai.Client(api_key=api_key, http_options=http_opts)
    except Exception as e:
        print(f"❌ Failed to initialize Gemini client: {e}")
        return

    # Create multi-turn chat session
    current_model = DEFAULT_MODEL
    try:
        chat, current_model = create_chat_session(client, current_model)
        print(f"✨ Connected to Gemini ({current_model}) [Timeout: {int(REQUEST_TIMEOUT_SECONDS)}s]. How can I help you today?\n")
    except Exception as e:
        print(f"⚠️ Error creating chat session with model '{current_model}': {e}")
        print("Please check your API key and internet connection.\n")
        return

    # Interactive Loop
    while True:
        try:
            user_input = input("You: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n\nGoodbye! Have a great day! 👋")
            break

        # Ignore empty input
        if not user_input:
            continue

        lower_input = user_input.lower()

        # Handle exit commands
        if lower_input in ("exit", "quit", "bye"):
            print("\nGoodbye! Have a great day! 👋")
            break

        # Handle reset commands
        if lower_input in ("clear", "reset", "new"):
            try:
                chat, current_model = create_chat_session(client, current_model)
                print(f"\n🔄 Conversation history cleared. Started a fresh session with {current_model}!\n")
            except Exception as e:
                print(f"\n⚠️ Could not reset conversation: {e}\n")
            continue

        # Handle help command
        if lower_input == "help":
            print_banner()
            continue

        # Send message to Gemini and stream response in real-time
        print(f"\nGemini: ", end="", flush=True)
        try:
            _, chat, current_model = send_prompt(chat, client, current_model, user_input)

        except errors.APIError as e:
            print("\n")
            if getattr(e, "code", None) in (400, 403):
                print("❌ API Key Error: Your API key appears to be invalid or unauthorized.")
                print("   Please check your GEMINI_API_KEY in the .env file or generate a new key at:")
                print("   https://aistudio.google.com/")
            elif getattr(e, "code", None) == 404:
                print(f"❌ Model Error: The configured model is not available.")
                print(f"   Details: {getattr(e, 'message', str(e))}")
            elif getattr(e, "code", None) == 429:
                print("⏳ Rate Limit Reached: You've exceeded your temporary API quota.")
                print("   Please wait a few moments before sending another message.")
            elif getattr(e, "code", None) and e.code >= 500:
                print(f"⚠️ Gemini Server Error ({e.code}): Google's servers experienced an issue. Please try again.")
            else:
                err_msg = getattr(e, "message", str(e))
                print(f"⚠️ Gemini API Error: {err_msg}")
            print("   You can ask another question or type 'exit' to quit.\n")

        except Exception as e:
            print("\n")
            err_str = str(e).lower()
            if "timeout" in err_str or "timed out" in err_str:
                print(f"⏱️ Request Timeout: The request took longer than {int(REQUEST_TIMEOUT_SECONDS)}s to respond.")
                print("   Please check your network connection and try again.")
            elif any(term in err_str for term in ("connect", "getaddrinfo", "network", "dns")):
                print("🌐 Network Connection Error: Unable to reach Google Gemini servers.")
                print("   Please verify your internet connection and try again.")
            else:
                print(f"⚠️ Unexpected Error: {e}")
            print("   You can ask another question or type 'exit' to quit.\n")


if __name__ == "__main__":
    chatbot()
