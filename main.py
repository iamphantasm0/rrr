# renamepic.py
import os
import re  # We'll use this to filter files by extension (case-insensitive)

import rawpy
import imageio
from PIL import Image

# --- Configuration ---
START_NUMBER = 422
NEW_PREFIX = 'photo-'
TARGET_DIR = "."

# Convert ANY of these current extensions to JPG (case-insensitive)
# Add/remove as needed.
SUPPORTED_INPUT_EXTENSIONS = (
    '.cr2', '.nef', '.arw', '.dng', '.rw2',  # RAW
    '.jpg', '.jpeg', '.png', '.webp', '.tif', '.tiff', '.bmp', '.heic', '.avif'  # common image types
)

TARGET_EXTENSION = '.JPG'  # output extension

P_CATEGORY_ID = 16
CAPTION_PREFIX = "AGM2025"

SQL_OUT_FILE = "tbl_photo_insert.sql"
TABLE_NAME = "tbl_photo"

# JPEG settings
JPEG_QUALITY = 95
# ---------------------


def rename_files_sequentially(directory, start_num, prefix):
    """
    Converts supported images (RAW + standard formats) to JPG, renames sequentially,
    deletes source files only after successful conversion, and generates a SQL INSERT
    script for the successfully created JPGs.
    """

    print(f"Starting file convert in: {os.path.abspath(directory)}")

    # 1. Get all files in the directory
    try:
        all_files = os.listdir(directory)
    except FileNotFoundError:
        print(f"Error: Directory not found at {directory}")
        print("Checking if path exists...")
        parent_dir = os.path.dirname(directory)
        if os.path.exists(parent_dir):
            print(f"Parent directory exists: {parent_dir}")
            print("Available folders in parent directory:")
            for item in os.listdir(parent_dir):
                if os.path.isdir(os.path.join(parent_dir, item)):
                    print(f"  - {item}")
        else:
            print(f"Parent directory does not exist: {parent_dir}")
        return
    except PermissionError:
        print(f"Error: Permission denied accessing directory {directory}")
        return
    except Exception as e:
        print(f"Unexpected error accessing directory: {e}")
        return

    # 2. Filter for supported input extensions (case-insensitive)
    # KEEPING YOUR ORIGINAL STYLE (regex match + sorted order)
    # Build pattern like: .*\.(cr2|nef|jpg|jpeg|png)$  (case-insensitive)
    exts_no_dot = [e.lstrip('.').lower() for e in SUPPORTED_INPUT_EXTENSIONS]
    extensions_group = "|".join(map(re.escape, exts_no_dot))
    extension_pattern = re.compile(rf".*\.({extensions_group})$", re.IGNORECASE)

    target_files = sorted([f for f in all_files if extension_pattern.match(f)])

    if not target_files:
        print("No supported image files found in the directory.")
        print(f"Supported extensions: {', '.join(SUPPORTED_INPUT_EXTENSIONS)}")
        print("Available files in directory:")
        for f in all_files:
            print(f"  - {f}")
        return

    current_number = start_num
    print(f"Found {len(target_files)} files to convert. Starting sequence at {prefix}{current_number}{TARGET_EXTENSION.upper()}")

    sql_rows = []

    def sql_escape(s: str) -> str:
        return s.replace("'", "''")

    RAW_EXTS = {'.cr2', '.nef', '.arw', '.dng', '.rw2'}

    for old_name in target_files:
        new_name = f"{prefix}{current_number}{TARGET_EXTENSION.upper()}"

        old_path = os.path.join(directory, old_name)
        new_path = os.path.join(directory, new_name)

        # Prevent overwriting / collisions
        if os.path.exists(new_path):
            print(f"Skipping {old_name}: Target name {new_name} already exists!")
            current_number += 1  # advance to avoid duplicate IDs/filenames
            continue

        try:
            ext = os.path.splitext(old_name)[1].lower()

            if ext in RAW_EXTS:
                # RAW → JPG
                with rawpy.imread(old_path) as raw:
                    rgb = raw.postprocess(
                        use_camera_wb=True,
                        no_auto_bright=True,
                        output_bps=8
                    )
                imageio.imwrite(new_path, rgb, format="JPEG", quality=JPEG_QUALITY)

            else:
                # Standard image → JPG (Pillow)
                with Image.open(old_path) as img:
                    # Handle transparency by flattening onto white
                    if img.mode in ("RGBA", "LA") or (img.mode == "P" and "transparency" in img.info):
                        img = img.convert("RGBA")
                        background = Image.new("RGB", img.size, (255, 255, 255))
                        background.paste(img, mask=img.split()[-1])
                        img = background
                    else:
                        img = img.convert("RGB")

                    img.save(new_path, "JPEG", quality=JPEG_QUALITY, subsampling=0)

            # Delete source only after successful conversion
            os.remove(old_path)

            print(f"Converted: **{old_name}** -> **{new_name}**")

            photo_id = current_number
            photo_caption = f"{CAPTION_PREFIX}{photo_id}"
            photo_name = new_name

            sql_rows.append(
                f"({photo_id}, '{sql_escape(photo_caption)}', '{sql_escape(photo_name)}', {P_CATEGORY_ID})"
            )

            current_number += 1

        except Exception as e:
            print(f"Error converting {old_name}: {e}")

    print("--- Conversion complete! ---")

    # Write SQL file
    if sql_rows:
        sql = (
            f"INSERT INTO `{TABLE_NAME}` (`photo_id`, `photo_caption`, `photo_name`, `p_category_id`) VALUES\n"
            + ",\n".join(sql_rows)
            + ";\n"
        )
        out_path = os.path.join(directory, SQL_OUT_FILE)
        try:
            with open(out_path, "w", encoding="utf-8") as f:
                f.write(sql)
            print(f"SQL script generated: {out_path}")
        except Exception as e:
            print(f"Error writing SQL file: {e}")
    else:
        print("No SQL generated (no successful conversions).")


# Execute
rename_files_sequentially(TARGET_DIR, START_NUMBER, NEW_PREFIX)
