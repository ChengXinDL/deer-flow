#!/usr/bin/env python3
"""
测试 GEOMETRY 字段插入 - 使用与迁移脚本相同的查询方式
"""

import mysql.connector
from mysql.connector import Error as MySQLError

def test_geometry_insert():
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
    
    # A 数据库连接配置
    source_config = {
        'user': 'app',
        'password': 'sykj_1234A',
        'host': '192.168.8.221',
        'port': 3307,
        'database': 'bim_data',
        'charset': 'utf8mb4',
        'collation': 'utf8mb4_unicode_ci'
    }
    
    table = 'table_wall'
    target_table = 'table_Wall'
    guid = '640672095077'
    
    try:
        # 连接源数据库获取数据
        source_conn = mysql.connector.connect(**source_config)
        source_cursor = source_conn.cursor()
        
        # 获取一条数据 - 使用 DictCursor
        source_cursor.execute(f"SELECT * FROM `{table}` WHERE `guid` = %s LIMIT 1", (guid,))
        row = source_cursor.fetchone()
        columns = [desc[0] for desc in source_cursor.description]
        
        # 转换为字典
        row_dict = dict(zip(columns, row))
        
        print("源数据 (Dict):")
        for col, value in row_dict.items():
            if isinstance(value, bytes):
                print(f"  {col}: bytes, length={len(value)}, hex={value[:30].hex()}")
            else:
                print(f"  {col}: {type(value).__name__} = {value}")
        
        source_cursor.close()
        source_conn.close()
        
        # 连接目标数据库测试插入
        target_conn = mysql.connector.connect(**config)
        target_cursor = target_conn.cursor()
        
        # 获取 boundaryPolygon 的值
        boundary_value = row_dict.get('boundaryPolygon')
        
        print("\n测试插入:")
        print(f"boundaryPolygon type: {type(boundary_value)}")
        print(f"boundaryPolygon length: {len(boundary_value) if boundary_value else 0}")
        
        # 构建插入语句（与迁移脚本相同的方式）
        insert_columns = list(row_dict.keys())
        column_names = ', '.join([f'`{col}`' for col in insert_columns])
        placeholders = ', '.join(['%s'] * len(insert_columns))
        
        insert_values = list(row_dict.values())
        
        print(f"\nInsert SQL: INSERT INTO `{target_table}` ({column_names}) VALUES ({placeholders})")
        print(f"Values count: {len(insert_values)}")
        
        try:
            target_cursor.execute(f"""
                INSERT INTO `{target_table}` ({column_names}) VALUES ({placeholders})
            """, insert_values)
            target_conn.commit()
            print("插入成功！")
        except MySQLError as e:
            print(f"插入失败: {e}")
            target_conn.rollback()
        
        target_cursor.close()
        target_conn.close()
        
    except MySQLError as e:
        print(f"数据库连接失败: {e}")

if __name__ == "__main__":
    test_geometry_insert()
