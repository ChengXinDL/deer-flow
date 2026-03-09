# BIM 数据库 Schema 指南

本文档提供了 BIM 模型数据库的详细 Schema 信息，包括表结构、字段说明、表关系等。

## 数据库概述

BIM 数据库存储建筑信息模型（BIM）的完整数据，包括建筑构件、属性、关系、类型等信息。数据库采用关系型结构，通过外键和 JSON 字段建立复杂的关联关系。

### 核心设计原则

1. **GUID 标识**：每个实体都有全局唯一标识符（guid），用于区分不同的建筑项目
2. **类型分离**：构件实体与类型信息分离，便于统一管理和查询
3. **关系定义**：通过专门的关系表定义对象间的复杂关系
4. **属性存储**：属性值独立存储，支持动态属性扩展

## 表结构详解

### 1. 项目信息表系列

#### table_building（建筑表）

存储 Revit 或 IFC 模型文件的相关信息。

| 字段名 | 类型 | 说明 | 示例值 |
|--------|------|------|--------|
| globalId | VARCHAR | 全局唯一标识符 | "building_001" |
| name | VARCHAR | 建筑名称 | "办公楼A栋" |
| guid | VARCHAR | 建筑项目GUID | "202504090930" |

**索引建议**：
- PRIMARY KEY: globalId
- INDEX: guid

#### table_buildinginfo（建筑信息表）

存储模型所属项目的相关信息。

| 字段名 | 类型 | 说明 | 示例值 |
|--------|------|------|--------|
| globalId | VARCHAR | 全局唯一标识符 | "info_001" |
| name | VARCHAR | 项目名称 | "XX商业综合体" |
| guid | VARCHAR | 建筑项目GUID | "202504090930" |

**索引建议**：
- PRIMARY KEY: globalId
- INDEX: guid

#### table_level（标高表）

存储模型中的标高信息（楼层信息）。

| 字段名 | 类型 | 说明 | 示例值 |
|--------|------|------|--------|
| globalId | VARCHAR | 全局唯一标识符 | "level_001" |
| name | VARCHAR | 楼层名称 | "F1" / "F2" / "1F" |
| elevation | DECIMAL | 标高值 | 0.0 / 3.6 / 7.2 |
| guid | VARCHAR | 建筑项目GUID | "202504090930" |

**索引建议**：
- PRIMARY KEY: globalId
- INDEX: guid, name

#### table_classification（分类信息表）

存储模型中构件对象所属的数据字典分类。

| 字段名 | 类型 | 说明 | 示例值 |
|--------|------|------|--------|
| globalId | VARCHAR | 全局唯一标识符 | "class_001" |
| name | VARCHAR | 分类名称 | "建筑构件" |
| code | VARCHAR | 分类代码 | "IFCWALLSTANDARDCASE" |
| guid | VARCHAR | 建筑项目GUID | "202504090930" |

**索引建议**：
- PRIMARY KEY: globalId
- INDEX: guid, code

### 2. 构件表系列

#### table_room（房间/空间表）

存储建筑中的房间和空间信息。

| 字段名 | 类型 | 说明 | 示例值 |
|--------|------|------|--------|
| globalId | VARCHAR | 全局唯一标识符 | "123456789" |
| name | VARCHAR | 房间名称 | "标准办公室" |
| longName | VARCHAR | 完整房间名称 | "办公楼:标准办公室:A101" |
| typeId | VARCHAR | 房间类型ID（外键） | "room_type_001" |
| levelId | VARCHAR | 所属楼层ID（外键） | "level_001" |
| guid | VARCHAR | 建筑项目GUID | "202504090930" |

**索引建议**：
- PRIMARY KEY: globalId
- INDEX: guid, levelId, typeId

#### table_wall（墙体表）

存储建筑中的墙体信息。

