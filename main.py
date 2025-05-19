import os
import re
import requests
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
# ------------------------------
# Functions
# ------------------------------

def extract_repo_and_sha(commit_url):
    match = re.match(r"https://github\.com/([^/]+)/([^/]+)/commit/([a-f0-9]+)", commit_url)
    return match.groups() if match else (None, None, None)

def download_files():
    url = url_entry.get().strip()
    folder = path_entry.get().strip()

    if not url or not folder:
        messagebox.showerror("Error", "Please enter a commit URL and choose a folder.")
        return

    owner, repo, sha = extract_repo_and_sha(url)
    if not owner:
        messagebox.showerror("Error", "Invalid GitHub commit URL.")
        return

    # Disable controls while downloading
    download_button.config(state=tk.DISABLED)
    browse_button.config(state=tk.DISABLED)
    status_label.config(text="Connecting...")
    progress_bar["value"] = 0
    root.update_idletasks()

    try:
        api_url = f"https://api.github.com/repos/{owner}/{repo}/commits/{sha}"
        response = requests.get(api_url)
        response.raise_for_status()
        data = response.json()

        files = [f for f in data['files'] if f['status'] in ['added', 'modified']]
        total_files = len(files)

        if total_files == 0:
            messagebox.showinfo("Info", "No added or modified files to download.")
            status_label.config(text="Idle")
            progress_bar["value"] = 0
            return

        progress_bar["maximum"] = total_files
        progress_bar["value"] = 0
        status_label.config(text=f"Starting download of {total_files} files...")
        root.update_idletasks()

        for i, file in enumerate(files, start=1):
            file_path = file["filename"]
            raw_url = f"https://raw.githubusercontent.com/{owner}/{repo}/{sha}/{file_path}"
            local_path = os.path.join(folder, file_path)

            os.makedirs(os.path.dirname(local_path), exist_ok=True)

            # --- This part is blocking and freezes the GUI ---
            file_resp = requests.get(raw_url)
            file_resp.raise_for_status()

            with open(local_path, "wb") as f:
                f.write(file_resp.content)
            # -------------------------------------------------

            # Calculate percentage
            percentage = (i / total_files) * 100

            # Update progress bar and status label with percentage
            progress_bar["value"] = i
            status_label.config(text=f"Downloaded ({i}/{total_files}) {percentage:.0f}%: {file_path}")
            root.update_idletasks()

        messagebox.showinfo("Success", "Files downloaded successfully.")
        status_label.config(text="Done ✅")

    except requests.exceptions.RequestException as e:
         messagebox.showerror("Error", f"Network or API error:\n{e}")
         status_label.config(text="Download failed ❌")
    except Exception as e:
        messagebox.showerror("Error", f"An unexpected error occurred:\n{e}")
        status_label.config(text="Download failed ❌")
    finally:
        download_button.config(state=tk.NORMAL)
        browse_button.config(state=tk.NORMAL)
        if "failed" in status_label.cget("text"):
             progress_bar["value"] = 0

def browse_folder():
    folder = filedialog.askdirectory()
    if folder:
        path_entry.delete(0, tk.END)
        path_entry.insert(0, folder)

# ------------------------------
# GUI
# ------------------------------

root = tk.Tk()
root.title("🌟 GitHub Commit Downloader")
root.geometry("640x280")
root.configure(bg="#f5f5f5")

# Style
style = ttk.Style()
style.theme_use("clam")
style.configure("TLabel", font=("Segoe UI", 10), background="#f5f5f5")
style.configure("TEntry", padding=5)
style.configure("TButton", font=("Segoe UI", 10, "bold"), padding=6)
style.map("TButton", background=[("active", "#d9e4f5")])

# Main frame
main_frame = ttk.Frame(root, padding=20)
main_frame.pack(fill=tk.BOTH, expand=True)

# URL input
ttk.Label(main_frame, text="🔗 GitHub Commit URL:").grid(row=0, column=0, sticky="w", pady=10)
url_entry = ttk.Entry(main_frame, width=70)
url_entry.grid(row=0, column=1, columnspan=2, sticky="we", padx=10)

# Folder input
ttk.Label(main_frame, text="📁 Download Folder:").grid(row=1, column=0, sticky="w", pady=10)
path_entry = ttk.Entry(main_frame, width=50)
path_entry.grid(row=1, column=1, sticky="we", padx=10)
browse_button = ttk.Button(main_frame, text="Browse", command=browse_folder)
browse_button.grid(row=1, column=2)


# Download button
download_button = ttk.Button(main_frame, text="⏬ Download Files", command=download_files)
download_button.grid(
    row=2, column=1, columnspan=2, pady=20, sticky="e"
)

# Progress bar
progress_bar = ttk.Progressbar(main_frame, orient="horizontal", length=400, mode="determinate")
progress_bar.grid(row=3, column=0, columnspan=3, pady=10, sticky="we")

# Status label
status_label = ttk.Label(main_frame, text="Idle", wraplength=600)
status_label.grid(row=4, column=0, columnspan=3, sticky="we")

# Column resizing
main_frame.grid_columnconfigure(1, weight=1)
main_frame.grid_columnconfigure(0, weight=0)
main_frame.grid_columnconfigure(2, weight=0)


# Run GUI
root.mainloop()