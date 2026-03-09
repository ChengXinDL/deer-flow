# BIM 模型查询示例

本文档提供了针对 BIM 模型数据库的常用 SQL 查询示例，涵盖房间查询、构件查询、属性查询等场景。

## 查询示例列表

### 1. 房间面积查询

**查询问题**：guid为'202504090930'的建筑中，globalId为11267的房间的面积是多少？

**SQL 查询**：
```sql
SELECT paramValue 
FROM table_propertyvalue tp 
JOIN table_reldefinesbyobject x ON JSON_CONTAINS(x.relatedObjectId, CAST(tp.globalId AS JSON)) 
WHERE x.relatingId = 11267 
  AND tp.guid = '202504090930' 
  AND x.guid = '202504090930' 
  AND tp.name = '面积';
```

**查询要点**：
- 使用 `JSON_CONTAINS` 处理 JSON 格式的关联关系
- 通过 `table_reldefinesbyobject` 表建立房间与属性的关系
- 筛选条件包含 guid 和属性名称

---

### 2. 门、窗基础数据查询

**查询问题**：guid为'202504090930'的建筑中，查找所有门、窗的基础数据，并且进行分组。

**SQL 查询**：
```sql
SELECT 
    w.globalId AS elementId, 
    '窗' AS categoryName, 
    SUBSTRING_INDEX(w.name, ':', 1) as familyName, 
    wt.symbolName AS typeName, 
    l.name AS levelName 
FROM table_window w 
LEFT JOIN table_windowtype wt ON w.typeId = wt.globalId AND wt.guid = '202504090930' 
LEFT JOIN table_level l ON w.levelId = l.globalId AND l.guid = '202504090930' 
WHERE w.guid = '202504090930' 

UNION ALL

SELECT 
    w.globalId AS elementId, 
    '墙' AS categoryName, 
    SUBSTRING_INDEX(w.name, ':', 1) as familyName, 
    wt.symbolName AS typeName,
    l.name AS levelName 
FROM table_wall w 
LEFT JOIN table_walltype wt ON w.typeId = wt.globalId AND wt.guid = '202504090930' 
LEFT JOIN table_level l ON w.levelId = l.globalId AND l.guid = '202504090930' 
WHERE w.guid = '202504090930' 
  AND l.name = 'F2' 
ORDER BY categoryName, familyName, typeName;
```

**查询要点**：
- 使用 `UNION ALL` 合并多个查询结果
- 使用 `SUBSTRING_INDEX` 提取族名称
- 通过 `LEFT JOIN` 确保所有记录都被包含

---

### 3. 特定楼层墙体查询

**查询问题**：guid为'202504090930'的建筑中，楼层F2中有哪些墙？

**SQL 查询**：
```sql
SELECT 
    w.globalId AS elementId, 
    '墙' AS categoryName, 
    SUBSTRING_INDEX(w.name, ':', 1) as familyName, 
    wt.name AS typeName, 
    l.name AS levelName 
FROM table_wall w 
LEFT JOIN table_walltype wt ON w.typeId = wt.globalId AND wt.guid = '202504090930' 
LEFT JOIN table_level l ON w.levelId = l.globalId AND l.guid = '202504090930' 
WHERE w.guid = '202504090930' 
  AND l.name = 'F2';
```

**查询要点**：
- 通过楼层名称筛选特定楼层的构件
- 使用 `LEFT JOIN` 关联类型表和楼层表
- 筛选条件包含 guid 和楼层名称

---

### 4. 宽度大于指定值的门查询

**查询问题**：guid为'202504090930'的建筑中，找到宽度大于1200的门。

**SQL 查询**：
```sql
SELECT 
    d.globalId as elementId, 
    SUBSTRING_INDEX(d.name, ':', 1) as familyName, 
    dt.symbolName as typeName, 
    l.name as levelName, 
    p.name as paraName, 
    p.paramValue as width 
FROM table_door d 
JOIN table_doortype dt ON d.typeId = dt.globalId AND d.guid = dt.guid 
JOIN table_level l ON d.levelId = l.globalId AND d.guid = l.guid 
JOIN table_reldefinesbyobject rel ON dt.globalId = rel.relatingId AND d.guid = rel.guid 
JOIN table_propertyvalue p ON JSON_CONTAINS(rel.relatedObjectId, cast(p.globalId as JSON)) AND p.guid = d.guid 
WHERE d.guid = '202504090930' 
  AND p.name IN ('宽度', 'Width') 
  AND cast(p.paramValue as DECIMAL(10, 2)) > 1200;
```

