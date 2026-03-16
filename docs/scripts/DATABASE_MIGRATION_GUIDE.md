# 数据库迁移功能复盘与使用指南

## 一、功能概述

### 1.1 核心功能
数据库迁移工具用于将数据从 **A数据库（源数据库）** 迁移到 **B数据库（目标数据库）**，基于 `guid` 字段进行数据筛选和迁移。

### 1.2 主要特性
- ✅ **基于 guid 的数据提取**：从 A 数据库所有表中提取指定 guid 的数据
- ✅ **表名自动转换**：支持 A 数据库（下划线命名）到 B 数据库（驼峰命名）的表名自动转换
- ✅ **表结构验证与同步**：自动验证 B 数据库表结构，必要时创建与 A 数据库相同的表结构
- ✅ **数据覆盖策略**：支持全量覆盖和增量更新两种模式
- ✅ **批量处理**：大数据表使用流式处理，避免内存溢出
- ✅ **GEOMETRY 字段处理**：自动跳过 GEOMETRY 空间数据字段，避免迁移错误
- ✅ **中文字符支持**：正确处理 UTF-8 编码，保留中文字符
- ✅ **完整性验证**：迁移完成后验证数据完整性
- ✅ **详细日志记录**：记录迁移过程的详细信息到日志文件
- ✅ **连接保活机制**：长时迁移过程中自动保持连接

---

## 二、数据库配置

### 2.1 源数据库（A数据库）
```
连接字符串：mysql+mysqlconnector://app:sykj_1234A@192.168.8.221:3307/bim_data
数据库名：bim_data
用途：数据源，从中提取指定 guid 的数据
命名规则：下划线命名（如 table_curtainwall）
```

### 2.2 目标数据库（B数据库）
```
连接字符串：mysql+mysqlconnector://app:sykj_1234A@49.234.197.113:33307/bim_agent_data
数据库名：bim_agent_data
用途：数据目标，接收从 A 数据库迁移的数据
命名规则：驼峰命名（如 table_Curtainwall）
```

---

## 三、脚本文件说明

### 3.1 主迁移脚本
**文件路径**：`backend/scripts/migrate_data_by_guid.py`

**核心功能**：
- 数据库连接管理
- 表名转换（下划线 → 驼峰）
- 表结构验证与创建
- 数据提取与迁移
- 批量插入与更新
- 数据完整性验证
- 日志记录

### 3.2 数据删除脚本
**文件路径**：`backend/scripts/delete_guid_data.py`

**功能**：删除 B 数据库中指定 guid 的所有数据

**使用场景**：
- 重新迁移前清空数据
- 测试迁移功能
- 数据回滚

### 3.3 SQL 删除脚本
**文件路径**：`backend/scripts/delete_guid_data.sql`

**功能**：提供手动删除数据的 SQL 语句模板

---

## 四、使用方法

### 4.1 环境准备

确保已激活虚拟环境：
```bash
.venv\Scripts\activate
```

### 4.2 基本用法

#### 全量迁移（覆盖模式）
```bash
uv run python backend/scripts/migrate_data_by_guid.py <guid>
```

**示例**：
```bash
uv run python backend/scripts/migrate_data_by_guid.py 640672095077
```

#### 增量迁移（只导入新数据）
```bash
uv run python backend/scripts/migrate_data_by_guid.py <guid> --incremental
```

**示例**：
```bash
uv run python backend/scripts/migrate_data_by_guid.py 640672095077 --incremental
```

### 4.3 删除数据

#### 使用 Python 脚本删除
```bash
uv run python backend/scripts/delete_guid_data.py
```

#### 使用 SQL 脚本删除
```bash
mysql -h 49.234.197.113 -P 33307 -u app -p bim_agent_data < backend/scripts/delete_guid_data.sql
```

---

## 五、迁移流程详解

### 5.1 初始化阶段
1. 解析命令行参数获取 guid 值
2. 初始化日志记录器
3. 连接到源数据库和目标数据库
4. 验证数据库连接

