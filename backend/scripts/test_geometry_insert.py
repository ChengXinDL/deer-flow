#!/usr/bin/env python3
"""
测试 GEOMETRY 字段插入
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
        
        # 获取一条数据
        source_cursor.execute(f"SELECT * FROM `{table}` WHERE `guid` = %s LIMIT 1", (guid,))
        row = source_cursor.fetchone()
        columns = [desc[0] for desc in source_cursor.description]
        
        print("源数据:")
        for i, col in enumerate(columns):
            value = row[i]
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
        boundary_idx = columns.index('boundaryPolygon')
        boundary_value = row[boundary_idx]
        
        print("\n测试不同的插入方式:")
        
        # 方法1: 使用 ST_GeomFromWKB
        try:
            target_cursor.execute(f"""
                INSERT INTO `{target_table}` (`guid`, `boundaryPolygon`) 
                VALUES (%s, ST_GeomFromWKB(%s))
            """, (guid, boundary_value))
            target_conn.commit()
            print("方法1 (ST_GeomFromWKB): 成功")
        except MySQLError as e:
            print(f"方法1 (ST_GeomFromWKB): 失败 - {e}")
            target_conn.rollback()
        
        # 方法2: 使用 ST_GeomFromText
        try:
            target_cursor.execute(f"""
                INSERT INTO `{target_table}` (`guid`, `boundaryPolygon`) 
                VALUES (%s, ST_GeomFromText('POINT(0 0)'))
            """, (guid,))
            target_conn.commit()
            print("方法2 (ST_GeomFromText): 成功")
        except MySQLError as e:
            print(f"方法2 (ST_GeomFromText): 失败 - {e}")
            target_conn.rollback()
        
        # 方法3: 直接插入 bytes（不使用函数）
        try:
            target_cursor.execute(f"""
                INSERT INTO `{target_table}` (`guid`, `boundaryPolygon`) 
                VALUES (%s, %s)
            """, (guid, boundary_value))
            target_conn.commit()
            print("方法3 (直接插入bytes): 成功")
        except MySQLError as e:
            print(f"方法3 (直接插入bytes): 失败 - {e}")
            target_conn.rollback()
        
        target_cursor.close()
        target_conn.close()
        
    except MySQLError as e:
        print(f"数据库连接失败: {e}")

if __name__ == "__main__":
    test_geometry_insert()
