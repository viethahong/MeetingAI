import gradio as gr
from pathlib import Path
import os
import json
import webbrowser
from .config import Settings
from .pipeline import run_pipeline

SETTINGS_FILE = Path("user_settings.json")

def load_settings():
    if SETTINGS_FILE.exists():
        try:
            return json.loads(SETTINGS_FILE.read_text())
        except Exception:
            return {}
    return {}

def save_settings(data):
    SETTINGS_FILE.write_text(json.dumps(data))

def process_transcription(input_file, youtube_url, language, progress=gr.Progress()):
    if not input_file and not youtube_url:
        raise gr.Error("Lỗi: Vui lòng cung cấp file hoặc YouTube URL")
    
    input_source = youtube_url.strip() if youtube_url else input_file.name
    
    config = Settings()
    config.WHISPER_LANGUAGE = language
    config.LLM_BACKEND = "none" # Chỉ transcribe thôi
    
    def progress_callback(msg: str, p: float):
        progress(p, desc=msg)
    
    # Text thông báo cụ thể khi bắt đầu
    progress(0.05, desc="Đang chép lời, đợi 1 chút....")
    
    try:
        def progress_callback(msg: str, p: float):
            # Luôn giữ text yêu cầu trong suốt quá trình chép lời
            display_msg = "Đang chép lời, đợi 1 chút...."
            if "Summarizing" in msg or "tóm tắt" in msg:
                display_msg = "Đang tóm tắt nội dung..."
            progress(p, desc=display_msg)
            
        result = run_pipeline(input_source, config, progress_callback=progress_callback)
        # Chỉ trả về transcript raw và file download
        return result.transcript, [str(p) for p in result.output_files]
    except Exception as e:
        import traceback
        err_msg = traceback.format_exc()
        raise gr.Error(f"Lỗi chép lời: {str(e)}")

def process_summarization(transcript, language, llm_choice, model, api_key):
    if not transcript or transcript.strip() == "":
        raise gr.Error("Vui lòng thực hiện chép lời trước khi tóm tắt.")
        
    config = Settings()
    config.LLM_BACKEND = llm_choice
    config.GEMINI_API_KEY = api_key if llm_choice == "gemini" else config.GEMINI_API_KEY
    config.GEMINI_MODEL = model if llm_choice == "gemini" else config.GEMINI_MODEL
    config.OLLAMA_MODEL = model if llm_choice == "ollama" else config.OLLAMA_MODEL
    # Bổ sung logic lưu settings
    save_settings({
        "language": language,
        "llm_choice": llm_choice,
        "model": model,
        "api_key": api_key
    })
    
    from .llm_processor import summarize
    try:
        summary = summarize(transcript, config)
        return summary
    except Exception as e:
        raise gr.Error(f"Lỗi tóm tắt: {str(e)}")

def prepare_manual_copy(transcript):
    if not transcript:
        return ""
    return f"Tóm tắt những ý chính quan trọng trong nội dung sau:\n\n{transcript}"

def show_copy_info(text):
    if text and text.strip() != "":
        gr.Info("✅ Đã copy vào clipboard thành công!")
    else:
        gr.Warning("⚠️ Không có nội dung để copy.")

