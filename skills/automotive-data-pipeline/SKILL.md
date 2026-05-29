---
name: automotive-data-pipeline
description: "汽车产品数据全链路管道：Excel/WPS 图片提取 → 车型分类（Wikipedia 验证）→ 飞书 Bitable 导入。支持多表注册、批量导入、快速添加单条、排序优化。"
---

# Automotive Data Pipeline

汽车产品数据全链路管道，从 Excel 文件到飞书多维表格。

## Quick Start

### 快速添加单条（最常用）

```bash
# 使用默认表
python scripts/quick_add.py --name "轩逸 14代 大灯" --size "30*38*76cm" --weight "12kg"

# 指定目标表
python scripts/quick_add.py --table 灯具表 --name "丰田超霸大灯" --size "74*60*28cm"

# 查看已注册的表
python scripts/quick_add.py --list-tables
```

### 完整导入流程

```bash
# 1. 提取 Excel 中的图片
python scripts/extract_images.py --input products.xlsx --output ./extracted/

# 2. 批量分类
python scripts/pipeline.py --input products.xlsx --classify --output classified.csv

# 3. 导入飞书
python scripts/pipeline.py --input classified.csv --import --config configs/灯具表.json
```

### 排序优化

```bash
python scripts/pipeline.py --config configs/灯具表.json --sort
```

## 多表管理

支持注册多张飞书表格，通过表名快速切换。

### 表注册表

`tables.json` 定义所有可用的表：

```json
{
  "default": "灯具表",
  "tables": {
    "灯具表": "configs/灯具表.json",
    "配件表": "configs/配件表.json"
  }
}
```

### 添加新表

1. 创建配置文件：`configs/新表名.json`
2. 在 `tables.json` 的 `tables` 中添加映射
3. 可选：修改 `default` 切换默认表

### 命令用法

```bash
# 使用默认表
python scripts/quick_add.py --name "车型名"

# 指定表
python scripts/quick_add.py --table 配件表 --name "H4灯泡"

# 直接指定配置文件（绕过注册表）
python scripts/quick_add.py --config /path/to/config.json --name "车型名"
```

## Core Capabilities

1. **多表注册**：支持注册多张飞书表格，通过表名快速切换
2. **Excel 图片提取**：从 .xlsx 文件中提取嵌入图片，按行号关联
3. **车型分类**：调用 vehicle-classifier 进行标准化
4. **飞书导入**：调用 feishu-bitable-ops 批量导入
5. **快速添加**：单条数据快速添加模式
6. **排序优化**：车系 → 核心车型 → 产品类型 → 年款

## Workflow Decision Tree

```
新数据？
├── Excel/WPS 文件（多条）
│   ├── 提取图片 → 分类 → 验证 → 批量导入
│   └── 已有分类数据 → 直接批量导入
├── 单条数据
│   └── quick_add.py --table 表名 --name "车型名"
└── 排序/整理
    └── pipeline.py --sort
```

## 目录结构

```
automotive-data-pipeline/
├── tables.json              # 表注册表
├── configs/                 # 各表配置文件
│   └── 灯具表.json
├── scripts/
│   ├── quick_add.py         # 快速添加单条
│   ├── pipeline.py          # 批量导入管道
│   └── extract_images.py    # Excel 图片提取
└── references/
    └── workflow-guide.md
```

## Dependencies

- `vehicle-classifier`：车型分类
- `feishu-bitable-ops`：飞书操作
- `openpyxl`：Excel 读取
- `pandas`：数据处理

## References

- `references/workflow-guide.md`：详细工作流指南
