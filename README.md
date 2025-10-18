# MP3 & MP4 Downloader (Python)

A simple and lightweight Python GUI tool to download online videos as **MP3** or **MP4** files on Windows and Linux (Mint).  
It automatically handles dependencies like **ffmpeg** and uses **yt-dlp** for extraction.  
Designed for private, legal use only. 

## Features
- GUI built with **Tkinter**
- Automatically downloads **ffmpeg** if missing
- Automatically downloads **yt-dlp** if missing 
- Supports MP3 and MP4 output
- Uses browser cookies (Firefox, Edge, Chrome, Opera, Brave) if login is required
- Saves files into a local `music` directory
- Tested with **Python 3.13.7**
Using the `.exe` file does not require a Python installation

---

## Usage Disclaimer
This tool is intended for **private, legal use only**.  
Downloading copyrighted content without permission may violate the Terms of Service of certain platforms.  
Only download content you own or that is licensed for free use.  

---

## Download
👉 [Get the latest release here (Win)](https://github.com/DimitriosPournarkas/media-url-downloader-Python/releases)

Download the `.exe` file from the releases page and run it directly.  
No Python installation required.  
##  Run the Downloader
1. Enter a video/audio URL in the GUI
2. Choose a Save name (for some sites the program will auto-detect the title).
3. Click __Download MP3__ or __Download MP4__.
4. Files will be saved in the local music directory (auto-created if missing).

---
## Installation & Usage (Python file __Optional__)

### Step 1: Install Python
- Download Python from [python.org](https://www.python.org/)  
- During installation, make sure to check **Add Python to PATH**

### Step 2: Verify Pip
Press: __Win + R__

Type: __cmd__
and click __OK__ to execute it. 
 
Execute in cmd: pip --version

If you see a version number it is already installed and go to the next step.

Usually it is already installed with Python V 3.4 or higher.

__If not__:
  Get the code (https://bootstrap.pypa.io/get-pip.py) and save it as get-pip.py.
  Open a cmd in the same dir as get-pip.py and execute: 
  
  python get-pip.py
  
  Test again by excecute: pip --version
### Step 3: Run the Downloader
1. Download the __PyMediaDownloader.pyw__ file.
2. Run the file and wait; it will automatically download ffmpeg and yt-dlp if missing.
3. Enter a video/audio URL in the GUI.
4. Choose a Save name.
5. Click __Download MP3__ or __Download MP4__.
6. Files will be saved in the local music directory (auto-created if missing).
## Installation & Usage on Linux
1. Install Python & Pip.
2. Download the __PyMediaDownloader_linux.py__ file.
3. Get a __cookies.txt__ file from (Firefox Extension) and save it in the same dir as the py file.
3. Run the Python file (Enter Url and Savename in GUI)
4. Click __Download MP3__ or __Download MP4__. 
## License

This project is licensed under the MIT License.  
See the [LICENSE](LICENSE) file for details.




