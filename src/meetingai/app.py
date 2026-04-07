import gradio as gr
from pathlib import Path
import os
from .config import Settings
from .pipeline import run_pipeline

def process(input_file, youtube_url, language, llm_choice, api_key, progress=gr.Progress()):
    if not input_file and not youtube_url:
        return "Lỗi: Vui lòng cung cấp file hoặc YouTube URL", "", []
    
    input_source = youtube_url.strip() if youtube_url else input_file.name
    
    config = Settings()
    config.WHISPER_LANGUAGE = language
    config.LLM_BACKEND = llm_choice
    
    if llm_choice == "gemini" and api_key and api_key.strip():
        config.GEMINI_API_KEY = api_key.strip()
        
    def progress_callback(msg: str, p: float):
        progress(p, desc=msg)
        
    try:
        result = run_pipeline(input_source, config, progress_callback=progress_callback)
        summary_text = result.summary if result.summary else "LLM Backend đã tắt."
        return result.transcript, summary_text, [str(p) for p in result.output_files]
    except Exception as e:
        import traceback
        err_msg = traceback.format_exc()
        return f"Đã xảy ra lỗi:\n{err_msg}", "Không thể tạo tóm tắt do lỗi", []

def launch():
    with gr.Blocks(title="MeetingAI") as demo:
        gr.Markdown("# MeetingAI - Transcribe & Summarize")
        
        with gr.Row():
            with gr.Column():
                gr.Markdown("### 1. Đầu vào (Audio/Video hoặc YouTube)")
                input_file = gr.File(label="Tải file lên (Kéo & Thả hỗ trợ file video/audio)")
                youtube_url = gr.Textbox(label="Hoặc nhập link YouTube")
                
                gr.Markdown("### 2. Cấu hình")
                language = gr.Dropdown(
                    choices=["Vietnamese", "English", "Japanese", "Korean", "Chinese"], 
                    value="Vietnamese", 
                    label="Ngôn ngữ"
                )
                llm_choice = gr.Radio(
                    choices=["gemini", "ollama", "none"], 
                    value="gemini", 
                    label="LLM Backend"
                )
                api_key = gr.Textbox(
                    label="Gemini API Key (Tùy chọn, ghi đè .env)", 
                    type="password"
                )
                
                submit_btn = gr.Button("Bắt đầu xử lý", variant="primary")
                
            with gr.Column():
                gr.Markdown("### KẾT QUẢ")
                transcript_out = gr.Textbox(label="Raw Transcript", lines=15)
                summary_out = gr.Markdown(label="Meeting Minutes (Tóm tắt)")
                files_out = gr.File(label="Tải kết quả")
                
        submit_btn.click(
            fn=process,
            inputs=[input_file, youtube_url, language, llm_choice, api_key],
            outputs=[transcript_out, summary_out, files_out]
        )
        
    demo.launch(server_name="0.0.0.0", server_port=7860)

if __name__ == "__main__":
    launch()
