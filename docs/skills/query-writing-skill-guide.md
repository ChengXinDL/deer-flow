# Query Writing 技能使用文档

## 概述

`query-writing` 技能是用于编写和执行 SQL 查询的通用技能，支持从简单的单表查询到复杂的多表 JOIN 和聚合查询。该技能特别针对 BIM 模型数据库进行了优化，提供了丰富的查询示例和 Schema 指南。

## 技能位置

- **技能路径**：`skills/public/query-writing/`
- **主文件**：`skills/public/query-writing/SKILL.md`
- **参考文档**：`skills/public/query-writing/references/`

## 技能结构

```
query-writing/
├── SKILL.md                           # 主技能文件
└── references/                         # 参考文档目录
    ├── bim_query_examples.md           # BIM 查询示例（10+ 实例）
    └── bim_schema_guide.md            # BIM Schema 完整指南
```

## 核心功能

### 1. 通用 SQL 查询支持

- **简单查询**：单表查询、条件筛选、排序、限制
- **复杂查询**：多表 JOIN、聚合函数、分组统计
- **子查询**：嵌套查询、关联子查询
- **窗口函数**：排名、累计、移动平均等

### 2. BIM 模型数据库专用支持

- **完整的 Schema 文档**：涵盖 30+ 个表结构
- **丰富的查询示例**：10+ 实际应用场景
- **最佳实践指南**：针对 BIM 查询的优化建议
- **渐进式加载**：按需加载参考文档

### 3. 查询优化建议

- **索引策略**：主键索引、复合索引、外键索引
- **性能优化**：避免 SELECT *、合理使用 LIMIT、优化 JOIN
- **JSON 处理**：JSON_CONTAINS、CAST 转换、避免复杂操作

## 使用方法

### 基本使用流程

#### 1. 确定查询类型

首先判断查询需求：

- **简单查询**：单表查询，使用基本工作流程
- **复杂查询**：多表关联，使用复杂工作流程
- **BIM 查询**：BIM 模型数据库，使用专用模式

#### 2. 选择参考文档

根据查询类型选择合适的参考文档：

| 查询类型 | 参考文档 | 使用场景 |
|----------|----------|----------|
| BIM 模型查询 | `references/bim_query_examples.md` | 查找相似查询模式 |
| BIM Schema 信息 | `references/bim_schema_guide.md` | 了解表结构和关系 |
| 通用 SQL 查询 | `SKILL.md` | 标准查询流程 |

#### 3. 渐进式加载

遵循渐进式加载原则：

1. **第一步**：加载 `SKILL.md` 了解基本工作流程
2. **第二步**：根据需要加载 `references/bim_query_examples.md` 查找示例
3. **第三步**：如需详细信息，加载 `references/bim_schema_guide.md`

### BIM 查询专用流程

#### 步骤 1：检查查询示例

```bash
# 查看是否有类似的查询示例
read_file skills/public/query-writing/references/bim_query_examples.md
```

#### 步骤 2：查找匹配模式

在示例文档中查找：
- 相似的查询场景
- 相同的表结构
- 相似的筛选条件

#### 步骤 3：参考 Schema 信息

如需了解表结构：

```bash
# 查看 Schema 指南
read_file skills/public/query-writing/references/bim_schema_guide.md
```

#### 步骤 4：构建查询

基于示例和 Schema 信息构建查询：

```sql
-- 示例：查询特定楼层的房间
SELECT 
    r.globalId AS roomId, 
    SUBSTRING_INDEX(r.longName, ':', -1) AS roomName, 
    l.name AS roomLevel 
FROM table_room r 
JOIN table_roomtype rt ON r.typeId = rt.globalId AND r.guid = rt.guid 
  AND rt.category IN ('房间', '面积', 'xRoomType') 
JOIN table_level l ON r.levelId = l.globalId AND r.guid = l.guid 
WHERE r.guid = '建筑guid' 
  AND l.name = '1F' 
ORDER BY roomName;
```

## BIM 查询最佳实践

### 1. 必须包含 GUID 过滤

所有 BIM 查询都必须包含 `WHERE guid = '建筑guid'` 条件：

```sql
-- 正确示例
SELECT * FROM table_room WHERE guid = '202504090930';

-- 错误示例（缺少 GUID 过滤）
SELECT * FROM table_room;
```

