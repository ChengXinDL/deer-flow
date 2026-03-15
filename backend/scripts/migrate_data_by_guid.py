import argparse
import logging
import os
import sys
from datetime import datetime
from pathlib import Path

import mysql.connector
from mysql.connector import Error as MySQLError
from mysql.connector import errorcode


class DataMigrator:
    def __init__(self, source_db_url, target_db_url, guid, batch_size=100):
        self.source_db_url = source_db_url
        self.target_db_url = target_db_url
        self.guid = guid
        self.batch_size = batch_size
        self.source_conn = None
        self.target_conn = None
        self.logger = self._setup_logger()
        
    def _setup_logger(self):
        log_dir = Path(__file__).parent.parent / "logs"
        log_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = log_dir / f"migrate_data_by_guid_{self.guid}_{timestamp}.log"
        
        logger = logging.getLogger(f"DataMigrator_{self.guid}")
        logger.setLevel(logging.DEBUG)
        
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        
        return logger
    
    def _parse_db_url(self, db_url):
        if db_url.startswith('mysql+mysqlconnector://'):
            db_url = db_url.replace('mysql+mysqlconnector://', '')
        
        parts = db_url.split('@')
        if len(parts) != 2:
            raise ValueError(f"Invalid database URL format: {db_url}")
        
        auth_part = parts[0]
        host_part = parts[1]
        
        username, password = auth_part.split(':')
        
        host_parts = host_part.split('/')
        if len(host_parts) != 2:
            raise ValueError(f"Invalid database URL format: {db_url}")
        
        host_port = host_parts[0]
        database = host_parts[1]
        
        if ':' in host_port:
            host, port = host_port.split(':')
            port = int(port)
        else:
            host = host_port
            port = 3306
        
        return {
            'user': username,
            'password': password,
            'host': host,
            'port': port,
            'database': database
        }
    
    def connect_databases(self):
        try:
            source_config = self._parse_db_url(self.source_db_url)
            target_config = self._parse_db_url(self.target_db_url)
            
            # 添加连接超时和读取超时设置
            connection_config = {
                'connect_timeout': 600,      # 10分钟连接超时
                'read_timeout': 1800,        # 30分钟读取超时
                'write_timeout': 1800,       # 30分钟写入超时
                'autocommit': False,         # 手动控制事务
                'buffered': True,            # 缓冲结果集
                'pool_size': 5,              # 连接池大小
                'pool_reset_session': True,
                'raise_on_warnings': True,
                'use_pure': True,            # 使用纯Python驱动，更稳定
                'charset': 'utf8mb4',        # 使用utf8mb4字符集
                'collation': 'utf8mb4_unicode_ci',
                'sql_mode': 'STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION',
            }
            
            # 合并配置
            source_config.update(connection_config)
            target_config.update(connection_config)
            
            self.logger.info(f"连接源数据库: {source_config['host']}:{source_config['port']}/{source_config['database']}")
            self.source_conn = mysql.connector.connect(**source_config)
            self.logger.info("源数据库连接成功")
            
            self.logger.info(f"连接目标数据库: {target_config['host']}:{target_config['port']}/{target_config['database']}")
            self.target_conn = mysql.connector.connect(**target_config)
            self.logger.info("目标数据库连接成功")
            
            return True
        except MySQLError as e:
            self.logger.error(f"数据库连接失败: {e}")
            return False
        except Exception as e:
            self.logger.error(f"解析数据库URL失败: {e}")
            return False
    
    def get_all_tables(self, conn):
        try:
            cursor = conn.cursor()
            cursor.execute("SHOW TABLES")
            tables = [table[0] for table in cursor.fetchall()]
            cursor.close()
            return tables
        except MySQLError as e:
            self.logger.error(f"获取表列表失败: {e}")
            return []
    
    def to_camel_case(self, table_name):
        """
        将A数据库表名（下划线命名）转换为B数据库表名（驼峰命名）
        规则：
        - table_curtainwall -> table_Curtainwall
        - table_basepoint -> table_Basepoint
        - 保留第一个单词小写，后续单词首字母大写
        """
        parts = table_name.split('_')
        if len(parts) <= 1:
            return table_name
        
        # 第一个单词保持小写，后续单词首字母大写
        result = [parts[0]]  # 第一个单词保持原样（小写）
        for word in parts[1:]:
            # 后续单词首字母大写，其余小写
            result.append(word.capitalize())
        
        return '_'.join(result)
    
    def to_snake_case(self, table_name):
        """将驼峰命名转换为小写下划线命名（A数据库命名规则）"""
        # 处理驼峰命名，如 TableColumn -> table_column
        result = []
        for i, char in enumerate(table_name):
            if char.isupper() and i > 0:
                result.append('_')
            result.append(char.lower())
        return ''.join(result)
    
    def find_target_table_name(self, source_table_name, target_tables):
        """根据A数据库表名查找B数据库中对应的表名（只匹配以 table_ 开头的表）"""
        # 只处理以 table_ 开头的源表
        if not source_table_name.startswith('table_'):
            return None
        
        # 直接匹配
        if source_table_name in target_tables:
            return source_table_name
        
        # 转换为驼峰命名后匹配
        camel_case_name = self.to_camel_case(source_table_name)
        if camel_case_name in target_tables:
            return camel_case_name
        
        # 尝试其他可能的命名变体（只匹配以 table_ 开头的目标表）
        for target_table in target_tables:
            # 只考虑以 table_ 开头的目标表
            if not target_table.lower().startswith('table_'):
                continue
            
            # 如果目标表名转小写后匹配
            if target_table.lower() == source_table_name.lower():
                return target_table
            # 如果目标表名转下划线后匹配
            if self.to_snake_case(target_table) == source_table_name:
                return target_table
        
        # 未找到匹配，返回驼峰命名作为新表名
        return camel_case_name
    
    def table_has_guid_column(self, conn, table_name):
        try:
            cursor = conn.cursor()
            cursor.execute(f"SHOW COLUMNS FROM `{table_name}` LIKE 'guid'")
            result = cursor.fetchone()
            cursor.close()
            return result is not None
        except MySQLError as e:
            self.logger.error(f"检查表 {table_name} 的guid列失败: {e}")
            return False
    
    def get_table_structure(self, conn, table_name):
        try:
            cursor = conn.cursor()
            cursor.execute(f"DESCRIBE `{table_name}`")
            columns = cursor.fetchall()
            cursor.close()
            return columns
        except MySQLError as e:
            self.logger.error(f"获取表 {table_name} 结构失败: {e}")
            return None
    
    def get_geometry_columns(self, conn, table_name):
        """获取表中所有 GEOMETRY 类型的列名"""
        try:
            cursor = conn.cursor()
            cursor.execute(f"""
                SELECT COLUMN_NAME, DATA_TYPE 
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_SCHEMA = DATABASE() 
                  AND TABLE_NAME = %s 
                  AND DATA_TYPE IN ('geometry', 'point', 'linestring', 'polygon', 
                                    'multipoint', 'multilinestring', 'multipolygon', 'geometrycollection')
            """, (table_name,))
            geometry_cols = {row[0]: row[1] for row in cursor.fetchall()}
            cursor.close()
            return geometry_cols
        except MySQLError as e:
            self.logger.warning(f"获取表 {table_name} 几何列信息失败: {e}")
            return {}
    
    def create_table(self, conn, table_name, structure):
        try:
            cursor = conn.cursor()
            
            column_defs = []
            for col in structure:
                col_name = col[0]
                col_type = col[1]
                col_null = "NULL" if col[2] == "YES" else "NOT NULL"
                col_key = col[3]
                col_default = col[4]
                col_extra = col[5]
                
                col_def = f"`{col_name}` {col_type} {col_null}"
                if col_default:
                    col_def += f" DEFAULT {col_default}"
                if col_extra:
                    col_def += f" {col_extra}"
                
                column_defs.append(col_def)
            
            create_sql = f"CREATE TABLE `{table_name}` ({', '.join(column_defs)})"
            cursor.execute(create_sql)
            conn.commit()
            cursor.close()
            
            self.logger.info(f"表 {table_name} 创建成功")
            return True
        except MySQLError as e:
            self.logger.error(f"创建表 {table_name} 失败: {e}")
            return False
    
    def compare_table_structure(self, source_structure, target_structure, source_table, target_table):
        """比较表结构，允许列名大小写不同"""
        if len(source_structure) != len(target_structure):
            self.logger.warning(f"表 {source_table} -> {target_table} 列数量不一致: 源表 {len(source_structure)} 列, 目标表 {len(target_structure)} 列")
            return False
        
        # 创建目标表列名映射（小写 -> 原始列名）
        target_columns_map = {col[0].lower(): col for col in target_structure}
        
        for src_col in source_structure:
            src_col_name = src_col[0]
            src_col_type = src_col[1]
            
            # 尝试查找匹配的目标列（不区分大小写）
            tgt_col = target_columns_map.get(src_col_name.lower())
            
            if tgt_col is None:
                self.logger.warning(f"表 {source_table} -> {target_table} 列不匹配: 源表列 '{src_col_name}' 在目标表中不存在")
                return False
            
            tgt_col_type = tgt_col[1]
            
            # 比较数据类型（不区分大小写）
            if src_col_type.lower() != tgt_col_type.lower():
                self.logger.warning(f"表 {source_table} -> {target_table} 列 '{src_col_name}' 数据类型不一致: 源表 {src_col_type}, 目标表 {tgt_col_type}")
                return False
        
        self.logger.info(f"表 {source_table} -> {target_table} 结构兼容（允许列名大小写不同）")
        return True
    
    def get_data_by_guid(self, conn, table_name, guid, limit=None):
        """获取数据，支持限制数量和流式读取"""
        try:
            cursor = conn.cursor(dictionary=True)
            if limit:
                cursor.execute(f"SELECT * FROM `{table_name}` WHERE `guid` = %s LIMIT %s", (guid, limit))
            else:
                cursor.execute(f"SELECT * FROM `{table_name}` WHERE `guid` = %s", (guid,))
            data = cursor.fetchall()
            cursor.close()
            return data
        except MySQLError as e:
            self.logger.error(f"从表 {table_name} 获取guid={guid}的数据失败: {e}")
            return []
    
    def get_data_by_guid_streaming(self, conn, table_name, guid, batch_size=1000):
        """流式获取数据，适用于大表，分批返回数据"""
        try:
            # 首先获取总数
            count_cursor = conn.cursor()
            count_cursor.execute(f"SELECT COUNT(*) FROM `{table_name}` WHERE `guid` = %s", (guid,))
            total_count = count_cursor.fetchone()[0]
            count_cursor.close()
            
            if total_count == 0:
                return [], 0
            
            # 使用服务器端游标进行流式读取
            cursor = conn.cursor(dictionary=True)
            cursor.execute(f"SELECT * FROM `{table_name}` WHERE `guid` = %s", (guid,))
            
            batch = []
            while True:
                row = cursor.fetchone()
                if row is None:
                    break
                batch.append(row)
                
                if len(batch) >= batch_size:
                    yield batch, total_count
                    batch = []
            
            # 返回最后一批
            if batch:
                yield batch, total_count
            
            cursor.close()
            
        except MySQLError as e:
            self.logger.error(f"从表 {table_name} 流式获取guid={guid}的数据失败: {e}")
            yield [], 0
    
    def get_data_count(self, conn, table_name, guid):
        """获取指定guid的数据总数"""
        try:
            cursor = conn.cursor()
            cursor.execute(f"SELECT COUNT(*) FROM `{table_name}` WHERE `guid` = %s", (guid,))
            count = cursor.fetchone()[0]
            cursor.close()
            return count
        except MySQLError as e:
            self.logger.error(f"获取表 {table_name} guid={guid} 的数据总数失败: {e}")
            return 0
    
    def get_table_primary_key(self, conn, table_name):
        try:
            cursor = conn.cursor()
            cursor.execute(f"SHOW KEYS FROM `{table_name}` WHERE Key_name = 'PRIMARY'")
            result = cursor.fetchone()
            cursor.close()
            if result:
                return result[4]
            return None
        except MySQLError as e:
            self.logger.error(f"获取表 {table_name} 主键失败: {e}")
            return None
    
    def insert_or_update_data(self, conn, table_name, data, guid, incremental=False):
        """批量插入或更新数据，支持增量更新
        
        Args:
            conn: 数据库连接
            table_name: 表名
            data: 待迁移的数据
            guid: guid值
            incremental: 是否使用增量更新模式（默认False，True时只插入新数据）
        """
        try:
            cursor = conn.cursor()
            
            primary_key = self.get_table_primary_key(conn, table_name)
            total_records = len(data)
            
            if total_records == 0:
                return True
            
            # 获取 GEOMETRY 列信息
            geometry_columns = self.get_geometry_columns(conn, table_name)
            if geometry_columns:
                self.logger.info(f"表 {table_name}: 发现 GEOMETRY 字段 {list(geometry_columns.keys())}")
            
            # 增量更新模式
            if incremental:
                if primary_key:
                    # 有主键表：查询目标表中已存在的主键值
                    existing_pks = self._get_existing_pks(cursor, table_name, primary_key, guid)
                    
                    # 过滤掉已存在的数据
                    new_data = [row for row in data if row.get(primary_key) not in existing_pks]
                    skipped_count = total_records - len(new_data)
                    
                    if skipped_count > 0:
                        self.logger.info(f"表 {table_name}: 跳过 {skipped_count} 条已存在的数据（增量更新）")
                    
                    if not new_data:
                        self.logger.info(f"表 {table_name}: 没有新数据需要迁移")
                        cursor.close()
                        return True
                    
                    data = new_data
                else:
                    # 无主键表：查询目标表中所有guid匹配的记录，通过比较所有字段判断是否已存在
                    existing_records = self._get_existing_records(cursor, table_name, guid)
                    
                    # 过滤掉已存在的数据（通过比较所有字段）
                    new_data = []
                    for row in data:
                        row_tuple = tuple(sorted(row.items()))
                        if row_tuple not in existing_records:
                            new_data.append(row)
                    
                    skipped_count = total_records - len(new_data)
                    
                    if skipped_count > 0:
                        self.logger.info(f"表 {table_name}: 跳过 {skipped_count} 条已存在的数据（增量更新）")
                    
                    if not new_data:
                        self.logger.info(f"表 {table_name}: 没有新数据需要迁移")
                        cursor.close()
                        return True
                    
                    data = new_data
            else:
                # 非增量模式：如果没有主键，先删除所有相同 guid 的旧记录
                if not primary_key:
                    delete_sql = f"DELETE FROM `{table_name}` WHERE `guid` = %s"
                    cursor.execute(delete_sql, (guid,))
                    deleted_count = cursor.rowcount
                    if deleted_count > 0:
                        self.logger.info(f"表 {table_name}: 已删除 {deleted_count} 条旧记录")
            
            # 批量处理
            for i in range(0, len(data), self.batch_size):
                batch = data[i:i + self.batch_size]
                
                if primary_key and not incremental:
                    # 有主键且非增量模式：逐条检查并更新/插入
                    self._batch_upsert_with_pk(cursor, table_name, batch, primary_key, geometry_columns)
                else:
                    # 无主键或增量模式：批量插入新数据
                    self._batch_insert(cursor, table_name, batch, geometry_columns)
                
                conn.commit()
            
            cursor.close()
            self.logger.info(f"表 {table_name}: 成功迁移 {len(data)} 条记录")
            return True
            
        except MySQLError as e:
            self.logger.error(f"表 {table_name} 数据迁移失败: {e}")
            conn.rollback()
            return False
    
    def _get_existing_pks(self, cursor, table_name, primary_key, guid):
        """获取目标表中已存在的主键值集合"""
        if not primary_key:
            # 无主键表，返回空集合（无法判断重复）
            return set()
        
        try:
            cursor.execute(f"SELECT `{primary_key}` FROM `{table_name}` WHERE `guid` = %s", (guid,))
            return {row[0] for row in cursor.fetchall()}
        except MySQLError as e:
            self.logger.warning(f"获取表 {table_name} 已存在主键失败: {e}")
            return set()
    
    def _get_existing_records(self, cursor, table_name, guid):
        """获取目标表中已存在的记录（用于无主键表的增量更新）"""
        try:
            cursor.execute(f"SELECT * FROM `{table_name}` WHERE `guid` = %s", (guid,))
            columns = [desc[0] for desc in cursor.description]
            records = cursor.fetchall()
            
            # 将记录转换为字典列表，然后转换为元组集合以便比较
            existing_set = set()
            for row in records:
                row_dict = dict(zip(columns, row))
                # 转换为排序后的元组，确保一致性
                row_tuple = tuple(sorted(row_dict.items()))
                existing_set.add(row_tuple)
            
            return existing_set
        except MySQLError as e:
            self.logger.warning(f"获取表 {table_name} 已存在记录失败: {e}")
            return set()
    
    def _batch_insert(self, cursor, table_name, batch, geometry_columns=None):
        """批量插入数据（无主键表）
        
        注意：跳过 GEOMETRY 字段，不复制空间数据
        """
        if not batch:
            return
        
        if geometry_columns is None:
            geometry_columns = {}
        
        # 过滤掉 GEOMETRY 字段
        all_columns = list(batch[0].keys())
        columns = [col for col in all_columns if col not in geometry_columns]
        
        if not columns:
            self.logger.warning(f"表 {table_name}: 所有字段都是 GEOMETRY 类型，跳过插入")
            return
        
        column_names = ', '.join([f'`{col}`' for col in columns])
        
        # 逐条插入数据
        for row in batch:
            # 构建插入语句
            placeholders = []
            values = []
            for col in columns:
                placeholders.append('%s')
                value = self._sanitize_value(row[col])
                values.append(value)
            
            # 执行单条插入
            insert_sql = f"INSERT INTO `{table_name}` ({column_names}) VALUES ({', '.join(placeholders)})"
            cursor.execute(insert_sql, values)
    
    def _batch_insert_data(self, conn, table_name, batch, geometry_columns=None):
        """批量插入数据（独立事务，用于流式处理）
        
        注意：跳过 GEOMETRY 字段，不复制空间数据
        """
        if not batch:
            return True
        
        if geometry_columns is None:
            geometry_columns = {}
        
        try:
            cursor = conn.cursor()
            
            # 过滤掉 GEOMETRY 字段
            all_columns = list(batch[0].keys())
            columns = [col for col in all_columns if col not in geometry_columns]
            
            if not columns:
                self.logger.warning(f"表 {table_name}: 所有字段都是 GEOMETRY 类型，跳过插入")
                cursor.close()
                return True
            
            column_names = ', '.join([f'`{col}`' for col in columns])
            
            # 逐条插入数据
            for row in batch:
                placeholders = []
                values = []
                for col in columns:
                    placeholders.append('%s')
                    value = self._sanitize_value(row[col])
                    values.append(value)
                
                insert_sql = f"INSERT INTO `{table_name}` ({column_names}) VALUES ({', '.join(placeholders)})"
                cursor.execute(insert_sql, values)
            cursor.close()
            return True
        except MySQLError as e:
            self.logger.error(f"表 {table_name} 批量插入失败: {e}")
            return False
    
    def _sanitize_value(self, value):
        """清理值中的特殊字符，确保可以安全地插入MySQL
        
        注意：保留中文字符，只移除真正的无效字符
        """
        if isinstance(value, str):
            try:
                # 移除NULL字符
                value = value.replace('\x00', '')
                
                # 移除控制字符（保留换行、回车、制表符）
                # 中文字符的 ord 值通常 > 127，不会被移除
                value = ''.join(char for char in value if ord(char) >= 32 or char in '\n\r\t')
                
            except Exception:
                # 如果失败，保留原始值
                pass
            
            return value
        elif isinstance(value, bytes):
            # 处理bytes类型 - 对于非GEOMETRY字段的bytes，尝试解码为字符串
            try:
                return value.decode('utf-8', errors='ignore')
            except Exception:
                try:
                    return value.decode('latin1', errors='ignore')
                except:
                    return ''
        return value
    
    def _batch_upsert_with_pk(self, cursor, table_name, batch, primary_key, geometry_columns=None):
        """批量 upsert 数据（有主键表）
        
        注意：跳过 GEOMETRY 字段，不复制空间数据
        """
        if not batch:
            return
        
        if geometry_columns is None:
            geometry_columns = {}
        
        # 过滤掉 GEOMETRY 字段
        all_columns = list(batch[0].keys())
        columns = [col for col in all_columns if col not in geometry_columns]
        
        if not columns:
            self.logger.warning(f"表 {table_name}: 所有字段都是 GEOMETRY 类型，跳过 upsert")
            return
        
        column_names = ', '.join([f'`{col}`' for col in columns])
        
        # 分离需要更新和插入的记录
        pk_values = [row[primary_key] for row in batch if primary_key in row]
        
        if pk_values:
            # 查询哪些主键已存在
            placeholders = ', '.join(['%s'] * len(pk_values))
            check_sql = f"SELECT `{primary_key}` FROM `{table_name}` WHERE `{primary_key}` IN ({placeholders})"
            cursor.execute(check_sql, tuple(pk_values))
            existing_pks = {row[0] for row in cursor.fetchall()}
        else:
            existing_pks = set()
        
        # 批量更新已存在的记录（跳过 GEOMETRY 字段）
        update_rows = [row for row in batch if row.get(primary_key) in existing_pks]
        if update_rows:
            for row in update_rows:
                set_parts = []
                update_values = []
                for col in columns:
                    if col != primary_key:
                        set_parts.append(f'`{col}` = %s')
                        value = self._sanitize_value(row[col])
                        update_values.append(value)
                
                if set_parts:  # 确保有要更新的字段
                    set_clause = ', '.join(set_parts)
                    update_values.append(row[primary_key])
                    update_sql = f"UPDATE `{table_name}` SET {set_clause} WHERE `{primary_key}` = %s"
                    cursor.execute(update_sql, update_values)
        
        # 批量插入新记录（跳过 GEOMETRY 字段）
        insert_rows = [row for row in batch if row.get(primary_key) not in existing_pks]
        if insert_rows:
            self._batch_insert(cursor, table_name, insert_rows, geometry_columns)
    
    def bulk_insert_via_csv(self, conn, table_name, data, temp_dir=None):
        """
        使用 LOAD DATA INFILE 进行大批量数据插入（性能最优）
        适用于上万行数据的迁移
        """
        import csv
        import tempfile
        import os
        
        if not data:
            return True
        
        try:
            # 创建临时CSV文件
            if temp_dir is None:
                temp_dir = tempfile.gettempdir()
            
            temp_file = os.path.join(temp_dir, f"migrate_{table_name}_{self.guid}.csv")
            
            # 获取列名
            columns = list(data[0].keys())
            
            # 写入CSV文件
            with open(temp_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f, quoting=csv.QUOTE_MINIMAL)
                for row in data:
                    writer.writerow([row[col] for col in columns])
            
            # 使用 LOAD DATA INFILE 导入数据
            cursor = conn.cursor()
            column_names = ', '.join([f'`{col}`' for col in columns])
            
            load_sql = f"""
                LOAD DATA LOCAL INFILE '{temp_file}'
                INTO TABLE `{table_name}`
                FIELDS TERMINATED BY ','
                ENCLOSED BY '"'
                LINES TERMINATED BY '\n'
                ({column_names})
            """
            
            cursor.execute(load_sql)
            conn.commit()
            cursor.close()
            
            # 删除临时文件
            os.remove(temp_file)
            
            self.logger.info(f"表 {table_name}: 通过CSV批量导入 {len(data)} 条记录")
            return True
            
        except Exception as e:
            self.logger.error(f"表 {table_name} CSV批量导入失败: {e}")
            # 失败时回退到普通批量插入
            return self.insert_or_update_data(conn, table_name, data, self.guid)
    
    def verify_data_integrity(self, source_conn, target_conn, table_name, guid):
        try:
            source_cursor = source_conn.cursor()
            target_cursor = target_conn.cursor()
            
            source_cursor.execute(f"SELECT COUNT(*) FROM `{table_name}` WHERE `guid` = %s", (guid,))
            source_count = source_cursor.fetchone()[0]
            
            target_cursor.execute(f"SELECT COUNT(*) FROM `{table_name}` WHERE `guid` = %s", (guid,))
            target_count = target_cursor.fetchone()[0]
            
            source_cursor.close()
            target_cursor.close()
            
            if source_count != target_count:
                self.logger.warning(f"表 {table_name} 数据完整性验证失败: 源数据库有 {source_count} 条记录，目标数据库有 {target_count} 条记录")
                return False
            else:
                self.logger.info(f"表 {table_name} 数据完整性验证通过: {source_count} 条记录")
                return True
        except MySQLError as e:
            self.logger.error(f"验证表 {table_name} 数据完整性失败: {e}")
            return False
    
    def migrate(self, incremental=False):
        """执行数据迁移任务
        
        Args:
            incremental: 是否使用增量更新模式（默认False）
        """
        start_time = datetime.now()
        self.logger.info(f"开始数据迁移任务 - GUID: {self.guid}")
        self.logger.info(f"源数据库: {self.source_db_url}")
        self.logger.info(f"目标数据库: {self.target_db_url}")
        self.logger.info(f"迁移模式: {'增量更新' if incremental else '全量覆盖'}")
        
        if not self.connect_databases():
            self.logger.error("数据库连接失败，迁移终止")
            return False
        
        # 统计信息
        stats = {
            'total_tables': 0,
            'processed_tables': 0,
            'created_tables': 0,
            'skipped_tables': 0,
            'failed_tables': 0,
            'total_records': 0,
            'table_times': []  # 记录每个表的处理时间
        }
        
        try:
            source_tables = self.get_all_tables(self.source_conn)
            target_tables = self.get_all_tables(self.target_conn)
            
            self.logger.info(f"源数据库: {len(source_tables)} 个表，目标数据库: {len(target_tables)} 个表")
            
            # 筛选包含 guid 字段且以 table_ 开头的表，排除 table_modeltree
            EXCLUDED_TABLES = {'table_modeltree'}  # 排除的表列表
            tables_with_guid = [
                t for t in source_tables
                if t.startswith('table_') 
                and t not in EXCLUDED_TABLES
                and self.table_has_guid_column(self.source_conn, t)
            ]
            stats['total_tables'] = len(tables_with_guid)
            self.logger.info(f"共有 {stats['total_tables']} 个以 'table_' 开头的表包含guid字段，开始迁移...")
            
            for table in tables_with_guid:
                table_start_time = datetime.now()
                
                # 查找目标表名
                target_table = self.find_target_table_name(table, target_tables)
                
                # 如果无法找到或创建目标表名，跳过
                if target_table is None:
                    self.logger.error(f"表 {table}: 无法确定目标表名，跳过")
                    stats['failed_tables'] += 1
                    continue
                
                # 获取源表结构
                source_structure = self.get_table_structure(self.source_conn, table)
                if not source_structure:
                    self.logger.error(f"表 {table}: 无法获取源结构，跳过")
                    stats['failed_tables'] += 1
                    continue
                
                # 检查目标表是否存在
                if target_table not in target_tables:
                    # 创建新表
                    if not self.create_table(self.target_conn, target_table, source_structure):
                        self.logger.error(f"表 {table} -> {target_table}: 创建目标表失败，跳过")
                        stats['failed_tables'] += 1
                        continue
                    target_tables.append(target_table)
                    stats['created_tables'] += 1
                else:
                    # 验证表结构兼容性
                    target_structure = self.get_table_structure(self.target_conn, target_table)
                    if target_structure and not self.compare_table_structure(source_structure, target_structure, table, target_table):
                        self.logger.warning(f"表 {table} -> {target_table}: 结构不兼容，尝试继续迁移")
                
                # 首先获取数据总数
                total_count = self.get_data_count(self.source_conn, table, self.guid)
                if total_count == 0:
                    stats['skipped_tables'] += 1
                    continue
                
                # 根据数据量选择处理方式
                STREAMING_THRESHOLD = 5000  # 超过5000条使用流式处理
                
                if total_count <= STREAMING_THRESHOLD:
                    # 小表：一次性获取并迁移
                    data = self.get_data_by_guid(self.source_conn, table, self.guid, limit=None)
                    if not data:
                        stats['skipped_tables'] += 1
                        continue
                    
                    # 迁移数据（小表使用增量更新）
                    if self.insert_or_update_data(self.target_conn, target_table, data, self.guid, incremental=incremental):
                        stats['processed_tables'] += 1
                        stats['total_records'] += len(data)
                        
                        # 记录处理时间
                        table_end_time = datetime.now()
                        table_duration = (table_end_time - table_start_time).total_seconds()
                        records_count = len(data)
                        efficiency = records_count / table_duration if table_duration > 0 else 0
                        
                        stats['table_times'].append({
                            'table': table,
                            'target_table': target_table,
                            'records': records_count,
                            'duration': table_duration,
                            'efficiency': efficiency
                        })
                        
                        self.logger.info(f"表 {table} -> {target_table}: {records_count}条记录，耗时{table_duration:.2f}秒，效率{efficiency:.1f}条/秒")
                        
                        # 验证数据完整性
                        if not self.verify_data_integrity(self.source_conn, self.target_conn, target_table, self.guid):
                            self.logger.warning(f"表 {target_table}: 数据完整性验证失败")
                    else:
                        self.logger.error(f"表 {table} -> {target_table}: 数据迁移失败")
                        stats['failed_tables'] += 1
                else:
                    # 大表：使用流式处理
                    self.logger.info(f"表 {table} -> {target_table}: 数据量较大({total_count}条)，使用流式处理")
                    
                    # 获取 GEOMETRY 列信息
                    geometry_columns = self.get_geometry_columns(self.target_conn, target_table)
                    if geometry_columns:
                        self.logger.info(f"表 {target_table}: 发现 GEOMETRY 字段 {list(geometry_columns.keys())}")
                    
                    # 先删除旧记录（对于大表，先清空再批量插入更高效）
                    primary_key = self.get_table_primary_key(self.target_conn, target_table)
                    if not primary_key:
                        # 无主键表：先删除所有相同guid的记录
                        delete_cursor = self.target_conn.cursor()
                        delete_cursor.execute(f"DELETE FROM `{target_table}` WHERE `guid` = %s", (self.guid,))
                        deleted_count = delete_cursor.rowcount
                        delete_cursor.close()
                        self.target_conn.commit()
                        if deleted_count > 0:
                            self.logger.info(f"表 {target_table}: 已删除 {deleted_count} 条旧记录")
                    
                    # 流式迁移数据 - 使用更小的批次和更频繁的提交
                    total_migrated = 0
                    batch_num = 0
                    streaming_batch_size = 50  # 大表使用更小的批次
                    
                    for batch, _ in self.get_data_by_guid_streaming(self.source_conn, table, self.guid, batch_size=streaming_batch_size):
                        if not batch:
                            continue
                        
                        batch_num += 1
                        
                        # 每5批保活一次连接
                        if batch_num % 5 == 0:
                            try:
                                self.source_conn.ping(reconnect=True, attempts=3, delay=5)
                                self.target_conn.ping(reconnect=True, attempts=3, delay=5)
                            except Exception as e:
                                self.logger.warning(f"连接保活失败: {e}")
                        
                        if incremental and primary_key:
                            # 增量更新模式：只插入新数据
                            # 查询本批次中已存在的主键
                            pk_values = [row[primary_key] for row in batch if primary_key in row]
                            if pk_values:
                                check_cursor = self.target_conn.cursor()
                                placeholders = ', '.join(['%s'] * len(pk_values))
                                check_sql = f"SELECT `{primary_key}` FROM `{target_table}` WHERE `{primary_key}` IN ({placeholders})"
                                check_cursor.execute(check_sql, tuple(pk_values))
                                existing_pks = {row[0] for row in check_cursor.fetchall()}
                                check_cursor.close()
                                
                                # 过滤掉已存在的数据
                                batch = [row for row in batch if row.get(primary_key) not in existing_pks]
                            
                            if batch:
                                if not self._batch_insert_data(self.target_conn, target_table, batch, geometry_columns):
                                    self.logger.error(f"表 {table} -> {target_table}: 第{batch_num}批数据插入失败")
                                    stats['failed_tables'] += 1
                                    break
                            else:
                                # 本批次所有数据都已存在，跳过
                                pass
                        elif primary_key:
                            # 有主键表：使用upsert（全量模式）
                            if not self.insert_or_update_data(self.target_conn, target_table, batch, self.guid, incremental=False):
                                self.logger.error(f"表 {table} -> {target_table}: 第{batch_num}批数据迁移失败")
                                stats['failed_tables'] += 1
                                break
                        else:
                            # 无主键表：直接批量插入
                            if not self._batch_insert_data(self.target_conn, target_table, batch, geometry_columns):
                                self.logger.error(f"表 {table} -> {target_table}: 第{batch_num}批数据插入失败")
                                stats['failed_tables'] += 1
                                break
                        
                        total_migrated += len(batch)
                        
                        # 每5批提交一次并记录进度（更频繁）
                        if batch_num % 5 == 0:
                            self.target_conn.commit()
                            self.logger.info(f"表 {table} -> {target_table}: 已迁移 {total_migrated}/{total_count} 条记录 ({total_migrated/total_count*100:.1f}%)")
                    
                    # 最终提交
                    self.target_conn.commit()
                    
                    stats['processed_tables'] += 1
                    stats['total_records'] += total_migrated
                    
                    # 记录处理时间
                    table_end_time = datetime.now()
                    table_duration = (table_end_time - table_start_time).total_seconds()
                    efficiency = total_migrated / table_duration if table_duration > 0 else 0
                    
                    stats['table_times'].append({
                        'table': table,
                        'target_table': target_table,
                        'records': total_migrated,
                        'duration': table_duration,
                        'efficiency': efficiency
                    })
                    
                    self.logger.info(f"表 {table} -> {target_table}: {total_migrated}条记录，耗时{table_duration:.2f}秒，效率{efficiency:.1f}条/秒")
                    
                    # 验证数据完整性
                    if not self.verify_data_integrity(self.source_conn, self.target_conn, target_table, self.guid):
                        self.logger.warning(f"表 {target_table}: 数据完整性验证失败")
            
            # 输出统计信息
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            # 计算整体效率
            overall_efficiency = stats['total_records'] / duration if duration > 0 else 0
            
            # 找出最快和最慢的表
            if stats['table_times']:
                fastest = max(stats['table_times'], key=lambda x: x['efficiency'])
                slowest = min(stats['table_times'], key=lambda x: x['efficiency'])
            else:
                fastest = slowest = None
            
            self.logger.info("=" * 60)
            self.logger.info("数据迁移任务完成")
            self.logger.info(f"总耗时: {duration:.2f} 秒")
            self.logger.info(f"总表数: {stats['total_tables']}")
            self.logger.info(f"成功迁移: {stats['processed_tables']} 个表")
            self.logger.info(f"新建表: {stats['created_tables']} 个")
            self.logger.info(f"跳过（无数据）: {stats['skipped_tables']} 个表")
            self.logger.info(f"失败: {stats['failed_tables']} 个表")
            self.logger.info(f"总记录数: {stats['total_records']} 条")
            self.logger.info(f"整体迁移效率: {overall_efficiency:.1f} 条/秒")
            
            if fastest and slowest:
                self.logger.info("-" * 60)
                self.logger.info("效率统计:")
                self.logger.info(f"  最快: {fastest['table']} -> {fastest['target_table']}")
                self.logger.info(f"        {fastest['records']}条记录，{fastest['duration']:.2f}秒，{fastest['efficiency']:.1f}条/秒")
                self.logger.info(f"  最慢: {slowest['table']} -> {slowest['target_table']}")
                self.logger.info(f"        {slowest['records']}条记录，{slowest['duration']:.2f}秒，{slowest['efficiency']:.1f}条/秒")
            
            self.logger.info("=" * 60)
            
            return stats['failed_tables'] == 0
            
        except Exception as e:
            self.logger.error(f"迁移过程中发生异常: {e}")
            return False
        finally:
            if self.source_conn:
                self.source_conn.close()
            if self.target_conn:
                self.target_conn.close()
            self.logger.info("数据库连接已关闭")


def main():
    parser = argparse.ArgumentParser(description='根据guid从A数据库迁移数据到B数据库')
    parser.add_argument('guid', help='要迁移的guid值')
    parser.add_argument('--batch-size', type=int, default=100, 
                       help='每批处理的记录数量，默认为100')
    parser.add_argument('--incremental', '-i', action='store_true',
                       help='使用增量更新模式，只导入新增数据，跳过已存在的数据')
    
    args = parser.parse_args()
    
    source_db_url = "mysql+mysqlconnector://app:sykj_1234A@192.168.8.221:3307/bim_data"
    target_db_url = "mysql+mysqlconnector://app:sykj_1234A@49.234.197.113:33307/bim_agent_data"
    
    migrator = DataMigrator(source_db_url, target_db_url, args.guid, args.batch_size)
    
    if migrator.migrate(incremental=args.incremental):
        print("数据迁移成功完成")
        sys.exit(0)
    else:
        print("数据迁移失败，请查看日志文件获取详细信息")
        sys.exit(1)


if __name__ == "__main__":
    main()
