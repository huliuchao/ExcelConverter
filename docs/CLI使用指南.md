# Excel Converter CLI 使用指南

## 基本语法

Excel Converter 使用标准的CLI格式：

```bash
excel-converter [全局选项] 子命令 [子命令选项]
```

## 全局选项

以下选项可以在**任意位置**使用：

- `-c, --config PATH`: 配置文件路径（默认: config.toml）
- `-v, --verbose`: 启用详细输出
- `--log-file PATH`: 日志文件路径

专用全局选项（仅在主命令使用）：
- `-V, --version`: 显示版本信息并退出

## 子命令

### 1. convert - 转换数据
将Excel文件转换为指定格式。

```bash
# 基本用法
excel-converter convert --config config.toml

# 指定导出和格式
excel-converter convert --config config.toml --export items --format lua

# 使用紧凑模式
excel-converter convert --config config.toml --format lua --compact

# 只生成服务器端数据
excel-converter convert --config config.toml --scope s

# 干运行（不生成文件）
excel-converter convert --config config.toml --dry-run
```

**选项**：
- `-c, --config PATH`: 配置文件路径（默认: config.toml）
- `-v, --verbose`: 启用详细输出
- `--log-file PATH`: 日志文件路径
- `-e, --export TEXT`: 指定要转换的导出配置
- `-f, --format [lua|json_map|json_array]`: 输出格式
- `--compact`: 使用紧凑格式（无缩进）
- `-s, --scope [s|c|sc]`: 导出范围（s=服务器，c=客户端，sc=全部）
- `-o, --output-dir PATH`: 输出目录
- `--excel-dir PATH`: Excel文件目录
- `--validators-dir PATH`: 验证器目录
- `--validation-report PATH`: 保存验证结果到文件
- `--dry-run`: 执行干运行（不生成文件）

### 2. list-exports - 列出导出配置
显示配置文件中的所有导出配置。

```bash
excel-converter list-exports --config config.toml
```

**选项**：
- `-c, --config PATH`: 配置文件路径（默认: config.toml）
- `-v, --verbose`: 启用详细输出
- `--log-file PATH`: 日志文件路径

### 3. validate-config - 验证配置文件
检查配置文件的语法和语义正确性。

```bash
excel-converter validate-config --config config.toml
```

**选项**：
- `-c, --config PATH`: 配置文件路径（默认: config.toml）
- `-v, --verbose`: 启用详细输出
- `--log-file PATH`: 日志文件路径

### 4. preview - 预览Excel文件
查看Excel文件的结构和字段信息。

```bash
# 预览第一个工作表
excel-converter preview excel/items.xlsx

# 预览指定工作表
excel-converter preview excel/items.xlsx --sheet weapon
```

**选项**：
- `-c, --config PATH`: 配置文件路径（默认: config.toml）
- `-v, --verbose`: 启用详细输出
- `--log-file PATH`: 日志文件路径
- `--sheet TEXT`: 要预览的工作表名称

## 帮助信息

### 无需配置文件即可查看帮助 ✅

```bash
# 主命令帮助
excel-converter --help

# 版本信息
excel-converter --version
excel-converter -V

# 子命令帮助
excel-converter convert --help
excel-converter list-exports --help
excel-converter preview --help
excel-converter validate-config --help
```

## 常见使用场景

### 1. 快速开始
```bash
# 1. 查看帮助了解功能
excel-converter --help

# 2. 预览Excel文件结构
excel-converter preview excel/items.xlsx

# 3. 验证配置文件
excel-converter validate-config --config config.toml

# 4. 列出所有导出配置
excel-converter list-exports --config config.toml

# 5. 执行转换
excel-converter convert --config config.toml
```

### 2. 开发调试
```bash
# 启用详细输出
excel-converter convert --config config.toml --verbose

# 干运行检查
excel-converter convert --config config.toml --dry-run

# 生成验证报告
excel-converter convert --config config.toml --validation-report validation.txt
```

### 3. 生产部署
```bash
# 只生成服务器数据，紧凑格式
excel-converter convert --config config.toml --scope s --compact

# 指定输出目录
excel-converter convert --config config.toml --output-dir /path/to/output
```

## 错误处理

### 配置文件不存在
如果指定的配置文件不存在，会显示友好的错误信息：

```
ERROR - Configuration file not found: config.toml
ERROR - Please ensure the config file exists or specify a valid path with --config
```

## 最佳实践

1. **先查看帮助**：`excel-converter --help`
2. **验证配置文件**：在转换前运行 `validate-config`
3. **使用干运行**：重要操作前先使用 `--dry-run`
4. **启用详细输出**：调试时使用 `--verbose`
5. **生成验证报告**：定期使用 `--validation-report` 检查数据质量
6. **灵活使用参数**：根据个人习惯和脚本需要自由排列参数位置

## 配置文件示例

确保有正确的配置文件（通常命名为 `config.toml`）：

```toml
[defaults]
primary_key = "ID"
separator = ","

[input]
source_dir = "./excel"
output_dir = "./output"

[output]
format = "lua"

[exports.items]
sources = [
    { file = "items.xlsx", sheet = "Sheet1" }
]
scope = "sc"
fields = [
    { name = "ID", scope = "sc" },
    { name = "Name", scope = "sc" }
]
``` 