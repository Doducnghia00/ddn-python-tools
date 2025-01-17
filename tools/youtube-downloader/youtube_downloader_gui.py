import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import yt_dlp
import os
import subprocess
from typing import Dict, List
import threading
import platform

class YouTubeDownloader:
    def __init__(self, root):
        self.root = root
        self.root.title("YouTube Video Downloader")
        self.root.geometry("1000x600")
        
        self.videos: Dict[str, dict] = {}
        self.ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': True,
        }
        
        # Store download threads
        self.download_threads: Dict[str, threading.Thread] = {}
        
        self._create_ui()
        
    def _create_ui(self):
        """Create all UI elements with enhanced controls"""
        # URL Input Section
        url_frame = ttk.LabelFrame(self.root, text="Input YouTube URLs", padding=10)
        url_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.url_text = tk.Text(url_frame, height=4)
        self.url_text.pack(fill=tk.X)
        
        button_frame = ttk.Frame(url_frame)
        button_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(button_frame, text="Add Videos", command=self._add_videos).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="Open Output Folder", 
                  command=self._open_output_folder).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="Select Output Folder", 
                  command=self._select_folder).pack(side=tk.LEFT, padx=2)
        
        # Video List Section
        video_frame = ttk.LabelFrame(self.root, text="Video List", padding=10)
        video_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Enhanced Treeview with editable cells and embedded controls
        self.tree = ttk.Treeview(video_frame, 
                                columns=("Title", "Quality", "Status", "Actions"),
                                show="headings",
                                selectmode="browse")
        
        # Configure row height
        style = ttk.Style()
        style.configure('Treeview', rowheight=30)  # Adjust this value as needed
        
        self.tree.heading("Title", text="Title")
        self.tree.heading("Quality", text="Quality")
        self.tree.heading("Status", text="Status")
        self.tree.heading("Actions", text="Actions")
        
        # Set column widths
        self.tree.column("Title", width=400)
        self.tree.column("Quality", width=100)
        self.tree.column("Status", width=150)
        self.tree.column("Actions", width=200)
        
        self.tree.pack(fill=tk.BOTH, expand=True)
        
        # Download All button
        ttk.Button(self.root, text="Download All Videos", 
                  command=self._download_all).pack(pady=10)
        
        # Default download folder
        self.download_folder = os.path.expanduser("~/Downloads")
        
        # Bind double-click event for editing
        self.tree.bind('<Double-1>', self._on_double_click)
        
    def _on_double_click(self, event):
        """Handle double-click event for editing cells"""
        region = self.tree.identify("region", event.x, event.y)
        if region == "cell":
            column = self.tree.identify_column(event.x)
            item = self.tree.identify_row(event.y)
            
            if column == "#1":  # Title column
                self._edit_title_inline(item)
            elif column == "#2":  # Quality column
                self._change_quality_inline(item)
                
    def _edit_title_inline(self, item):
        """Edit title directly in the tree"""
        current_title = self.tree.item(item)['values'][0]
        
        entry = ttk.Entry(self.root)
        entry.insert(0, current_title)
        
        # Get cell bbox
        bbox = self.tree.bbox(item, "#1")
        entry.place(x=bbox[0], y=bbox[1], width=bbox[2])
        
        def save_title(event=None):
            new_title = entry.get()
            if new_title:
                values = list(self.tree.item(item)['values'])
                values[0] = new_title
                self.tree.item(item, values=values)
                self.videos[item]['custom_title'] = new_title
            entry.destroy()
            
        entry.bind('<Return>', save_title)
        entry.bind('<FocusOut>', save_title)
        entry.focus_set()
        
    def _change_quality_inline(self, item):
        """Change quality directly in the tree"""
        qualities = ['2160p', '1440p', '1080p', '720p', '480p', '360p']
        current_quality = self.tree.item(item)['values'][1]
        
        combo = ttk.Combobox(self.root, values=qualities, state='readonly')
        combo.set(current_quality)
        
        # Get cell bbox
        bbox = self.tree.bbox(item, "#2")
        combo.place(x=bbox[0], y=bbox[1], width=bbox[2])
        
        def save_quality(event=None):
            new_quality = combo.get()
            values = list(self.tree.item(item)['values'])
            values[1] = new_quality
            self.tree.item(item, values=values)
            self.videos[item]['selected_quality'] = new_quality
            combo.destroy()
            
        combo.bind('<<ComboboxSelected>>', save_quality)
        combo.bind('<FocusOut>', save_quality)
        combo.focus_set()
        
    def _create_action_buttons(self, video_id):
        """Create action buttons for a video row"""
        frame = ttk.Frame(self.tree)
        
        # Download button
        ttk.Button(frame, text="⬇", width=3,
                  command=lambda: self._download_single(video_id)).pack(side=tk.LEFT, padx=1)
        
        # Delete button
        ttk.Button(frame, text="✖", width=3,
                  command=lambda: self._remove_video(video_id)).pack(side=tk.LEFT, padx=1)
        
        return frame
        
    def _add_videos(self):
        """Add videos from URL input to the list"""
        urls = self.url_text.get("1.0", tk.END).strip().split("\n")
        
        for url in urls:
            if not url.strip():
                continue
                
            try:
                with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=False)
                    video_id = info.get('id', str(hash(url)))
                    
                    self.videos[video_id] = {
                        'info': info,
                        'url': url,
                        'custom_title': info.get('title'),
                        'selected_quality': '720p'
                    }
                    
                    # Insert with action buttons
                    item = self.tree.insert("", tk.END, video_id,
                                          values=(info.get('title'),
                                                 '720p',
                                                 "Pending",
                                                 ""))
                    
                    # Add action buttons
                    action_frame = self._create_action_buttons(video_id)
                    self.tree.set(item, "Actions", "")
                    
                    # Position the action buttons in the Actions column
                    bbox = self.tree.bbox(item, "#4")
                    if bbox:  # Ensure bbox exists
                        action_frame.place(x=bbox[0], y=bbox[1])
                    
            except Exception as e:
                messagebox.showerror("Error", f"Error adding video: {str(e)}")
        
        self.url_text.delete("1.0", tk.END)
        
    def _download_single(self, video_id):
        """Download a single video"""
        if video_id in self.download_threads and self.download_threads[video_id].is_alive():
            return
            
        thread = threading.Thread(target=self._download_video, args=(video_id,))
        thread.daemon = True
        self.download_threads[video_id] = thread
        thread.start()
        
    def _download_all(self):
        """Download all videos in the list"""
        for video_id in self.videos.keys():
            self._download_single(video_id)
            
    def _download_video(self, video_id):
        """Download individual video with progress tracking"""
        try:
            video_data = self.videos[video_id]
            quality = video_data['selected_quality']
            custom_title = video_data['custom_title']
            
            def progress_hook(d):
                if d['status'] == 'downloading' and 'total_bytes' in d:
                    progress = (d['downloaded_bytes'] / d['total_bytes']) * 100
                    self.tree.set(video_id, "Status", f"{progress:.1f}%")
                
            ydl_opts = {
                'format': f'bestvideo[height<={quality[:-1]}]+bestaudio/best[height<={quality[:-1]}]',
                'outtmpl': os.path.join(self.download_folder, f'{custom_title}.%(ext)s'),
                'progress_hooks': [progress_hook],
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([video_data['url']])
                
            self.tree.set(video_id, "Status", "Completed")
            
        except Exception as e:
            self.tree.set(video_id, "Status", f"Error: {str(e)}")
            
    def _remove_video(self, video_id):
        """Remove video from the list"""
        self.tree.delete(video_id)
        self.videos.pop(video_id, None)
        
    def _select_folder(self):
        """Open dialog to select download folder"""
        folder = filedialog.askdirectory(initialdir=self.download_folder)
        if folder:
            self.download_folder = folder
            
    def _open_output_folder(self):
        """Open the current output folder in file explorer"""
        if platform.system() == "Windows":
            os.startfile(self.download_folder)
        elif platform.system() == "Darwin":  # macOS
            subprocess.Popen(["open", self.download_folder])
        else:  # Linux
            subprocess.Popen(["xdg-open", self.download_folder])

if __name__ == "__main__":
    root = tk.Tk()
    app = YouTubeDownloader(root)
    root.mainloop()