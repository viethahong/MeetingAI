import httpx
from google import genai
from .config import Settings
from .prompts import get_meeting_minutes_prompt

def summarize_with_gemini(transcript: str, api_key: str, model: str) -> str:
    if not api_key:
        raise ValueError("GEMINI_API_KEY chưa được thiết lập. Vui lòng điền API Key vào ô cấu hình.")
    
    client = genai.Client(api_key=api_key)
    prompt = get_meeting_minutes_prompt(transcript)
    
    response = client.models.generate_content(
        model=model,
        contents=prompt,
    )
    return response.text

def summarize_with_ollama(transcript: str, base_url: str, model: str) -> str:
    prompt = get_meeting_minutes_prompt(transcript)
    url = f"{base_url.rstrip('/')}/api/generate"
    
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False
    }
    
    # Increased timeout for LLM generation
    with httpx.Client(timeout=120.0) as client:
        response = client.post(url, json=payload)
        response.raise_for_status()
        result = response.json()
        return result.get("response", "")

def summarize(transcript: str, config: Settings) -> str:
    if config.LLM_BACKEND == "gemini":
        return summarize_with_gemini(transcript, config.GEMINI_API_KEY, config.GEMINI_MODEL)
    elif config.LLM_BACKEND == "ollama":
        return summarize_with_ollama(transcript, config.OLLAMA_BASE_URL, config.OLLAMA_MODEL)
    elif config.LLM_BACKEND == "none":
        return "LLM Summary is disabled (backend=none)."
    else:
        raise ValueError(f"Unsupported LLM backend: {config.LLM_BACKEND}")