def launch():
    initial_settings = load_settings()
    
    # CSS để làm đẹp giao diện
    css = """
    .section-box { border: 1px solid #e5e7eb; padding: 25px; border-radius: 12px; margin-bottom: 25px; background: #ffffff; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1); }
    .footer-note { font-size: 0.85em; color: #6b7280; margin-top: 10px; font-style: italic; }
    .ai-links { margin-top: 10px; }
    .ai-links a { display: inline-block; padding: 8px 16px; margin-right: 12px; border-radius: 8px; background: #f3f4f6; text-decoration: none; color: #2563eb; font-weight: 600; border: 1px solid #e5e7eb; transition: all 0.2s ease; }
    .ai-links a:hover { background: #dbeafe; border-color: #bfdbfe; transform: translateY(-2px); }
    /* Loading animation style */
    .loading-container { display: flex; align-items: center; justify-content: center; margin-top: 10px; }
    .spinner { width: 40px; height: 40px; border: 4px solid #f3f3f3; border-top: 4px solid #3498db; border-radius: 50%; animation: spin 1s linear infinite; }
    @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
    footer { display: none !important; }
    """

    copy_js = """
    async (text) => {
        if (!text) return;
        try {
            await navigator.clipboard.writeText(text);
            alert("✅ Đã copy vào clipboard!");
        } catch (e) {
            const input = document.createElement('textarea');
            input.value = text;
            input.style.position = 'fixed';
            input.style.left = '-9999px';
            document.body.appendChild(input);
            input.select();
            try {
                document.execCommand('copy');
                alert("✅ Đã copy vào clipboard!");
            } catch (err) {
                alert("❌ Lỗi khi copy!");
            }
            document.body.removeChild(input);
        }
    }
    """

    with gr.Blocks(title="MeetingAI") as demo:
        gr.Markdown("# 🎙️ MeetingAI: Chép lời & Tóm tắt chuyên nghiệp")
        
        # --- SECTION 1: CHÉP LỜI ---
        with gr.Column(elem_classes="section-box"):
            gr.Markdown("## 📋 GIAI ĐOẠN 1: CHÉP LỜI (TRANSCRIPTION)")
            
            with gr.Row():
                with gr.Column(scale=4):
                    input_file = gr.File(label="Tải file Audio/Video lên")
                    youtube_url = gr.Textbox(label="Hoặc dán Link YouTube", placeholder="https://youtube.com/...")
                    lang_select = gr.Dropdown(
                        choices=["Vietnamese", "English", "Japanese", "Korean", "Chinese"], 
                        value=initial_settings.get("language", "Vietnamese"), 
                        label="Ngôn ngữ audio"
                    )
                    transcribe_btn = gr.Button("🚀 Bắt đầu chép lời", variant="primary", size="lg")
                    
                    # Thành phần hiển thị loading gif cao cấp
                    loading_status = gr.HTML("""
                        <div class="loading-container" id="loading-spinner" style="display: none;">
                            <img src="https://i.gifer.com/ZZ5H.gif" width="40" height="40" style="margin-right: 10px;">
                            <span style="color: #666; font-weight: 500;">Hệ thống đang xử lý, vui lòng không tắt trình duyệt...</span>
                        </div>
                    """)
                    
                with gr.Column(scale=6):
                    transcript_raw = gr.Textbox(
                        label="Kết quả chuyển đổi văn bản", 
                        lines=16
                    )
                    with gr.Row():
                        copy_transcript_btn = gr.Button("📋 Copy kết quả văn bản", variant="secondary")
                        download_files = gr.File(label="Tải file tài liệu về máy", file_count="multiple", height=80)

        # --- SECTION 2: TÓM TẮT ---
        with gr.Column(elem_classes="section-box"):
            gr.Markdown("## 📑 GIAI ĐOẠN 2: TÓM TẮT (SUMMARIZATION)")
            
            with gr.Tabs():
                # Tab 1: Tóm tắt bằng AI bên ngoài
                with gr.TabItem("🔗 Gửi tới AI bên ngoài"):
                    gr.Markdown("Hệ thống sẽ chuẩn bị nội dung đi kèm yêu cầu tóm tắt. Bạn chỉ cần copy và dán vào các công cụ AI yêu thích.")
                    prepare_btn = gr.Button("📝 Chuẩn bị nội dung tóm tắt cho AI bên ngoài", variant="primary")
                    manual_text = gr.Textbox(label="Nội dung đã được chuẩn bị", lines=5, interactive=False)
                    copy_manual_btn = gr.Button("📋 Copy nội dung trên", variant="secondary")
                    
                    gr.Markdown("### 🚀 Mở nhanh các trình chat AI:", elem_classes="ai-links")
                    gr.HTML("""
                        <div class='ai-links'>
                            <a href='https://chatgpt.com' target='_blank'>🤖 ChatGPT</a>
                            <a href='https://gemini.google.com' target='_blank'>✨ Google Gemini</a>
                            <a href='https://claude.ai' target='_blank'>🧠 Anthropic Claude</a>
                        </div>
                    """)
                
                # Tab 2: Tóm tắt tự động trong ứng dụng
                with gr.TabItem("🤖 Tóm tắt tự động"):
                    with gr.Row():
                        with gr.Column():
                            llm_choice = gr.Radio(
                                choices=["gemini", "ollama"], 
                                value=initial_settings.get("llm_choice", "gemini"), 
                                label="Nhà cung cấp LLM"
                            )
                            llm_model = gr.Textbox(
                                label="Mô hình (Ví dụ: llama3.1, gemini-2.0-flash)", 
                                value=initial_settings.get("model", "gemini-2.0-flash")
                            )
                            api_key = gr.Textbox(
                                label="Mã API (Token)", 
                                type="password", 
                                value=initial_settings.get("api_key", ""),
                                placeholder="Dán API Key vào đây..."
                            )
                            gr.Markdown(
                                "*Lưu ý: Mã này chỉ được lưu trên máy của bạn, hãy bảo mật, đừng để lộ!*", 
                                elem_classes="footer-note"
                            )
                            auto_summarize_btn = gr.Button("🪄 Thực hiện tóm tắt tự động", variant="primary")
                        
                        with gr.Column():
                            summary_out = gr.Markdown(label="Kết quả tóm tắt")

        # --- EVENT HANDLING ---
        # 1. Click Chép lời (Chuỗi event show loading -> process -> hide loading)
        transcribe_btn.click(
            fn=lambda: gr.update(visible=True),
            outputs=loading_status
        ).then(
            fn=process_transcription,
            inputs=[input_file, youtube_url, lang_select],
            outputs=[transcript_raw, download_files]
        ).then(
            fn=lambda: gr.update(visible=False),
            outputs=loading_status
        )
        
        # 2. Click Chuẩn bị nội dung tóm tắt (Manual)
        prepare_btn.click(
            fn=prepare_manual_copy,
            inputs=[transcript_raw],
            outputs=[manual_text]
        )
        
        # 3. Click Tóm tắt tự động
        auto_summarize_btn.click(
            fn=process_summarization,
            inputs=[transcript_raw, lang_select, llm_choice, llm_model, api_key],
            outputs=[summary_out]
        )
        
        # 4. Copy logic (Client-side JS + Python Notification)
        copy_transcript_btn.click(
            fn=show_copy_info,
            inputs=[transcript_raw],
            js=copy_js
        )
        copy_manual_btn.click(
            fn=show_copy_info,
            inputs=[manual_text],
            js=copy_js
        )

    demo.launch(server_name="0.0.0.0", server_port=7860, css=css)

if __name__ == "__main__":
    launch()
