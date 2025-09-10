# photo_json.py
from __future__ import annotations
import argparse
import json
import datetime
import sys
import logging
import threading
from pathlib import Path
from typing import List, Dict, Optional

try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

try:
    import tkinter as tk
    from tkinter import filedialog, messagebox, ttk
    TK_AVAILABLE = True
except ImportError:
    TK_AVAILABLE = False

CONFIG = {
    "image_extensions": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".heic", ".heif", ".webp", ".tiff"],
    "output_json_file": "image_index.json",
    "exclude_dirs": [".git", "__pycache__", "venv", ".vscode"]
}

logger = logging.getLogger("photo_json")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)


def scan_for_images(root_dir: Path, valid_extensions: List[str], exclude_dirs: List[str]) -> List[Dict]:
    """Scans a directory and returns a list of image descriptions (does not write to file)."""
    images = []
    if not root_dir.is_dir():
        raise FileNotFoundError(f"Directory does not exist: {root_dir}")
    for p in root_dir.rglob("*"):
        # Skip directories and excluded paths
        if p.is_dir():
            continue
        if any(part in exclude_dirs for part in p.parts):
            continue
        if p.suffix.lower() in valid_extensions:
            info = {
                "filename": p.name,
                "relative_path": str(p.relative_to(root_dir)).replace("\\", "/")
            }
            # If Pillow is available, try to read dimensions (optional)
            if PIL_AVAILABLE:
                try:
                    with Image.open(p) as im:
                        info.update({"width": im.width, "height": im.height})
                except Exception as e:
                    logger.debug(f"Could not read image dimensions: {p} ({e})")
            images.append(info)
    return images


