import os
import sys
import subprocess
import urllib.request
import zipfile
import tkinter as tk
from tkinter import messagebox, scrolledtext
import threading
import shutil

# --- Music directory ---
path_music_dir = os.path.join(os.getcwd(), "music")
os.makedirs(path_music_dir, exist_ok=True)

# --- Check if running in a PyInstaller build ---
def is_frozen():
    return getattr(sys, 'frozen', False)

# --- Set paths for ffmpeg and yt-dlp ---
if is_frozen():
    base_path = sys._MEIPASS
    bin_path = os.path.join(base_path, "ffmpeg_bin")
    # For frozen build, use a writable location for yt-dlp
    ytdlp_dir = os.path.join(os.getcwd(), "yt-dlp_bin")
    os.makedirs(ytdlp_dir, exist_ok=True)
    ytdlp_cmd = os.path.join(ytdlp_dir, "yt-dlp.exe")
    
    # Copy bundled yt-dlp to writable location if not exists
    bundled_ytdlp = os.path.join(base_path, "yt-dlp_bin", "yt-dlp.exe")
    if os.path.exists(bundled_ytdlp) and not os.path.exists(ytdlp_cmd):
        shutil.copy2(bundled_ytdlp, ytdlp_cmd)
else:
    # Python mode
    bin_path = os.path.join(os.environ['USERPROFILE'], "ffmpeg", "bin")
    ytdlp_cmd = "yt-dlp"

# Global flag to track if dependencies are ready
dependencies_ready = False
setup_error = None

def log_output(message):
    """Log messages to console window if it exists"""
    try:
        console_text.insert(tk.END, message + "\n")
        console_text.see(tk.END)
        root.update_idletasks()
    except:
        print(message)

def update_ytdlp():
    """Update yt-dlp to latest version"""
    def do_update():
        try:
            log_output("\n" + "="*50)
            log_output("Updating yt-dlp...")
            log_output("="*50)
            
            if is_frozen():
                # Download latest yt-dlp.exe
                url = "https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp.exe"
                temp_file = ytdlp_cmd + ".tmp"
                
                log_output(f"Downloading from: {url}")
                
                def download_progress(block_num, block_size, total_size):
                    downloaded = block_num * block_size
                    percent = min(100, int(downloaded * 100 / total_size))
                    root.after(0, lambda p=percent: status_label.config(
                        text=f"Downloading yt-dlp: {p}%", fg="orange"))
                
                urllib.request.urlretrieve(url, temp_file, download_progress)
                
                # Replace old version
                if os.path.exists(ytdlp_cmd):
                    os.remove(ytdlp_cmd)
                os.rename(temp_file, ytdlp_cmd)
                
                log_output("✓ yt-dlp updated successfully!")
                root.after(0, lambda: status_label.config(text="yt-dlp updated! Ready", fg="green"))
                root.after(0, lambda: messagebox.showinfo("Success", "yt-dlp updated to latest version!"))
            else:
                # Python mode: use pip
                log_output("Running: pip install --upgrade yt-dlp")
                result = subprocess.run(
                    [sys.executable, "-m", "pip", "install", "--upgrade", "yt-dlp"],
                    capture_output=True,
                    text=True
                )
                
                if result.returncode == 0:
                    log_output("✓ yt-dlp updated successfully!")
                    root.after(0, lambda: status_label.config(text="yt-dlp updated! Ready", fg="green"))
                    root.after(0, lambda: messagebox.showinfo("Success", "yt-dlp updated to latest version!"))
                else:
                    log_output(f"ERROR: {result.stderr}")
                    root.after(0, lambda: messagebox.showerror("Update Failed", result.stderr))
                    
        except Exception as e:
            log_output(f"ERROR updating yt-dlp: {e}")
            root.after(0, lambda: status_label.config(text="Update failed", fg="red"))
            root.after(0, lambda: messagebox.showerror("Update Failed", str(e)))
    
    threading.Thread(target=do_update, daemon=True).start()

