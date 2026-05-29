# lark-cli 命令速查

## 认证

```bash
lark-cli auth status          # 查看认证状态
lark-cli auth login           # 登录
lark-cli auth logout          # 登出
```

## Bitable 操作

### 记录操作

```bash
# 列出记录
lark-cli base +record-list --base-token <token> --table-id <table-id> --page-size 100

# 批量创建
lark-cli base +record-batch-create --base-token <token> --table-id <table-id> --json '{"records": [...]}'

# 批量更新
lark-cli base +record-batch-update --base-token <token> --table-id <table-id> --json '{"record_id_list": [...], "patch": {...}}'

# 删除附件
lark-cli base +record-remove-attachment --base-token <token> --table-id <table-id> --record-id <id> --field-id <field-id> --file-token <token> --yes
```

### 字段操作

```bash
# 列出字段
lark-cli base +field-list --base-token <token> --table-id <table-id>

# 创建字段
lark-cli base +field-create --base-token <token> --table-id <table-id> --json '{...}'

# 更新字段
lark-cli base +field-update --base-token <token> --table-id <table-id> --field-id <id> --json '{...}'
```

### 视图操作

```bash
# 列出视图
lark-cli base +view-list --base-token <token> --table-id <table-id>

# 设置排序
lark-cli base +view-set-sort --base-token <token> --table-id <table-id> --json '{"sort": [...]}'

# 设置分组
lark-cli base +view-set-group --base-token <token> --table-id <table-id> --json '{"group": [...]}'

# 设置可见字段
lark-cli base +view-set-visible-fields --base-token <token> --table-id <table-id> --json '{"visible_field_ids": [...]}'
```

### 附件操作

```bash
# 上传附件
lark-cli base +record-upload-attachment --base-token <token> --table-id <table-id> --record-id <id> --field-id <field-id> --file <path>
```

## 常见问题

### 1. proxy 警告

lark-cli 会输出 proxy 警告到 stdout，影响 JSON 解析。解决方法：
```bash
lark-cli base +record-list ... 2>/dev/null
```

### 2. 批量操作限制

每批最多 500 条记录，超过需要分批处理。

### 3. JSON 格式

`--json` 参数需要是有效的 JSON 字符串，注意转义。
