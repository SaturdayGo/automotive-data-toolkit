---
name: vehicle-classifier
description: "汽车车型标准化引擎：底盘代号映射（Wikipedia 验证）、品牌归一化、车系推断、产品类型提取。支持批量分类、单条查询、验收报告。"
---

# Vehicle Classifier

汽车车型标准化引擎，将原始车型名转换为结构化分类。

## Quick Start

### 单条分类
```bash
python scripts/classify.py --input "宝马E90大灯4片"
# 输出: brand=宝马, series=宝马 3系, model=E90, product_type=大灯, year_range=2004-2011
```

### 批量分类
```bash
python scripts/classify.py --input data.csv --output classified.csv --wikipedia-verify
```

### 底盘代号查询
```bash
python scripts/classify.py --lookup E60
# 输出: 宝马 5系, 2003-2010, E60=sedan E61=wagon
```

### 验收报告
```bash
python scripts/verify_mapping.py --mapping assets/mapping-data.json --report report.md
```

## Core Capabilities

1. **品牌归一化**：三菱系列→三菱、奥迪大灯→奥迪
2. **底盘代号映射**：E60→宝马 5系、W204→奔驰 C级（Wikipedia 验证）
3. **车系推断**：E90/F30/G20→宝马 3系
4. **产品类型提取**：从车型名中提取"尾灯/大灯/贯穿灯"
5. **年款提取**：正则匹配年份范围
6. **验收机制**：子 Agent 对照 Wikipedia 验证映射

## 输入格式

原始车型名字符串，支持格式：
- "宝马E90大灯4片"
- "丰田 凌放XU60 2012-2019"
- "03-09款丰田超霸大灯"

## 输出格式

```json
{
  "brand": "宝马",
  "series": "宝马 3系",
  "model": "E90",
  "product_type": "大灯",
  "year_range": "2004-2011",
  "wikipedia_verified": true,
  "confidence": 0.95
}
```

## References

- `references/chassis-code-mapping.md`：底盘代号映射表
- `references/brand-normalization.md`：品牌归一化规则
- `references/wikipedia-sources.md`：Wikipedia 来源链接
