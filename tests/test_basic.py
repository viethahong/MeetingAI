import pytest
from meetingai.downloader import is_youtube_url

def test_is_youtube_url():
    assert is_youtube_url("https://www.youtube.com/watch?v=dQw4w9WgXcQ") is True
    assert is_youtube_url("https://youtu.be/dQw4w9WgXcQ") is True
    assert is_youtube_url("https://example.com") is False
