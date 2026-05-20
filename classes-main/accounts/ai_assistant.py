import os
import requests
import time
from functools import lru_cache
from threading import Lock

# Google Gemini API (Free tier available)
GEMINI_API_KEY = "AIzaSyBMY0FtXoCMlkHxMsw--QRy8G3kulhFzxI"  # Get from https://makersuite.google.com/app/apikey
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-001:generateContent"

# Ollama settings (local AI for zero cost and no rate limits)
OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "mistral"  # Fast and good for career advice

# Rate limiting is handled server-side by APIs
# Ollama has no rate limits, Gemini will return 429 if exceeded
rate_limit_lock = Lock()

# To get a free Gemini API key:
# 1. Go to https://makersuite.google.com/app/apikey
# 2. Sign in with your Google account
# 3. Create a new API key
# 4. Replace the API key above with your actual API key
# Note: Gemini has a generous free tier (60 requests per minute, 1000 requests per day)
# Using gemini-2.0-flash-001 which is a stable, fast model

SYSTEM_MESSAGE = (
    "You are a career expert AI assistant. Answer ONLY about jobs, CVs, and professional growth. "
    "Refuse any other topics like food or hobbies. Be helpful and provide specific career advice."
)

def try_ollama(user_message):
    """Try to get response from local Ollama (no rate limits, no cost)."""
    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": OLLAMA_MODEL,
                "prompt": f"{SYSTEM_MESSAGE}\n\nUser: {user_message}",
                "stream": False,
                "temperature": 0.7,
            },
            timeout=60  # Ollama can be slow on first run, give it more time
        )
        response.raise_for_status()
        result = response.json()
        text = result.get("response", "").strip()
        if text:
            return text
        return None
    except Exception as e:
        # Ollama not available or failed, will fall back to Gemini
        return None

def get_ai_response(user_message):
    # Try local Ollama first (no rate limits, no cost) - ALWAYS PREFERRED
    ollama_response = try_ollama(user_message)
    if ollama_response:
        return ollama_response
    
    # Fall back to Gemini if Ollama not available
    if GEMINI_API_KEY == "YOUR_GEMINI_API_KEY_HERE":
        return "AI Assistant Error: Please set up a free Gemini API key. Go to https://makersuite.google.com/app/apikey to get one and update GEMINI_API_KEY in accounts/ai_assistant.py"

    url = f"{GEMINI_API_URL}?key={GEMINI_API_KEY}"

    headers = {
        "Content-Type": "application/json"
    }

    data = {
        "contents": [{
            "parts": [{
                "text": f"{SYSTEM_MESSAGE}\n\nUser: {user_message}"
            }]
        }],
        "generationConfig": {
            "temperature": 0.7,
            "maxOutputTokens": 300,
        }
    }

    try:
        response = requests.post(url, headers=headers, json=data, timeout=10)
        response.raise_for_status()
        result = response.json()

        # Extract the text from Gemini's response format
        if result.get("candidates") and len(result["candidates"]) > 0:
            content = result["candidates"][0].get("content", {})
            if content.get("parts") and len(content["parts"]) > 0:
                return content["parts"][0].get("text", "No response content").strip()

        return "No response received"

    except requests.exceptions.Timeout:
        return "AI Assistant: Request timed out. Please try again in a moment."
    except Exception as e:
        error_msg = str(e)
        # Check for rate limit errors in response
        if hasattr(e, 'response') and e.response and e.response.status_code == 429:
            return "AI Assistant: Rate limit reached. Please wait a moment and try again. Consider setting up local Ollama for unlimited free access."
        elif "API_KEY_INVALID" in error_msg or "PERMISSION_DENIED" in error_msg:
            return "AI Assistant Error: Invalid Gemini API key. Please check your API key at https://makersuite.google.com/app/apikey"
        elif "RESOURCE_EXHAUSTED" in error_msg or "QUOTA_EXCEEDED" in error_msg:
            return "AI Assistant: Daily limit reached. Please try again tomorrow or set up free local Ollama for unlimited access."
        elif "429" in error_msg or "Too Many Requests" in error_msg:
            return "AI Assistant: Rate limit exceeded. Please wait and try again. Running out of free tier quota - consider Ollama."
        return f"Error communicating with AI service. Please try again: {error_msg[:100]}"
