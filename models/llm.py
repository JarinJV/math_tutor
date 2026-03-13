import os
import requests

PROVIDERS = {
    "Google Gemini (Free)": {
        "env": "GEMINI_API_KEY",
        "models": [
            "gemini-2.5-flash",
        ],
        "get_key_url": "https://aistudio.google.com/app/apikey",
        "note": "🟡 Free tier unavailable in India/some regions. Use Ollama instead.",
        "badge": "warning",
    },
    "Ollama (Local)": {
        "env": "",  # no API key needed
        "models": [
            "qwen2.5:3b",
            "qwen2.5:7b",
        ],
        "get_key_url": "https://ollama.com/download",
        "note": "🟢 100% Free & Private — runs on your machine, no internet needed",
        "badge": "green",
    },
    "Anthropic Claude (Limited Free)": {
        "env": "ANTHROPIC_API_KEY",
        "models": [
            "claude-haiku-4-5-20251001",
            "claude-3-5-haiku-20241022",
        ],
        "get_key_url": "https://console.anthropic.com/",
        "note": "🟡 $5 credit on signup, then paid",
        "badge": "warning",
    },
}


def call_llm(system_prompt: str, user_message: str, max_tokens: int = 2000,
             provider: str = "Google Gemini (Free)", model: str = "gemini-2.0-flash") -> str:
    if provider == "Google Gemini (Free)":
        return _call_gemini(system_prompt, user_message, max_tokens, model)
    elif provider == "Ollama (Local)":
        return _call_ollama(system_prompt, user_message, max_tokens, model)
    elif provider == "Anthropic Claude (Limited Free)":
        return _call_anthropic(system_prompt, user_message, max_tokens, model)
    else:
        raise ValueError(f"Unknown provider: {provider}")


def _call_gemini(system_prompt, user_message, max_tokens, model):
    api_key = os.getenv("GEMINI_API_KEY", "")
    if not api_key:
        raise ValueError("GEMINI_API_KEY not set. Get a free key at https://aistudio.google.com/app/apikey")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
    resp = requests.post(
        url,
        headers={"Content-Type": "application/json"},
        json={
            "system_instruction": {"parts": [{"text": system_prompt}]},
            "contents": [{"parts": [{"text": user_message}]}],
            "generationConfig": {"maxOutputTokens": max_tokens, "temperature": 0.7},
        },
        timeout=60,
    )
    if not resp.ok:
        try:
            msg = resp.json().get("error", {}).get("message", resp.text)
        except Exception:
            msg = resp.text
        raise ValueError(f"Gemini API error {resp.status_code}: {msg}")
    return resp.json()["candidates"][0]["content"]["parts"][0]["text"]


def _call_ollama(system_prompt, user_message, max_tokens, model):
    """Call local Ollama instance. Must have Ollama running: `ollama serve`"""
    ollama_url = os.getenv("OLLAMA_URL", "http://localhost:11434")
    try:
        resp = requests.post(
            f"{ollama_url}/api/chat",
            json={
                "model": model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message},
                ],
                "stream": False,
                "options": {"num_predict": max_tokens, "temperature": 0.7},
            },
            timeout=120,  # local models can be slower
        )
    except requests.exceptions.ConnectionError:
        raise ValueError(
            "Cannot connect to Ollama. Make sure it's running:\n"
            "1. Install: https://ollama.com/download\n"
            f"2. Pull model: ollama pull {model}\n"
            "3. Start server: ollama serve"
        )
    if not resp.ok:
        raise ValueError(f"Ollama error {resp.status_code}: {resp.text}")
    return resp.json()["message"]["content"]


def _call_anthropic(system_prompt, user_message, max_tokens, model):
    api_key = os.getenv("ANTHROPIC_API_KEY", "")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY not set.")
    resp = requests.post(
        "https://api.anthropic.com/v1/messages",
        headers={
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        },
        json={
            "model": model,
            "max_tokens": max_tokens,
            "system": system_prompt,
            "messages": [{"role": "user", "content": user_message}],
        },
        timeout=60,
    )
    if not resp.ok:
        try:
            msg = resp.json().get("error", {}).get("message", resp.text)
        except Exception:
            msg = resp.text
        raise ValueError(f"Anthropic API error {resp.status_code}: {msg}")
    return resp.json()["content"][0]["text"]

"""
def _call_openai(system_prompt, user_message, max_tokens, model):
    api_key = os.getenv("OPENAI_API_KEY", "")
    if not api_key:
        raise ValueError("OPENAI_API_KEY not set.")
    resp = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        json={
            "model": model,
            "max_tokens": max_tokens,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
        },
        timeout=60,
    )
    if not resp.ok:
        try:
            msg = resp.json().get("error", {}).get("message", resp.text)
        except Exception:
            msg = resp.text
        raise ValueError(f"OpenAI API error {resp.status_code}: {msg}")
    return resp.json()["choices"][0]["message"]["content"]
"""

# ── Prompts ───────────────────────────────────────────────────────────────────
EXPLANATION_SYSTEM = """You are an expert math tutor — clear, encouraging, and visual-minded like a great teacher at a whiteboard.

When a student asks about a math concept or problem, respond in this EXACT format using these exact section tags:

[WHAT_IT_IS]
1-2 sentences. Plain English. What IS this concept? Make it click immediately.
[/WHAT_IT_IS]

[INTUITION]
The "aha!" explanation. Use an analogy or real-world connection. 2-3 sentences.
[/INTUITION]

[STEP_BY_STEP]
Walk through a concrete example step by step. Number each step clearly.
Step 1: ...
Step 2: ...
Step 3: ...
(use as many steps as needed, be thorough)
[/STEP_BY_STEP]

[KEY_FORMULA]
The core formula or rule, written clearly. Example: f'(x) = lim(h→0) [f(x+h) - f(x)] / h
[/KEY_FORMULA]

[VISUAL_HINT]
One sentence describing what the graph/diagram shows and why it helps understand the concept.
[/VISUAL_HINT]

[PRACTICE_PROBLEM]
Give the student ONE practice problem to try. Keep it approachable.
Problem: ...
Hint: ...
[/PRACTICE_PROBLEM]

Rules:
- ALWAYS include all six sections with the exact tags shown
- Use plain text math notation (e.g. x^2, sqrt(x), f'(x))
- Be warm and encouraging
- Make the step-by-step GENUINELY useful, not vague
"""

LESSON_SYSTEM = """You are creating a 5-slide lesson presentation for a math topic.

Return EXACTLY this format. No extra commentary before or after.

SLIDE 1 TITLE: [Topic Name]
SLIDE 1 CONTENT: [1-2 sentence compelling hook or real-world context]

SLIDE 2 TITLE: The Core Idea
SLIDE 2 CONTENT: [Plain English explanation, 2-3 sentences]

SLIDE 3 TITLE: The Formula / Method
SLIDE 3 CONTENT: [Key formula then one sentence explaining each part]

SLIDE 4 TITLE: Worked Example
SLIDE 4 CONTENT: [Step-by-step example, 3-4 numbered steps]

SLIDE 5 TITLE: Key Takeaways
SLIDE 5 CONTENT: [3 bullet points starting with - ]
"""