### 2. 正确使用 JSON 函数

BIM 数据库使用 JSON 格式存储关系：

```sql
-- 正确：使用 JSON_CONTAINS 和 CAST
JOIN table_reldefinesbyobject rel ON type.globalId = rel.relatingId
JOIN table_propertyvalue p ON JSON_CONTAINS(rel.relatedObjectId, CAST(p.globalId AS JSON))

-- 错误：直接比较 JSON 字符串
JOIN table_propertyvalue p ON rel.relatedObjectId = p.globalId
```

### 3. 处理双语属性名称

属性名称可能同时存在中英文版本：

```sql
-- 方法 1：使用 IN 操作符
WHERE p.name IN ('宽度', 'Width')

-- 方法 2：使用 LIKE 模糊匹配
WHERE p.name LIKE '%宽度%' OR p.name LIKE '%Width%'
```

### 4. 数值类型转换

数值属性存储为字符串，需要转换：

```sql
-- 正确：转换为数值类型进行比较
WHERE CAST(p.paramValue AS DECIMAL(10,2)) > 1200

-- 错误：直接比较字符串
WHERE p.paramValue > 1200
```

### 5. 名称提取技巧

使用 `SUBSTRING_INDEX` 提取名称：

```sql
-- 提取族名称（第一个冒号前）
SUBSTRING_INDEX(element.name, ':', 1)

-- 提取房间名称（最后一个冒号后）
SUBSTRING_INDEX(room.longName, ':', -1)
```

### 6. 使用 LEFT JOIN

优先使用 LEFT JOIN 确保所有记录：

```sql
-- 推荐：使用 LEFT JOIN
LEFT JOIN table_roomtype rt ON r.typeId = rt.globalId AND r.guid = rt.guid

-- 避免：使用 INNER JOIN 可能丢失记录
INNER JOIN table_roomtype rt ON r.typeId = rt.globalId AND r.guid = rt.guid
```

## 常用查询模式

### 模式 1：构件基本信息查询

```sql
SELECT 
    element.globalId AS elementId, 
    '类别' AS categoryName, 
    SUBSTRING_INDEX(element.name, ':', 1) as familyName, 
    type.symbolName AS typeName, 
    level.name AS levelName 
FROM table_element element 
LEFT JOIN table_elementtype type ON element.typeId = type.globalId AND element.guid = type.guid 
LEFT JOIN table_level level ON element.levelId = level.globalId AND element.guid = level.guid 
WHERE element.guid = '建筑guid';
```

### 模式 2：属性值查询

```sql
SELECT 
    element.globalId AS elementId, 
    p.name AS paramName, 
    p.paramValue AS paramValue 
FROM table_element element 
JOIN table_elementtype type ON element.typeId = type.globalId AND element.guid = type.guid 
JOIN table_reldefinesbyobject rel ON type.globalId = rel.relatingId AND element.guid = rel.guid 
JOIN table_propertyvalue p ON JSON_CONTAINS(rel.relatedObjectId, CAST(p.globalId AS JSON)) AND p.guid = element.guid 
WHERE element.guid = '建筑guid' 
  AND p.name = '属性名称';
```

### 模式 3：数值属性筛选

```sql
SELECT 
    element.globalId AS elementId, 
    p.paramValue AS paramValue 
FROM table_element element 
JOIN table_elementtype type ON element.typeId = type.globalId AND element.guid = type.guid 
JOIN table_reldefinesbyobject rel ON type.globalId = rel.relatingId AND element.guid = rel.guid 
JOIN table_propertyvalue p ON JSON_CONTAINS(rel.relatedObjectId, CAST(p.globalId AS JSON)) AND p.guid = element.guid 
WHERE element.guid = '建筑guid' 
  AND p.name IN ('宽度', 'Width') 
  AND CAST(p.paramValue AS DECIMAL(10,2)) > 1200;
```

### 模式 4：多表联合查询