**查询要点**：
- 使用 `CAST` 将字符串转换为数值进行比较
- 通过 `table_reldefinesbyobject` 建立类型与属性的关系
- 使用 `IN` 操作符匹配中英文属性名称

---

### 5. 特定楼层柱子查询

**查询问题**：guid为'202504090930'的建筑中，找到一层中宽度大于300的柱。

**SQL 查询**：
```sql
SELECT 
    c.globalId AS elementId, 
    '柱' AS categoryName, 
    SUBSTRING_INDEX(c.name, ':', 1) AS familyName, 
    ct.symbolName AS typeName, 
    l.name AS levelName, 
    p.name AS paramName, 
    p.paramValue AS widthValue 
FROM table_column c 
JOIN table_columntype ct ON c.typeId = ct.globalId AND c.guid = ct.guid 
JOIN table_level l ON c.levelId = l.globalId AND c.guid = l.guid 
JOIN table_reldefinesbyobject rel ON ct.globalId = rel.relatingId AND c.guid = rel.guid 
JOIN table_propertyvalue p ON JSON_CONTAINS(rel.relatedObjectId, CAST(p.globalId AS JSON)) AND p.guid = c.guid 
WHERE c.guid = '202504090930' 
  AND l.name = 'F1' 
  AND (p.name LIKE '%宽度%' OR p.name like '%Width%') 
  AND CAST(p.paramValue AS DECIMAL(10,2)) > 300;
```

**查询要点**：
- 使用 `LIKE` 操作符进行模糊匹配
- 通过 `table_reldefinesbyobject` 建立多表关联
- 数值转换和比较确保查询准确性

---

### 6. 大面积房间查询

**查询问题**：guid为'202504090930'的建筑中，请查找面积大于30平米的房间。

**SQL 查询**：
```sql
SELECT 
    r.globalId AS roomId, 
    SUBSTRING_INDEX(r.longName, ':', -1) AS roomName, 
    p.paramValue AS param_value 
FROM table_room r 
JOIN table_roomtype rt ON r.typeId = rt.globalId AND r.guid = rt.guid 
  AND rt.category IN ('房间', '面积', 'xRoomType') 
JOIN table_reldefinesbyobject rel ON r.globalId = rel.relatingId AND rel.guid = r.guid 
JOIN table_propertyvalue p ON JSON_CONTAINS(rel.relatedObjectId, CAST(p.globalId AS JSON)) AND p.guid = r.guid 
WHERE r.guid = '202504090930' 
  AND p.name = '面积' 
  AND CAST(p.paramValue AS DECIMAL(10,2)) > 30;
```

**查询要点**：
- 使用 `IN` 操作符匹配多种房间类型
- 通过 `SUBSTRING_INDEX` 提取房间名称
- 数值转换确保面积比较的准确性

---

### 7. 大面积房间详细信息查询

**查询问题**：guid为'202504090930'的建筑中，请查找面积大于30平米的房间的相关信息。

**SQL 查询**：
```sql
SELECT 
    r.globalId AS roomId, 
    SUBSTRING_INDEX(r.longName, ':', -1) AS roomName, 
    l.name as roomLevel, 
    p.paramValue AS param_value 
FROM table_room r 
JOIN table_roomtype rt ON r.typeId = rt.globalId AND r.guid = rt.guid 
  AND rt.category IN ('房间', '面积', 'xRoomType') 
JOIN table_level l ON r.levelId = l.globalId AND r.guid = l.guid 
JOIN table_reldefinesbyobject rel ON rel.relatingId = r.globalId AND rel.guid = r.guid 
JOIN table_propertyvalue p ON JSON_CONTAINS(rel.relatedObjectId, CAST(p.globalId AS JSON)) AND p.guid = r.guid 
WHERE r.guid = '202504090930' 
  AND p.name = '面积' 
  AND CAST(p.paramValue AS DECIMAL(10,2)) > 30;
```

**查询要点**：
- 在查询中包含楼层信息
- 使用 `SUBSTRING_INDEX` 提取房间名称的最后一部分
- 多表关联获取完整的房间信息

---

### 8. 空间设计冷负荷查询

**查询问题**：guid为'335834679343'的建筑中，请查找1F所有空间的设计冷负荷。

