import pyodbc
import sqlite3
import sys

def map_access_type_to_sqlite(access_type):
    # 将 Python 数据类型映射到 SQLite 数据类型
    if access_type == str:
        return "TEXT"
    elif access_type == int:
        return "INTEGER"
    elif access_type == float:
        return "REAL"
    elif access_type == bool:
        return "BOOLEAN"
    elif access_type == bytearray:
        return "BLOB"
    else:
        # 默认类型为 TEXT
        return "TEXT"

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
        columns_info = [(column[0], column[1]) for column in access_cursor.description]

        # 创建 SQLite 表，包含字段类型
        column_defs = []
        for column_name, column_type in columns_info:
            sqlite_type = map_access_type_to_sqlite(column_type)
            column_defs.append(f"{column_name} {sqlite_type}")
        create_table_query = f"CREATE TABLE {table_name} ({', '.join(column_defs)})"
        sqlite_cursor.execute(create_table_query)

        # 插入数据
        for row in access_cursor.fetchall():
            placeholders = ', '.join('?' * len(columns_info))
            insert_query = f"INSERT INTO {table_name} ({', '.join([col[0] for col in columns_info])}) VALUES ({placeholders})"
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
