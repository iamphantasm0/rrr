"""
Main entry point for the image processing automation workflow.

This script orchestrates:
1. Image conversion and renaming
2. FTP upload to server
3. SQL execution on remote database
"""
from config import (
    TARGET_DIR, START_NUMBER, NEW_PREFIX,
    ENABLE_FTP_UPLOAD, ENABLE_MYSQL_EXECUTE
)
from image_processing import convert_and_rename_images
from ftp_upload import upload_images_ftp
from mysql_execution import execute_sql_on_database


def run_full_automation():
    """
    Main automation function that:
    1. Converts and renames images
    2. Uploads converted images to FTP server
    3. Executes SQL INSERT statements on remote database
    """
    print("=" * 60)
    print("🚀 FULL AUTOMATION: Image Processing Workflow")
    print("=" * 60)

    # Step 1: Convert and rename images
    print("\n📷 STEP 1: Converting and renaming images...")
    converted_files, sql_rows = convert_and_rename_images(TARGET_DIR, START_NUMBER, NEW_PREFIX)

    if not converted_files:
        print("\n⚠️ No files were converted. Automation stopped.")
        return

    print(f"\n✅ Successfully converted {len(converted_files)} file(s)")

    # Step 2: Upload to FTP server
    if ENABLE_FTP_UPLOAD:
        print("\n📤 STEP 2: Uploading images to FTP server...")
        upload_success, upload_failed = upload_images_ftp(TARGET_DIR, converted_files)

        if upload_failed:
            print(f"⚠️ {len(upload_failed)} file(s) failed to upload")
    else:
        print("\n⏭️ STEP 2: FTP upload disabled (ENABLE_FTP_UPLOAD = False)")

    # Step 3: Execute SQL on database
    if ENABLE_MYSQL_EXECUTE:
        print("\n🗄️ STEP 3: Executing SQL on remote database...")
        db_success = execute_sql_on_database(sql_rows)

        if not db_success:
            print("⚠️ Database operation failed. SQL file is still available locally.")
    else:
        print("\n⏭️ STEP 3: MySQL execution disabled (ENABLE_MYSQL_EXECUTE = False)")

    # Summary
    print("\n" + "=" * 60)
    print("🏁 AUTOMATION COMPLETE")
    print("=" * 60)
    print(f"   📷 Images converted: {len(converted_files)}")
    if ENABLE_FTP_UPLOAD:
        print(f"   📤 Images uploaded: {upload_success}/{len(converted_files)}")
    if ENABLE_MYSQL_EXECUTE:
        print(f"   🗄️ Database updated: {'Yes' if db_success else 'No'}")
    print("=" * 60)


# Execute
if __name__ == "__main__":
    run_full_automation()
    