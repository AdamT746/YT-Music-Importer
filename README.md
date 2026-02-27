# YT Music Library Importer

A desktop application that scans your local music library and recreates it as a playlist on YouTube Music. Built with Python and CustomTkinter.

DO NOT SHARE THE headers_auth.json FILE CREATED BY THIS PROGRAM

## Features

* Has a UI instead of most console based applications.
* Automatically searches recursively, reads internal metadata (Artist/Title) using `tinytag`, rather than relying on messy filenames.
* Fuzzy logic removes tags ([Live], (Remastered), feat.)
* Uses chunking to not overload yt servers, tested on 2500+ song library.
* JSON Generator
* Generates a `skipped_songs.txt` log at the end of the import, listing exactly which obscure tracks couldn't be found so you can add them manually.

##  How-To

If you just want to run the app without installing Python, download `music_importer_gui.exe`.

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
2. Select which file types you want to include (MP3, FLAC, M4A, WAV, ALAC).
3. Name your new playlist.
4. Click **START IMPORT** and watch the live console do the heavy lifting!


## Building the App

Dependencies:
* ytmusicapi
* tinytag
* customtkinter

python -m PyInstaller --noconsole --onefile --icon=Logo.ico --collect-all ytmusicapi --collect-all customtkinter musicImporterGUI2.py  


## Disclaimer
This is an unofficial tool. It relies on the `ytmusicapi` library. Please be mindful of YouTube's rate limits. Do not use this tool to spam requests to YouTube's servers. 

The creation of this tool was aided by Google Gemini.

## License
This project is licensed under the GNU General Public License v3.0 - see the LICENSE file for details.