### 5.2 表名转换阶段
**转换规则**：
- A 数据库：`table_curtainwall`（下划线命名）
- B 数据库：`table_Curtainwall`（驼峰命名）
- 规则：第一个单词小写，后续单词首字母大写

**示例**：
```
table_curtainwall    → table_Curtainwall
table_basepoint      → table_Basepoint
table_distributionport → table_Distributionport
```

### 5.3 表筛选阶段
- 只处理以 `table_` 开头的表
- 排除 `table_modeltree` 表
- 只处理包含 `guid` 字段的表

### 5.4 表结构验证阶段
对每个表进行验证：
1. 检查目标数据库中是否存在该表
2. 如果不存在，从源数据库获取表结构并在目标数据库中创建
3. 如果存在，比较表结构是否兼容（允许列名大小写不同）
4. 如果结构不兼容，记录警告但继续迁移

### 5.5 数据迁移阶段

#### 小表处理（≤5000 条记录）
- 一次性获取所有数据
- 使用批量插入或更新

#### 大表处理（>5000 条记录）
- 使用流式处理，分批获取数据
- 每批 50 条记录
- 每 5 批提交一次事务
- 每 5 批执行连接保活（ping）

#### 数据插入策略

**无主键表**：
- 先删除目标表中相同 guid 的旧记录
- 批量插入新记录
- 跳过 GEOMETRY 字段

**有主键表**：
- 查询已存在的主键
- 已存在的记录：执行 UPDATE
- 不存在的记录：执行 INSERT
- 跳过 GEOMETRY 字段

### 5.6 GEOMETRY 字段处理
**处理方式**：自动跳过，不复制空间数据

**涉及表**：
- table_Door
- table_Stair
- table_StairFlight
- table_Wall
- table_Flowcontroller
- table_Flowfitting
- table_Flowsegment
- table_Flowterminal
- table_Hole
- table_Member
- table_Plate
- table_Column
- table_Beam
- table_Railing
- table_CurtainWall
- table_Distributionport

**日志提示**：
```
表 table_Door: 发现 GEOMETRY 字段 ['boundaryPolygon', 'boundaryElevation']
表 table_Door: 成功迁移 912 条记录（跳过 GEOMETRY 字段）
```

### 5.7 完整性验证阶段
对每个迁移的表：
- 比较源数据库和目标数据库中的记录数量
- 验证记录数是否一致
- 记录验证结果

### 5.8 统计报告阶段
迁移完成后输出统计信息：
- 总耗时
- 处理的表数
- 成功/失败的表数
- 总记录数
- 平均迁移效率（条/秒）
- 最快/最慢的表

---

## 六、关键技术实现

### 6.1 表名转换算法
```python
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
```

### 6.2 连接配置优化
```python
connection_config = {
    'connect_timeout': 600,      # 10分钟连接超时
    'read_timeout': 1800,        # 30分钟读取超时
    'write_timeout': 1800,       # 30分钟写入超时
    'autocommit': False,         # 手动控制事务
    'buffered': True,            # 缓冲结果集
    'pool_size': 5,              # 连接池大小
    'charset': 'utf8mb4',        # 使用utf8mb4字符集
    'collation': 'utf8mb4_unicode_ci',
}
```

### 6.3 字符清理（保留中文）
```python
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
            return ''
    return value
```

### 6.4 GEOMETRY 字段跳过
```python
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
    
    # ... 执行插入
```

### 6.5 流式处理大数据表
```python
def get_data_by_guid_streaming(self, conn, table_name, guid, batch_size=1000):
    """流式获取数据（适用于大数据表）"""
    try:
        cursor = conn.cursor(dictionary=True)
        
        # 使用服务器端游标（流式）
        query = f"SELECT * FROM `{table_name}` WHERE `guid` = %s"
        cursor.execute(query, (guid,))
        
        batch = []
        while True:
            row = cursor.fetchone()
            if row is None:
                if batch:
                    yield batch, True  # 最后一批
                break
            
            batch.append(dict(row))
            
            if len(batch) >= batch_size:
                yield batch, False  # 中间批次
                batch = []
        
        cursor.close()
    except MySQLError as e:
        self.logger.error(f"流式获取数据失败 {table_name}: {e}")
        raise
```

