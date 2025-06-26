# Excel数据转换器

一个功能强大的Excel数据转换工具，专为游戏开发设计。将Excel表格数据转换为Lua、JSON等格式，支持复杂的数据类型、多数据源合并和灵活的验证系统。

## 特性

- **标准三行格式**：支持标准的Excel格式（描述行、字段名行、类型行、数据行）
- **多种数据类型**：支持基本类型（int、float、string、bool）、数组类型、自定义对象类型
- **多数据源合并**：可将不同Excel文件或工作表的数据合并到一个输出文件
- **作用域控制**：支持服务器端(s)、客户端(c)、全部(sc)的作用域过滤
- **灵活验证**：支持字段级、行级、数据集级的自定义验证器
- **多种输出格式**：支持Lua表格式和JSON格式输出
- **命令行工具**：提供完整的CLI界面

## 📖 文档

- **[CLI使用指南](docs/CLI使用指南.md)** - 详细的命令行工具使用说明

## 安装

### 从源码安装

```bash
git clone https://github.com/huliuchao/ExcelConverter.git
cd ExcelConverter
pip install -e .
```

## 快速开始

### 1. 准备配置文件

创建 `config.toml` 文件：

```toml
[defaults]
primary_key = "ID"
separator = ","

[exports.items]
sources = [
    { file = "items.xlsx", sheet = "武器" },
    { file = "items.xlsx", sheet = "防具" }
]
scope = "sc"
fields = [
    { name = "ID", type = "int", scope = "sc" },
    { name = "ItemName", type = "string", scope = "c" },
    { name = "Icon", type = "string", scope = "c" }
]
```

### 2. 准备Excel文件

Excel文件需要遵循标准三行格式：

- 第1行：字段描述（可选，不会导出）
- 第2行：字段名称
- 第3行：字段类型
- 第4行开始：实际数据

### 3. 运行转换

```bash
# 转换所有配置的导出
excel-converter --config config.toml convert

# 转换特定导出为Lua格式
excel-converter --config config.toml convert --export items --format lua

# 只转换服务器端数据
excel-converter --config config.toml convert --scope s

# 预览Excel文件结构
excel-converter --config config.toml preview excel/items.xlsx

# 验证配置文件
excel-converter --config config.toml validate-config

# 列出所有导出配置
excel-converter --config config.toml list-exports
```

> 💡 **更多CLI用法**：查看 [CLI使用指南](docs/CLI使用指南.md) 了解完整的命令行选项和使用示例。

## 配置文件详解

### 基本配置结构

```toml
[defaults]
primary_key = "ID"           # 默认主键字段名
separator = ","              # 数组分隔符
validate_unique_keys = true  # 验证主键唯一性
validate_schema = true       # 验证数据schema

[object_schemas.attribute]
description = "角色/道具属性配置"
separator = ","
key_value_separator = ":"
fields = [
    { key = "Attack", type = "int", description = "攻击力" },
    { key = "Defense", type = "int", description = "防御力" },
    { key = "HP", type = "int", description = "血量" }
]

[exports.items]
sources = [
    { file = "items.xlsx", sheet = "武器" }
]
scope = "sc"
primary_key = "ItemID"  # 覆盖默认主键
fields = [
    { name = "ItemID", scope = "sc" },
    { name = "ItemName", scope = "c" },
    { name = "Attributes", scope = "sc" }
]
validators = [
    { field = "ItemID", script = "unique.py" },
    { field = "ItemType", script = "enum.py", params = { values = ["weapon", "armor"] } }
]
```

### 支持的数据类型

#### 基本类型

- `int`: 整数
- `float`: 浮点数
- `string`: 字符串
- `bool`: 布尔值

#### 数组类型

- `array<int>`: 整数数组，如 `1,2,3`
- `array<string>`: 字符串数组，如 `火,水,土`

#### 自定义对象类型

- `object:attribute`: 自定义属性对象

对象类型支持两种填写方式：

1. 按顺序：`100,50,200` （对应Attack、Defense、HP）
2. Key-Value：`Attack:100,Defense:50,HP:200`

### 作用域控制

- `s`: 仅服务器端
- `c`: 仅客户端
- `sc`: 服务器端和客户端

## 验证系统

支持三个级别的验证：

- **字段级验证**：验证单个字段的值
- **行级验证**：验证行内多个字段的关系
- **数据集级验证**：验证整个数据集的一致性

### 预设验证器

#### 字段级验证器

**required.py** - 必填验证

```toml
{ field = "ItemName", script = "required.py" }
```

**enum.py** - 枚举值验证

```toml
{ field = "ItemType", script = "enum.py", params = { values = ["weapon", "armor", "consumable"] } }
```

**range.py** - 数值范围验证

```toml
{ field = "Price", script = "range.py", params = { min = 0, max = 99999 } }
```

