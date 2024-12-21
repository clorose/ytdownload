# path: ~/Develop/ytdown/ytdown/config.py
import os

class DownloadItem:
    def __init__(self, url: str, format: str):
        self.url = url
        self.format = format

class Config:

    # 현재 디렉토리
    CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

    # 기본 설정
    APP_NAME = "YouTube Downloader"
    DEFAULT_DOWNLOAD_PATH = os.path.join(CURRENT_DIR, "../downloads")
    
    # 다운로드 포맷 설정
    FORMAT_OPTIONS = {
        'mp4': {
            'name': 'mp4 (best quality)',
            'options': {
                'format': 'best',
            }
        },
        'mp3': {
            'name': 'mp3 (192kbps)',
            'options': {
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }]
            }
        },
        'aac': {
            'name': 'aac (original)',
            'options': {
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'm4a',
                    'preferredquality': '0',
                }]
            }
        },
        'aac96': {
            'name': 'aac96 (~3.3MB/5min)',
            'options': {
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'm4a',
                    'preferredquality': '96',
                }]
            }
        },
        'aac64': {
            'name': 'aac64 (~2.2MB/5min)',
            'options': {
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'm4a',
                    'preferredquality': '64',
                }]
            }
        },
        'aac32': {
            'name': 'aac32 (~1.1MB/5min)',
            'options': {
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'm4a',
                    'preferredquality': '32',
                }]
            }
        }
    }
    
    # UI 설정
    WINDOW_MIN_WIDTH = 1000
    WINDOW_MIN_HEIGHT = 600
    URL_PLACEHOLDER = "Enter YouTube URL"   