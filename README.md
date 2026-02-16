# Image Processing Automation

A fully automated image processing workflow that converts images, uploads to FTP server, and executes SQL on a remote MySQL database.

## Features

- **Image Conversion**: Converts RAW and standard image formats to JPG
- **Sequential Renaming**: Renames files with a configurable prefix and numbering
- **FTP Upload**: Automatically uploads converted images to a remote server
- **MySQL Integration**: Executes INSERT statements on a remote database
- **Modular Architecture**: Clean separation of concerns across multiple modules

## Project Structure

```text
├── main.py              # Entry point - orchestrates the workflow
├── config.py            # Configuration & environment variables
├── image_processing.py  # Image conversion and renaming logic
├── ftp_upload.py        # FTP upload functionality
├── mysql_execution.py   # MySQL database operations
├── sql_creation.py      # SQL generation utilities
├── .env                 # Credentials (not committed to git)
├── .env.example         # Template for .env file
├── requirements.txt     # Python dependencies
└── .gitignore           # Git ignore rules
```

## Supported Input Formats

| Type | Extensions |
|------|------------|
| **RAW** | CR2, NEF, ARW, DNG, RW2 |
| **Standard** | JPG, JPEG, PNG, WEBP, TIF, TIFF, BMP, HEIC, AVIF |

## Installation

1. Ensure Python 3.9 or newer is installed.

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   .\venv\Scripts\activate      # Windows
   source venv/bin/activate     # Linux/Mac
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure credentials by copying `.env.example` to `.env` and updating values.

## Configuration

Edit `config.py` or `.env` to customize:

| Variable | Description | Default |
|----------|-------------|---------|
| `START_NUMBER` | Starting number for sequential naming | 422 |
| `NEW_PREFIX` | Filename prefix | `photo-` |
| `TARGET_DIR` | Directory containing images | `.` |
| `P_CATEGORY_ID` | Category ID for SQL records | 16 |
| `CAPTION_PREFIX` | Prefix for photo captions | `AGM2025` |
| `ENABLE_FTP_UPLOAD` | Enable/disable FTP upload | `True` |
| `ENABLE_MYSQL_EXECUTE` | Enable/disable MySQL execution | `True` |

### Environment Variables (.env)

```env
FTP_HOST=your_ftp_host
FTP_USER=your_ftp_username
FTP_PASS=your_ftp_password
FTP_PORT=21
FTP_UPLOAD_DIR=public_html/images

MYSQL_HOST=your_mysql_host
MYSQL_USER=your_mysql_username
MYSQL_PASS=your_mysql_password
MYSQL_DATABASE=your_database_name
MYSQL_PORT=3306
```

## Usage

Place images in the target directory and run:

```bash
python main.py
```

### Workflow Steps

1. **Step 1**: Convert and rename images to JPG format
2. **Step 2**: Upload converted images to FTP server
3. **Step 3**: Execute SQL INSERT statements on MySQL database

## Output

- Sequentially named JPG files (`photo-<ID>.JPG`)
- SQL file: `tbl_photo_insert.sql`

## Module Overview

| Module | Responsibility |
|--------|----------------|
| `main.py` | Entry point, workflow orchestration |
| `config.py` | Centralized configuration management |
| `image_processing.py` | RAW/standard image conversion, file renaming |
| `ftp_upload.py` | FTP connection, directory creation, file upload |
| `mysql_execution.py` | MySQL connection, SQL execution |
| `sql_creation.py` | SQL statement generation, file writing |

## Safety Guarantees

- Real image conversion (not just renaming)
- Avoids overwriting existing files
- Prevents duplicate IDs
- Deletes originals only after successful conversion
- SQL matches filesystem output exactly
- Credentials stored securely in `.env` (not committed)

