import os
import sys
import subprocess
import urllib.request
import zipfile
import shutil
import tkinter as tk
from tkinter import messagebox
import threading

# --- Music directory ---
path_music_dir = os.path.join(os.getcwd(), "music")
os.makedirs(path_music_dir, exist_ok=True)

# --- Check if running in a PyInstaller build ---
def is_frozen():
    return getattr(sys, 'frozen', False)

# --- Set paths for ffmpeg and yt-dlp ---
if is_frozen():
    base_path = getattr(sys, "_MEIPASS", "")
    bin_path = os.path.join(base_path, "ffmpeg", "bin")  # bundled ffmpeg
    ytdlp_cmd = os.path.join(base_path, "yt-dlp_bin", "yt-dlp.exe")  # bundled yt-dlp CLI
else:
    # Python mode: auto-install yt-dlp and ffmpeg
    bin_path = os.path.join(os.environ['USERPROFILE'], "ffmpeg", "bin")
    ytdlp_cmd = "yt-dlp"  # system or installed yt-dlp

    # --- Install yt-dlp if missing ---
    try:
        import yt_dlp
    except ImportError:
        print("yt-dlp not found. Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "yt-dlp"])
        import yt_dlp

    # --- Download ffmpeg if missing ---
    ffmpeg_exe = os.path.join(bin_path, "ffmpeg.exe")
    ffprobe_exe = os.path.join(bin_path, "ffprobe.exe")
    ffplay_exe = os.path.join(bin_path, "ffplay.exe")

    if not (os.path.isfile(ffmpeg_exe) and os.path.isfile(ffprobe_exe) and os.path.isfile(ffplay_exe)):
        print("ffmpeg not found. Downloading...")
        os.makedirs(bin_path, exist_ok=True)
        zip_url = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"
        zip_file = os.path.join(bin_path, "ffmpeg.zip")
        urllib.request.urlretrieve(zip_url, zip_file)
        with zipfile.ZipFile(zip_file, "r") as zip_ref:
            zip_ref.extractall(bin_path)
        os.remove(zip_file)
        print("ffmpeg setup complete.")

# --- Function to update the title in the Save-as field for YouTube URLs ---
def update_title(*args):
    url = entry_url.get().strip()
    if "youtube.com" in url or "youtu.be" in url:
        url = url.split("&list=")[0]
        try:
            import yt_dlp
            ydl_opts = {"quiet": True, "no_warnings": True}
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                title = info.get("title", "")
                if title:
                    entry_name.delete(0, tk.END)
                    entry_name.insert(0, title)
        except Exception:
            pass

# --- Function to clean filenames ---
def clean_filename(name, ext):
    invalid_chars = r'\/:*?"<>|'
    for c in invalid_chars:
        name = name.replace(c, "_")
    if not name.lower().endswith(ext):
        name += ext
    return name

# --- Threaded download function using subprocess ---
def download_file_thread(url, filename, format_type="mp3"):
    out_path = os.path.join(path_music_dir, filename)
    url = url.split("&list=")[0]

    if format_type == "mp3":
        cmd = [
            ytdlp_cmd, "-x", "--audio-format", "mp3",
            "--ffmpeg-location", bin_path,
            "-o", out_path,
            "--newline", url
        ]
    else:
        cmd = [
            ytdlp_cmd, "-f", "best",
            "--ffmpeg-location", bin_path,
            "-o", out_path,
            "--newline", url
        ]

    try:
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        for line in process.stdout:
            line = line.strip()
            if "%" in line:
                try:
                    perc = line.split("%")[0].split()[-1]
                    root.after(0, lambda p=perc: progress_label.config(text=f"Progress: {p}%"))
                except:
                    pass
        process.wait()
        if process.returncode == 0:
            root.after(0, lambda: progress_label.config(text="Progress: 100% - Complete!"))
            root.after(0, lambda: messagebox.showinfo("Success", f"Download complete!\nSaved as {out_path}"))
        else:
            root.after(0, lambda: progress_label.config(text="Download failed"))
            root.after(0, lambda: messagebox.showerror("Download failed", "Check URL or login if needed."))
    except Exception as e:
        print("Download error:", e)
        root.after(0, lambda: progress_label.config(text="Download failed"))
        root.after(0, lambda: messagebox.showerror("Download failed", str(e)))

# --- Wrapper functions ---
def download_mp3():
    url = entry_url.get().strip()
    title = entry_name.get().strip()
    if not url or not title:
        messagebox.showwarning("Input error", "Please enter URL and filename.")
        return
    filename = clean_filename(title, ".mp3")
    threading.Thread(target=download_file_thread, args=(url, filename, "mp3"), daemon=True).start()

def download_mp4():
    url = entry_url.get().strip()
    title = entry_name.get().strip()
    if not url or not title:
        messagebox.showwarning("Input error", "Please enter URL and filename.")
        return
    filename = clean_filename(title, ".mp4")
    threading.Thread(target=download_file_thread, args=(url, filename, "mp4"), daemon=True).start()

# --- GUI ---
root = tk.Tk()
root.title("Universal Audio/Video Downloader")

tk.Label(root, text="Video/Audio URL:").grid(row=0, column=0, padx=10, pady=10)
entry_url = tk.Entry(root, width=50)
entry_url.grid(row=0, column=1, padx=10, pady=10)
entry_url.bind("<FocusOut>", update_title)

tk.Label(root, text="Save as:").grid(row=1, column=0, padx=10, pady=5)
entry_name = tk.Entry(root, width=50)
entry_name.grid(row=1, column=1, padx=10, pady=5)

btn_download_mp3 = tk.Button(root, text="Download MP3", command=download_mp3)
btn_download_mp4 = tk.Button(root, text="Download MP4", command=download_mp4)
btn_download_mp3.grid(row=2, column=0, columnspan=2, pady=10)
btn_download_mp4.grid(row=3, column=0, columnspan=2, pady=10)

progress_label = tk.Label(root, text="Progress: 0%")
progress_label.grid(row=4, column=0, columnspan=2, pady=5)

root.mainloop()
