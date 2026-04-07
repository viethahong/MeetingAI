# MeetingAI - Implementation Plan

## Context

Xây dựng MeetingAI từ con số 0 - một công cụ open source chạy local, chuyển đổi audio/video cuộc họp thành text (whisper) và tóm tắt biên bản họp (LLM). Ưu tiên quyền riêng tư, chạy trên Apple Silicon, đóng gói sẵn sàng cho GitHub.

**Hiện trạng**: Thư mục `/Users/viethahong/Documents/MeetingAI/` trống. Máy M4, macOS 26.2, Python 3.9.6 (system). Chưa có brew, ffmpeg, yt-dlp.

**Quyết định đã chốt**:
- Package manager: `uv` + `pyproject.toml` (kèm hướng dẫn pip trong README cho người dùng phổ thông)
- Web UI: Gradio
- Whisper: `mlx-whisper` only (bổ sung faster-whisper cho Docker sau)
- Secrets: dùng `.env`, KHÔNG hardcode

---

## Project Structure

```
MeetingAI/
├── pyproject.toml
├── .python-version             # "3.12"
├── .env.example
├── .gitignore
├── LICENSE                     # MIT
├── README.md
├── Makefile
├── Dockerfile
├── docker-compose.yml
│
├── src/meetingai/
│   ├── __init__.py
│   ├── config.py               # pydantic-settings, load .env
│   ├── downloader.py           # YouTube download + video -> audio
│   ├── transcriber.py          # mlx-whisper wrapper
│   ├── llm_processor.py        # Gemini API / Ollama
│   ├── prompts.py              # Meeting minutes prompt template
│   ├── pipeline.py             # Orchestrator: download -> transcribe -> summarize
│   ├── cli.py                  # CLI entry point (click)
│   └── app.py                  # Gradio Web UI
│
├── tests/
│   ├── conftest.py
│   ├── test_downloader.py
│   ├── test_transcriber.py
│   └── test_pipeline.py
│
└── output/                     # Default output (gitignored)
```

---

## Phase 0: Bootstrap (Prerequisites)

1. Cài Homebrew (nếu chưa có):
   ```bash
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   ```
2. Cài dependencies hệ thống:
   ```bash
   brew install ffmpeg uv yt-dlp
   ```
3. Khởi tạo project:
   ```bash
   cd /Users/viethahong/Documents/MeetingAI
   uv init --lib --name meetingai
   uv python install 3.12
   uv python pin 3.12
   git init
   ```
4. Tạo `.gitignore`, `LICENSE` (MIT), `.env.example`

---

## Phase 1: Core Modules

### 1.1 `src/meetingai/config.py`
- Class `Settings(BaseSettings)` dùng pydantic-settings
- Load từ `.env`:
  - `GEMINI_API_KEY` - API key cho Gemini
  - `OLLAMA_BASE_URL` - URL Ollama (default: `http://localhost:11434`)
  - `OLLAMA_MODEL` - Model Ollama (default: `llama3.1`)
  - `WHISPER_MODEL` - Model whisper (default: `large-v3-turbo`)
  - `WHISPER_LANGUAGE` - Ngôn ngữ (default: `Vietnamese`)
  - `OUTPUT_DIR` - Thư mục output (default: `./output`)
  - `LLM_BACKEND` - Backend LLM: `gemini` | `ollama` | `none`

### 1.2 `src/meetingai/downloader.py`
- `is_youtube_url(url: str) -> bool` - Nhận diện link YouTube
- `download_youtube_audio(url: str, output_dir: Path) -> Path` - Dùng `yt_dlp` Python lib (không subprocess), trả về path file .mp3
- `extract_audio_from_video(video_path: Path, output_dir: Path) -> Path` - Dùng subprocess ffmpeg tách audio từ video (.mp4, .mov, .avi, .mkv, .webm)
- `prepare_audio(input_source: str, output_dir: Path) -> Path` - Router chính:
  - YouTube URL -> `download_youtube_audio()`
  - Video file -> `extract_audio_from_video()`
  - Audio file -> trả về path gốc

### 1.3 `src/meetingai/transcriber.py`
- `TranscriptionResult` dataclass:
  - `text: str` - Full transcript text
  - `language: str` - Ngôn ngữ phát hiện/chỉ định
  - `segments: list[dict]` - Segment-level data (timestamps)
- `transcribe(audio_path: Path, language: str, model: str) -> TranscriptionResult`
  - Dùng `mlx_whisper.transcribe()`
  - Model repo: `mlx-community/whisper-{model}` (e.g., `mlx-community/whisper-large-v3-turbo`)
  - Trả về TranscriptionResult

### 1.4 `src/meetingai/prompts.py`
- Prompt template cho meeting minutes (Vietnamese mặc định):
  ```
  ## Biên bản họp
  - **Chủ đề chính**: (đoán từ nội dung)
  - **Các điểm thảo luận chính**: (bullet points)
  - **Quyết định**: (nếu có)
  - **Hành động tiếp theo** (bảng: Người - Việc - Deadline)
  - **Tóm tắt**: (3-5 câu)
  ```
- Format output: Markdown chuẩn

### 1.5 `src/meetingai/llm_processor.py`
- `summarize_with_gemini(transcript: str, api_key: str) -> str`
  - Dùng `google-genai` SDK
  - Model: `gemini-2.0-flash` (nhanh, rẻ)
- `summarize_with_ollama(transcript: str, base_url: str, model: str) -> str`
  - HTTP POST qua `httpx` tới `/api/generate`
  - Hoàn toàn offline, privacy 100%
- `summarize(transcript: str, config: Settings) -> str`
  - Router theo `config.llm_backend`