---

## 七、日志记录

### 7.1 日志文件位置
```
backend/logs/migrate_data_by_guid_<guid>_<timestamp>.log
```

**示例**：
```
backend/logs/migrate_data_by_guid_640672095077_20260315_084512.log
```

### 7.2 日志级别
- **INFO**：记录正常操作流程
- **WARNING**：记录警告信息（如表结构不一致、GEOMETRY 字段跳过）
- **ERROR**：记录错误信息（如连接失败、迁移失败）
- **DEBUG**：记录详细的调试信息

### 7.3 日志内容示例
```
2026-03-15 08:45:12 - DataMigrator_640672095077 - INFO - 开始数据迁移任务
2026-03-15 08:45:12 - DataMigrator_640672095077 - INFO - 连接源数据库: 192.168.8.221:3307/bim_data
2026-03-15 08:45:13 - DataMigrator_640672095077 - INFO - 源数据库连接成功
2026-03-15 08:45:13 - DataMigrator_640672095077 - INFO - 连接目标数据库: 49.234.197.113:33307/bim_agent_data
2026-03-15 08:45:14 - DataMigrator_640672095077 - INFO - 目标数据库连接成功
2026-03-15 08:45:15 - DataMigrator_640672095077 - INFO - 找到 65 个包含 guid 字段的表
2026-03-15 08:45:16 - DataMigrator_640672095077 - INFO - 表 table_curtainwall -> table_Curtainwall 结构兼容
2026-03-15 08:45:20 - DataMigrator_640672095077 - INFO - 表 table_Curtainwall: 成功迁移 1572 条记录
2026-03-15 08:45:20 - DataMigrator_640672095077 - INFO - 表 table_curtainwall -> table_Curtainwall: 1572条记录，耗时4.23秒，效率371.6条/秒
2026-03-15 08:45:20 - DataMigrator_640672095077 - INFO - 表 table_Curtainwall 数据完整性验证通过: 1572 条记录
...
2026-03-15 11:19:18 - DataMigrator_640672095077 - INFO - 表 table_reldefinesbyobject -> table_RelDefinesByObject: 56626条记录，耗时2477.10秒，效率22.9条/秒
2026-03-15 11:19:18 - DataMigrator_640672095077 - INFO - 表 table_RelDefinesByObject 数据完整性验证通过: 56626 条记录
```

---

## 八、性能数据

### 8.1 迁移效率统计

| 表名 | 记录数 | 耗时(秒) | 效率(条/秒) |
|------|--------|----------|-------------|
| table_Curtainwall | 1,572 | 4.23 | 371.6 |
| table_Distributionport | 22,555 | 904.99 | 24.9 |
| table_Door | 912 | 39.04 | 23.4 |
| table_Flowfitting | 4,373 | 190.03 | 23.0 |
| table_Member | 5,306 | 183.56 | 28.9 |
| table_Plate | 3,036 | 99.24 | 30.6 |
| table_PropertyValue | 88,358 | ~3600 | ~24.5 |
| table_RelDefinesByObject | 56,626 | 2477.10 | 22.9 |
| table_RelDefinesByType | 28,719 | 1232.73 | 23.3 |
| table_Relnests | 11,076 | ~450 | ~24.6 |

### 8.2 整体统计

**guid=640672095077 迁移结果**：
- 总耗时：约 3.5 小时
- 处理的表数：65 个
- 成功迁移：65 个表
- 失败：0 个表
- 总记录数：约 400,000+ 条
- 平均效率：约 30 条/秒

---

## 九、常见问题与解决方案

### 9.1 GEOMETRY 字段错误
**问题**：`Cannot get geometry object from data you send to the GEOMETRY field`

