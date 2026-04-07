import re
import subprocess
from pathlib import Path
import yt_dlp

def is_youtube_url(url: str) -> bool:
    youtube_regex = r'(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})'
    return bool(re.match(youtube_regex, url))

def download_youtube_audio(url: str, output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': str(output_dir / '%(title)s.%(ext)s'),
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'quiet': True,
        'no_warnings': True,
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(url, download=True)
        # Bỏ đi extention gốc (.webm/.m4a) và thay bằng .mp3 do postprocessor xử lý
        filename = ydl.prepare_filename(info_dict)
        return Path(filename).with_suffix('.mp3')

def extract_audio_from_video(video_path: Path, output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    audio_path = output_dir / f"{video_path.stem}.mp3"
    
    cmd = [
        'ffmpeg', '-y', '-i', str(video_path), 
        '-vn', '-acodec', 'libmp3lame', '-ab', '192k', 
        '-ar', '44100', str(audio_path)
    ]
    
    # Run ffmpeg synchronously
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return audio_path

def prepare_audio(input_source: str, output_dir: Path) -> Path:
    if is_youtube_url(input_source):
        return download_youtube_audio(input_source, output_dir)
    
    input_path = Path(input_source)
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")
        
    video_extensions = {".mp4", ".mov", ".avi", ".mkv", ".webm", ".flv"}
    if input_path.suffix.lower() in video_extensions:
        return extract_audio_from_video(input_path, output_dir)
        
    return input_path
