# 🎧💾 YT Music Library Importer

A sleek, modern desktop application that automatically scans your local music library and recreates it as a playlist on YouTube Music. Built with Python and CustomTkinter, this tool handles massive libraries (2,500+ songs) with ease, utilizing smart fuzzy-matching and chunked batch uploading.

*(Note: Upload your app_icon.png to your repo so it displays here!)*

## ✨ Features

* **Modern Dark Mode UI:** A responsive, sleek interface built with CustomTkinter.
* **Deep Folder Scanning:** Recursively searches your selected directory and reads internal metadata (Artist/Title) using `tinytag`, rather than relying on messy filenames.
* **Smart Fuzzy Matching:** Automatically strips out "(Remastered)", "[Live]", and "feat." tags, and uses fuzzy string matching to ensure the right song is added, even with slight spelling differences.
* **Massive Library Support:** Safely processes thousands of songs by pushing them to YouTube Music in chunks of 100, preventing server timeouts and rate-limiting.
* **Built-in Authentication:** No need to manually edit JSON files. A built-in setup wizard securely handles your login tokens.
* **Detailed Receipts:** Automatically generates a `skipped_songs.txt` log at the end of the import, listing exactly which obscure tracks couldn't be found so you can add them manually.

## 🚀 How to Use (Pre-compiled .exe)

If you just want to run the app without installing Python, download the latest `music_importer_gui.exe` from the **Releases** tab.

### Step 1: Get your YouTube Music Headers
To allow the app to create a playlist on your behalf, you need to provide it with a temporary digital ID badge (Headers). 
1. Open YouTube Music in your browser (Chrome/Edge/Firefox).
2. Press F12 to open Developer Tools and navigate to the **Network** tab.
3. Filter by **Fetch/XHR**.
4. Click on a different page in YouTube Music (like "Library" or "Explore").
5. Look for a request named `browse` in the Network list and click on it.
6. Look under the **Headers** -> **Request Headers** section and copy your `Cookie` and `authorization` text.


### Step 2: Setup Authentication
1. Launch `music_importer_gui.exe`.
2. Click the blue **⚙️ Setup Authentication** button.
3. Paste your `Cookie` and `Authorization` data into the provided boxes and click Generate.

### Step 3: Import!
1. Click **Browse...** to select your local music folder.
2. Select which file types you want to include (MP3, FLAC, M4A, WAV, OGG).
3. Name your new playlist.
4. Click **START IMPORT** and watch the live console do the heavy lifting!

## 💻 Running from Source (For Developers)

If you prefer to run the raw Python script:

1. Clone this repository:
    git clone https://github.com/YOUR-USERNAME/yt-music-importer.git

2. Install the required dependencies:
    pip install ytmusicapi tinytag customtkinter

3. Run the application:
    python music_importer_gui.py

## ⚠️ Disclaimer
This is an unofficial tool. It relies on the `ytmusicapi` library. Please be mindful of YouTube's rate limits. Do not use this tool to spam requests to YouTube's servers. 

## 📜 License
This project is licensed under the GNU General Public License v3.0 - see the LICENSE file for details.
