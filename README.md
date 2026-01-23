# Image Converter, Sequential Renamer & SQL Generator

## What This Code Is

This codebase is a batch image processing utility designed to standardize image assets and keep a database in sync with the filesystem. It converts images of various formats into real JPEG files, renames them sequentially, and generates a MySQL-compatible SQL INSERT script that matches the generated image files exactly.

## What It Does

For every supported image in the target directory, the script:

- Detects the image format
- Converts it to a real JPG file
- Renames it using a sequential numeric scheme
- Deletes the original file only after successful conversion
- Generates a matching SQL INSERT statement

## Supported Input Formats

**RAW formats:** CR2, NEF, ARW, DNG, RW2  
**Standard formats:** JPG, JPEG, PNG, WEBP, TIF, TIFF, BMP, HEIC  

All formats are processed case-insensitively.

## Installation

1. Ensure Python 3.9 or newer is installed.
2. (Recommended) Create a virtual environment:
   ```bash
   python -m venv venv
   ```
3. Activate the virtual environment.
4. Install dependencies:
   ```bash
   pip install rawpy imageio pillow
   ```

## How to Use

Place the script in the directory containing your images or update the `TARGET_DIR` variable. Adjust configuration values as needed, then run:

```bash
python main.py
```

## Output

The script generates:

- Sequentially named JPG files (`photo-<ID>.JPG`)
- A SQL file named `tbl_photo_insert.sql` containing matching database records

## Safety Guarantees

The script:

- Performs real image conversion
- Avoids overwriting files
- Prevents duplicate IDs
- Ensures SQL matches filesystem output
- Deletes original files only after successful conversion