### 1.6 `src/meetingai/pipeline.py`
- `PipelineResult` dataclass:
  - `audio_path: Path`
  - `transcript: str`
  - `summary: str | None`
  - `output_files: list[Path]`
- `run_pipeline(input_source: str, config: Settings, progress_callback) -> PipelineResult`
  - Step 1 (10%): Download/extract audio
  - Step 2 (30%): Transcribe với whisper
  - Step 3 (70%): Summarize với LLM (nếu backend != none)
  - Step 4 (90%): Lưu file .txt và .md vào output_dir
  - `progress_callback(message: str, progress: float)` - hook cho Gradio progress bar

---

## Phase 2: CLI (`src/meetingai/cli.py`)

- Entry point: `uv run meetingai <file_or_url>`
- Options:
  - `--language` / `-l` : Ngôn ngữ (default: Vietnamese)
  - `--llm` : gemini / ollama / none (default: gemini)
  - `--output-dir` / `-o` : Thư mục output
  - `--model` : Whisper model (default: large-v3-turbo)
- Đăng ký trong `pyproject.toml`:
  ```toml
  [project.scripts]
  meetingai = "meetingai.cli:main"
  ```

---

## Phase 3: Web UI (`src/meetingai/app.py`)

Gradio Blocks interface:

**Input column (trái)**:
- File upload component (drag-drop, accept audio + video)
- Textbox cho YouTube URL
- Dropdown: Language (Vietnamese, English, Japanese, ...)
- Radio: LLM Backend (gemini / ollama / none)
- Textbox: API Key (password type)
- Button: "Bắt đầu xử lý" (primary)

**Output column (phải)**:
- Textbox: Raw transcript (scrollable, 15 dòng)
- Markdown: Meeting minutes summary
- File download: Tải .txt và .md

**Progress bar**: `gr.Progress()` wired vào pipeline callback

**Entry point**:
```toml
[project.scripts]
meetingai-ui = "meetingai.app:launch"
```

---

## Phase 4: Docker + Open Source

### Dockerfile
```dockerfile
FROM python:3.12-slim
RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv
WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen
COPY src/ src/
EXPOSE 7860
CMD ["uv", "run", "meetingai-ui"]
```

> **Note**: Docker version sẽ cần chuyển sang `faster-whisper` vì mlx-whisper chỉ chạy trên macOS. Sẽ bổ sung dual backend sau.

### docker-compose.yml
```yaml
services:
  meetingai:
    build: .
    ports:
      - "7860:7860"
    volumes:
      - ./output:/app/output
    env_file:
      - .env
```

### Makefile
```makefile
install:
	uv sync

run:
	uv run meetingai $(ARGS)

ui:
	uv run meetingai-ui

docker:
	docker compose up --build

test:
	uv run pytest
```

### README.md
- Giới thiệu project + screenshot
- Quick Start (native macOS + Docker)
- CLI usage examples
- Web UI guide
- Configuration reference (.env)
- Contributing guide
- License (MIT)

---

## Dependencies (`pyproject.toml`)

```toml
[project]
name = "meetingai"
version = "0.1.0"
description = "Local-first meeting transcription and summarization tool"
requires-python = ">=3.11"
license = "MIT"

dependencies = [
    "yt-dlp>=2024.0",
    "mlx-whisper>=0.4",
    "click>=8.0",
    "gradio>=5.0",
    "pydantic-settings>=2.0",
    "google-genai>=1.0",
    "httpx>=0.27",
]

[project.optional-dependencies]
dev = ["pytest>=8.0", "ruff>=0.8"]

[project.scripts]
meetingai = "meetingai.cli:main"
meetingai-ui = "meetingai.app:launch"
```

---

## Implementation Order

| Step | File(s) | Mô tả |
|------|---------|--------|
| 0 | System | Cài brew, uv, ffmpeg, git init |
| 1 | `pyproject.toml`, `.gitignore`, `LICENSE`, `.env.example` | Project skeleton |
| 2 | `src/meetingai/__init__.py`, `config.py` | Settings class |
| 3 | `src/meetingai/downloader.py` | Audio download/extract |
| 4 | `src/meetingai/transcriber.py` | Whisper transcription |
| 5 | `src/meetingai/prompts.py` | Prompt template |
| 6 | `src/meetingai/llm_processor.py` | Gemini/Ollama integration |
| 7 | `src/meetingai/pipeline.py` | Orchestrator |
| 8 | `src/meetingai/cli.py` | CLI entry point |
| 9 | `src/meetingai/app.py` | Gradio UI |
| 10 | `Dockerfile`, `docker-compose.yml`, `Makefile` | Containerization |
| 11 | `README.md` | Documentation |
| 12 | `tests/` | Unit tests |

---

## Verification Checklist

- [ ] **Phase 1**: `uv run meetingai test.mp3` -> tạo file `.txt` trong `output/`
- [ ] **Phase 2**: `uv run meetingai test.mp3 --llm gemini` -> tạo thêm file `.md` summary
- [ ] **Phase 3**: `uv run meetingai-ui` -> mở browser tại `localhost:7860`, kéo thả file, thấy kết quả 2 cột
- [ ] **Phase 4**: `docker compose up` -> chạy được trên máy khác
- [ ] **Open Source**: README đầy đủ, không có secrets trong code, LICENSE MIT

---

## Security Notes

- **CRITICAL**: Revoke Telegram bot token trong file `voice_transcribe.sh` (dòng 10: `8629300588:AAFaX1NKNUg1PXeRD82o0eLp0nm3bjfFpes`) qua BotFather TRƯỚC khi publish bất kỳ thứ gì
- Tất cả secrets đều qua `.env` (gitignored)
- `.env.example` chỉ chứa key names, không có values
- Không bao giờ commit file `.env`
