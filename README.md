# 汽车改装灯具数据工具包

> Automotive Data Toolkit — 飞书多维表格 + 车型分类 + 数据管道

一套专为汽车改装灯具行业设计的数据管理工具，解决 Excel/WPS 数据导入飞书、车型名称标准化、批量数据清洗等痛点。

## 适用场景

- 汽车配件产品数据管理
- Excel/WPS 图片批量提取 + 上传飞书
- 车型名称标准化（底盘代号 → 市场名称）
- 飞书多维表格批量操作
- 产品数据排序优化

## 项目结构

```
automotive-data-toolkit/
├── skills/
│   ├── vehicle-classifier/      # 车型分类引擎
│   │   ├── scripts/             # 核心脚本
│   │   ├── tests/               # 测试用例
│   │   ├── references/          # 参考文档
│   │   └── assets/              # 映射数据
│   ├── feishu-bitable-ops/      # 飞书操作封装
│   │   ├── scripts/
│   │   ├── tests/
│   │   ├── references/
│   │   └── assets/
│   └── automotive-data-pipeline/ # 全链路管道
│       ├── scripts/
│       └── references/
├── examples/                    # 使用示例
├── docs/                        # 详细文档
├── requirements.txt
├── LICENSE
└── README.md
```

## 快速开始

### 1. 环境准备

```bash
# 克隆项目
git clone https://github.com/SaturdayGo/automotive-data-toolkit.git
cd automotive-data-toolkit

# 安装依赖
pip install -r requirements.txt
```

### 2. 安装 lark-cli（飞书命令行工具）

```bash
npm install -g @anthropic-ai/lark-cli
```

### 3. 配置飞书连接

复制配置模板并填入你的飞书信息：

```bash
cp skills/feishu-bitable-ops/assets/config-template.json my-config.json
```

编辑 `my-config.json`：

```json
{
  "base_token": "你的飞书多维表格 base_token",
  "table_id": "你的表格 ID",
  "field_mapping": {
    "核心车型": "fldxxxxxx",
    "车系": "fldxxxxxx",
    "产品类型": "fldxxxxxx",
    "年款": "fldxxxxxx",
    "尺寸": "fldxxxxxx",
    "重量": "fldxxxxxx",
    "图片": "fldxxxxxx",
    "备注": "fldxxxxxx",
    "原始车型名": "fldxxxxxx"
  }
}
```

> **如何获取 field_mapping？**
> 运行 `lark-cli base +field-list --base-token <token> --table-id <table-id>` 查看字段 ID

---

## 功能详解

### 功能 1：车型分类引擎

将原始车型名转换为结构化分类，支持 Wikipedia 验证。

```bash
# 单条分类
cd skills/vehicle-classifier
python scripts/classify.py --input "宝马E90大灯4片"
# 输出: brand=宝马, series=宝马 3系, model=E90, product_type=大灯, year_range=2004-2011

# 底盘代号查询
python scripts/classify.py --lookup E60
# 输出: 宝马 5系, 2003-2010, E60=sedan E61=wagon

# 批量分类
python scripts/classify.py --input data.csv --output classified.csv

# 跳过 Wikipedia 验证（离线模式）
python scripts/classify.py --input "宝马E90大灯" --no-wikipedia
```

**支持的品牌：** 宝马、奔驰、丰田、日产、路虎、三菱、大众、本田、马自达、福特、现代、雷克萨斯、雪佛兰、吉普

**支持的产品类型：** 大灯、尾灯、贯穿灯、雾灯、转向灯、刹车灯、后杠灯、日行灯等

### 功能 2：飞书批量操作

统一封装 lark-cli，自动处理各种坑（proxy 警告、JSON 解析、null 值过滤）。

```bash
cd skills/feishu-bitable-ops

# 批量创建
python scripts/batch_ops.py --action create --config my-config.json --data records.json

# 批量更新
python scripts/batch_ops.py --action update --config my-config.json --data updates.json

# 图片上传
python scripts/image_upload.py --config my-config.json --images ./images/ --mapping mapping.json

# 设置排序
python scripts/view_config.py --config my-config.json --sort '[{"field":"车系","order":"asc"}]'

# 设置分组
python scripts/view_config.py --config my-config.json --group '[{"field":"车系","order":"asc"}]'

# 去重（先预览再执行）
python scripts/dedup.py --config my-config.json --field 图片 --dry-run
python scripts/dedup.py --config my-config.json --field 图片
```

### 功能 3：全链路管道

从 Excel 到飞书的一站式数据导入。