def write_json(output_path: Path, data: Dict):
    """Writes data to a JSON file."""
    try:
        with output_path.open("w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        logger.info(f"Written to {output_path}")
    except Exception as e:
        logger.error(f"Failed to write JSON: {e}")
        raise


def cli_main(argv: Optional[List[str]] = None):
    """Handles the command-line interface logic."""
    ap = argparse.ArgumentParser(description="Scans a directory for images and outputs a JSON file.")
    ap.add_argument("--scan", "-s", required=True, help="Path of the directory to scan")
    ap.add_argument("--output", "-o", default=CONFIG["output_json_file"], help="Name or path of the output JSON file")
    ap.add_argument("--exclude", help="Directories to exclude, comma-separated", default=",".join(CONFIG["exclude_dirs"]))
    args = ap.parse_args(argv)

    scan_path = Path(args.scan).expanduser().resolve()
    output_path = Path(args.output).expanduser().resolve()
    exclude_dirs = [d.strip() for d in args.exclude.split(',') if d.strip()]

    logger.info(f"Scanning: {scan_path}")
    try:
        images = scan_for_images(scan_path, CONFIG["image_extensions"], exclude_dirs)
        final = {
            "scan_info": {
                "scan_date": datetime.datetime.now().isoformat(),
                "total_images": len(images),
                "scan_directory": str(scan_path)
            },
            "images": images
        }
        write_json(output_path, final)
    except FileNotFoundError as e:
        logger.error(str(e))
        sys.exit(1)
    except Exception as e:
        logger.exception("An error occurred during scanning or writing")
        sys.exit(1)


def run_gui():
    """Handles the graphical user interface (GUI) logic."""
    if not TK_AVAILABLE:
        logger.error("Could not load tkinter. GUI will not start. Use --scan in headless environments.")
        sys.exit(1)

    class App:
        def __init__(self, root):
            self.root = root
            self.root.title("Image Scanner and Indexer")
            self.root.geometry("600x450")
            self.root.deiconify()
            self.scan_thread = None

            self.main_frame = ttk.Frame(root, padding="10")
            self.main_frame.pack(fill=tk.BOTH, expand=True)

            control_frame = ttk.Frame(self.main_frame)
            control_frame.pack(fill=tk.X)
            control_frame.grid_columnconfigure(1, weight=1)

            ttk.Label(control_frame, text="Folder to scan:").grid(row=0, column=0, sticky=tk.W)
            self.path_var = tk.StringVar()
            self.path_entry = ttk.Entry(control_frame, textvariable=self.path_var)
            self.path_entry.grid(row=0, column=1, sticky=tk.EW, padx=5)
            self.browse_button = ttk.Button(control_frame, text="Browse", command=self.select_directory)
            self.browse_button.grid(row=0, column=2)

            self.start_button = ttk.Button(control_frame, text="Start Scan", command=self.start_scan)
            self.start_button.grid(row=1, column=1, pady=6, sticky=tk.EW)

            self.results_text = tk.Text(self.main_frame, height=15, state=tk.DISABLED)
            self.results_text.pack(fill=tk.BOTH, expand=True, pady=6)

            self.status_var = tk.StringVar(value="Ready")
            ttk.Label(self.main_frame, textvariable=self.status_var).pack(anchor=tk.W)

        def select_directory(self):
            path = filedialog.askdirectory()
            if path:
                self.path_var.set(path)

        def start_scan(self):
            scan_path = Path(self.path_var.get())
            if not scan_path.exists():
                messagebox.showerror("Error", "Please select an existing directory.")
                return
            
            self.status_var.set("Scanning...")
            self.results_text.config(state=tk.NORMAL)
            self.results_text.delete('1.0', tk.END)
            self.start_button.config(state=tk.DISABLED)
            self.browse_button.config(state=tk.DISABLED)

            # Start a new thread to run the scan task and avoid blocking the main UI
            self.scan_thread = threading.Thread(target=self.perform_scan, args=(scan_path,))
            self.scan_thread.daemon = True  # Ensure the thread exits when the main program does
            self.scan_thread.start()

        def perform_scan(self, scan_path: Path):
            """Performs the scan and write operations in a separate thread."""
            try:
                images = scan_for_images(scan_path, CONFIG["image_extensions"], CONFIG["exclude_dirs"])
                final = {
                    "scan_info": {
                        "scan_date": datetime.datetime.now().isoformat(),
                        "total_images": len(images),
                        "scan_directory": str(scan_path)
                    },
                    "images": images
                }
                output_file = scan_path / CONFIG["output_json_file"]
                write_json(output_file, final)

                # Use root.after to update the main UI thread with the results
                self.root.after(0, self.update_ui_on_success, images, output_file, scan_path)

            except Exception as e:
                logger.exception("An error occurred during scanning")
                self.root.after(0, self.update_ui_on_error, e)
            
        def update_ui_on_success(self, images: List[Dict], output_file: Path, scan_path: Path):
            """Updates the UI after a successful scan, formatting the output as requested."""
            self.results_text.tag_config("bold", font=("", 10, "bold"))
            
            # 1. Output the scan summary
            summary = (
                f"Scan Summary:\n"
                f"  Total Images: {len(images)}\n"
                f"  Scan Directory: {scan_path}\n"
                f"  JSON Output File (1): {output_file}\n"
                f"{'-' * 40}\n"
                f"Found Images:\n"
            )
            self.results_text.insert(tk.END, summary)

            # 2. Output the numbered list of images
            for i, img in enumerate(images, 1):
                self.results_text.insert(tk.END, f"{i}. {img['relative_path']}\n")

            self.results_text.config(state=tk.DISABLED)
            messagebox.showinfo("Complete", f"Scan complete! Found {len(images)} images.\nJSON saved to:\n{output_file}")
            self.status_var.set(f"Complete. Found {len(images)} images.")
            self.start_button.config(state=tk.NORMAL)
            self.browse_button.config(state=tk.NORMAL)

        def update_ui_on_error(self, error: Exception):
            """Updates the UI after a scan failure."""
            messagebox.showerror("Error", str(error))
            self.status_var.set("Error")
            self.results_text.config(state=tk.DISABLED)
            self.start_button.config(state=tk.NORMAL)
            self.browse_button.config(state=tk.NORMAL)

    root = tk.Tk()
    app = App(root)
    root.mainloop()


if __name__ == '__main__':
    # Determine whether to launch CLI or GUI
    if '--scan' in sys.argv or '--no-gui' in sys.argv:
        cli_main(sys.argv[1:])
    else:
        run_gui()