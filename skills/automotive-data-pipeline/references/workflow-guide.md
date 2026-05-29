# 工作流指南

## 场景 1：Excel 批量导入

### 步骤

1. **准备 Excel 文件**
   - 第一行为列名
   - 建议列：车型名、尺寸、重量、供应商、备注
   - 图片可嵌入在 Excel 中

2. **提取图片**（如果有嵌入图片）
   ```bash
   python scripts/extract_images.py --input products.xlsx --output ./images/
   ```

3. **分类数据**
   ```bash
   python scripts/pipeline.py --input products.xlsx --classify --output classified.csv
   ```

4. **验证分类结果**
   - 检查 classified.csv 中的分类是否正确
   - 手动修正错误的分类

5. **导入飞书**
   ```bash
   python scripts/pipeline.py --input classified.csv --import --config feishu-config.json
   ```

6. **排序优化**
   ```bash
   python scripts/pipeline.py --config feishu-config.json --sort
   ```

### 完整命令

```bash
python scripts/pipeline.py --input products.xlsx --config feishu-config.json --full
```

---

## 场景 2：快速添加单条

### 步骤

1. **添加记录**
   ```bash
   python scripts/quick_add.py --config feishu-config.json \
     --name "丰田 凌放XU60 2012-2019" \
     --size "64*57*20.5cm" \
     --weight "6.1kg"
   ```

2. **自动分类**
   - 如果不指定 --brand, --series 等参数，会自动分类
   - 分类结果基于 vehicle-classifier

---

## 场景 3：排序优化

### 排序规则

排序优先级：车系 → 核心车型 → 产品类型 → 年款

```
宝马 3系
  ├── E90 大灯
  ├── F30 尾灯
  └── G20 尾灯
宝马 5系
  ├── E60 大灯
  ├── F10 大灯
  ├── G30 尾灯
  └── G38 尾灯
丰田 普拉多
  ├── LC95,90 尾灯
  ├── LC250 尾灯
  └── 霸道 大灯
```

### 命令

```bash
python scripts/pipeline.py --config feishu-config.json --sort
```

---

## 配置文件格式

```json
{
  "base_token": "YOUR_BASE_TOKEN",
  "table_id": "YOUR_TABLE_ID",
  "field_mapping": {
    "核心车型": "fldonaIzpu",
    "车系": "fldx9YIC7e",
    "产品类型": "fldoxR19iy",
    "年款": "fldkYltBIQ",
    "尺寸": "fld2Bvkpp7",
    "重量": "fldzFIZFZo",
    "图片": "fldpWSnOh5",
    "备注": "fldrtH2N5f",
    "原始车型名": "fld3R3HmL4"
  }
}
```

---

## 常见问题

### Q: 分类结果不准确怎么办？

A: 手动修正 classified.csv 中的错误，然后重新导入。

### Q: 如何更新已有记录？

A: 使用 batch_ops.py 的 update 功能，需要提供 record_id。

### Q: 图片上传失败？

A: 检查 lark-cli 认证状态：`lark-cli auth status`

### Q: 批量操作有数量限制吗？

A: lark-cli 每批最多 500 条记录，超过会自动分批。
