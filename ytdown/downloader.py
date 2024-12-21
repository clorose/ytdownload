import sys
import os
import asyncio
from typing import Optional, Dict
from queue import Queue
from threading import Thread
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QLineEdit, QPushButton, QComboBox, 
                            QProgressBar, QLabel, QScrollArea, QFrame)
from PyQt6.QtCore import pyqtSignal, QObject, Qt
from yt_dlp import YoutubeDL
from config import Config, DownloadItem

class DownloadSignals(QObject):
    progress = pyqtSignal(str, int)      # url, progress percentage
    status = pyqtSignal(str, str)        # url, status message
    title = pyqtSignal(str, str)         # url, video title
    finished = pyqtSignal(str, str)      # url, downloaded file path

class YouTubeDownloader:
    def __init__(self, download_path: str = Config.DEFAULT_DOWNLOAD_PATH):
        self.download_path = download_path
        self.signals = DownloadSignals()
        self._ensure_download_directory()
        
    def _ensure_download_directory(self):
        os.makedirs(self.download_path, exist_ok=True)
        
    def _get_ydl_opts(self, format: str) -> dict:
        if format not in Config.FORMAT_OPTIONS:
            raise ValueError(f"Unsupported format: {format}")
            
        format_opts = Config.FORMAT_OPTIONS[format]['options']
        
        return {
            **format_opts,
            'outtmpl': os.path.join(self.download_path, '%(title)s.%(ext)s'),
            'progress_hooks': [self._progress_hook],
        }
    
    def _format_size(self, bytes: int) -> str:
        """Convert bytes to human readable size."""
        if bytes < 1000:
            return f"{bytes} B"
        elif bytes < 1000 * 1000:
            return f"{bytes / 1000:.1f} KB"
        elif bytes < 1000 * 1000 * 1000:
            return f"{bytes / 1000 / 1000:.1f} MB"
        else:
            return f"{bytes / 1000 / 1000 / 1000:.1f} GB"

    def _progress_hook(self, d: dict):
        if d['status'] == 'downloading':
            try:
                # ANSI 색상 코드 제거
                percent_str = d['_percent_str'].replace('%', '').strip()
                percent_str = ''.join(c for c in percent_str if c.isdigit() or c == '.')
                percentage = int(float(percent_str))
                self.signals.progress.emit(self.current_url, percentage)
            except Exception as e:
                print(f"Error in progress hook: {e}")
                pass
        elif d['status'] == 'finished':
            self.signals.status.emit(self.current_url, 'Converting...')

    async def get_video_info(self, url: str) -> Optional[dict]:
        """Get video information."""
        try:
            with YoutubeDL({'quiet': True}) as ydl:
                info = ydl.extract_info(url, download=False)
                return info
        except Exception as e:
            self.signals.status.emit(url, f'Error: {str(e)}')
            return None
            
    async def download_video(self, url: str, format: str = 'mp4') -> Optional[str]:
        self.current_url = url
        try:
            # Get initial info for title
            info = await self.get_video_info(url)
            if info:
                self.signals.title.emit(url, info.get('title', ''))
                
            with YoutubeDL(self._get_ydl_opts(format)) as ydl:
                info = ydl.extract_info(url, download=True)
                if info:
                    filename = ydl.prepare_filename(info)
                    # Convert filename extension based on format options
                    if 'postprocessors' in self._get_ydl_opts(format):
                        codec = self._get_ydl_opts(format)['postprocessors'][0]['preferredcodec']
                        filename = os.path.splitext(filename)[0] + '.' + codec
                    
                    self.signals.status.emit(url, 'Complete')
                    self.signals.finished.emit(url, filename)
                    return filename
            return None
        except Exception as e:
            self.signals.status.emit(url, f'Error: {str(e)}')
            return None

class DownloadQueueWorker(Thread):
    def __init__(self, queue: Queue, download_path: str):
        super().__init__()
        self.queue = queue
        self.downloader = YouTubeDownloader(download_path)
        self.daemon = True
        
    def run(self):
        while True:
            item: DownloadItem = self.queue.get()
            if item is None:
                break
                
            asyncio.run(self.downloader.download_video(item.url, item.format))
            self.queue.task_done()

