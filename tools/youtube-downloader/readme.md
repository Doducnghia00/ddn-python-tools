# YouTube Video Downloader

A Python tool for downloading YouTube videos with both GUI and CLI interfaces.

## Requirements

```bash
pip install yt-dlp
```

## GUI Version (youtube_downloader_gui.py)

### Features
- Multiple video downloads
- Quality selection (360p to 2160p)
- Custom output directory
- Progress tracking
- Editable video titles
- Queue management

### Usage
1. Run the GUI:
```bash
python youtube_downloader_gui.py
```

2. How to use:
- Paste YouTube URLs (one per line) in the text area
- Click "Add Videos" to add them to the queue
- Double-click title or quality to edit
- Use ⬇ button to download individual videos
- Use ✖ button to remove videos
- Click "Download All Videos" to batch download
- Use "Select Output Folder" to change save location

## CLI Version (youtube_downloader_cli.py)

### Features
- Multiple URL support
- Quality selection
- Custom output directory
- Progress tracking in terminal

### Usage Examples

1. Download a single video:
```bash
python youtube_downloader_cli.py -u "https://www.youtube.com/watch?v=VIDEO_ID"
```

2. Download multiple videos:
```bash
python youtube_downloader_cli.py -u "URL1" "URL2" "URL3"
```

3. Select quality (360p to 2160p):
```bash
python youtube_downloader_cli.py -u "URL" -q 1080p
```

4. Custom output directory:
```bash
python youtube_downloader_cli.py -u "URL" -o "/path/to/folder"
```

### CLI Arguments
- `-u` or `--urls`: YouTube URLs (required, space-separated)
- `-q` or `--quality`: Video quality (optional, default: 720p)
- `-o` or `--output`: Output directory (optional)
- `-h` or `--help`: Show help message

## Notes
- Default download location: `~/Downloads`
- Supported qualities: 360p, 480p, 720p, 1080p, 1440p, 2160p
- Files are saved in the best available format