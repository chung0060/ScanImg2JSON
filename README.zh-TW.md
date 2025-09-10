# ScanImg2JSON

[English](README.md)

一個能掃描指定資料夾及其子目錄下的圖片檔案，並建立 JSON 索引檔的 Python 工具。本專案同時支援簡單的 GUI (Tkinter) 桌面操作與用於自動化腳本的 CLI。

## 功能

* **掃描**常見的圖片檔案類型（例如：.jpg, .png, .webp, .heic）。
* **生成** `image_index.json` 檔案，其中包含掃描中繼資料與圖片清單。
* 提供簡單的 Tkinter **GUI** 供使用者互動操作。
* 支援 **CLI**，適用於無頭環境和自動化。
* （可選）若安裝了 Pillow 函式庫，可額外擷取圖片尺寸。

## 快速開始

### 前置需求

本程式僅使用標準 Python 函式庫。若要啟用圖片尺寸擷取功能，請安裝 Pillow：

```bash
pip install Pillow
```

### 使用方法

首先，請將專案下載至您的本機，或直接取得 `photo_json.py` 檔案。

#### 1. GUI (預設)

直接執行程式以啟動圖形介面。點擊「瀏覽」選擇資料夾，然後點擊「開始掃描」。`image_index.json` 檔案將會在被掃描的目錄中生成。

```bash
python photo_json.py
```

#### 2. CLI (命令列)

為了用於自動化或伺服器環境，請使用 `--scan` 旗標。

```bash
python photo_json.py --scan /path/to/your/images
```

**常見命令列選項：**
* `--scan` 或 `-s`: **(必填)** 要掃描的目錄。
* `--output` 或 `-o`: 輸出的 JSON 檔名。（預設為 `image_index.json`）
* `--exclude`: 要排除的資料夾列表，以逗號分隔。
* `--no-gui`: 強制使用 CLI 模式，即使 GUI 環境可用。

## JSON 輸出範例

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

## 授權

本專案使用 MIT License 授權 - 詳細內容請參閱 `LICENSE` 檔案。