```bash
cd skills/automotive-data-pipeline

# 完整流程
python scripts/pipeline.py --input products.xlsx --config my-config.json --full

# 分步执行
# Step 1: 提取图片
python scripts/extract_images.py --input products.xlsx --output ./images/

# Step 2: 分类
python scripts/pipeline.py --input products.xlsx --classify --output classified.csv

# Step 3: 导入飞书
python scripts/pipeline.py --input classified.csv --import --config my-config.json

# Step 4: 排序优化
python scripts/pipeline.py --config my-config.json --sort

# 快速添加单条
python scripts/quick_add.py --config my-config.json \
  --name "丰田 凌放XU60 2012-2019" --size "64*57*20.5cm" --weight "6.1kg"
```

---

## 配置指南

### 飞书多维表格字段要求

| 字段名 | 类型 | 说明 |
|--------|------|------|
| 核心车型 | 文本 | 标准化车型名（如 E90、W204） |
| 车系 | 单选 | 车系分类（如 宝马 3系、奔驰 C级） |
| 产品类型 | 单选 | 产品类型（大灯、尾灯等） |
| 年款 | 文本 | 年份范围（如 2004-2011） |
| 尺寸 | 文本 | 产品尺寸 |
| 重量 | 文本 | 产品重量 |
| 图片 | 附件 | 产品图片 |
| 备注 | 文本 | 其他信息 |
| 人工审核 | 复选框 | 是否已审核 |
| 原始车型名 | 文本 | 原始输入的车型名 |

### 底盘代号映射

映射数据存储在 `skills/vehicle-classifier/assets/mapping-data.json`，已通过 Wikipedia 验证。

添加新映射：
1. 在 Wikipedia 查找对应车型页面
2. 确认底盘代号与市场名称的对应关系
3. 编辑 `mapping-data.json`
4. 运行 `python scripts/verify_mapping.py` 验证

---

## 注意事项

### 重要提醒

1. **lark-cli 认证**：首次使用前需要运行 `lark-cli auth login` 完成飞书授权

2. **field_mapping 必须正确**：字段 ID 是飞书多维表格的唯一标识，填错会导致数据写入错误字段

3. **批量操作限制**：lark-cli 每批最多 500 条记录，超过会自动分批处理

4. **null 值处理**：脚本会自动过滤 null/None/空字符串，避免飞书 API 报错

5. **proxy 警告**：lark-cli 会输出 proxy 警告到 stdout，脚本已自动处理（stderr 抑制）

6. **CSV 编码**：所有 CSV 输出使用 `utf-8-sig` 编码，确保 Excel 打开不乱码

7. **Wikipedia 验证**：底盘代号映射基于 Wikipedia，但部分冷门车型可能缺失，需手动补充

### 常见问题

**Q: 提示 "lark-cli not found"**
A: 安装 lark-cli：`npm install -g @anthropic-ai/lark-cli`

**Q: 飞书 API 返回权限错误**
A: 检查 lark-cli 认证状态：`lark-cli auth status`，必要时重新登录

**Q: 分类结果不准确**
A: 检查 `mapping-data.json` 是否包含该车型，或手动修正分类结果

**Q: 图片上传失败**
A: 确认图片格式支持（jpg/png），检查飞书附件字段 ID 是否正确

---

## 后续优化计划

### P0 — 高优先级

- [ ] 支持更多品牌（起亚、标致、雪铁龙等）
- [ ] 图片自动压缩（超过飞书限制时自动处理）
- [ ] 批量分类结果预览 + 手动修正界面

### P1 — 中优先级

- [ ] 支持从飞书导出数据到 Excel
- [ ] 分类结果置信度可视化
- [ ] 支持自定义产品类型关键词
- [ ] 批量去重功能增强（多字段组合去重）

### P2 — 低优先级

- [ ] Web UI 界面
- [ ] 支持阿里国际站数据导入
- [ ] 支持淘宝/1688 数据导入
- [ ] 自动生成产品描述文案

### P3 — 远期规划

- [ ] AI 辅助分类（GPT/Claude 自动识别车型）
- [ ] 多语言支持（英文车型名）
- [ ] 数据统计报表
- [ ] 与 ERP 系统对接

---

## 开发指南

### 运行测试

```bash
# 测试车型分类器
cd skills/vehicle-classifier
python -m pytest tests/ -v

# 测试飞书操作
cd skills/feishu-bitable-ops
python -m pytest tests/ -v
```

### 项目依赖

- Python 3.10+
- pandas（数据处理）
- openpyxl（Excel 读取）
- lark-cli（飞书命令行工具）
- pytest（测试）

### 贡献指南

1. Fork 本项目
2. 创建特性分支：`git checkout -b feature/your-feature`
3. 提交更改：`git commit -m 'Add your feature'`
4. 推送分支：`git push origin feature/your-feature`
5. 创建 Pull Request

---

## 致谢

- 底盘代号映射数据参考 Wikipedia
- 飞书多维表格 API 文档
- lark-cli 工具

## 许可证

MIT License — 详见 [LICENSE](LICENSE)

---

> **作者**：SaturdayGo
> **行业**：汽车改装灯具（跨境电商）
> **联系方式**：GitHub Issues
