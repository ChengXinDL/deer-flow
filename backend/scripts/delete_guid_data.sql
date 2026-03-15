-- 删除 B 数据库中所有 guid=640672095077 的数据
-- 执行前请先备份数据

-- 方式1：手动执行每个表的删除语句（推荐，可以控制每个表的删除）
-- 请先查询有哪些表包含该 guid 的数据：
-- SELECT TABLE_NAME, COUNT(*) as count
-- FROM INFORMATION_SCHEMA.COLUMNS c
-- JOIN (
--     SELECT 'table_Building' as t UNION ALL
--     SELECT 'table_Column' UNION ALL
--     SELECT 'table_Wall' UNION ALL
--     SELECT 'table_WallType' UNION ALL
--     SELECT 'table_Window' UNION ALL
--     SELECT 'table_WindowType'
--     -- 添加其他表...
-- ) tables ON c.TABLE_NAME = tables.t
-- WHERE c.COLUMN_NAME = 'guid'
--   AND c.TABLE_SCHEMA = 'bim_agent_data'
-- GROUP BY TABLE_NAME;

-- 方式2：使用以下脚本生成删除语句
-- 查询所有包含 guid 字段且以 table_ 开头的表
SELECT 
    CONCAT('DELETE FROM `', TABLE_NAME, '` WHERE `guid` = ''640672095077'';') as delete_sql
FROM INFORMATION_SCHEMA.COLUMNS 
WHERE COLUMN_NAME = 'guid' 
  AND TABLE_SCHEMA = 'bim_agent_data'
  AND TABLE_NAME LIKE 'table_%'
ORDER BY TABLE_NAME;

-- 将上面查询结果复制出来，然后批量执行
