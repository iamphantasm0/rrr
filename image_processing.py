"""
Image processing module for converting and renaming images.
"""
import os
import re

import rawpy
import imageio
from PIL import Image

from config import (
    SUPPORTED_INPUT_EXTENSIONS, TARGET_EXTENSION, JPEG_QUALITY,
    P_CATEGORY_ID, CAPTION_PREFIX
)
from sql_creation import generate_sql_row, write_sql_file


# RAW file extensions that require rawpy processing
RAW_EXTS = {'.cr2', '.nef', '.arw', '.dng', '.rw2'}


def convert_and_rename_images(directory: str, start_num: int, prefix: str) -> tuple:
    """
    Converts supported images (RAW + standard formats) to JPG, renames sequentially,
    deletes source files only after successful conversion, and generates SQL rows.
    
    Args:
        directory: Directory containing images to process
        start_num: Starting number for sequential naming
        prefix: Prefix for renamed files (e.g., 'photo-')
    
    Returns:
        tuple: (converted_files, sql_rows) - Lists of converted filenames and SQL value tuples
    """
    print(f"Starting file convert in: {os.path.abspath(directory)}")
    converted_files = []
    sql_rows = []

    # Get all files in the directory
    all_files = _get_files_in_directory(directory)
    if all_files is None:
        return [], []

    # Filter for supported input extensions
    target_files = _filter_supported_files(all_files)
    
    if not target_files:
        print("No supported image files found in the directory.")
        print(f"Supported extensions: {', '.join(SUPPORTED_INPUT_EXTENSIONS)}")
        print("Available files in directory:")
        for f in all_files:
            print(f"  - {f}")
        return [], []

    current_number = start_num
    print(f"Found {len(target_files)} files to convert. Starting sequence at {prefix}{current_number}{TARGET_EXTENSION}")

    for old_name in target_files:
        new_name = f"{prefix}{current_number}{TARGET_EXTENSION}"
        old_path = os.path.join(directory, old_name)
        new_path = os.path.join(directory, new_name)

        # Prevent overwriting / collisions
        if os.path.exists(new_path):
            print(f"Skipping {old_name}: Target name {new_name} already exists!")
            current_number += 1
            continue

        try:
            _convert_image(old_path, new_path)
            os.remove(old_path)
            print(f"Converted: **{old_name}** -> **{new_name}**")

            converted_files.append(new_name)
            
            photo_caption = f"{CAPTION_PREFIX}{current_number}"
            sql_rows.append(generate_sql_row(current_number, photo_caption, new_name, P_CATEGORY_ID))
            
            current_number += 1

        except Exception as e:
            print(f"Error converting {old_name}: {e}")

    print("--- Conversion complete! ---")
    
    # Write SQL file
    write_sql_file(directory, sql_rows)

    return converted_files, sql_rows


def _get_files_in_directory(directory: str) -> list:
    """Get list of files in directory with error handling."""
    try:
        return os.listdir(directory)
    except FileNotFoundError:
        print(f"Error: Directory not found at {directory}")
        return None
    except PermissionError:
        print(f"Error: Permission denied accessing directory {directory}")
        return None
    except Exception as e:
        print(f"Unexpected error accessing directory: {e}")
        return None


def _filter_supported_files(all_files: list) -> list:
    """Filter files to only include supported image extensions."""
    exts_no_dot = [e.lstrip('.').lower() for e in SUPPORTED_INPUT_EXTENSIONS]
    extensions_group = "|".join(map(re.escape, exts_no_dot))
    extension_pattern = re.compile(rf".*\.({extensions_group})$", re.IGNORECASE)
    return sorted([f for f in all_files if extension_pattern.match(f)])


def _convert_image(input_path: str, output_path: str) -> None:
    """Convert an image to JPG format."""
    ext = os.path.splitext(input_path)[1].lower()

    if ext in RAW_EXTS:
        _convert_raw_to_jpg(input_path, output_path)
    else:
        _convert_standard_to_jpg(input_path, output_path)


def _convert_raw_to_jpg(input_path: str, output_path: str) -> None:
    """Convert RAW image to JPG using rawpy."""
    with rawpy.imread(input_path) as raw:
        rgb = raw.postprocess(
            use_camera_wb=True,
            no_auto_bright=True,
            output_bps=8
        )
    imageio.imwrite(output_path, rgb, format="JPEG", quality=JPEG_QUALITY)


def _convert_standard_to_jpg(input_path: str, output_path: str) -> None:
    """Convert standard image formats to JPG using Pillow."""
    with Image.open(input_path) as img:
        # Handle transparency by flattening onto white
        if img.mode in ("RGBA", "LA") or (img.mode == "P" and "transparency" in img.info):
            img = img.convert("RGBA")
            background = Image.new("RGB", img.size, (255, 255, 255))
            background.paste(img, mask=img.split()[-1])
            img = background
        else:
            img = img.convert("RGB")

        img.save(output_path, "JPEG", quality=JPEG_QUALITY, subsampling=0)

