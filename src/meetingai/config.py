from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Literal

class Settings(BaseSettings):
    GEMINI_API_KEY: str = ""
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama3.1"
    WHISPER_MODEL: str = "large-v3-turbo"
    WHISPER_LANGUAGE: str = "Vietnamese"
    OUTPUT_DIR: Path = Path("./output")
    LLM_BACKEND: Literal["gemini", "ollama", "none"] = "gemini"

    model_config = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding="utf-8", 
        extra="ignore"
    )
