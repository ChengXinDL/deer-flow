#!/usr/bin/env python3
"""
测试 GEOMETRY 字段插入 - 使用不同的参数绑定方式
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
        'collation': 'utf8mb4_unicode_ci',
        'use_pure': True  # 使用纯 Python 实现
    }
    
    # A 数据库连接配置
    source_config = {
        'user': 'app',
        'password': 'sykj_1234A',
        'host': '192.168.8.221',
        'port': 3307,
        'database': 'bim_data',
        'charset': 'utf8mb4',
        'collation': 'utf8mb4_unicode_ci',
        'use_pure': True
    }
    
    table = 'table_wall'
    target_table = 'table_Wall'
    guid = '640672095077'
    
    try:
        # 连接源数据库获取数据
        source_conn = mysql.connector.connect(**source_config)
        source_cursor = source_conn.cursor(dictionary=True)
        
        # 获取一条数据
        source_cursor.execute(f"SELECT * FROM `{table}` WHERE `guid` = %s LIMIT 1", (guid,))
        row = source_cursor.fetchone()
        
        print("源数据:")
        for col, value in row.items():
            if isinstance(value, bytes):
                print(f"  {col}: bytes, length={len(value)}, hex={value[:30].hex()}")
            else:
                print(f"  {col}: {type(value).__name__} = {value}")
        
        source_cursor.close()
        source_conn.close()
        
        # 连接目标数据库测试插入
        target_conn = mysql.connector.connect(**config)
        target_cursor = target_conn.cursor()
        
        # 获取所有列
        columns = list(row.keys())
        column_names = ', '.join([f'`{col}`' for col in columns])
        placeholders = ', '.join(['%s'] * len(columns))
        values = list(row.values())
        
        print(f"\n测试批量插入...")
        print(f"Values types: {[type(v).__name__ for v in values]}")
        
        try:
            target_cursor.execute(f"""
                INSERT INTO `{target_table}` ({column_names}) VALUES ({placeholders})
            """, values)
            target_conn.commit()
            print("批量插入成功！")
        except MySQLError as e:
            print(f"批量插入失败: {e}")
            target_conn.rollback()
        
        # 测试单独插入 GEOMETRY 字段
        boundary_value = row.get('boundaryPolygon')
        print(f"\n测试单独插入 GEOMETRY 字段...")
        print(f"boundaryPolygon type: {type(boundary_value)}")
        print(f"boundaryPolygon length: {len(boundary_value)}")
        
        try:
            target_cursor.execute("""
                INSERT INTO `table_Wall` (`guid`, `boundaryPolygon`) VALUES (%s, %s)
            """, (guid, boundary_value))
            target_conn.commit()
            print("单独插入成功！")
        except MySQLError as e:
            print(f"单独插入失败: {e}")
            target_conn.rollback()
        
        target_cursor.close()
        target_conn.close()
        
    except MySQLError as e:
        print(f"数据库连接失败: {e}")

if __name__ == "__main__":
    test_geometry_insert()
