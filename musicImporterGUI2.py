import os
import time
import re
import difflib
import threading
import sys
import json
import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk  # <-- The new modern UI library
from tinytag import TinyTag
from ytmusicapi import YTMusic

# --- UI Configuration ---
ctk.set_appearance_mode("Dark")       # Forces Dark Mode
ctk.set_default_color_theme("green")  # Gives buttons that hacker green accent

# --- Helper Functions (Untouched) ---
def clean_text(text):
    if not text:
        return ""
    text = text.lower()
    text = re.sub(r'\(.*?\)|\[.*?\]', '', text)
    text = re.sub(r'\b(feat\.?|ft\.?|featuring)\b', '', text)
    text = re.sub(r'[^a-z0-9 ]', '', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def is_artist_match(local_artist, yt_artists_data):
    if not local_artist:
        return True 
    local_clean = clean_text(local_artist)
    for yt_artist in yt_artists_data:
        yt_clean = clean_text(yt_artist['name'])
        similarity = difflib.SequenceMatcher(None, local_clean, yt_clean).ratio()
        if similarity > 0.75 or local_clean in yt_clean or yt_clean in local_clean:
            return True
    return False

# --- Core Logic (Minor tweaks for CTk button states) ---
def run_import(music_folder, playlist_name, playlist_desc, start_button, valid_exts):
    print("Connecting to YouTube Music...")
    auth_file = "headers_auth.json"
    
    if not os.path.exists(auth_file):
        print(f"\n[FATAL ERROR] '{auth_file}' not found.\nPlease click 'Setup Authentication' first to generate your login file.")
        start_button.configure(state="normal")
        return

    try:
        yt = YTMusic(auth_file)
    except Exception as e:
        print(f"\n[FATAL ERROR] Failed to authenticate.\nYour auth file might be expired or invalid.\nError: {e}")
        start_button.configure(state="normal")
        return

    print(f"\nScanning directory and subfolders: {music_folder}")
    print(f"Looking for file types: {', '.join(valid_exts)}")
    
    local_songs = []

    for dirpath, _, filenames in os.walk(music_folder):
        for filename in filenames:
            if filename.lower().endswith(valid_exts):
                filepath = os.path.join(dirpath, filename)
                try:
                    tag = TinyTag.get(filepath)
                    artist, title = tag.artist, tag.title
                    
                    if artist and title:
                        query = f"{artist} {title}"
                    elif title:
                        query = title
                    elif " - " in filename:
                        parts = os.path.splitext(filename)[0].split(" - ", 1)
                        artist = parts[0].strip()
                        query = f"{artist} {parts[1].strip()}"
                    else:
                        query = os.path.splitext(filename)[0]
                    
                    local_songs.append({'filename': filename, 'search_term': query, 'expected_artist': artist})
                except Exception:
                    pass

    if not local_songs:
        print("\nNo valid music files found matching your selected types.")
        start_button.configure(state="normal")
        return

    video_ids = []
    skipped_songs_log = []
    print(f"\nFound {len(local_songs)} songs. Starting search...")
    
    for song in local_songs:
        results = yt.search(song['search_term'], filter="songs") 
        best_match = None
        
        if results:
            for result in results[:3]:
                if is_artist_match(song['expected_artist'], result.get('artists', [])):
                    best_match = result
                    break
            
            if best_match:
                video_ids.append(best_match['videoId'])
                print(f"[SUCCESS] {song['search_term']} -> Matched with '{best_match['title']}'")
            else:
                print(f"[SKIPPED] {song['search_term']} -> Artist names did not match.")
                skipped_songs_log.append(f"{song['search_term']} (Artist Mismatch)")
        else:
            print(f"[FAILED]  {song['search_term']} -> No results found.")
            skipped_songs_log.append(f"{song['search_term']} (No Results Found)")

    if skipped_songs_log:
        try:
            with open("skipped_songs.txt", "w", encoding="utf-8") as f:
                f.write("--- Songs unable to be matched automatically ---\n\n")
                for skipped in skipped_songs_log:
                    f.write(f"{skipped}\n")
            print(f"\n[NOTE] Saved {len(skipped_songs_log)} skipped songs to 'skipped_songs.txt'")
        except Exception as e:
            print(f"Failed to write skipped log: {e}")

    if video_ids:
        unique_video_ids = list(dict.fromkeys(video_ids))
        print(f"\nCreating playlist '{playlist_name}'...")
        try:
            playlist_id = yt.create_playlist(playlist_name, playlist_desc)
            print("Waiting 3 seconds for YouTube servers to sync...")
            time.sleep(3)  
            
            print(f"Pushing {len(unique_video_ids)} unique songs in batches...")
            chunk_size = 100
            for i in range(0, len(unique_video_ids), chunk_size):
                chunk = unique_video_ids[i:i + chunk_size]
                start_num = i + 1
                end_num = min(i + chunk_size, len(unique_video_ids))
                print(f"-> Uploading batch {start_num} to {end_num}...")
                
                yt.add_playlist_items(playlist_id, chunk, duplicates=True)
                time.sleep(2) 
                    
            print("\n*** IMPORT COMPLETE! *** Check your YouTube Music account.")
        except Exception as e:
            print(f"\n[ERROR] Failed to upload playlist: {e}")
    else:
        print("\nNo songs were successfully matched to add to a playlist.")

    start_button.configure(state="normal")

# --- CustomTkinter GUI Class ---
class RedirectText(object):
    def __init__(self, text_ctrl):
        self.output = text_ctrl
    def write(self, string):
        self.output.insert("end", string)
        self.output.see("end")
    def flush(self):
        pass

class MusicImporterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("YT Music Library Importer")
        self.root.geometry("750x700")
        
        # Grid setup for responsiveness
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(11, weight=1)

        self.folder_var = tk.StringVar()
        self.playlist_name_var = tk.StringVar(value="Imported Local Music")
        self.playlist_desc_var = tk.StringVar(value="Automatically imported from local drive.")

        self.ext_vars = {
            '.mp3': tk.BooleanVar(value=True),
            '.flac': tk.BooleanVar(value=True),
            '.m4a': tk.BooleanVar(value=True),
            '.wav': tk.BooleanVar(value=True),
            '.ogg': tk.BooleanVar(value=True)
        }

        # --- UI Layout using CTk Widgets ---
        ctk.CTkLabel(root, text="Local Music Folder:", font=("Arial", 14, "bold")).grid(row=0, column=0, sticky="w", padx=20, pady=(20, 5))
        
        # Frame for folder input + browse button
        folder_frame = ctk.CTkFrame(root, fg_color="transparent")
        folder_frame.grid(row=1, column=0, sticky="ew", padx=20)
        folder_frame.grid_columnconfigure(0, weight=1)
        
        ctk.CTkEntry(folder_frame, textvariable=self.folder_var, height=35).grid(row=0, column=0, sticky="ew", padx=(0, 10))
        ctk.CTkButton(folder_frame, text="Browse...", command=self.browse_folder, width=100, height=35).grid(row=0, column=1)

        # Filters
        ctk.CTkLabel(root, text="Include File Types:", font=("Arial", 14, "bold")).grid(row=2, column=0, sticky="w", padx=20, pady=(15, 5))
        checkbox_frame = ctk.CTkFrame(root, fg_color="transparent")
        checkbox_frame.grid(row=3, column=0, sticky="w", padx=20)
        for ext, var in self.ext_vars.items():
            ctk.CTkCheckBox(checkbox_frame, text=ext, variable=var).pack(side=tk.LEFT, padx=(0, 15))

        # Playlist Info
        ctk.CTkLabel(root, text="Playlist Name:", font=("Arial", 14, "bold")).grid(row=4, column=0, sticky="w", padx=20, pady=(15, 5))
        ctk.CTkEntry(root, textvariable=self.playlist_name_var, height=35).grid(row=5, column=0, sticky="ew", padx=20)

        ctk.CTkLabel(root, text="Playlist Description:", font=("Arial", 14, "bold")).grid(row=6, column=0, sticky="w", padx=20, pady=(15, 5))
        ctk.CTkEntry(root, textvariable=self.playlist_desc_var, height=35).grid(row=7, column=0, sticky="ew", padx=20)

        # Action Buttons
        self.auth_btn = ctk.CTkButton(
            root, text="⚙️ Setup Authentication", command=self.open_auth_dialog, 
            fg_color="#008CBA", hover_color="#005f7a", height=35, font=("Arial", 13, "bold")
        )
        self.auth_btn.grid(row=8, column=0, pady=(25, 5), padx=20, sticky="ew")

        self.start_btn = ctk.CTkButton(
            root, text="START IMPORT", command=self.start_thread, 
            height=45, font=("Arial", 15, "bold")
        )
        self.start_btn.grid(row=9, column=0, pady=(0, 15), padx=20, sticky="ew")

        # Console
        ctk.CTkLabel(root, text="Live Activity Log:", font=("Arial", 14, "bold")).grid(row=10, column=0, sticky="w", padx=20)
        
        self.console = ctk.CTkTextbox(root, text_color="#4af626", font=("Consolas", 12))
        self.console.grid(row=11, column=0, pady=(5, 20), padx=20, sticky="nsew")

        sys.stdout = RedirectText(self.console)

    def browse_folder(self):
        selected_dir = filedialog.askdirectory(title="Select Music Folder")
        if selected_dir:
            self.folder_var.set(selected_dir)

    def open_auth_dialog(self):
        auth_win = ctk.CTkToplevel(self.root)
        auth_win.title("Authentication Setup")
        auth_win.geometry("650x700")
        auth_win.grab_set() 
        auth_win.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(auth_win, text="Paste your YouTube Music request headers below:", font=("Arial", 15, "bold")).grid(row=0, column=0, columnspan=2, sticky="w", padx=20, pady=(20, 15))

        headers_config = {
            "User-Agent": "",
            "Accept": "*/*",
            "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8",
            "Content-Type": "application/json",
            "X-Goog-AuthUser": "0",
            "x-origin": "https://music.youtube.com",
            "Authorization": "",
            "Cookie": ""
        }

        entries = {}
        row = 1
        for key, default_val in headers_config.items():
            ctk.CTkLabel(auth_win, text=f"{key}:", font=("Arial", 12)).grid(row=row, column=0, sticky="ne", pady=5, padx=(20, 10))
            
            if key in ["Cookie", "Authorization"]:
                widget = ctk.CTkTextbox(auth_win, height=80)
                widget.grid(row=row, column=1, sticky="ew", pady=5, padx=(0, 20))
                widget.insert("end", default_val)
            else:
                widget = ctk.CTkEntry(auth_win)
                widget.grid(row=row, column=1, sticky="ew", pady=5, padx=(0, 20))
                widget.insert(0, default_val)
                
            entries[key] = widget
            row += 1

        def save_headers():
            auth_data = {}
            for k, widget in entries.items():
                if isinstance(widget, ctk.CTkTextbox):
                    val = widget.get("1.0", "end-1c").strip()
                else:
                    val = widget.get().strip()
                
                auth_data[k.lower()] = val
                
                if not val:
                    messagebox.showerror("Missing Data", f"The field '{k}' cannot be empty!", parent=auth_win)
                    return

            try:
                with open("headers_auth.json", "w") as f:
                    json.dump(auth_data, f, indent=4)
                messagebox.showinfo("Success", "Authentication file created successfully!\nYou can now start the import.", parent=auth_win)
                print("[SYSTEM] Authentication file configured securely.")
                auth_win.destroy()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save file: {e}", parent=auth_win)

        save_btn = ctk.CTkButton(
            auth_win, text="Generate Auth File", command=save_headers, 
            fg_color="#008CBA", hover_color="#005f7a", height=40, font=("Arial", 14, "bold")
        )
        save_btn.grid(row=row, column=0, columnspan=2, pady=25, padx=20, sticky="ew")

    def start_thread(self):
        folder = self.folder_var.get()
        p_name = self.playlist_name_var.get()
        p_desc = self.playlist_desc_var.get()
        
        selected_exts = tuple(ext for ext, var in self.ext_vars.items() if var.get())

        if not folder or not os.path.exists(folder):
            messagebox.showerror("Error", "Please select a valid folder path first!")
            return
            
        if not selected_exts:
            messagebox.showerror("Error", "Please select at least one file type!")
            return
        
        self.start_btn.configure(state="disabled")
        self.console.delete("1.0", "end") 
        
        import_thread = threading.Thread(target=run_import, args=(folder, p_name, p_desc, self.start_btn, selected_exts), daemon=True)
        import_thread.start()

# --- Run App ---
if __name__ == "__main__":
    root = ctk.CTk()  # Swapped from tk.Tk()
    app = MusicImporterApp(root)
    root.mainloop()