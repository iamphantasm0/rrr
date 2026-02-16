"""
Image processing module for converting and renaming images.
Hybrid approach: ffmpeg for standard formats (speed), dcraw_emu for RAW (quality).
"""
import os
import re
import subprocess
import shutil
from pathlib import Path

from config import (
    SUPPORTED_INPUT_EXTENSIONS, TARGET_EXTENSION, JPEG_QUALITY,
    P_CATEGORY_ID, CAPTION_PREFIX
)
from sql_creation import generate_sql_row, write_sql_file


# RAW file extensions that require dcraw_emu processing
RAW_EXTS = {'.cr2', '.nef', '.arw', '.dng', '.rw2'}


def check_dependencies() -> dict:
    """
    Check if required command-line tools are available.
    
    Returns:
        dict: Status of each tool (ffmpeg, dcraw_emu)
    """
    status = {}
    
    # Check ffmpeg
    try:
        subprocess.run(['ffmpeg', '-version'], 
                      stdout=subprocess.PIPE, 
                      stderr=subprocess.PIPE, 
                      check=True)
        status['ffmpeg'] = True
    except (subprocess.CalledProcessError, FileNotFoundError):
        status['ffmpeg'] = False
    
    # Check dcraw_emu (part of libraw)
    try:
        subprocess.run(['dcraw_emu'], 
                      stdout=subprocess.PIPE, 
                      stderr=subprocess.PIPE)
        status['dcraw_emu'] = True
    except FileNotFoundError:
        status['dcraw_emu'] = False
    
    return status


def convert_and_rename_images(directory: str, start_num: int, prefix: str) -> tuple:
    """
    Converts supported images (RAW + standard formats) to JPG, renames sequentially,
    deletes source files only after successful conversion, and generates SQL rows.
    
    Uses hybrid approach:
    - RAW files: dcraw_emu → TIFF → ffmpeg → JPG (quality processing)
    - Standard files: ffmpeg → JPG (fast processing)
    
    Args:
        directory: Directory containing images to process
        start_num: Starting number for sequential naming
        prefix: Prefix for renamed files (e.g., 'photo-')
    
    Returns:
        tuple: (converted_files, sql_rows) - Lists of converted filenames and SQL value tuples
    """
    print(f"Starting file convert in: {os.path.abspath(directory)}")
    
    # Check dependencies
    deps = check_dependencies()
    print(f"Dependencies: ffmpeg={deps['ffmpeg']}, dcraw_emu={deps['dcraw_emu']}")
    
    if not deps['ffmpeg']:
        print("⚠️ WARNING: ffmpeg not found! Falling back to Python libraries.")
        print("   Install ffmpeg for better performance: https://ffmpeg.org/download.html")
        return _fallback_to_python_libs(directory, start_num, prefix)
    
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
            _convert_image_hybrid(old_path, new_path, deps)
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


def _convert_image_hybrid(input_path: str, output_path: str, deps: dict) -> None:
    """
    Convert an image to JPG format using hybrid approach.
    
    Args:
        input_path: Source image path
        output_path: Destination JPG path
        deps: Dictionary of available dependencies
    """
    ext = os.path.splitext(input_path)[1].lower()

    if ext in RAW_EXTS:
        if deps['dcraw_emu']:
            _convert_raw_with_dcraw(input_path, output_path)
        else:
            print(f"   ⚠️ dcraw_emu not found, using ffmpeg for RAW (lower quality)")
            _convert_with_ffmpeg(input_path, output_path)
    else:
        _convert_with_ffmpeg(input_path, output_path)


