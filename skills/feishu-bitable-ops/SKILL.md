---
name: feishu-bitable-ops
description: "飞书多维表格批量操作封装：批量创建/更新/删除记录、图片上传、排序/分组配置、去重工具。统一处理 lark-cli 的各种坑。"
---

# Feishu Bitable Ops

飞书多维表格批量操作封装，统一处理 lark-cli 的各种坑。

## Quick Start

### 批量创建记录
```bash
python scripts/batch_ops.py --action create --config feishu-config.json --data records.json
```

### 批量更新记录
```bash
python scripts/batch_ops.py --action update --config feishu-config.json --data updates.json
```

### 图片上传
```bash
python scripts/image_upload.py --config feishu-config.json --images ./images/ --mapping mapping.json
```

### 设置排序
```bash
python scripts/view_config.py --config feishu-config.json --sort '[{"field":"车系","order":"asc"}]'
```

### 去重
```bash
python scripts/dedup.py --config feishu-config.json --field 图片 --dry-run
```

## Core Capabilities

1. **批量操作**：创建/更新/删除记录，自动分批、过滤 null
2. **图片上传**：批量上传图片获取 file_token
3. **视图配置**：排序/分组/字段可见性
4. **去重工具**：按字段去重，支持 dry-run
5. **lark-cli 封装**：统一处理 stderr、JSON 解析、重试

## 配置格式

```json
{
  "base_token": "XHuabhMFcaSX8zsUob5cBXDanNc",
  "table_id": "tblfwPp6QmXqhRF7",
  "field_mapping": {
    "车系": "fldx9YIC7e",
    "核心车型": "fldonaIzpu",
    "产品类型": "fldoxR19iy",
    "年款": "fldkYltBIQ"
  }
}
```

## References

- `references/lark-cli-cheatsheet.md`：lark-cli 命令速查
- `references/field-id-template.md`：字段 ID 模板