class DownloadItemWidget(QFrame):
    def __init__(self, item: DownloadItem, parent=None):
        super().__init__(parent)
        self.item = item
        self.setup_ui()
        
    def setup_ui(self):
        layout = QHBoxLayout(self)
        
        # Title and URL
        info_layout = QVBoxLayout()
        self.title_label = QLabel(self.item.url)
        self.title_label.setMinimumWidth(500)
        self.title_label.setWordWrap(True)
        info_layout.addWidget(self.title_label)
        
        # Size label
        self.size_label = QLabel("")
        info_layout.addWidget(self.size_label)
        layout.addLayout(info_layout)
        
        # Format
        format_label = QLabel(self.item.format)
        layout.addWidget(format_label)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        layout.addWidget(self.progress_bar)
        
        # Status
        self.status_label = QLabel("Pending")
        self.status_label.setMinimumWidth(100)
        layout.addWidget(self.status_label)
        
        self.setFrameStyle(QFrame.Shape.Box)

    def update_progress(self, progress: int):
        self.progress_bar.setValue(progress)
        
    def update_status(self, status: str):
        self.status_label.setText(status)
        
    def update_title(self, title: str):
        self.title_label.setText(title)
        
    def update_size(self, size: str):
        self.size_label.setText(size)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.download_queue = Queue()
        self.downloads: Dict[str, DownloadItemWidget] = {}
        self.setup_ui()
        self.setup_worker()
        
    def setup_worker(self):
        self.worker = DownloadQueueWorker(self.download_queue, Config.DEFAULT_DOWNLOAD_PATH)
        self.worker.downloader.signals.progress.connect(self.update_progress)
        self.worker.downloader.signals.status.connect(self.update_status)
        self.worker.downloader.signals.title.connect(self.update_title)
        self.worker.downloader.signals.finished.connect(self.download_finished)
        self.worker.start()
        
    def setup_ui(self):
        self.setWindowTitle(Config.APP_NAME)
        self.setMinimumWidth(Config.WINDOW_MIN_WIDTH)
        self.setMinimumHeight(Config.WINDOW_MIN_HEIGHT)
        
        # Main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        
        # Input area
        input_widget = QWidget()
        input_layout = QHBoxLayout(input_widget)
        
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText(Config.URL_PLACEHOLDER)
        input_layout.addWidget(self.url_input)
        
        self.format_combo = QComboBox()
        self.format_combo.addItems([format_info['name'] for format_info in Config.FORMAT_OPTIONS.values()])
        input_layout.addWidget(self.format_combo)
        
        add_button = QPushButton("Add to Queue")
        add_button.clicked.connect(self.add_to_queue)
        input_layout.addWidget(add_button)
        
        layout.addWidget(input_widget)
        
        # Downloads area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        self.downloads_widget = QWidget()
        self.downloads_layout = QVBoxLayout(self.downloads_widget)
        self.downloads_layout.addStretch()
        scroll.setWidget(self.downloads_widget)
        layout.addWidget(scroll)
        
    def add_to_queue(self):
        url = self.url_input.text().strip()
        if not url:
            return
            
        format = self.format_combo.currentText().split()[0]  # Get format key (e.g., 'mp4', 'mp3')
        item = DownloadItem(url=url, format=format)
        
        # Create and add widget to the top of the list
        widget = DownloadItemWidget(item)
        self.downloads_layout.insertWidget(0, widget)
        self.downloads[url] = widget
        
        # Add to download queue
        self.download_queue.put(item)
        self.url_input.clear()
        
    def update_progress(self, url: str, progress: int):
        if url in self.downloads:
            self.downloads[url].update_progress(progress)
            
    def update_status(self, url: str, status: str):
        if url in self.downloads:
            self.downloads[url].update_status(status)
            
    def update_title(self, url: str, title: str):
        if url in self.downloads:
            self.downloads[url].update_title(title)
            
    def download_finished(self, url: str, file_path: str):
        if url in self.downloads:
            widget = self.downloads[url]
            widget.update_status("Complete")
            widget.progress_bar.setValue(100)
            
            # 실제 파일 크기 표시
            try:
                size = os.path.getsize(file_path)
                formatted_size = self.worker.downloader._format_size(size)
                widget.update_size(f"Size: {formatted_size}")
            except Exception as e:
                print(f"Error getting file size: {e}")

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()