"""
MySQL execution module for running SQL queries on the remote database.
"""
import mysql.connector
from config import (
    MYSQL_HOST, MYSQL_USER, MYSQL_PASS, MYSQL_DATABASE, MYSQL_PORT, TABLE_NAME
)


def execute_sql_on_database(sql_statements) -> bool:
    """
    Execute SQL INSERT statements on the remote MySQL database.
    
    Args:
        sql_statements: List of SQL value tuples or the full SQL string
    
    Returns:
        bool: True if successful, False otherwise
    """
    if not MYSQL_PASS:
        print("❌ MySQL password not set! Please update your .env file.")
        return False
    
    print(f"\n🗄️ Connecting to MySQL database...")
    print(f"   Host: {MYSQL_HOST}")
    print(f"   Database: {MYSQL_DATABASE}")
    
    try:
        conn = mysql.connector.connect(
            host=MYSQL_HOST,
            port=MYSQL_PORT,
            user=MYSQL_USER,
            password=MYSQL_PASS,
            database=MYSQL_DATABASE,
            connection_timeout=30
        )
        cursor = conn.cursor()
        print(f"✅ Connected to MySQL database")
        
        # Build and execute the INSERT statement
        if isinstance(sql_statements, list) and len(sql_statements) > 0:
            sql = (
                f"INSERT INTO `{TABLE_NAME}` (`photo_id`, `photo_caption`, `photo_name`, `p_category_id`) VALUES\n"
                + ",\n".join(sql_statements)
            )
            cursor.execute(sql)
            conn.commit()
            print(f"✅ Inserted {cursor.rowcount} record(s) into {TABLE_NAME}")
        elif isinstance(sql_statements, str) and sql_statements.strip():
            cursor.execute(sql_statements)
            conn.commit()
            print(f"✅ SQL executed successfully")
        else:
            print("⚠️ No SQL statements to execute")
            cursor.close()
            conn.close()
            return True
        
        cursor.close()
        conn.close()
        print("🗄️ Database connection closed")
        return True
        
    except mysql.connector.Error as e:
        print(f"❌ MySQL Error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error during database operation: {e}")
        return False