| 字段名 | 类型 | 说明 | 示例值 |
|--------|------|------|--------|
| globalId | VARCHAR | 全局唯一标识符 | "234567890" |
| name | VARCHAR | 墙体名称 | "外墙:200mm" |
| typeId | VARCHAR | 墙体类型ID（外键） | "wall_type_001" |
| levelId | VARCHAR | 所属楼层ID（外键） | "level_001" |
| guid | VARCHAR | 建筑项目GUID | "202504090930" |

**索引建议**：
- PRIMARY KEY: globalId
- INDEX: guid, levelId, typeId

#### table_window（窗户表）

存储建筑中的窗户信息。

| 字段名 | 类型 | 说明 | 示例值 |
|--------|------|------|--------|
| globalId | VARCHAR | 全局唯一标识符 | "345678901" |
| name | VARCHAR | 窗户名称 | "标准窗:1500x1800" |
| typeId | VARCHAR | 窗户类型ID（外键） | "window_type_001" |
| levelId | VARCHAR | 所属楼层ID（外键） | "level_001" |
| guid | VARCHAR | 建筑项目GUID | "202504090930" |

**索引建议**：
- PRIMARY KEY: globalId
- INDEX: guid, levelId, typeId

#### table_door（门表）

存储建筑中的门信息。

| 字段名 | 类型 | 说明 | 示例值 |
|--------|------|------|--------|
| globalId | VARCHAR | 全局唯一标识符 | "456789012" |
| name | VARCHAR | 门名称 | "标准门:900x2100" |
| typeId | VARCHAR | 门类型ID（外键） | "door_type_001" |
| levelId | VARCHAR | 所属楼层ID（外键） | "level_001" |
| guid | VARCHAR | 建筑项目GUID | "202504090930" |

**索引建议**：
- PRIMARY KEY: globalId
- INDEX: guid, levelId, typeId

#### table_column（柱子表）

存储建筑中的柱子信息（结构柱、建筑柱等）。

| 字段名 | 类型 | 说明 | 示例值 |
|--------|------|------|--------|
| globalId | VARCHAR | 全局唯一标识符 | "567890123" |
| name | VARCHAR | 柱子名称 | "混凝土柱:400x400" |
| typeId | VARCHAR | 柱子类型ID（外键） | "column_type_001" |
| levelId | VARCHAR | 所属楼层ID（外键） | "level_001" |
| guid | VARCHAR | 建筑项目GUID | "202504090930" |

**索引建议**：
- PRIMARY KEY: globalId
- INDEX: guid, levelId, typeId

#### table_beam（梁表）

存储建筑中的梁信息（结构梁、木梁、钢梁等）。

| 字段名 | 类型 | 说明 | 示例值 |
|--------|------|------|--------|
| globalId | VARCHAR | 全局唯一标识符 | "beam_001" |
| name | VARCHAR | 梁名称 | "混凝土梁:300x500" |
| typeId | VARCHAR | 梁类型ID（外键） | "beam_type_001" |
| levelId | VARCHAR | 所属楼层ID（外键） | "level_001" |
| guid | VARCHAR | 建筑项目GUID | "202504090930" |

**索引建议**：
- PRIMARY KEY: globalId
- INDEX: guid, levelId, typeId

#### table_slab（楼板表）

存储建筑中的楼板信息（瓷砖、地毯、地板、木地板、设备基础、楼面面层、楼梯平台、屋顶等）。

| 字段名 | 类型 | 说明 | 示例值 |
|--------|------|------|--------|
| globalId | VARCHAR | 全局唯一标识符 | "slab_001" |
| name | VARCHAR | 楼板名称 | "混凝土楼板:120mm" |
| typeId | VARCHAR | 楼板类型ID（外键） | "slab_type_001" |
| levelId | VARCHAR | 所属楼层ID（外键） | "level_001" |
| guid | VARCHAR | 建筑项目GUID | "202504090930" |

**索引建议**：
- PRIMARY KEY: globalId
- INDEX: guid, levelId, typeId

#### table_stair（楼梯表）

存储建筑中的楼梯信息。