**解决方案**：
- 已自动跳过 GEOMETRY 字段
- 空间数据需要单独处理

### 9.2 中文字符丢失
**问题**：迁移后中文字符变成乱码或被忽略

**解决方案**：
- 使用 UTF-8 编码处理字符串
- 移除 latin1 编码转换
- 只清理控制字符，保留中文字符

### 9.3 连接超时
**问题**：`Lost connection to MySQL server during query`

**解决方案**：
- 增加连接超时设置（connect_timeout=600）
- 增加读取超时设置（read_timeout=1800）
- 添加连接保活机制（每 5 批 ping 一次）

### 9.4 无效字符错误
**问题**：`Invalid utf8mb4 character string`

**解决方案**：
- 清理 NULL 字符和控制字符
- 使用 utf8mb4 字符集

### 9.5 表结构不兼容
**问题**：源表和目标表结构不一致

**解决方案**：
- 允许列名大小写不同
- 允许 varchar 长度不同
- 记录警告但继续迁移

---

## 十、注意事项

### 10.1 迁移前准备
1. **备份目标数据库**：防止数据丢失
2. **检查网络连接**：确保能访问两个数据库
3. **确认数据库权限**：需要读写权限
4. **清理目标数据**：如需重新迁移，先删除旧数据

### 10.2 迁移过程中
1. **不要中断迁移**：可能导致数据不完整
2. **监控日志输出**：及时发现异常
3. **注意大表迁移**：可能需要较长时间

### 10.3 迁移后验证
1. **检查记录数**：对比源表和目标表记录数
2. **抽查数据**：验证关键字段值是否正确
3. **检查中文字符**：确保中文正常显示

---

## 十一、扩展功能

### 11.1 未来可能的扩展
1. 支持多个 guid 值的批量迁移
2. 支持自定义字段筛选条件
3. 支持数据转换和映射
4. 支持更多数据库类型（PostgreSQL、Oracle 等）
5. 支持图形化界面
6. 支持迁移进度实时显示

### 11.2 维护建议
1. 定期检查日志文件，监控迁移情况
2. 根据实际使用情况优化性能
3. 更新文档以反映功能变化
4. 处理用户反馈的问题和建议

---

## 十二、版本历史

### v2.0.0 (2026-03-15)
- ✅ 新增 GEOMETRY 字段自动跳过功能
- ✅ 修复中文字符丢失问题
- ✅ 新增表名自动转换功能（下划线 → 驼峰）
- ✅ 新增流式处理大数据表功能
- ✅ 新增连接保活机制
- ✅ 优化字符清理逻辑
- ✅ 新增增量更新模式

### v1.0.0 (2026-03-14)
- ✅ 初始版本，支持基本的 guid 数据迁移功能
- ✅ 支持表结构验证与同步
- ✅ 支持数据完整性验证
- ✅ 支持详细日志记录

---

## 十三、附录

### 13.1 相关脚本文件

| 文件路径 | 功能说明 |
|----------|----------|
| `backend/scripts/migrate_data_by_guid.py` | 主迁移脚本 |
| `backend/scripts/delete_guid_data.py` | 删除数据脚本（Python） |
| `backend/scripts/delete_guid_data.sql` | 删除数据脚本（SQL） |

### 13.2 相关文档

| 文档路径 | 内容说明 |
|----------|----------|
| `docs/backend/DATA_MIGRATION_TOOL.md` | 数据迁移工具基础文档 |
| `docs/scripts/DATABASE_MIGRATION_GUIDE.md` | 本复盘文档 |

### 13.3 快速命令参考

```bash
# 全量迁移
uv run python backend/scripts/migrate_data_by_guid.py 640672095077

# 增量迁移
uv run python backend/scripts/migrate_data_by_guid.py 640672095077 --incremental

# 删除数据
uv run python backend/scripts/delete_guid_data.py
```

---

**文档版本**：v2.0.0  
**最后更新**：2026-03-15  
**作者**：AI Assistant
