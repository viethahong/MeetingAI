import sys
import platform
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

@dataclass
class TranscriptionResult:
    text: str
    language: str
    segments: List[Dict[str, Any]]

def is_apple_silicon():
    return sys.platform == "darwin" and platform.machine() == "arm64"

def transcribe(audio_path: Path, language: str, model: str) -> TranscriptionResult:
    # Bản thân ngôn ngữ cho mlx-whisper thường cần lowercase hai ký tự (ví dụ 'vi' hoặc 'en')
    # Nhưng nếu user gõ "Vietnamese", chúng ta truyền vào cho faster-whisper tốt hơn,
    # mlx-whisper hỗ trợ vài ngôn ngữ full name. Để cho chắc, parse nhẹ.
    
    language_code = language.lower()
    if language_code == "vietnamese":
        language_code = "vi"
    elif language_code == "english":
        language_code = "en"
        
    if is_apple_silicon():
        try:
            import mlx_whisper
            logger.info("Using MLX-Whisper backend for transcription")
            
            model_repo = f"mlx-community/whisper-{model}"
            result = mlx_whisper.transcribe(
                str(audio_path),
                path_or_hf_repo=model_repo,
                language=language_code
            )
            
            segments_data = result.get("segments", [])
            formatted_text = "\n\n".join(seg.get("text", "").strip() for seg in segments_data if seg.get("text", "").strip())
            if not formatted_text:
                formatted_text = result.get("text", "")
            
            return TranscriptionResult(
                text=formatted_text,
                language=result.get("language", language),
                segments=segments_data
            )
        except ImportError:
            logger.warning("mlx-whisper not installed or failed to import. Falling back to faster-whisper")
    
    # Fallback / Dual backend: Faster-Whisper
    logger.info("Using faster-whisper backend for transcription")
    from faster_whisper import WhisperModel
    
    device = "cuda" if not is_apple_silicon() else "cpu" 
    w_model = None
    try:
        w_model = WhisperModel(model, device=device, compute_type="float16")
    except Exception:
        w_model = WhisperModel(model, device="cpu", compute_type="int8")
        
    segments_gen, info = w_model.transcribe(str(audio_path), language=language_code if language else None)
    
    text_chunks = []
    segments = []
    
    for segment in segments_gen:
        text_chunks.append(segment.text)
        segments.append({
            "start": segment.start,
            "end": segment.end,
            "text": segment.text
        })
        
    formatted_text = "\n\n".join(chunk.strip() for chunk in text_chunks if chunk.strip())
    
    return TranscriptionResult(
        text=formatted_text,
        language=info.language,
        segments=segments
    )