| 字段名 | 类型 | 说明 | 示例值 |
|--------|------|------|--------|
| globalId | VARCHAR | 全局唯一标识符 | "stair_001" |
| name | VARCHAR | 楼梯名称 | "标准楼梯" |
| typeId | VARCHAR | 楼梯类型ID（外键） | "stair_type_001" |
| levelId | VARCHAR | 所属楼层ID（外键） | "level_001" |
| guid | VARCHAR | 建筑项目GUID | "202504090930" |

**索引建议**：
- PRIMARY KEY: globalId
- INDEX: guid, levelId, typeId

#### table_stairflight（楼梯梯段表）

存储建筑中的楼梯梯段信息。

| 字段名 | 类型 | 说明 | 示例值 |
|--------|------|------|--------|
| globalId | VARCHAR | 全局唯一标识符 | "stairflight_001" |
| name | VARCHAR | 梯段名称 | "梯段1" |
| typeId | VARCHAR | 梯段类型ID（外键） | "stairflight_type_001" |
| levelId | VARCHAR | 所属楼层ID（外键） | "level_001" |
| guid | VARCHAR | 建筑项目GUID | "202504090930" |

**索引建议**：
- PRIMARY KEY: globalId
- INDEX: guid, levelId, typeId

#### table_roof（屋顶表）

存储建筑中的屋顶信息（斜屋顶、平屋顶、坡屋顶等）。

| 字段名 | 类型 | 说明 | 示例值 |
|--------|------|------|--------|
| globalId | VARCHAR | 全局唯一标识符 | "roof_001" |
| name | VARCHAR | 屋顶名称 | "平屋顶" |
| typeId | VARCHAR | 屋顶类型ID（外键） | "roof_type_001" |
| levelId | VARCHAR | 所属楼层ID（外键） | "level_001" |
| guid | VARCHAR | 建筑项目GUID | "202504090930" |

**索引建议**：
- PRIMARY KEY: globalId
- INDEX: guid, levelId, typeId

#### table_curtainwall（幕墙表）

存储建筑中的幕墙信息（幕墙窗、幕墙门、幕墙面板等）。

| 字段名 | 类型 | 说明 | 示例值 |
|--------|------|------|--------|
| globalId | VARCHAR | 全局唯一标识符 | "curtainwall_001" |
| name | VARCHAR | 幕墙名称 | "玻璃幕墙" |
| typeId | VARCHAR | 幕墙类型ID（外键） | "curtainwall_type_001" |
| levelId | VARCHAR | 所属楼层ID（外键） | "level_001" |
| guid | VARCHAR | 建筑项目GUID | "202504090930" |

**索引建议**：
- PRIMARY KEY: globalId
- INDEX: guid, levelId, typeId

#### table_plate（面板表）

存储建筑中的面板信息（玻璃、幕墙面板、金属板等）。

| 字段名 | 类型 | 说明 | 示例值 |
|--------|------|------|--------|
| globalId | VARCHAR | 全局唯一标识符 | "plate_001" |
| name | VARCHAR | 面板名称 | "钢化玻璃板" |
| typeId | VARCHAR | 面板类型ID（外键） | "plate_type_001" |
| levelId | VARCHAR | 所属楼层ID（外键） | "level_001" |
| guid | VARCHAR | 建筑项目GUID | "202504090930" |

**索引建议**：
- PRIMARY KEY: globalId
- INDEX: guid, levelId, typeId

#### table_ramp（坡道表）

存储建筑中的坡道信息。

| 字段名 | 类型 | 说明 | 示例值 |
|--------|------|------|--------|
| globalId | VARCHAR | 全局唯一标识符 | "ramp_001" |
| name | VARCHAR | 坡道名称 | "无障碍坡道" |
| typeId | VARCHAR | 坡道类型ID（外键） | "ramp_type_001" |
| levelId | VARCHAR | 所属楼层ID（外键） | "level_001" |
| guid | VARCHAR | 建筑项目GUID | "202504090930" |

**索引建议**：
- PRIMARY KEY: globalId
- INDEX: guid, levelId, typeId

#### table_rampflight（坡道段表）

存储建筑中的坡道段信息。