**SQL 查询**：
```sql
SELECT 
    r.globalId AS room_id, 
    SUBSTRING_INDEX(r.longName, ':', -1) AS room_name, 
    p.paramValue AS param_value 
FROM table_room r 
JOIN table_roomtype rt ON r.typeId = rt.globalId AND r.guid = rt.guid 
  AND rt.category IN ('空间', 'xRoomType') 
JOIN table_level l ON r.levelId = l.globalId AND r.guid = l.guid 
JOIN table_reldefinesbyobject rel ON rel.relatingId = r.globalId AND rel.guid = r.guid 
JOIN table_propertyvalue p ON JSON_CONTAINS(rel.relatedObjectId, CAST(p.globalId AS JSON)) AND p.guid = r.guid 
WHERE r.guid = '335834679343' 
  AND l.name = '1F' 
  AND p.name = '设计冷负荷' 
ORDER BY room_name;
```

**查询要点**：
- 筛选特定类别的空间（'空间', 'xRoomType'）
- 查询特定属性（'设计冷负荷'）
- 使用 `ORDER BY` 对结果进行排序

---

### 9. 特定楼层房间查询

**查询问题**：guid为'335834679343'的建筑中，请查找1F的所有房间。

**SQL 查询**：
```sql
SELECT 
    r.globalId AS room_id, 
    SUBSTRING_INDEX(r.longName, ':', -1) AS room_name 
FROM table_room r 
JOIN table_roomtype rt ON r.typeId = rt.globalId AND r.guid = rt.guid 
  AND rt.category IN ('房间', '面积', 'xRoomType') 
JOIN table_level l ON r.levelId = l.globalId AND r.guid = l.guid 
WHERE r.guid = '335834679343' 
  AND l.name = '1F' 
ORDER BY room_name;
```

**查询要点**：
- 筛选特定楼层的房间
- 使用 `IN` 操作符匹配多种房间类型
- 结果按房间名称排序

---

### 10. 特定楼层空间查询

**查询问题**：guid为'335834679343'的建筑中，请查找1F的所有空间。

**SQL 查询**：
```sql
SELECT 
    r.globalId AS room_id, 
    SUBSTRING_INDEX(r.longName, ':', -1) AS room_name 
FROM table_room r 
JOIN table_roomtype rt ON r.typeId = rt.globalId AND r.guid = rt.guid 
  AND rt.category IN ('空间', 'xRoomType') 
JOIN table_level l ON r.levelId = l.globalId AND l.guid = l.guid 
WHERE r.guid = '335834679343' 
  AND l.name = '1F' 
ORDER BY room_name;
```

**查询要点**：
- 筛选特定楼层的空间
- 使用 `IN` 操作符匹配空间类型
- 结果按空间名称排序

---

## 查询模式总结

### 常用表结构

| 表名 | 用途 | 关键字段 |
|------|------|----------|
| `table_room` | 房间/空间信息 | globalId, name, longName, typeId, levelId, guid |
| `table_roomtype` | 房间类型信息 | globalId, name, category, symbolName, guid |
| `table_wall` | 墙体信息 | globalId, name, typeId, levelId, guid |
| `table_walltype` | 墙体类型信息 | globalId, name, symbolName, guid |
| `table_window` | 窗户信息 | globalId, name, typeId, levelId, guid |
| `table_windowtype` | 窗户类型信息 | globalId, name, symbolName, guid |
| `table_door` | 门信息 | globalId, name, typeId, levelId, guid |
| `table_doortype` | 门类型信息 | globalId, name, symbolName, guid |
| `table_column` | 柱子信息 | globalId, name, typeId, levelId, guid |
| `table_columntype` | 柱子类型信息 | globalId, name, symbolName, guid |
| `table_level` | 楼层信息 | globalId, name, guid |
| `table_propertyvalue` | 属性值信息 | globalId, name, paramValue, guid |
| `table_reldefinesbyobject` | 对象关系定义 | relatingId, relatedObjectId, guid |

### 常用查询模式

#### 1. 构件基本信息查询
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

#### 2. 属性值查询
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

#### 3. 数值属性筛选
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

### 查询优化建议

1. **使用索引**：确保 `globalId`、`guid`、`typeId`、`levelId` 等字段有适当的索引
2. **避免 SELECT ***：只查询需要的列
3. **使用 LIMIT**：限制返回的行数，避免返回过多数据
4. **合理使用 JOIN**：根据实际需求选择 INNER JOIN 或 LEFT JOIN
5. **数值转换**：对数值属性使用 `CAST` 进行类型转换，确保比较的准确性
6. **模糊匹配**：使用 `LIKE` 进行属性名称的模糊匹配
7. **结果排序**：使用 `ORDER BY` 对结果进行排序，提高可读性

---

**版本**：1.0  
**更新时间**：2026-03-08  
**适用范围**：BIM 模型数据库查询