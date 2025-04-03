# Listing tables
import sqlite3

    conn = sqlite3.connect('my_database.sqlite')
    cursor = conn.cursor()

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()

    for table in tables:
        print(table[0])

    conn.close()
    
# Getting Table Schema:
import sqlite3

    conn = sqlite3.connect('my_database.sqlite')
    cursor = conn.cursor()

    cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='my_table'")
    schema = cursor.fetchone()

    if schema:
        print(schema[0])

    conn.close()