from dataclasses import dataclass
from pathlib import Path
from typing import Optional, List, Callable
from .config import Settings
from .downloader import prepare_audio
from .transcriber import transcribe
from .llm_processor import summarize

@dataclass
class PipelineResult:
    audio_path: Path
    transcript: str
    summary: Optional[str]
    output_files: List[Path]

def run_pipeline(
    input_source: str, 
    config: Settings, 
    progress_callback: Callable[[str, float], None] = lambda m, p: None
) -> PipelineResult:
    
    progress_callback("Đang chuẩn bị file âm thanh...", 0.1)
    audio_path = prepare_audio(input_source, config.OUTPUT_DIR)
    
    progress_callback("Đang chuyển đổi giọng nói thành văn bản bằng Whisper...", 0.3)
    transcription_result = transcribe(
        audio_path, 
        language=config.WHISPER_LANGUAGE, 
        model=config.WHISPER_MODEL
    )
    transcript_text = transcription_result.text
    
    txt_output_path = config.OUTPUT_DIR / f"{audio_path.stem}_transcript.txt"
    config.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    with open(txt_output_path, "w", encoding="utf-8") as f:
        f.write(transcript_text)
        
    output_files = [txt_output_path]
    
    summary_text = None
    if config.LLM_BACKEND != "none":
        progress_callback("Đang thiết lập báo cáo tóm tắt...", 0.7)
        try:
            summary_text = summarize(transcript_text, config)
            
            md_output_path = config.OUTPUT_DIR / f"{audio_path.stem}_summary.md"
            with open(md_output_path, "w", encoding="utf-8") as f:
                f.write(summary_text)
                
            output_files.append(md_output_path)
        except Exception as e:
            summary_text = f"⚠️ **Lỗi tạo tóm tắt**: {str(e)}\n\n*Tuy nhiên, Nội dung bóc băng (raw) vẫn được sinh ra thành công.*"
            progress_callback("Bỏ qua mã tóm tắt do lỗi LLM, giữ text raw.", 0.9)
        
    progress_callback("Hoàn thành!", 1.0)
    
    return PipelineResult(
        audio_path=audio_path,
        transcript=transcript_text,
        summary=summary_text,
        output_files=output_files
    )