| 字段名 | 类型 | 说明 | 示例值 |
|--------|------|------|--------|
| globalId | VARCHAR | 全局唯一标识符 | "rampflight_001" |
| name | VARCHAR | 坡道段名称 | "坡道段1" |
| typeId | VARCHAR | 坡道段类型ID（外键） | "rampflight_type_001" |
| levelId | VARCHAR | 所属楼层ID（外键） | "level_001" |
| guid | VARCHAR | 建筑项目GUID | "202504090930" |

**索引建议**：
- PRIMARY KEY: globalId
- INDEX: guid, levelId, typeId

#### table_buildingelementproxy（常规构件表）

存储建筑中的常规构件信息（植被、树木、办公设备、家具、停车位、电气设备、照明设备、机械设备等）。

| 字段名 | 类型 | 说明 | 示例值 |
|--------|------|------|--------|
| globalId | VARCHAR | 全局唯一标识符 | "proxy_001" |
| name | VARCHAR | 构件名称 | "办公桌:标准型" |
| typeId | VARCHAR | 构件类型ID（外键） | "proxy_type_001" |
| levelId | VARCHAR | 所属楼层ID（外键） | "level_001" |
| guid | VARCHAR | 建筑项目GUID | "202504090930" |

**索引建议**：
- PRIMARY KEY: globalId
- INDEX: guid, levelId, typeId

#### table_system（系统表）

存储建筑中的系统信息（水系统、风系统、电气系统等）。

| 字段名 | 类型 | 说明 | 示例值 |
|--------|------|------|--------|
| globalId | VARCHAR | 全局唯一标识符 | "system_001" |
| name | VARCHAR | 系统名称 | "空调系统" |
| guid | VARCHAR | 建筑项目GUID | "202504090930" |

**索引建议**：
- PRIMARY KEY: globalId
- INDEX: guid

### 3. 类型表系列

#### table_roomtype（空间类型表）

存储房间和空间的类型定义。

| 字段名 | 类型 | 说明 | 示例值 |
|--------|------|------|--------|
| globalId | VARCHAR | 全局唯一标识符 | "room_type_001" |
| name | VARCHAR | 类型名称 | "办公室" |
| category | VARCHAR | 类型类别 | "房间" / "面积" / "xRoomType" / "空间" |
| symbolName | VARCHAR | 符号名称 | "OfficeRoom" |
| guid | VARCHAR | 建筑项目GUID | "202504090930" |

**索引建议**：
- PRIMARY KEY: globalId
- INDEX: guid, category

#### table_walltype（墙体类型表）

存储墙体的类型定义（承重墙、隔墙、隔板、栏板等）。

| 字段名 | 类型 | 说明 | 示例值 |
|--------|------|------|--------|
| globalId | VARCHAR | 全局唯一标识符 | "wall_type_001" |
| name | VARCHAR | 类型名称 | "外墙" |
| symbolName | VARCHAR | 符号名称 | "ExteriorWall" |
| guid | VARCHAR | 建筑项目GUID | "202504090930" |

**索引建议**：
- PRIMARY KEY: globalId
- INDEX: guid

#### table_windowtype（窗户类型表）

存储窗户的类型定义。

| 字段名 | 类型 | 说明 | 示例值 |
|--------|------|------|--------|
| globalId | VARCHAR | 全局唯一标识符 | "window_type_001" |
| name | VARCHAR | 类型名称 | "标准窗" |
| symbolName | VARCHAR | 符号名称 | "StandardWindow" |
| guid | VARCHAR | 建筑项目GUID | "202504090930" |

**索引建议**：
- PRIMARY KEY: globalId
- INDEX: guid

#### table_doortype（门类型表）

存储门的类型定义。

| 字段名 | 类型 | 说明 | 示例值 |
|--------|------|------|--------|
| globalId | VARCHAR | 全局唯一标识符 | "door_type_001" |
| name | VARCHAR | 类型名称 | "标准门" |
| symbolName | VARCHAR | 符号名称 | "StandardDoor" |
| guid | VARCHAR | 建筑项目GUID | "202504090930" |