**length.py** - 字符串长度验证

```toml
{ field = "ItemName", script = "length.py", params = { min = 2, max = 20 } }
```

**pattern.py** - 正则表达式验证

```toml
{ field = "ItemCode", script = "pattern.py", params = { pattern = "^[A-Z]{2}\\d{4}$" } }
```

**unique.py** - 唯一性验证

```toml
{ field = "ItemID", script = "unique.py" }
```

**array_length.py** - 数组长度验证

```toml
{ field = "Tags", script = "array_length.py", params = { min = 1, max = 5 } }
{ field = "Requirements", script = "array_length.py", params = { exact = 3 } }
```

### 自定义验证器

#### 字段级验证器

创建 `validators/custom_validator.py`：

```python
def validate_field(field_name, value, params, row_data):
    """
    字段级验证（必需方法）

    Args:
        field_name: 字段名
        value: 字段值
        params: 验证参数
        row_data: 整行数据

    Returns:
        (bool, str): (是否有效, 错误信息)
    """
    if value < 0:
        return False, f"Field {field_name} cannot be negative"
    return True, ""

def validate_row(row_data, params, export_config):
    """
    行级验证（可选方法）
    用于验证行内多个字段的关系
    """
    if row_data.get('StartTime') >= row_data.get('EndTime'):
        return False, "Start time must be before end time"
    return True, ""

def validate_dataset(dataset, export_config):
    """
    数据集级验证（可选方法）
    用于验证整个数据集的一致性
    """
    ids = [row.get('ID') for row in dataset]
    if len(ids) != len(set(ids)):
        return False, "Duplicate IDs found in dataset"
    return True, ""
```

#### 验证器接口要求

- `validate_field(field_name, value, params, row_data)`: 必需，字段级验证
- `validate_row(row_data, params, export_config)`: 可选，行级验证
- `validate_dataset(dataset, export_config)`: 可选，数据集级验证

## 命令行参考

### 全局选项

- `-c, --config`: 配置文件路径（默认：config.toml）
- `-v, --verbose`: 详细输出
- `--log-file`: 日志文件路径

### convert 命令

```bash
excel-converter convert [OPTIONS]
```

选项：

- `-e, --export`: 指定要转换的导出配置
- `-f, --format`: 输出格式（lua/json_map/json_array）
- `--compact`: 使用紧凑格式（无缩进）
- `-s, --scope`: 作用域过滤（s/c/sc）
- `-o, --output-dir`: 输出目录（默认：output）
- `--excel-dir`: Excel文件目录（默认：.）
- `--validators-dir`: 验证器目录（默认：validators）
- `--validation-report`: 保存验证结果到文件
- `--dry-run`: 仅模拟运行，不生成文件

### 其他命令

- `validate-config`: 验证配置文件
- `list-exports`: 列出所有导出配置
- `preview <file>`: 预览Excel文件结构

## 输出格式

### Lua格式

```lua
-- items Data
-- Auto-generated by Excel Converter

local items = {
    [1001] = {
        ItemID = 1001,
        ItemName = "长剑",
        Price = 100,
        Attributes = {Attack = 50, Defense = 10, HP = 200}
    },
    [1002] = {
        ItemID = 1002,
        ItemName = "盾牌",
        Price = 80,
        Attributes = {Attack = 5, Defense = 30, HP = 150}
    }
}

return items
```

### JSON格式

支持两种JSON输出格式：

#### JSON映射格式 (`json_map`)

键值对映射结构，适合通过ID快速查找：

```json
{
  "1001": {
    "ItemID": 1001,
    "ItemName": "长剑",
    "Price": 100,
    "Attributes": {"Attack": 50, "Defense": 10, "HP": 200}
  },
  "1002": {
    "ItemID": 1002,
    "ItemName": "盾牌",
    "Price": 80,
    "Attributes": {"Attack": 5, "Defense": 30, "HP": 150}
  }
}
```

#### JSON数组格式 (`json_array`)

数组形式，适合顺序遍历的场景：

```json
[
  {
    "ItemID": 1001,
    "ItemName": "长剑",
    "Price": 100,
    "Attributes": {"Attack": 50, "Defense": 10, "HP": 200}
  },
  {
    "ItemID": 1002,
    "ItemName": "盾牌",
    "Price": 80,
    "Attributes": {"Attack": 5, "Defense": 30, "HP": 150}
  }
]
```

两种JSON格式和Lua都支持紧凑模式（使用 `--compact` 参数），输出时不包含缩进和空格。

### 添加新的验证器

1. 在 `validators/` 目录下创建新的 `.py` 文件
2. 实现必需的 `validate_field` 方法
3. 可选实现 `validate_row` 和 `validate_dataset` 方法
4. 在配置文件中引用新验证器
