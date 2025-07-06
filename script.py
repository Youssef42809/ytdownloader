from pytube import YouTube
import yt_dlp
import tkinter as tk
from tkinter import messagebox, filedialog, ttk
import os
import logging

# Configure logging to suppress yt-dlp warnings
logging.basicConfig(level=logging.ERROR)

# Global variables
save_path = os.path.join(os.path.expanduser("~"), "Downloads")
download_format = 'mp4'  # Default format
download_type = 'video'  # Default type (video or playlist)


# Function to choose the download folder
def choose_folder():
    global save_path
    user_choice = filedialog.askdirectory(initialdir=save_path)
    if user_choice:
        save_path = user_choice
        folder_label.config(text=f"Folder: {save_path}")


# Function to handle progress updates
def progress_hook(d):
    if d['status'] == 'downloading':
        downloaded = d.get('_percent_str', '0%').strip()
        speed = d.get('_speed_str', '?').strip()
        eta = d.get('_eta_str', '?').strip()
        progress_label.config(text=f"Progress: {downloaded} at {speed} ETA {eta}")

        if '_total_bytes' in d and '_downloaded_bytes' in d:
            try:
                progress = (float(d['_downloaded_bytes']) / float(d['_total_bytes'])) * 100
                progress_bar['value'] = progress
            except:
                pass
        root.update_idletasks()
    elif d['status'] == 'finished':
        progress_label.config(text="Finalizing download...")


# Function to download a single video
def download_video():
    global save_path, download_format
    video_url = url_entry.get().strip()

    if not video_url:
        messagebox.showwarning("Input Error", "Please enter a YouTube URL.")
        return

    if not save_path:
        messagebox.showwarning("Folder Error", "Please select a download folder.")
        return

    # yt-dlp options with better error handling
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'ignoreerrors': True,
        'outtmpl': f'{save_path}/%(title)s.%(ext)s',
        'progress_hooks': [progress_hook],
        'extract_flat': False,
    }

    if download_format == 'mp4':
        ydl_opts.update({
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            'merge_output_format': 'mp4',
        })
    else:  # For MP3
        ydl_opts.update({
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        })

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            progress_label.config(text="Starting download...")
            progress_bar['value'] = 0
            root.update_idletasks()

            info = ydl.extract_info(video_url, download=False)
            if 'entries' in info:
                # This is a playlist, but user selected single video
                messagebox.showwarning("Input Error", "URL appears to be a playlist. Please use the playlist option.")
                return

            ydl.download([video_url])
            messagebox.showinfo("Success", f"Download completed as {download_format.upper()}!")
            progress_label.config(text="Download completed!")
            progress_bar['value'] = 100
    except Exception as e:
        messagebox.showerror("Error", f"Download error: {str(e)}")
        progress_label.config(text="Download failed")
        progress_bar['value'] = 0


# Function to download a playlist
def download_playlist():
    global save_path, download_format
    playlist_url = url_entry.get().strip()

    if not playlist_url:
        messagebox.showwarning("Input Error", "Please enter a YouTube playlist URL.")
        return

    if not save_path:
        messagebox.showwarning("Folder Error", "Please select a download folder.")
        return

    # Create a subfolder for the playlist
    playlist_name = "YouTube_Playlist"
    try:
        with yt_dlp.YoutubeDL({'quiet': True, 'ignoreerrors': True}) as ydl:
            info = ydl.extract_info(playlist_url, download=False)
            if 'title' in info:
                playlist_name = info['title'].replace('/', '_')  # Remove invalid chars
    except:
        pass

    playlist_path = os.path.join(save_path, playlist_name)
    os.makedirs(playlist_path, exist_ok=True)

    # yt-dlp options for playlist with better error handling
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'ignoreerrors': True,
        'progress_hooks': [progress_hook],
        'extract_flat': False,
    }

    if download_format == 'mp4':
        ydl_opts.update({
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            'merge_output_format': 'mp4',
            'outtmpl': f'{playlist_path}/%(playlist_index)s - %(title)s.%(ext)s',
        })
    else:  # For MP3
        ydl_opts.update({
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'outtmpl': f'{playlist_path}/%(playlist_index)s - %(title)s.%(ext)s',
        })

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            progress_label.config(text="Starting playlist download...")
            progress_bar['value'] = 0
            root.update_idletasks()

            ydl.download([playlist_url])
            messagebox.showinfo("Success", f"Playlist download completed as {download_format.upper()}!")
            progress_label.config(text="Playlist download completed!")
            progress_bar['value'] = 100
    except Exception as e:
        messagebox.showerror("Error", f"Playlist download error: {str(e)}")
        progress_label.config(text="Playlist download failed")
        progress_bar['value'] = 0


