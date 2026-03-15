#!/usr/bin/env python3
"""
删除 B 数据库中所有 guid=640672095077 的数据
"""

import mysql.connector
from mysql.connector import Error as MySQLError

def delete_guid_data():
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
    
    guid = '640672095077'
    
    try:
        conn = mysql.connector.connect(**config)
        cursor = conn.cursor()
        
        print(f"开始删除 guid={guid} 的数据...")
        print("-" * 60)
        
        # 获取所有包含 guid 字段且以 table_ 开头的表
        cursor.execute("""
            SELECT TABLE_NAME 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE COLUMN_NAME = 'guid' 
              AND TABLE_SCHEMA = 'bim_agent_data'
              AND TABLE_NAME LIKE 'table_%'
            ORDER BY TABLE_NAME
        """)
        
        tables = [row[0] for row in cursor.fetchall()]
        
        total_deleted = 0
        deleted_tables = 0
        
        # 对每个表执行删除
        for table in tables:
            try:
                cursor.execute(f"DELETE FROM `{table}` WHERE `guid` = %s", (guid,))
                deleted_count = cursor.rowcount
                conn.commit()
                
                if deleted_count > 0:
                    print(f"表 {table}: 删除 {deleted_count} 条记录")
                    total_deleted += deleted_count
                    deleted_tables += 1
                    
            except MySQLError as e:
                print(f"表 {table}: 删除失败 - {e}")
        
        print("-" * 60)
        print(f"删除完成！")
        print(f"涉及表数: {deleted_tables}")
        print(f"总删除记录数: {total_deleted}")
        
        cursor.close()
        conn.close()
        
    except MySQLError as e:
        print(f"数据库连接失败: {e}")

if __name__ == "__main__":
    delete_guid_data()
