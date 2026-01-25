"""
SQL generation module for creating INSERT statements.
"""
import os
from config import TABLE_NAME, SQL_OUT_FILE


def sql_escape(s: str) -> str:
    """Escape single quotes for SQL strings."""
    return s.replace("'", "''")


def generate_sql_row(photo_id: int, photo_caption: str, photo_name: str, category_id: int) -> str:
    """
    Generate a single SQL VALUES tuple.
    
    Args:
        photo_id: The photo ID
        photo_caption: Caption for the photo
        photo_name: Filename of the photo
        category_id: Category ID for the photo
    
    Returns:
        str: SQL VALUES tuple string
    """
    return f"({photo_id}, '{sql_escape(photo_caption)}', '{sql_escape(photo_name)}', {category_id})"


def build_insert_statement(sql_rows: list) -> str:
    """
    Build a complete INSERT statement from a list of value tuples.
    
    Args:
        sql_rows: List of SQL VALUES tuple strings
    
    Returns:
        str: Complete INSERT statement
    """
    if not sql_rows:
        return ""
    
    return (
        f"INSERT INTO `{TABLE_NAME}` (`photo_id`, `photo_caption`, `photo_name`, `p_category_id`) VALUES\n"
        + ",\n".join(sql_rows)
        + ";\n"
    )


def write_sql_file(directory: str, sql_rows: list) -> bool:
    """
    Write SQL INSERT statements to a file.
    
    Args:
        directory: Directory to write the SQL file
        sql_rows: List of SQL VALUES tuple strings
    
    Returns:
        bool: True if successful, False otherwise
    """
    if not sql_rows:
        print("No SQL generated (no successful conversions).")
        return False
    
    sql = build_insert_statement(sql_rows)
    out_path = os.path.join(directory, SQL_OUT_FILE)
    
    try:
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(sql)
        print(f"SQL script generated: {out_path}")
        return True
    except Exception as e:
        print(f"Error writing SQL file: {e}")
        return False