```sql
SELECT 
    element.globalId AS elementId, 
    type.symbolName AS typeName, 
    level.name AS levelName, 
    p.paramValue AS paramValue 
FROM table_element element 
JOIN table_elementtype type ON element.typeId = type.globalId AND element.guid = type.guid 
JOIN table_level level ON element.levelId = level.globalId AND element.guid = level.guid 
JOIN table_reldefinesbyobject rel ON type.globalId = rel.relatingId AND element.guid = rel.guid 
JOIN table_propertyvalue p ON JSON_CONTAINS(rel.relatedObjectId, CAST(p.globalId AS JSON)) AND p.guid = element.guid 
WHERE element.guid = '建筑guid' 
  AND p.name = '属性名称';
```

## 参考文档详细说明

### bim_query_examples.md

**内容概要**：
- 10+ 实际 BIM 查询示例
- 涵盖房间、墙体、门窗、柱子等构件
- 包含查询要点和优化建议
- 提供常用查询模式总结

**主要章节**：
1. 房间面积查询
2. 门、窗基础数据查询
3. 特定楼层构件查询
4. 宽度/尺寸筛选查询
5. 大面积房间查询
6. 空间设计冷负荷查询
7. 查询模式总结
8. 性能优化建议

**使用场景**：
- 查找类似查询模式
- 学习 BIM 查询最佳实践
- 了解常用查询结构
- 获取性能优化建议

### bim_schema_guide.md

**内容概要**：
- 30+ 个表的完整结构说明
- 表关系图和关联说明
- 常用字段说明和命名约定
- 常用查询模式和示例
- 性能优化和常见问题

**主要章节**：
1. 数据库概述和设计原则
2. 项目信息表系列（4 个表）
3. 构件表系列（13 个表）
4. 类型表系列（13 个表）
5. 辅助表系列（4 个表）
6. 表关系图
7. 常用字段说明
8. 常用查询模式
9. 性能优化建议
10. 常见问题解答

**使用场景**：
- 了解表结构和字段说明
- 查找表之间的关系
- 学习字段命名约定
- 获取性能优化建议
- 解决查询问题

## 质量指南

### 通用 SQL 最佳实践

- ✅ **查询相关列**：避免使用 `SELECT *`
- ✅ **应用 LIMIT**：默认限制返回 5 行
- ✅ **使用表别名**：提高查询可读性
- ✅ **规划复杂查询**：使用 `write_todos` 分解任务
- ❌ **避免 DML 语句**：不要使用 INSERT、UPDATE、DELETE、DROP

### BIM 专用最佳实践

- ✅ **包含 GUID 过滤**：所有查询必须包含 `WHERE guid = '建筑guid'`
- ✅ **正确使用 JSON 函数**：使用 `JSON_CONTAINS` 和 `CAST`
- ✅ **处理双语属性**：同时检查中英文属性名称
- ✅ **转换数值类型**：使用 `CAST` 进行数值比较
- ✅ **提取名称正确**：使用 `SUBSTRING_INDEX` 提取名称
- ✅ **使用 LEFT JOIN**：确保所有记录都被包含
- ✅ **参考示例模式**：先查找类似查询，再编写新查询

## 性能优化建议

### 索引策略

1. **主键索引**：所有表的 `globalId` 字段都应有主键索引
2. **复合索引**：为常用查询组合创建复合索引
   - `(guid, levelId)` - 按项目查询楼层
   - `(guid, name)` - 按项目查询属性
   - `(guid, category)` - 按项目查询类型
3. **外键索引**：所有外键字段都应有索引

### 查询优化

1. **避免 SELECT ***：只查询需要的列
2. **使用 LIMIT**：限制返回的行数
3. **合理使用 JOIN**：根据实际需求选择 INNER JOIN 或 LEFT JOIN
4. **利用索引**：确保查询条件使用索引字段
5. **减少子查询**：尽量使用 JOIN 替代子查询

### JSON 处理优化

1. **JSON_CONTAINS**：用于检查 JSON 数组中是否包含特定值
2. **CAST 转换**：将字符串转换为 JSON 类型进行比较
3. **避免复杂 JSON 操作**：复杂的 JSON 操作可能影响性能

## 常见问题

### Q1: 如何查询特定楼层的所有构件？

```sql
SELECT 
    w.globalId AS elementId, 
    SUBSTRING_INDEX(w.name, ':', 1) as familyName, 
    wt.symbolName AS typeName, 
    l.name AS levelName 
FROM table_wall w 
LEFT JOIN table_walltype wt ON w.typeId = wt.globalId AND w.guid = wt.guid 
LEFT JOIN table_level l ON w.levelId = l.globalId AND w.guid = l.guid 
WHERE w.guid = '建筑guid' 
  AND l.name = 'F1';
```

