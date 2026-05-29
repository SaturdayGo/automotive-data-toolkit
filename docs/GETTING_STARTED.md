# 快速入门指南

## 前置条件

1. Python 3.10+
2. Node.js 16+（用于安装 lark-cli）
3. 飞书多维表格的访问权限

## 第一步：环境搭建

```bash
# 克隆项目
git clone https://github.com/SaturdayGo/automotive-data-toolkit.git
cd automotive-data-toolkit

# 创建虚拟环境（推荐）
python -m venv venv
source venv/bin/activate  # macOS/Linux
# 或 venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt

# 安装 lark-cli
npm install -g @anthropic-ai/lark-cli
```

## 第二步：飞书授权

```bash
# 登录飞书
lark-cli auth login

# 验证登录状态
lark-cli auth status
```

## 第三步：获取飞书表格信息

1. 打开你的飞书多维表格
2. 从 URL 中获取 `base_token` 和 `table_id`
   - URL 格式：`https://xxx.feishu.cn/base/XXX?table=YYY`
   - `XXX` = base_token
   - `YYY` = table_id

3. 获取字段 ID：
```bash
lark-cli base +field-list --base-token <你的base_token> --table-id <你的table_id>
```

## 第四步：配置文件

```bash
# 复制配置模板
cp examples/feishu-config-example.json my-config.json

# 编辑配置文件，填入你的信息
# 重点修改：base_token, table_id, field_mapping
```

## 第五步：测试连接

```bash
# 测试读取记录
lark-cli base +record-list --base-token <token> --table-id <table-id> --page-size 5
```

## 第六步：开始使用

### 示例 1：分类单条车型

```bash
cd skills/vehicle-classifier
python scripts/classify.py --input "宝马E90大灯4片"
```

### 示例 2：快速添加一条记录

```bash
cd skills/automotive-data-pipeline
python scripts/quick_add.py --config ../../my-config.json \
  --name "丰田 凌放XU60 2012-2019" \
  --size "64*57*20.5cm" \
  --weight "6.1kg"
```

### 示例 3：批量导入 Excel

```bash
cd skills/automotive-data-pipeline
python scripts/pipeline.py --input ../examples/sample-data.csv --config ../../my-config.json --full
```

---

## 常用命令速查

| 场景 | 命令 |
|------|------|
| 单条分类 | `python scripts/classify.py --input "车型名"` |
| 底盘查询 | `python scripts/classify.py --lookup E60` |
| 批量分类 | `python scripts/classify.py --input data.csv --output result.csv` |
| 快速添加 | `python scripts/quick_add.py --config config.json --name "车型名"` |
| 批量导入 | `python scripts/pipeline.py --input data.csv --config config.json --full` |
| 排序优化 | `python scripts/pipeline.py --config config.json --sort` |
| 去重预览 | `python scripts/dedup.py --config config.json --field 图片 --dry-run` |

---

## 下一步

- 阅读 [README.md](../README.md) 了解完整功能
- 查看 `references/` 目录了解底盘代号映射
- 运行测试验证环境：`python -m pytest skills/*/tests/ -v`
