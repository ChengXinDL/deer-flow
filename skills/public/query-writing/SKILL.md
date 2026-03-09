---
name: query-writing
description: For writing and executing SQL queries - from simple single-table queries to complex multi-table JOINs and aggregations. Includes specialized support for BIM model database queries.
---

# Query Writing Skill

## When to Use This Skill

Use this skill when you need to answer a question by writing and executing a SQL query.

## Database-Specific References

For BIM model database queries, consult these specialized references:

- **BIM Query Examples**: [references/bim_query_examples.md](references/bim_query_examples.md) - 10+ real-world BIM query patterns
- **BIM Schema Guide**: [references/bim_schema_guide.md](references/bim_schema_guide.md) - Complete table structure and relationships

**Progressive Loading Pattern**:
1. Check if your query is for a BIM model database
2. If yes, load [references/bim_query_examples.md](references/bim_query_examples.md) first for similar query patterns
3. If needed, load [references/bim_schema_guide.md](references/bim_schema_guide.md) for table structure details
4. Use the examples and schema information to construct your query

## Workflow for Simple Queries

For straightforward questions about a single table:

1. **Check for existing patterns** - Look for similar queries in reference documents
2. **Identify the table** - Which table has the data?
3. **Get the schema** - Use `sql_db_schema` or reference guides to see columns
4. **Write the query** - SELECT relevant columns with WHERE/LIMIT/ORDER BY
5. **Execute** - Run with `sql_db_query`
6. **Format answer** - Present results clearly

## Workflow for Complex Queries

For questions requiring multiple tables:

### 1. Plan Your Approach
**Use `write_todos` to break down the task:**
- Identify all tables needed
- Map relationships (foreign keys)
- Plan JOIN structure
- Determine aggregations

### 2. Examine Schemas
- For BIM queries: Check [references/bim_schema_guide.md](references/bim_schema_guide.md) for table relationships
- For other databases: Use `sql_db_schema` for EACH table to find join columns and needed fields.

### 3. Construct Query
- SELECT - Columns and aggregates
- FROM/JOIN - Connect tables on FK = PK
- WHERE - Filters before aggregation
- GROUP BY - All non-aggregate columns
- ORDER BY - Sort meaningfully
- LIMIT - Default 5 rows

### 4. Validate and Execute
Check all JOINs have conditions, GROUP BY is correct, then run query.

## BIM-Specific Query Patterns

For BIM model database queries, follow these specialized patterns:

### Common BIM Query Structure
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

### Property Value Query Pattern
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

### Numeric Property Filtering
```sql
WHERE p.name IN ('宽度', 'Width') 
  AND CAST(p.paramValue AS DECIMAL(10,2)) > 1200;
```

For more BIM query examples, see [references/bim_query_examples.md](references/bim_query_examples.md).

## Example: Revenue by Country
```sql
SELECT
    c.Country,
    ROUND(SUM(i.Total), 2) as TotalRevenue
FROM Invoice i
INNER JOIN Customer c ON i.CustomerId = c.CustomerId
GROUP BY c.Country
ORDER BY TotalRevenue DESC
LIMIT 5;
```

## Quality Guidelines

### General SQL Best Practices
- Query only relevant columns (not SELECT *)
- Always apply LIMIT (5 default)
- Use table aliases for clarity
- For complex queries: use write_todos to plan
- Never use DML statements (INSERT, UPDATE, DELETE, DROP)

### BIM-Specific Guidelines
- **Always include GUID filter**: All BIM queries must include `WHERE guid = 'building_guid'` to limit scope
- **Use JSON functions properly**: Use `JSON_CONTAINS` and `CAST` for JSON relationship queries
- **Handle bilingual property names**: Check both Chinese and English property names using `IN` or `LIKE`
- **Cast numeric values**: Always `CAST` property values to numeric types for comparisons
- **Extract names carefully**: Use `SUBSTRING_INDEX` with appropriate parameters for name extraction
- **Use LEFT JOIN**: Prefer LEFT JOIN to ensure all records are included even without type/level info
- **Reference patterns first**: Check [references/bim_query_examples.md](references/bim_query_examples.md) for similar queries before writing new ones
