#!/usr/bin/env python3
"""
检查 GEOMETRY 字段的数据格式
"""

import mysql.connector
from mysql.connector import Error as MySQLError

def check_geometry_data():
    # A 数据库连接配置
    config = {
        'user': 'app',
        'password': 'sykj_1234A',
        'host': '192.168.8.221',
        'port': 3307,
        'database': 'bim_data',
        'charset': 'utf8mb4',
        'collation': 'utf8mb4_unicode_ci'
    }
    
    guid = '640672095077'
    table = 'table_wall'
    
    try:
        conn = mysql.connector.connect(**config)
        cursor = conn.cursor()
        
        print(f"检查表 {table} 的 GEOMETRY 字段数据...")
        print("-" * 60)
        
        # 获取表结构
        cursor.execute(f"DESCRIBE `{table}`")
        columns = cursor.fetchall()
        
        geometry_cols = []
        for col in columns:
            col_name = col[0]
            col_type = col[1]
            if 'geometry' in col_type.lower() or 'point' in col_type.lower() or 'polygon' in col_type.lower():
                geometry_cols.append(col_name)
        
        print(f"GEOMETRY 字段: {geometry_cols}")
        print()
        
        # 查询几条数据查看 GEOMETRY 字段的值
        cursor.execute(f"SELECT * FROM `{table}` WHERE `guid` = %s LIMIT 3", (guid,))
        rows = cursor.fetchall()
        
        for i, row in enumerate(rows):
            print(f"记录 {i+1}:")
            for j, col in enumerate(columns):
                col_name = col[0]
                value = row[j]
                if col_name in geometry_cols:
                    print(f"  {col_name}: {type(value)} = {value[:50] if value else 'NULL'}...")
                    if isinstance(value, bytes):
                        print(f"    Bytes length: {len(value)}")
                        print(f"    First 20 bytes (hex): {value[:20].hex()}")
                elif col_name in ['id', 'guid', 'name']:
                    print(f"  {col_name}: {value}")
            print()
        
        cursor.close()
        conn.close()
        
    except MySQLError as e:
        print(f"数据库连接失败: {e}")

if __name__ == "__main__":
    check_geometry_data()
