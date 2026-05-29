---
name: automotive-data-pipeline
description: "汽车产品数据全链路管道：Excel/WPS 图片提取 → 车型分类（Wikipedia 验证）→ 飞书 Bitable 导入。支持批量导入、快速添加单条、排序优化。"
---

# Automotive Data Pipeline

汽车产品数据全链路管道，从 Excel 文件到飞书多维表格。

## Quick Start

### 完整导入流程
```bash
# 1. 提取 Excel 中的图片
python scripts/extract_images.py --input products.xlsx --output ./extracted/

# 2. 批量分类
python scripts/pipeline.py --input products.xlsx --classify --output classified.csv

# 3. 导入飞书
python scripts/pipeline.py --input classified.csv --import --config feishu-config.json
```

### 快速添加单条
```bash
python scripts/quick_add.py --config feishu-config.json \
  --name "丰田 凌放XU60 2012-2019" --size "64*57*20.5cm" --weight "6.1kg"
```

### 排序优化
```bash
python scripts/pipeline.py --config feishu-config.json --sort
```

## Core Capabilities

1. **Excel 图片提取**：从 .xlsx 文件中提取嵌入图片，按行号关联
2. **车型分类**：调用 vehicle-classifier 进行标准化
3. **飞书导入**：调用 feishu-bitable-ops 批量导入
4. **快速添加**：单条数据快速添加模式
5. **排序优化**：车系 → 核心车型 → 产品类型 → 年款

## Workflow Decision Tree

```
新数据？
├── Excel/WPS 文件（多条）
│   ├── 提取图片 → 分类 → 验证 → 批量导入
│   └── 已有分类数据 → 直接批量导入
├── 单条数据
│   └── quick_add.py 快速添加
└── 排序/整理
    └── pipeline.py --sort
```

## Dependencies

- `vehicle-classifier`：车型分类
- `feishu-bitable-ops`：飞书操作
- `openpyxl`：Excel 读取
- `pandas`：数据处理

## References

- `references/workflow-guide.md`：详细工作流指南