def setup_dependencies():
    """Run dependency checks in background thread"""
    global dependencies_ready, setup_error
    
    if is_frozen():
        # Check if bundled files exist
        if not os.path.exists(ytdlp_cmd):
            setup_error = f"yt-dlp not found at: {ytdlp_cmd}"
            log_output(f"ERROR: {setup_error}")
            root.after(0, lambda: status_label.config(text="yt-dlp missing! Click Update", fg="red"))
            return
        
        if not os.path.exists(bin_path):
            setup_error = f"ffmpeg not found at: {bin_path}"
            log_output(f"ERROR: {setup_error}")
            root.after(0, lambda: status_label.config(text="ffmpeg missing!", fg="red"))
            return
        
        log_output(f"✓ Found yt-dlp: {ytdlp_cmd}")
        log_output(f"✓ Found ffmpeg: {bin_path}")
        dependencies_ready = True
        root.after(0, lambda: status_label.config(text="Ready", fg="green"))
        return
    
    try:
        # --- Install/Update yt-dlp in Python mode ---
        try:
            import yt_dlp
            log_output("✓ yt-dlp module found")
            
            # Auto-update on startup in Python mode
            log_output("Checking for yt-dlp updates...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "yt-dlp"],
                                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            log_output("✓ yt-dlp is up to date")
        except ImportError:
            log_output("Installing yt-dlp...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", "yt-dlp"])
            import yt_dlp
            log_output("✓ yt-dlp installed")

        # --- Download ffmpeg if missing ---
        ffmpeg_exe = os.path.join(bin_path, "ffmpeg.exe")
        ffprobe_exe = os.path.join(bin_path, "ffprobe.exe")

        if not (os.path.isfile(ffmpeg_exe) and os.path.isfile(ffprobe_exe)):
            log_output("Downloading ffmpeg...")
            os.makedirs(bin_path, exist_ok=True)
            zip_url = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"
            zip_file = os.path.join(bin_path, "ffmpeg.zip")
            urllib.request.urlretrieve(zip_url, zip_file)
            
            log_output("Extracting ffmpeg...")
            with zipfile.ZipFile(zip_file, "r") as zip_ref:
                # Extract and move files from nested folder
                for member in zip_ref.namelist():
                    if member.endswith(('.exe', '.dll')) and '/bin/' in member:
                        filename = os.path.basename(member)
                        source = zip_ref.open(member)
                        target = open(os.path.join(bin_path, filename), "wb")
                        target.write(source.read())
                        target.close()
                        source.close()
            
            os.remove(zip_file)
            log_output("✓ ffmpeg setup complete")
        else:
            log_output("✓ ffmpeg found")
        
        dependencies_ready = True
        root.after(0, lambda: status_label.config(text="Ready", fg="green"))
    except Exception as e:
        setup_error = str(e)
        log_output(f"ERROR: {e}")
        root.after(0, lambda: status_label.config(text="Setup failed!", fg="red"))

# --- Function to update the title in the Save-as field for YouTube URLs ---
def update_title(*args):
    url = entry_url.get().strip()
    if not url or not ("youtube.com" in url or "youtu.be" in url):
        return
    
    url = url.split("&list=")[0]
    url = url.split("?")[0] if "?" in url and "v=" not in url else url
    
    try:
        import yt_dlp
        log_output(f"Fetching title for: {url}")
        ydl_opts = {
            "quiet": True, 
            "no_warnings": True,
            "extractor_args": {"youtube": {"player_client": ["android", "web"]}}
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            title = info.get("title", "")
            if title:
                entry_name.delete(0, tk.END)
                entry_name.insert(0, title)
                log_output(f"✓ Title: {title}")
    except Exception as e:
        log_output(f"Could not fetch title: {e}")

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
    if not dependencies_ready:
        root.after(0, lambda: messagebox.showwarning("Not Ready", "Dependencies are still loading. Please wait..."))
        return
    
    if setup_error:
        root.after(0, lambda: messagebox.showerror("Setup Error", f"Dependencies failed to load:\n{setup_error}"))
        return
    
    # Clean URL
    url = url.strip()
    url = url.split("&list=")[0]  # Remove playlist parameter
    
    out_path = os.path.join(path_music_dir, filename)
    
    log_output(f"\n{'='*50}")
    log_output(f"Starting download: {format_type.upper()}")
    log_output(f"URL: {url}")
    log_output(f"Output: {out_path}")
    log_output(f"yt-dlp: {ytdlp_cmd}")
    log_output(f"ffmpeg: {bin_path}")
    log_output(f"{'='*50}\n")

    if format_type == "mp3":
        cmd = [
            ytdlp_cmd,
            "-x",
            "--audio-format", "mp3",
            "--audio-quality", "0",
            "--ffmpeg-location", bin_path,
            "-o", out_path,
            "--newline",
            "--no-playlist",
            "--extractor-args", "youtube:player_client=android,web",
            url
        ]
    else:
        cmd = [
            ytdlp_cmd,
            "-f", "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
            "--ffmpeg-location", bin_path,
            "-o", out_path,
            "--newline",
            "--no-playlist",
            "--extractor-args", "youtube:player_client=android,web",
            url
        ]

    try:
        log_output(f"Command: {' '.join(cmd)}\n")
        
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0
        )
        
        for line in process.stdout:
            line = line.strip()
            if line:
                log_output(line)
                
                if "%" in line:
                    try:
                        perc = line.split("%")[0].split()[-1]
                        root.after(0, lambda p=perc: progress_label.config(text=f"Progress: {p}%"))
                    except:
                        pass
        
        process.wait()
        
        log_output(f"\nProcess finished with code: {process.returncode}")
        
        if process.returncode == 0:
            root.after(0, lambda: progress_label.config(text="Progress: 100% - Complete!"))
            root.after(0, lambda: messagebox.showinfo("Success", f"Download complete!\nSaved as:\n{out_path}"))
        else:
            root.after(0, lambda: progress_label.config(text="Download failed"))
            root.after(0, lambda: messagebox.showerror("Download failed", 
                f"yt-dlp returned error code {process.returncode}\n\nCheck the console for details.\n\nTry updating yt-dlp with the Update button!"))
    
    except Exception as e:
        log_output(f"\nERROR: {e}")
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