**索引建议**：
- PRIMARY KEY: globalId
- INDEX: guid

#### table_columntype（柱子类型表）

存储柱子的类型定义。

| 字段名 | 类型 | 说明 | 示例值 |
|--------|------|------|--------|
| globalId | VARCHAR | 全局唯一标识符 | "column_type_001" |
| name | VARCHAR | 类型名称 | "混凝土柱" |
| symbolName | VARCHAR | 符号名称 | "ConcreteColumn" |
| guid | VARCHAR | 建筑项目GUID | "202504090930" |

**索引建议**：
- PRIMARY KEY: globalId
- INDEX: guid

#### table_beamtype（梁类型表）

存储梁的类型定义。

| 字段名 | 类型 | 说明 | 示例值 |
|--------|------|------|--------|
| globalId | VARCHAR | 全局唯一标识符 | "beam_type_001" |
| name | VARCHAR | 类型名称 | "混凝土梁" |
| symbolName | VARCHAR | 符号名称 | "ConcreteBeam" |
| guid | VARCHAR | 建筑项目GUID | "202504090930" |

**索引建议**：
- PRIMARY KEY: globalId
- INDEX: guid

#### table_slabtype（楼板类型表）

存储楼板的类型定义。

| 字段名 | 类型 | 说明 | 示例值 |
|--------|------|------|--------|
| globalId | VARCHAR | 全局唯一标识符 | "slab_type_001" |
| name | VARCHAR | 类型名称 | "混凝土楼板" |
| symbolName | VARCHAR | 符号名称 | "ConcreteSlab" |
| guid | VARCHAR | 建筑项目GUID | "202504090930" |

**索引建议**：
- PRIMARY KEY: globalId
- INDEX: guid

#### table_stairtype（楼梯类型表）

存储楼梯的类型定义。

| 字段名 | 类型 | 说明 | 示例值 |
|--------|------|------|--------|
| globalId | VARCHAR | 全局唯一标识符 | "stair_type_001" |
| name | VARCHAR | 类型名称 | "标准楼梯" |
| symbolName | VARCHAR | 符号名称 | "StandardStair" |
| guid | VARCHAR | 建筑项目GUID | "202504090930" |

**索引建议**：
- PRIMARY KEY: globalId
- INDEX: guid

#### table_stairflighttype（楼梯梯段类型表）

存储楼梯梯段的类型定义。

| 字段名 | 类型 | 说明 | 示例值 |
|--------|------|------|--------|
| globalId | VARCHAR | 全局唯一标识符 | "stairflight_type_001" |
| name | VARCHAR | 类型名称 | "标准梯段" |
| symbolName | VARCHAR | 符号名称 | "StandardFlight" |
| guid | VARCHAR | 建筑项目GUID | "202504090930" |

**索引建议**：
- PRIMARY KEY: globalId
- INDEX: guid

#### table_rooftype（屋顶类型表）

存储屋顶的类型定义（斜屋顶、平屋顶、坡屋顶等）。

| 字段名 | 类型 | 说明 | 示例值 |
|--------|------|------|--------|
| globalId | VARCHAR | 全局唯一标识符 | "roof_type_001" |
| name | VARCHAR | 类型名称 | "平屋顶" |
| symbolName | VARCHAR | 符号名称 | "FlatRoof" |
| guid | VARCHAR | 建筑项目GUID | "202504090930" |

**索引建议**：
- PRIMARY KEY: globalId
- INDEX: guid

#### table_curtainwalltype（幕墙类型表）

存储幕墙的类型定义。

| 字段名 | 类型 | 说明 | 示例值 |
|--------|------|------|--------|
| globalId | VARCHAR | 全局唯一标识符 | "curtainwall_type_001" |
| name | VARCHAR | 类型名称 | "玻璃幕墙" |
| symbolName | VARCHAR | 符号名称 | "GlassCurtainWall" |
| guid | VARCHAR | 建筑项目GUID | "202504090930" |

