import tkinter as tk
import os
from tkinter import filedialog
from pathlib import Path


def file_dialog(callback, extensions: list = None, base_dir: str = None, title: str = None):

    if not base_dir:
        base_dir = os.getcwd()
    
    if not title:
        title = "Окно выбора файла"

    root = tk.Tk()
    root.withdraw()

    filetypes = []

    if extensions:
        for ext in extensions:
            filetypes.append((f"{ext.upper()} files", f"*{ext}"))

    # filetypes.append(("All files", "*.*"))

    file_path = filedialog.askopenfilename(filetypes=filetypes, initialdir = base_dir, title = title)

    root.destroy()


    if file_path:
        path = Path(file_path)

        data = {
            "file_path_name": str(path),
            "file_name": path.name
        }

        callback(None, data)