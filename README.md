# ScanImg2JSON

[繁體中文](README.zh-TW.md)

A Python tool to scan image files in a specified directory and its subdirectories, generating a JSON index file. The project supports both a simple GUI (Tkinter) for desktop use and a CLI for automated scripts.

## Features

* **Scans** common image file types (e.g., .jpg, .png, .webp, .heic).
* **Generates** a `image_index.json` file with scan metadata and a list of images.
* Provides a simple Tkinter **GUI** for interactive use.
* Supports a **CLI** for headless environments and automation.
* (Optional) Extracts image dimensions if the Pillow library is installed.

## Getting Started

### Prerequisites

The script uses only standard Python libraries. To enable image dimension extraction, install Pillow:

```bash
pip install Pillow
```

### Usage

First, clone the repository or download `photo_json.py` to your local machine.

#### 1. GUI (Default)

Run the script directly to launch the graphical interface. Click "Browse" to select a folder, and then "Start Scan." The `image_index.json` file will be created in the scanned directory.

```bash
python photo_json.py
```

#### 2. CLI (Command-Line)

For automation or server environments, use the `--scan` flag.

```bash
python photo_json.py --scan /path/to/your/images
```

**Common CLI Options:**
* `--scan` or `-s`: **(Required)** The directory to scan.
* `--output` or `-o`: The name of the output JSON file. (Defaults to `image_index.json`)
* `--exclude`: A comma-separated list of directories to exclude from the scan.
* `--no-gui`: Force CLI mode, even if a GUI environment is available.

## JSON Output Example

```json
{
  "scan_info": {
    "scan_date": "2024-01-01T12:34:56",
    "total_images": 123,
    "scan_directory": "/absolute/path/to/scan"
  },
  "images": [
    {"filename": "IMG_0001.jpg", "relative_path": "sub/IMG_0001.jpg"},
    {"filename": "logo.png", "relative_path": "logo.png"}
  ]
}
```

---

## License

This project is licensed under the MIT License - see the `LICENSE` file for details.
