#!/usr/bin/env python3
"""
测试 _get_existing_records 方法返回的数据格式
"""

import mysql.connector
from mysql.connector import Error as MySQLError

def test_existing_records():
    # B 数据库连接配置
    config = {
        'user': 'app',
        'password': 'sykj_1234A',
        'host': '49.234.197.113',
        'port': 33307,
        'database': 'bim_agent_data',
        'charset': 'utf8mb4',
        'collation': 'utf8mb4_unicode_ci'
    }
    
    table = 'table_Wall'
    guid = '640672095077'
    
    try:
        conn = mysql.connector.connect(**config)
        cursor = conn.cursor()
        
        # 查询已存在的记录
        cursor.execute(f"SELECT * FROM `{table}` WHERE `guid` = %s", (guid,))
        columns = [desc[0] for desc in cursor.description]
        records = cursor.fetchall()
        
        print(f"找到 {len(records)} 条记录")
        
        if records:
            row = records[0]
            row_dict = dict(zip(columns, row))
            
            print("\n目标数据库中的记录格式:")
            for col, value in row_dict.items():
                if isinstance(value, bytes):
                    print(f"  {col}: bytes, length={len(value)}, hex={value[:30].hex()}")
                elif isinstance(value, str):
                    print(f"  {col}: str, length={len(value)}, value={value[:50]}")
                else:
                    print(f"  {col}: {type(value).__name__} = {value}")
        
        cursor.close()
        conn.close()
        
    except MySQLError as e:
        print(f"数据库连接失败: {e}")

if __name__ == "__main__":
    test_existing_records()