# Function to start download based on selected type
def start_download():
    global download_format, download_type
    download_format = format_var.get()
    download_type = type_var.get()

    # Clear previous progress
    progress_label.config(text="Preparing download...")
    progress_bar['value'] = 0
    root.update_idletasks()

    if download_type == 'video':
        download_video()
    else:
        download_playlist()


# Create the main window
root = tk.Tk()
root.title("YouTube Video Downloader")
root.geometry("600x450")
root.configure(bg="#65AFD4")

# Try to set the icon (comment out if you don't have the icon file)
try:
    icon = tk.PhotoImage(file="Youtube video downloader.png")
    root.iconphoto(True, icon)
except:
    pass

# Styling for better design
header_label = tk.Label(root, text="YouTube Downloader", font=("Helvetica", 16, "bold"), bg="#48CAE4")
header_label.pack(pady=10)

# URL entry label and field
url_label = tk.Label(root, text="Enter YouTube URL:", font=("Helvetica", 12), bg="#65AFD4")
url_label.pack(pady=5)
url_entry = tk.Entry(root, width=60)
url_entry.pack(pady=5)

# Download type selection
type_frame = tk.Frame(root, bg="#65AFD4")
type_frame.pack(pady=5)

type_label = tk.Label(type_frame, text="Download type:", bg="#65AFD4", font=("Helvetica", 10))
type_label.pack(side=tk.LEFT)

type_var = tk.StringVar(value='video')
video_type_radio = tk.Radiobutton(type_frame, text="Single Video", variable=type_var, value='video', bg="#48CAE4",
                                  font=("Helvetica", 10))
playlist_type_radio = tk.Radiobutton(type_frame, text="Playlist", variable=type_var, value='playlist', bg="#48CAE4",
                                     font=("Helvetica", 10))
video_type_radio.pack(side=tk.LEFT, padx=5)
playlist_type_radio.pack(side=tk.LEFT, padx=5)

# Folder selection button and label
choose_folder_button = tk.Button(root, text="Choose Download Folder", command=choose_folder, bg="#F72585", fg="white",
                                 font=("Helvetica", 10))
choose_folder_button.pack(pady=5)

folder_label = tk.Label(root, text=f"Folder: {save_path}", bg="#48CAE4", font=("Helvetica", 10))
folder_label.pack(pady=5)

# Format selection radio buttons
format_frame = tk.Frame(root, bg="#65AFD4")
format_frame.pack(pady=5)

format_label = tk.Label(format_frame, text="Select format:", bg="#65AFD4", font=("Helvetica", 10))
format_label.pack(side=tk.LEFT)

format_var = tk.StringVar(value='mp4')
mp4_radio = tk.Radiobutton(format_frame, text="MP4", variable=format_var, value='mp4', bg="#48CAE4",
                           font=("Helvetica", 10))
mp3_radio = tk.Radiobutton(format_frame, text="MP3", variable=format_var, value='mp3', bg="#48CAE4",
                           font=("Helvetica", 10))
mp4_radio.pack(side=tk.LEFT, padx=5)
mp3_radio.pack(side=tk.LEFT, padx=5)

# Progress label and bar
progress_label = tk.Label(root, text="Progress: Not started", bg="#65AFD4", font=("Helvetica", 10))
progress_label.pack(pady=5)
progress_bar = ttk.Progressbar(root, length=400, mode='determinate')
progress_bar.pack(pady=5)

# Download button
download_button = tk.Button(root, text="Start Download", command=start_download, bg="#DA4195", fg="white",
                            font=("Helvetica", 12))
download_button.pack(pady=20)

# Run the main loop
root.mainloop()
