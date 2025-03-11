# YouTube Downloader

A simple and intuitive application for downloading YouTube videos in various formats and qualities.

## Features

- Download videos from YouTube by URL
- Choose from multiple video formats (MP4, FLV, AVI)
- Select video quality (Best, 4K, 1080p, 720p, 480p)
- Extract audio only (MP3)
- Track download progress
- Select custom save location

## Requirements

- Python 3.6 or higher
- FFmpeg (for audio extraction and format conversion)

## Installation

1. Clone this repository or download the source code

2. Install the required dependencies:

```
pip install -r requirements.txt
```

3. Make sure FFmpeg is installed on your system:
   - Windows: Download from [ffmpeg.org](https://ffmpeg.org/download.html) and add to PATH
   - macOS: `brew install ffmpeg`
   - Linux: `sudo apt install ffmpeg` or equivalent for your distribution

## Usage

1. Run the application:

```
python main.py
```

2. Enter a YouTube URL in the input field
3. Select your desired format and quality
4. Choose whether to download audio only
5. Select a save location or use the default
6. Click the "Download" button
7. Wait for the download to complete

## Legal Notice

This application is for personal use only. Please respect YouTube's Terms of Service and copyright laws. Do not download videos that you do not have permission to download.

## License

MIT License

## Acknowledgements

- [yt-dlp](https://github.com/yt-dlp/yt-dlp) - The core downloading library
- [PyQt6](https://www.riverbankcomputing.com/software/pyqt/) - GUI framework
- [FFmpeg](https://ffmpeg.org/) - Media processing library

Download ffmpeg here: https://drive.google.com/drive/folders/1YWEji2QZbZt9792ovK7xlzfYnAiL35vM?usp=sharing
