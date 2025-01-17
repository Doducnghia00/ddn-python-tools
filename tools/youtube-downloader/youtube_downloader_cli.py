import yt_dlp
import argparse
import os
from typing import List, Dict
import sys

class YouTubeDownloaderCLI:
    def __init__(self):
        self.download_folder = os.path.expanduser("~/Downloads")
        self.qualities = ['2160p', '1440p', '1080p', '720p', '480p', '360p']
        
    def progress_hook(self, d):
        """Display download progress"""
        if d['status'] == 'downloading':
            if 'total_bytes' in d:
                progress = (d['downloaded_bytes'] / d['total_bytes']) * 100
                sys.stdout.write(f"\rDownloading: {progress:.1f}%")
            else:
                sys.stdout.write(f"\rDownloading: {d['downloaded_bytes']} bytes")
            sys.stdout.flush()
        elif d['status'] == 'finished':
            print("\nDownload completed!")

    def download_video(self, url: str, quality: str = '720p', custom_title: str = None) -> bool:
        """Download a single video"""
        try:
            # Get video info first
            with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
                info = ydl.extract_info(url, download=False)
                title = custom_title or info.get('title')
                print(f"\nVideo title: {title}")

            # Download options
            ydl_opts = {
                'format': f'bestvideo[height<={quality[:-1]}]+bestaudio/best[height<={quality[:-1]}]',
                'outtmpl': os.path.join(self.download_folder, f'{title}.%(ext)s'),
                'progress_hooks': [self.progress_hook],
            }

            # Download video
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            return True

        except Exception as e:
            print(f"\nError downloading video: {str(e)}")
            return False

    def download_multiple(self, urls: List[str], quality: str = '720p'):
        """Download multiple videos"""
        total = len(urls)
        success = 0

        print(f"\nStarting download of {total} videos...")
        for i, url in enumerate(urls, 1):
            print(f"\nProcessing video {i}/{total}")
            if self.download_video(url, quality):
                success += 1

        print(f"\nCompleted: {success}/{total} videos downloaded successfully")

def main():
    parser = argparse.ArgumentParser(description='YouTube Video Downloader CLI')
    parser.add_argument('-u', '--urls', nargs='+', required=True,
                        help='YouTube URLs to download (space-separated)')
    parser.add_argument('-q', '--quality', choices=['2160p', '1440p', '1080p', '720p', '480p', '360p'],
                        default='720p', help='Video quality (default: 720p)')
    parser.add_argument('-o', '--output', help='Output directory (default: ~/Downloads)')
    
    args = parser.parse_args()
    
    downloader = YouTubeDownloaderCLI()
    
    if args.output:
        downloader.download_folder = args.output
        if not os.path.exists(args.output):
            os.makedirs(args.output)
    
    downloader.download_multiple(args.urls, args.quality)

if __name__ == "__main__":
    main()
