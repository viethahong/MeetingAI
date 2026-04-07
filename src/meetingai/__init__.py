__version__ = "0.1.0"

import os

# Tự động thêm ffmpeg từ imageio-ffmpeg vào PATH nếu không có system ffmpeg
try:
    import shutil
    if not shutil.which("ffmpeg"):
        import imageio_ffmpeg
        ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
        ffmpeg_dir = os.path.dirname(ffmpeg_exe)
        os.environ["PATH"] = ffmpeg_dir + os.pathsep + os.environ.get("PATH", "")
except Exception:
    pass