### Q2: 如何查询具有特定属性的构件？

```sql
SELECT 
    element.globalId AS elementId, 
    p.paramValue AS paramValue 
FROM table_element element 
JOIN table_elementtype type ON element.typeId = type.globalId AND element.guid = type.guid 
JOIN table_reldefinesbyobject rel ON type.globalId = rel.relatingId AND element.guid = rel.guid 
JOIN table_propertyvalue p ON JSON_CONTAINS(rel.relatedObjectId, CAST(p.globalId AS JSON)) AND p.guid = element.guid 
WHERE element.guid = '建筑guid' 
  AND p.name = '属性名称';
```

### Q3: 如何进行数值比较查询？

```sql
SELECT 
    element.globalId AS elementId, 
    p.paramValue AS paramValue 
FROM table_element element 
JOIN table_elementtype type ON element.typeId = type.globalId AND element.guid = type.guid 
JOIN table_reldefinesbyobject rel ON type.globalId = rel.relatingId AND element.guid = rel.guid 
JOIN table_propertyvalue p ON JSON_CONTAINS(rel.relatedObjectId, CAST(p.globalId AS JSON)) AND p.guid = element.guid 
WHERE element.guid = '建筑guid' 
  AND p.name = '属性名称' 
  AND CAST(p.paramValue AS DECIMAL(10,2)) > 数值;
```

### Q4: 如何查询多个构件类型？

```sql
SELECT 
    w.globalId AS elementId, 
    '墙' AS categoryName, 
    SUBSTRING_INDEX(w.name, ':', 1) as familyName, 
    wt.symbolName AS typeName, 
    l.name AS levelName 
FROM table_wall w 
LEFT JOIN table_walltype wt ON w.typeId = wt.globalId AND w.guid = wt.guid 
LEFT JOIN table_level l ON w.levelId = l.globalId AND w.guid = l.guid 
WHERE w.guid = '建筑guid' 

UNION ALL

SELECT 
    d.globalId AS elementId, 
    '门' AS categoryName, 
    SUBSTRING_INDEX(d.name, ':', 1) as familyName, 
    dt.symbolName AS typeName, 
    l.name AS levelName 
FROM table_door d 
LEFT JOIN table_doortype dt ON d.typeId = dt.globalId AND d.guid = dt.guid 
LEFT JOIN table_level l ON d.levelId = l.globalId AND d.guid = l.guid 
WHERE d.guid = '建筑guid' 

ORDER BY categoryName, familyName, typeName;
```

## 扩展和定制

### 添加新的查询示例

1. 在 `references/bim_query_examples.md` 中添加新示例
2. 遵循现有格式：问题描述 + SQL 查询 + 查询要点
3. 包含完整的查询说明和优化建议

### 更新 Schema 信息

1. 在 `references/bim_schema_guide.md` 中添加新表结构
2. 遵循现有格式：表说明 + 字段表格 + 索引建议
3. 更新表关系图和常用查询模式

### 创建项目级技能

如需为特定项目创建专用技能：

1. 复制 `query-writing` 技能到 `skills/project/` 目录
2. 修改 `SKILL.md` 的描述和触发条件
3. 在 `references/` 中添加项目特定的 Schema 和查询示例
4. 更新技能文档和使用说明

## 总结

`query-writing` 技能是一个功能强大的 SQL 查询工具，特别针对 BIM 模型数据库进行了优化。通过渐进式加载参考文档，用户可以：

1. **快速上手**：通过示例快速学习查询模式
2. **深入理解**：通过 Schema 指南了解数据结构
3. **高效查询**：遵循最佳实践编写优化的查询
4. **持续改进**：基于示例和指南不断提升查询技能

该技能的设计遵循了技能系统的核心原则：简洁明了、渐进式加载、实用导向，为用户提供了从入门到精通的完整学习路径。

---

**版本**：1.0  
**更新时间**：2026-03-08  
**适用范围**：MAGICFlow 项目 Query Writing 技能  
**维护责任人**：AI Integration Team