def _convert_raw_with_dcraw(input_path: str, output_path: str) -> None:
    """
    Convert RAW image to JPG using dcraw_emu for quality, then ffmpeg for final JPEG.
    
    Process: RAW → dcraw_emu → TIFF → ffmpeg → JPG
    
    Args:
        input_path: Source RAW file
        output_path: Destination JPG file
    """
    # Create temporary TIFF file
    temp_tiff = output_path.replace('.JPG', '_temp.tiff').replace('.jpg', '_temp.tiff')
    
    try:
        # Step 1: RAW → TIFF with dcraw_emu
        # -w: Use camera white balance
        # -H 0: No highlight reconstruction (preserve detail)
        # -q 3: High quality interpolation (AHD)
        # -o 1: sRGB color space
        # -T: Output TIFF format
        subprocess.run([
            'dcraw_emu',
            '-w',           # Camera white balance
            '-H', '0',      # No highlight clipping
            '-q', '3',      # AHD interpolation (high quality)
            '-o', '1',      # sRGB output
            '-T',           # TIFF format
            input_path
        ], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # dcraw_emu outputs to same directory with .tiff extension
        dcraw_output = os.path.splitext(input_path)[0] + '.tiff'
        
        if not os.path.exists(dcraw_output):
            raise FileNotFoundError(f"dcraw_emu did not create expected output: {dcraw_output}")
        
        # Step 2: TIFF → JPG with ffmpeg
        # Map JPEG quality (0-100) to ffmpeg's qscale (2-31, lower is better)
        # Quality 95 ≈ qscale 2
        qscale = max(2, min(31, int((100 - JPEG_QUALITY) / 3)))
        
        subprocess.run([
            'ffmpeg',
            '-i', dcraw_output,
            '-q:v', str(qscale),
            '-y',  # Overwrite output file
            output_path
        ], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Clean up temporary TIFF
        if os.path.exists(dcraw_output):
            os.remove(dcraw_output)
            
    except subprocess.CalledProcessError as e:
        # Clean up any temporary files on error
        if os.path.exists(temp_tiff):
            os.remove(temp_tiff)
        dcraw_output = os.path.splitext(input_path)[0] + '.tiff'
        if os.path.exists(dcraw_output):
            os.remove(dcraw_output)
        raise RuntimeError(f"RAW conversion failed: {e.stderr.decode() if e.stderr else str(e)}")


def _convert_with_ffmpeg(input_path: str, output_path: str) -> None:
    """
    Convert standard image formats to JPG using ffmpeg.
    
    Args:
        input_path: Source image file
        output_path: Destination JPG file
    """
    # Map JPEG quality (0-100) to ffmpeg's qscale (2-31, lower is better)
    # Quality 95 ≈ qscale 2
    qscale = max(2, min(31, int((100 - JPEG_QUALITY) / 3)))
    
    try:
        subprocess.run([
            'ffmpeg',
            '-i', input_path,
            '-q:v', str(qscale),
            '-y',  # Overwrite output file
            output_path
        ], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"ffmpeg conversion failed: {e.stderr.decode() if e.stderr else str(e)}")


def _fallback_to_python_libs(directory: str, start_num: int, prefix: str) -> tuple:
    """
    Fallback to original Python library approach if ffmpeg is not available.
    
    Args:
        directory: Directory containing images to process
        start_num: Starting number for sequential naming
        prefix: Prefix for renamed files
    
    Returns:
        tuple: (converted_files, sql_rows)
    """
    try:
        import rawpy
        import imageio
        from PIL import Image
    except ImportError as e:
        print(f"❌ Required Python libraries not found: {e}")
        print("   Install with: pip install rawpy imageio Pillow")
        return [], []
    
    converted_files = []
    sql_rows = []
    
    all_files = _get_files_in_directory(directory)
    if all_files is None:
        return [], []
    
    target_files = _filter_supported_files(all_files)
    
    if not target_files:
        return [], []
    
    current_number = start_num
    print(f"Found {len(target_files)} files to convert (using Python libraries)")
    
    for old_name in target_files:
        new_name = f"{prefix}{current_number}{TARGET_EXTENSION}"
        old_path = os.path.join(directory, old_name)
        new_path = os.path.join(directory, new_name)
        
        if os.path.exists(new_path):
            print(f"Skipping {old_name}: Target name {new_name} already exists!")
            current_number += 1
            continue
        
        try:
            ext = os.path.splitext(old_path)[1].lower()
            
            if ext in RAW_EXTS:
                # RAW processing with rawpy
                with rawpy.imread(old_path) as raw:
                    rgb = raw.postprocess(
                        use_camera_wb=True,
                        no_auto_bright=True,
                        output_bps=8
                    )
                imageio.imwrite(new_path, rgb, format="JPEG", quality=JPEG_QUALITY)
            else:
                # Standard format processing with Pillow
                with Image.open(old_path) as img:
                    if img.mode in ("RGBA", "LA") or (img.mode == "P" and "transparency" in img.info):
                        img = img.convert("RGBA")
                        background = Image.new("RGB", img.size, (255, 255, 255))
                        background.paste(img, mask=img.split()[-1])
                        img = background
                    else:
                        img = img.convert("RGB")
                    img.save(new_path, "JPEG", quality=JPEG_QUALITY, subsampling=0)
            
            os.remove(old_path)
            print(f"Converted: **{old_name}** -> **{new_name}** (Python)")
            
            converted_files.append(new_name)
            photo_caption = f"{CAPTION_PREFIX}{current_number}"
            sql_rows.append(generate_sql_row(current_number, photo_caption, new_name, P_CATEGORY_ID))
            current_number += 1
            
        except Exception as e:
            print(f"Error converting {old_name}: {e}")
    
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