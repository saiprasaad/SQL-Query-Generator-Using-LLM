import json
import mysql.connector

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "yourpassword",
    "database": "yourdbname"
}

def extract_schema():
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT table_name, column_name, column_type
        FROM information_schema.columns
        WHERE table_schema = DATABASE()
        ORDER BY table_name, ordinal_position
    """)

    schema = {"tables": {}, "relationships": []}

    for table, column, col_type in cursor.fetchall():
        schema["tables"].setdefault(table, []).append({"column": column, "type": col_type})

    cursor.execute("""
        SELECT TABLE_NAME, COLUMN_NAME, REFERENCED_TABLE_NAME, REFERENCED_COLUMN_NAME
        FROM information_schema.key_column_usage
        WHERE referenced_table_name IS NOT NULL
        AND table_schema = DATABASE()
    """)

    for child, child_col, parent, parent_col in cursor.fetchall():
        schema["relationships"].append({
            "child_table": child,
            "child_column": child_col,
            "parent_table": parent,
            "parent_column": parent_col
        })

    cursor.close()
    conn.close()

    with open("schema.json", "w") as f:
        json.dump(schema, f, indent=2)

    print("schema.json generated successfully!")

if __name__ == "__main__":
    extract_schema()