def toggle_console():
    """Toggle console visibility"""
    if console_frame.winfo_viewable():
        console_frame.grid_remove()
        btn_toggle_console.config(text="Show Console ▼")
        root.geometry("600x220")
    else:
        console_frame.grid()
        btn_toggle_console.config(text="Hide Console ▲")
        root.geometry("600x520")

# --- GUI ---
root = tk.Tk()
root.title("Universal Audio/Video Downloader")
root.geometry("600x220")

# Main frame
main_frame = tk.Frame(root)
main_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

tk.Label(main_frame, text="Video/Audio URL:").grid(row=0, column=0, padx=10, pady=10, sticky="w")
entry_url = tk.Entry(main_frame, width=50)
entry_url.grid(row=0, column=1, padx=10, pady=10)
entry_url.bind("<FocusOut>", update_title)

tk.Label(main_frame, text="Save as:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
entry_name = tk.Entry(main_frame, width=50)
entry_name.grid(row=1, column=1, padx=10, pady=5)

# Download buttons frame
download_frame = tk.Frame(main_frame)
download_frame.grid(row=2, column=1, pady=10, sticky="w")

btn_download_mp3 = tk.Button(download_frame, text="Download MP3", command=download_mp3, width=15, bg="#2196F3", fg="white")
btn_download_mp3.pack(side="left", padx=5)

btn_download_mp4 = tk.Button(download_frame, text="Download MP4", command=download_mp4, width=15, bg="#2196F3", fg="white")
btn_download_mp4.pack(side="left", padx=5)

progress_label = tk.Label(main_frame, text="Progress: 0%")
progress_label.grid(row=3, column=0, columnspan=2, pady=5)

status_label = tk.Label(main_frame, text="Loading dependencies...", fg="orange")
status_label.grid(row=4, column=0, columnspan=2, pady=5)

# Button frame for console and update
button_frame = tk.Frame(main_frame)
button_frame.grid(row=5, column=0, columnspan=2, pady=5)

btn_toggle_console = tk.Button(button_frame, text="Show Console ▼", command=toggle_console, width=20)
btn_toggle_console.pack(side="left", padx=5)

btn_update_ytdlp = tk.Button(button_frame, text="Update yt-dlp", command=update_ytdlp, width=20, bg="#4CAF50", fg="white")
btn_update_ytdlp.pack(side="left", padx=5)

# Console frame (hidden by default)
console_frame = tk.Frame(root)
console_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
console_frame.grid_remove()  # Hide by default

tk.Label(console_frame, text="Console Output:", anchor="w").pack(fill="x")
console_text = scrolledtext.ScrolledText(console_frame, height=15, width=70, bg="black", fg="lime")
console_text.pack(fill="both", expand=True)

# Configure grid weights
root.grid_rowconfigure(1, weight=1)
root.grid_columnconfigure(0, weight=1)

# Start dependency setup in background thread
log_output("Initializing...")
threading.Thread(target=setup_dependencies, daemon=True).start()

root.mainloop()