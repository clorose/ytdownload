# Youtube Downloader

- Got tired of manually downloading D&D background music from YouTube, so I made this simple downloader. Just a convenient tool that gets the job done.
- This is a GUI app that can download videos in different formats, built with PyQt6 and yt-dlp.

## Features

- Simple and intuitive GUI interface
- Multiple format support:
  - MP4 (best quality)
  - MP3 (192kbps)
  - AAC (original quality)
  - AAC96 (~3.3MB/5min)
  - AAC64 (~2.2MB/5min)
  - AAC32 (~1.1MB/5min)
- Download queue system
- Real-time progress tracking
- Final file size display

## Prerequisites

Make sure you have the following installed:
- Python 3.8 or higher
- Poetry (Python package manager)
- FFmpeg (for audio extraction)

### FFmpeg Installation

#### macOS
```bash
brew install ffmpeg
```

#### Ubuntu/Debian
```bash
sudo apt install ffmpeg
```

#### Windows
Download from [FFmpeg website](https://ffmpeg.org/download.html)

## Installation

1. Clone the repository
```bash
git clone git@github.com:clorose/ytdownload.git
cd ytdownload
```

2. Install dependencies using Poetry
```bash
poetry install
```

## Usage

There are two ways to run the application:

1. Using Poetry shell:
```bash
poetry shell
cd src
python downloader.py
```

2. Direct execution through Poetry:
```bash
poetry run python src/downloader.py
```

## How to Use

1. Launch the application
2. Paste a YouTube URL into the input field
3. Select desired format from the dropdown menu
4. Click "Add to Queue" to start downloading
5. Monitor progress in the downloads area
6. Files will be saved to the 'downloads' directory

## Project Structure

```
youtube-downloader/
├── src/
│   ├── downloader.py    # Main application file
│   └── config.py        # Configuration settings
├── downloads/           # Downloaded files directory
├── pyproject.toml       # Poetry configuration
└── README.md           # This file
```

## Acknowledgments

- [yt-dlp](https://github.com/yt-dlp/yt-dlp) for the YouTube download functionality
- [PyQt6](https://www.riverbankcomputing.com/software/pyqt/) for the GUI framework