**索引建议**：
- PRIMARY KEY: globalId
- INDEX: guid

#### table_platetype（面板类型表）

存储面板的类型定义。

| 字段名 | 类型 | 说明 | 示例值 |
|--------|------|------|--------|
| globalId | VARCHAR | 全局唯一标识符 | "plate_type_001" |
| name | VARCHAR | 类型名称 | "钢化玻璃板" |
| symbolName | VARCHAR | 符号名称 | "TemperedGlassPlate" |
| guid | VARCHAR | 建筑项目GUID | "202504090930" |

**索引建议**：
- PRIMARY KEY: globalId
- INDEX: guid

#### table_ramptype（坡道类型表）

存储坡道的类型定义。

| 字段名 | 类型 | 说明 | 示例值 |
|--------|------|------|--------|
| globalId | VARCHAR | 全局唯一标识符 | "ramp_type_001" |
| name | VARCHAR | 类型名称 | "无障碍坡道" |
| symbolName | VARCHAR | 符号名称 | "AccessibleRamp" |
| guid | VARCHAR | 建筑项目GUID | "202504090930" |

**索引建议**：
- PRIMARY KEY: globalId
- INDEX: guid

#### table_rampflighttype（坡道段类型表）

存储坡道段的类型定义。

| 字段名 | 类型 | 说明 | 示例值 |
|--------|------|------|--------|
| globalId | VARCHAR | 全局唯一标识符 | "rampflight_type_001" |
| name | VARCHAR | 类型名称 | "标准坡道段" |
| symbolName | VARCHAR | 符号名称 | "StandardRampFlight" |
| guid | VARCHAR | 建筑项目GUID | "202504090930" |

**索引建议**：
- PRIMARY KEY: globalId
- INDEX: guid

#### table_buildingelementproxytype（常规构件类型表）

存储常规构件的类型定义。

| 字段名 | 类型 | 说明 | 示例值 |
|--------|------|------|--------|
| globalId | VARCHAR | 全局唯一标识符 | "proxy_type_001" |
| name | VARCHAR | 类型名称 | "办公桌" |
| symbolName | VARCHAR | 符号名称 | "OfficeDesk" |
| guid | VARCHAR | 建筑项目GUID | "202504090930" |

**索引建议**：
- PRIMARY KEY: globalId
- INDEX: guid

### 4. 辅助表系列

#### table_level（标高表）

存储模型中的标高信息（楼层信息）。

| 字段名 | 类型 | 说明 | 示例值 |
|--------|------|------|--------|
| globalId | VARCHAR | 全局唯一标识符 | "level_001" |
| name | VARCHAR | 楼层名称 | "F1" / "F2" / "1F" |
| elevation | DECIMAL | 标高值 | 0.0 / 3.6 / 7.2 |
| guid | VARCHAR | 建筑项目GUID | "202504090930" |

**索引建议**：
- PRIMARY KEY: globalId
- INDEX: guid, name

#### table_propertydefinition（构件属性名表）

存储模型中所有构件的属性名称定义。

| 字段名 | 类型 | 说明 | 示例值 |
|--------|------|------|--------|
| globalId | VARCHAR | 全局唯一标识符 | "prop_def_001" |
| name | VARCHAR | 属性名称 | "面积" / "宽度" / "设计冷负荷" |
| dataType | VARCHAR | 数据类型 | "String" / "Double" / "Integer" |
| guid | VARCHAR | 建筑项目GUID | "202504090930" |

**索引建议**：
- PRIMARY KEY: globalId
- INDEX: guid, name

#### table_propertyvalue（构件属性值表）

存储模型中构件的属性名对应的值。

| 字段名 | 类型 | 说明 | 示例值 |
|--------|------|------|--------|
| globalId | VARCHAR | 全局唯一标识符 | "prop_001" |
| name | VARCHAR | 属性名称 | "面积" / "宽度" / "设计冷负荷" |
| paramValue | VARCHAR | 属性值 | "45.5" / "1200" / "2500" |
| guid | VARCHAR | 建筑项目GUID | "202504090930" |

