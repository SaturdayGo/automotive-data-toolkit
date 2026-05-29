"""快速添加单条记录到飞书。"""

import json
import argparse
import sys
from pathlib import Path
from typing import Dict, List, Optional

SCRIPT_DIR = Path(__file__).parent
SKILL_DIR = SCRIPT_DIR.parent
TABLES_REGISTRY = SKILL_DIR / "tables.json"


def resolve_config(table_name: str = None) -> str:
    """根据表名解析配置文件路径。

    Args:
        table_name: 表名（如 "灯具表"），为 None 时使用默认表

    Returns:
        配置文件绝对路径
    """
    if not TABLES_REGISTRY.exists():
        # 回退到旧的 my-config.json
        fallback = SKILL_DIR / "my-config.json"
        if fallback.exists():
            return str(fallback)
        raise FileNotFoundError(f"找不到 tables.json 和 my-config.json")

    with open(TABLES_REGISTRY, "r", encoding="utf-8") as f:
        registry = json.load(f)

    tables = registry.get("tables", {})

    if table_name:
        if table_name not in tables:
            available = ", ".join(tables.keys())
            raise ValueError(f"未找到表 '{table_name}'，可用的表：{available}")
        config_file = tables[table_name]
    else:
        default_name = registry.get("default")
        if not default_name or default_name not in tables:
            raise ValueError("未配置默认表，请在 tables.json 中设置 default")
        config_file = tables[default_name]

    config_path = SKILL_DIR / config_file
    if not config_path.exists():
        raise FileNotFoundError(f"配置文件不存在：{config_path}")

    return str(config_path)


def list_tables() -> None:
    """列出所有已注册的表。"""
    if not TABLES_REGISTRY.exists():
        print("未找到 tables.json")
        return

    with open(TABLES_REGISTRY, "r", encoding="utf-8") as f:
        registry = json.load(f)

    default = registry.get("default", "")
    tables = registry.get("tables", {})

    print("已注册的表：")
    for name, config in tables.items():
        marker = " (默认)" if name == default else ""
        print(f"  - {name}{marker}: {config}")


def quick_add(config_path: str, name: str, size: str = None, weight: str = None,
              brand: str = None, series: str = None, model: str = None,
              product_type: str = None, year_range: str = None,
              supplier: str = None, notes: str = None) -> List[Dict]:
    """快速添加单条记录。

    Args:
        config_path: 飞书配置文件路径
        name: 原始车型名
        size: 尺寸
        weight: 重量
        brand: 品牌
        series: 车系
        model: 核心车型
        product_type: 产品类型
        year_range: 年款
        supplier: 供应商
        notes: 备注

    Returns:
        添加结果
    """
    # 如果没有指定分类信息，尝试自动分类
    if not all([brand, series, model, product_type]):
        sys.path.insert(0, str(SCRIPT_DIR))
        from classify import VehicleClassifier
        classifier = VehicleClassifier()
        result = classifier.classify(name)
        brand = brand or result.get("brand")
        series = series or result.get("series")
        model = model or result.get("model")
        product_type = product_type or result.get("product_type")
        year_range = year_range or result.get("year_range")

    # 构建记录
    record = {
        "原始车型名": name,
        "核心车型": model,
        "车系": series,
        "产品类型": product_type,
        "年款": year_range,
    }

    if size:
        record["尺寸"] = size
    if weight:
        record["重量"] = weight
    if supplier:
        record["供应商/来源"] = supplier
    if notes:
        record["备注"] = notes

    # 调用批量操作
    sys.path.insert(0, str(SCRIPT_DIR))
    from batch_ops import BatchOperator
    operator = BatchOperator(config_path)

    return operator.batch_create([record])


def main():
    parser = argparse.ArgumentParser(description="快速添加单条记录到飞书")
    parser.add_argument("--table", "-t", help="目标表名（如 '灯具表'），不指定则用默认表")
    parser.add_argument("--config", "-c", help="直接指定配置文件路径（优先于 --table）")
    parser.add_argument("--list-tables", "-l", action="store_true", help="列出所有已注册的表")
    parser.add_argument("--name", "-n", required=False, help="原始车型名")
    parser.add_argument("--size", "-s", help="尺寸")
    parser.add_argument("--weight", "-w", help="重量")
    parser.add_argument("--brand", help="品牌")
    parser.add_argument("--series", help="车系")
    parser.add_argument("--model", help="核心车型")
    parser.add_argument("--product-type", help="产品类型")
    parser.add_argument("--year-range", help="年款")
    parser.add_argument("--supplier", help="供应商")
    parser.add_argument("--notes", help="备注")

    args = parser.parse_args()

    # 列出表
    if args.list_tables:
        list_tables()
        return

    if not args.name:
        parser.error("需要 --name 参数")

    # 解析配置路径
    if args.config:
        config_path = args.config
    else:
        try:
            config_path = resolve_config(args.table)
        except (FileNotFoundError, ValueError) as e:
            print(f"错误: {e}")
            return

    result = quick_add(
        config_path=config_path,
        name=args.name,
        size=args.size,
        weight=args.weight,
        brand=args.brand,
        series=args.series,
        model=args.model,
        product_type=args.product_type,
        year_range=args.year_range,
        supplier=args.supplier,
        notes=args.notes
    )

    print("添加完成:")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
