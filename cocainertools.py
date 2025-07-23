import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import subprocess
import os
import sys
import threading
from pathlib import Path



def get_base_path():
    if getattr(sys, 'frozen', False):
        return sys._MEIPASS
    else:
        return os.path.dirname(__file__)

def get_ffmpeg_path():
    base_path = get_base_path()
    return os.path.join(base_path, 'ffmpegFolder', 'bin', 'ffmpeg.exe')

def get_ytdlp_path():
    base_path = get_base_path()
    return os.path.join(base_path, 'yt-dlp.exe')

def open_output_dir(path):
    if os.name == 'nt':
        os.startfile(path)
    else:
        try:
            subprocess.Popen(['xdg-open', path])
        except Exception:
            messagebox.showerror("Error", "Could not open directory.")


output_dir = str(Path.home() / "Downloads")

def update_output_path_label():
    output_path_label.config(text=f"Output here: {output_dir}")

def change_output_folder():
    global output_dir
    selected_dir = filedialog.askdirectory(initialdir=output_dir, title="Select Output Folder")
    if selected_dir:
        output_dir = selected_dir
        update_output_path_label()

def run_yt_dlp(url, file_type, status_label, open_button, output_label):
    ytdlp_path = get_ytdlp_path()
    ffmpeg_path = get_ffmpeg_path()

    output_template = os.path.join(output_dir, '%(title)s.%(ext)s')

    command = [
        ytdlp_path,
        '-t', file_type,
        '--ffmpeg-location', ffmpeg_path,
        '-o', output_template,
        url
    ]

    try:
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        stdout, stderr = process.communicate()

        if process.returncode == 0:
            status_label.config(text="Download completed successfully!")
            messagebox.showinfo("Success", "Download completed successfully!")

            update_output_path_label()
            output_label.pack(pady=(5,0))

            open_button.pack(pady=(0,10))
            open_button.config(state=tk.NORMAL)

        else:
            status_label.config(text="Download failed.")
            messagebox.showerror("Error", f"Download failed:\n{stderr}")
            open_button.pack_forget()
            output_label.pack_forget()

    except Exception as e:
        status_label.config(text="Error during download.")
        messagebox.showerror("Exception", str(e))
        open_button.pack_forget()
        output_label.pack_forget()

    finally:
        download_button.config(state=tk.NORMAL)

def start_download():
    url = url_entry.get().strip()
    if not url:
        messagebox.showwarning("Input Error", "Please enter a YouTube URL.")
        return

    file_type = type_var.get()

    download_button.config(state=tk.DISABLED)
    status_label.config(text="Downloading... Please wait and don't close the program.")
    open_folder_button.pack_forget()
    output_path_label.pack_forget()

    threading.Thread(
        target=run_yt_dlp,
        args=(url, file_type, status_label, open_folder_button, output_path_label),
        daemon=True
    ).start()


root = tk.Tk()
root.title("Cocainer YouTube Downloader by AlreadyClosed :)")
root.geometry("460x200")
root.resizable(False, False)

url_frame = tk.Frame(root)
url_frame.pack(pady=(10,5), padx=10, fill='x')

url_label = tk.Label(url_frame, text="YouTube URL:")
url_label.pack(side=tk.LEFT)

url_entry = tk.Entry(url_frame, width=40)
url_entry.pack(side=tk.LEFT, padx=(5,5), fill='x', expand=True)

folder_icon_button = tk.Button(url_frame, text="📁", width=3, command=change_output_folder)
folder_icon_button.pack(side=tk.LEFT)


center_frame = tk.Frame(root)
center_frame.pack(pady=(5,5))

type_label = tk.Label(center_frame, text="Type:")
type_label.pack(side=tk.LEFT)

type_var = tk.StringVar(value="mp4")
type_dropdown = ttk.Combobox(center_frame, textvariable=type_var, values=["mp3", "mp4"], state="readonly", width=7)
type_dropdown.pack(side=tk.LEFT, padx=(5, 15))

download_button = tk.Button(center_frame, text="Download", command=start_download, width=12)
download_button.pack(side=tk.LEFT)


status_label = tk.Label(root, text="", fg="blue")
status_label.pack(pady=(5,0))


output_path_label = tk.Label(root, text="", fg="blue", cursor="hand2")
output_path_label.pack_forget()

def on_output_label_click(event):
    open_output_dir(output_dir)

output_path_label.bind("<Button-1>", on_output_label_click)


open_folder_button = tk.Button(root, text="Open Output Folder", state=tk.DISABLED,
                               command=lambda: open_output_dir(output_dir))
open_folder_button.pack_forget()

 
update_output_path_label()
output_path_label.pack(pady=(5, 5))

root.mainloop()
