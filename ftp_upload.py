"""
FTP upload module for uploading images to the server.
"""
import os
import ftplib
from config import FTP_HOST, FTP_USER, FTP_PASS, FTP_PORT, FTP_UPLOAD_DIR


def upload_images_ftp(local_dir: str, file_list: list, remote_dir: str = None) -> tuple:
    """
    Upload converted JPG files to the server via FTP.
    
    Args:
        local_dir: Local directory containing the files
        file_list: List of filenames to upload
        remote_dir: Remote directory path (defaults to FTP_UPLOAD_DIR)
    
    Returns:
        tuple: (success_count, failed_files)
    """
    if not FTP_PASS:
        print("❌ FTP password not set! Please update your .env file.")
        return 0, file_list
    
    if remote_dir is None:
        remote_dir = FTP_UPLOAD_DIR
    
    success_count = 0
    failed_files = []
    
    print(f"\n📤 Starting FTP upload to {FTP_HOST}...")
    print(f"   Remote directory: {remote_dir}")
    
    try:
        # Connect to FTP server
        ftp = ftplib.FTP()
        ftp.connect(FTP_HOST, FTP_PORT, timeout=30)
        ftp.login(FTP_USER, FTP_PASS)
        print(f"✅ Connected to FTP server: {FTP_HOST}")
        
        # Navigate to remote directory (create if needed)
        _navigate_to_directory(ftp, remote_dir)
        
        # Upload each file
        for filename in file_list:
            local_path = os.path.join(local_dir, filename)
            if not os.path.exists(local_path):
                print(f"   ⚠️ File not found: {filename}")
                failed_files.append(filename)
                continue
            
            try:
                with open(local_path, 'rb') as f:
                    ftp.storbinary(f'STOR {filename}', f)
                print(f"   ✅ Uploaded: {filename}")
                success_count += 1
            except Exception as e:
                print(f"   ❌ Failed to upload {filename}: {e}")
                failed_files.append(filename)
        
        ftp.quit()
        print(f"\n📤 FTP Upload complete: {success_count}/{len(file_list)} files uploaded")
        
    except ftplib.all_errors as e:
        print(f"❌ FTP Error: {e}")
        return success_count, failed_files
    except Exception as e:
        print(f"❌ Unexpected error during FTP upload: {e}")
        return success_count, failed_files
    
    return success_count, failed_files


def _navigate_to_directory(ftp: ftplib.FTP, remote_dir: str) -> None:
    """
    Navigate to remote directory, creating it if necessary.
    
    Args:
        ftp: FTP connection object
        remote_dir: Remote directory path
    """
    try:
        ftp.cwd(remote_dir)
    except ftplib.error_perm:
        # Try to create directory path
        print(f"   Creating remote directory: {remote_dir}")
        dirs = remote_dir.split('/')
        current_path = ""
        for d in dirs:
            if d:
                current_path += f"/{d}"
                try:
                    ftp.cwd(current_path)
                except ftplib.error_perm:
                    try:
                        ftp.mkd(current_path)
                        ftp.cwd(current_path)
                    except ftplib.error_perm as e:
                        print(f"❌ Cannot create directory {current_path}: {e}")
                        raise

