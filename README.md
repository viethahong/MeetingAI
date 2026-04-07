# 🎙️ MeetingAI: Local-first Transcription & Summarization

MeetingAI là công cụ mã nguồn mở giúp chuyển đổi nội dung cuộc họp từ âm thanh/video sang văn bản (Transcription) và tự động tóm tắt biên bản họp (Summarization) bằng trí tuệ nhân tạo.

**Quyền riêng tư là ưu tiên hàng đầu**: Dự án hỗ trợ chạy hoàn toàn local trên Apple Silicon (M-series) và hỗ trợ Docker (với Faster-Whisper).

---

## ✨ Tính năng nổi bật

-   **Dual-Backend Whisper**: Tự động nhận diện thiết bị. Ưu tiên **MLX-Whisper** (tối ưu cực cao cho Apple Silicon Mac) và tự động chuyển sang **Faster-Whisper** khi chạy trên các nền tảng khác hoặc Docker.
-   **Hỗ trợ đa phương tiện**: Chấp nhận mọi định dạng phổ biến (.mp3, .mp4, .mov, .mkv, .wav...) hoặc tải trực tiếp âm thanh từ link **YouTube**.
-   **Tóm tắt thông minh**: Hỗ trợ Google Gemini (Cloud) hoặc **Ollama** (100% Offline/Private) để tạo biên bản họp theo cấu trúc chuẩn: Chủ đề, Thảo luận, Quyết định, Action Items.
-   **Cơ chế Fail-safe**: Nếu bạn chưa thiết lập API Key hoặc LLM gặp lỗi, hệ thống vẫn ưu tiên xử lý và lưu trữ bản ghi văn bản (Raw Transcript) để không làm gián đoạn công việc của bạn.
-   **Giao diện hiện đại**: Cung cấp cả Web UI (Gradio) dễ sử dụng và CLI cho người dùng chuyên sâu.

---

## 🚀 Cài đặt nhanh (Quick Start)

### 1. Yêu cầu hệ thống
Đảm bảo máy của bạn đã cài đặt `ffmpeg`, `uv`, và `yt-dlp`. 

#### 🍎 macOS (Apple Silicon / Intel)
```bash
brew install ffmpeg uv yt-dlp
```

#### 🪟 Windows
1.  **Cài đặt `uv`**: Mở PowerShell và chạy:
    ```powershell
    powershell -c "irmo https://astral.sh/uv/install.ps1 | iex"
    ```
2.  **Cài đặt `ffmpeg`**: Khuyên dùng [Chocolatey](https://chocolatey.org/):
    ```powershell
    choco install ffmpeg
    ```
    Hoặc tải bản build sẵn tại [gyan.dev](https://www.gyan.dev/ffmpeg/builds/) và thêm vào `PATH`.
3.  **Cài đặt `yt-dlp`**:
    ```powershell
    pip install yt-dlp
    ```

#### 🐧 Linux (Ubuntu/Debian)
```bash
sudo apt update && sudo apt install ffmpeg
curl -LsSf https://astral.sh/uv/install.sh | sh
```

---

## 💻 Khả năng tương thích (Compatibility)

Dự án sử dụng cơ chế **Dual-Backend** để tối ưu hóa hiệu năng trên mọi thiết bị:

| Phần cứng | Backend Whisper | Ghi chú |
| :--- | :--- | :--- |
| **Mac M1/M2/M3/M4** | `mlx-whisper` | Tốc độ nhanh nhất, tối ưu Unified Memory. |
| **Windows / Linux / Mac Intel** | `faster-whisper` | Sử dụng CPU hoặc NVIDIA GPU (nếu có CUDA). |
| **Docker** | `faster-whisper` | Chạy ổn định trên mọi môi trường container. |

### 2. Cài đặt dự án
```bash
# Clone dự án (nếu bạn tải qua git)
# git clone https://github.com/your-username/MeetingAI.git
# cd MeetingAI

# Cài đặt môi trường ảo và dependencies tự động
uv sync
```

### 3. Cấu hình biến môi trường
Tạo file `.env` từ file mẫu:
```bash
cp .env.example .env
```
Mở tệp `.env` và cập nhật thông tin cần thiết:
- `GEMINI_API_KEY`: Lấy tại Google AI Studio.
- `LLM_BACKEND`: Chọn `gemini`, `ollama` hoặc `none`.

---

## 🖥️ Cách sử dụng

### Sử dụng Web UI (Gradio)
Đây là cách dễ dàng nhất để trải nghiệm kéo-thả file.
```bash
uv run meetingai-ui
```
Truy cập: [http://localhost:7860](http://localhost:7860)

### Sử dụng CLI (Dòng lệnh)
Phù hợp cho việc tự động hóa:
```bash
uv run meetingai path/to/your/video.mp4 --llm gemini --language Vietnamese
```

---

## 🐳 Triển khai với Docker

MeetingAI hỗ trợ Docker để chạy trên server hoặc môi trường không phải macOS.
```bash
docker compose up --build
```
*Lưu ý: Phiên bản Docker sử dụng `faster-whisper`. Hãy đảm bảo bạn đã cấp đủ RAM và CPU cho container.*

---

## 📂 Cấu trúc thư mục (Project Structure)

```text
MeetingAI/
├── src/meetingai/      # Mã nguồn chính
│   ├── app.py          # Giao diện Web (Gradio)
│   ├── cli.py          # Giao diện dòng lệnh (Click)
│   ├── transcriber.py  # Xử lý Dual-Backend Whisper
│   ├── llm_processor.py# Kết nối Gemini/Ollama
│   └── downloader.py   # Xử lý YouTube & Trích xuất ffmpeg
├── tests/              # Kiểm thử
├── output/             # Thư mục chứa kết quả (gitignored)
├── Dockerfile          # Cấu hình Docker
└── pyproject.toml      # Quản lý dependencies (uv)
```

---

## 🔐 Bảo mật & Quyền riêng tư
- API Key của bạn chỉ được lưu tại file `.env` local.
- Khi chọn backend `ollama`, dữ liệu âm thanh và văn bản không bao giờ rời khỏi máy của bạn.

---

## 📜 Giấy phép
Dự án được phát hành dưới giấy phép **MIT**. Hoàn toàn miễn phí cho mục đích cá nhân và thương mại.

---

## 🤝 Đóng góp
Mọi đóng góp (Pull Request, Bug Report) đều được hoan nghênh để cải thiện dự án tốt hơn cho cộng đồng Việt Nam.
