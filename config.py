"""
Configuration module for the image processing automation.
Loads settings from environment variables and defines constants.
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# --- Image Processing Configuration ---
START_NUMBER = 4490
NEW_PREFIX = 'photo-'
TARGET_DIR = "img"

# Supported input image extensions (case-insensitive)
SUPPORTED_INPUT_EXTENSIONS = (
    '.cr2', '.nef', '.arw', '.dng', '.rw2',  # RAW formats
    '.jpg', '.jpeg', '.png', '.webp', '.tif', '.tiff', '.bmp', '.heic', '.avif'
)

TARGET_EXTENSION = '.JPG'
JPEG_QUALITY = 95

# --- SQL Configuration ---
P_CATEGORY_ID = 17
CAPTION_PREFIX = "TEST1"
SQL_OUT_FILE = "tbl_photo_insert.sql"
TABLE_NAME = "tbl_photo"

# --- FTP Configuration (from .env) ---
FTP_HOST = os.getenv('FTP_HOST', '212.85.30.97')
FTP_USER = os.getenv('FTP_USER', 'u321880591')
FTP_PASS = os.getenv('FTP_PASS', '')
FTP_PORT = int(os.getenv('FTP_PORT', '21'))
FTP_UPLOAD_DIR = os.getenv('FTP_UPLOAD_DIR', 'public_html/images')

# --- MySQL Configuration (from .env) ---
MYSQL_HOST = os.getenv('MYSQL_HOST', 'srv661.hstgr.io')
MYSQL_USER = os.getenv('MYSQL_USER', 'u321880591_admincms')
MYSQL_PASS = os.getenv('MYSQL_PASS', '')
MYSQL_DATABASE = os.getenv('MYSQL_DATABASE', 'u321880591_admincms')
MYSQL_PORT = int(os.getenv('MYSQL_PORT', '3306'))

# --- Automation Flags ---
ENABLE_FTP_UPLOAD = True
ENABLE_MYSQL_EXECUTE = True