**索引建议**：
- PRIMARY KEY: globalId
- INDEX: guid, name

#### table_reldefinesbyobject（对象与对象属性关联关系表）

存储模型中构件及其属性名的关联关系。

| 字段名 | 类型 | 说明 | 示例值 |
|--------|------|------|--------|
| relatingId | VARCHAR | 关系发起方ID | "room_type_001" |
| relatedObjectId | JSON | 相关对象ID列表 | `["prop_001", "prop_002"]` |
| guid | VARCHAR | 建筑项目GUID | "202504090930" |

**索引建议**：
- INDEX: guid, relatingId

## 表关系图

```
table_room (房间)
    ├── typeId → table_roomtype.globalId (房间类型)
    ├── levelId → table_level.globalId (楼层)
    └── globalId → table_reldefinesbyobject.relatingId (关系)
                    └── relatedObjectId → table_propertyvalue.globalId (属性)

table_wall (墙体)
    ├── typeId → table_walltype.globalId (墙体类型)
    ├── levelId → table_level.globalId (楼层)
    └── globalId → table_reldefinesbyobject.relatingId (关系)
                    └── relatedObjectId → table_propertyvalue.globalId (属性)

table_window (窗户)
    ├── typeId → table_windowtype.globalId (窗户类型)
    ├── levelId → table_level.globalId (楼层)
    └── globalId → table_reldefinesbyobject.relatingId (关系)
                    └── relatedObjectId → table_propertyvalue.globalId (属性)

table_door (门)
    ├── typeId → table_doortype.globalId (门类型)
    ├── levelId → table_level.globalId (楼层)
    └── globalId → table_reldefinesbyobject.relatingId (关系)
                    └── relatedObjectId → table_propertyvalue.globalId (属性)

table_column (柱子)
    ├── typeId → table_columntype.globalId (柱子类型)
    ├── levelId → table_level.globalId (楼层)
    └── globalId → table_reldefinesbyobject.relatingId (关系)
                    └── relatedObjectId → table_propertyvalue.globalId (属性)
```

## 常用字段说明

### GUID 字段

所有表都包含 `guid` 字段，用于标识不同的建筑项目。查询时必须包含此字段以限定范围。

**示例**：
```sql
WHERE guid = '202504090930'
```

### 命名约定

#### 构件名称格式
- **格式**：`类别:规格:标识`
- **示例**：`标准办公室:45平米:A101`

#### 提取族名称
使用 `SUBSTRING_INDEX` 提取名称的第一部分：
```sql
SUBSTRING_INDEX(name, ':', 1)  -- 提取第一个冒号前的内容
```

#### 提取房间名称
使用 `SUBSTRING_INDEX` 提取完整名称的最后一部分：
```sql
SUBSTRING_INDEX(longName, ':', -1)  -- 提取最后一个冒号后的内容
```

### 属性名称

属性名称可能同时存在中英文版本，查询时需要同时考虑：

**示例**：
```sql
WHERE p.name IN ('宽度', 'Width')
WHERE p.name LIKE '%宽度%' OR p.name LIKE '%Width%'
```

### 数值属性

数值属性存储为字符串类型，查询时需要进行类型转换：

**示例**：
```sql
CAST(p.paramValue AS DECIMAL(10,2)) > 30
CAST(p.paramValue AS DECIMAL(10,2)) > 1200
```

## 常用查询模式

### 1. 构件基本信息查询

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

### 2. 属性值查询

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

### 3. 多表联合查询

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

## 数据完整性约束

### 外键关系

- 构件表的 `typeId` 必须引用对应的类型表
- 构件表的 `levelId` 必须引用楼层表
- 所有表的 `guid` 字段必须在同一建筑项目中保持一致

### 数据一致性

- 同一建筑项目中的 `guid` 必须相同
- 构件和其类型必须在同一建筑项目中
- 关系表中的对象必须在同一建筑项目中

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

---

**版本**：1.0  
**更新时间**：2026-03-08  
**适用范围**：BIM 模型数据库 Schema