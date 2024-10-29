import pyodbc
import sqlite3
import sys

def mdb_to_sqlite(mdb_file, sqlite_file):
    # 连接到 Access 数据库
    access_conn = pyodbc.connect(f"Driver={{Microsoft Access Driver (*.mdb, *.accdb)}};DBQ={mdb_file};")
    access_cursor = access_conn.cursor()

    # 连接到 SQLite 数据库
    sqlite_conn = sqlite3.connect(sqlite_file)
    sqlite_cursor = sqlite_conn.cursor()

    # 获取 Access 数据库中的所有表
    access_cursor.tables()
    tables = [table.table_name for table in access_cursor.fetchall()]

    for table_name in tables:
        # 跳过系统表
        if table_name.startswith("MSys"):
            print(f"Skipping system table: {table_name}")
            continue
        
        print(f"Processing table: {table_name}")
        
        # 获取表结构
        access_cursor.execute(f"SELECT * FROM {table_name}")
        columns = [column[0] for column in access_cursor.description]

        # 创建 SQLite 表
        create_table_query = f"CREATE TABLE {table_name} ({', '.join(columns)})"
        sqlite_cursor.execute(create_table_query)

        # 插入数据
        for row in access_cursor.fetchall():
            placeholders = ', '.join('?' * len(columns))
            insert_query = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({placeholders})"
            sqlite_cursor.execute(insert_query, row)

    # 提交并关闭连接
    sqlite_conn.commit()
    access_conn.close()
    sqlite_conn.close()
    print("Data transfer completed.")

# 使用示例
mdb_file = sys.argv[1]
sqlite_file = sys.argv[2]

mdb_to_sqlite(mdb_file, sqlite_file)
