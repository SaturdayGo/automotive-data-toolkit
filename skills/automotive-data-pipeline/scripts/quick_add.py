"""快速添加单条记录到飞书。"""

import json
import argparse
import sys
from pathlib import Path
from typing import Dict, Optional


def quick_add(config_path: str, name: str, size: str = None, weight: str = None,
              brand: str = None, series: str = None, model: str = None,
              product_type: str = None, year_range: str = None,
              supplier: str = None, notes: str = None) -> Dict:
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
        sys.path.insert(0, str(Path(__file__).parent))
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
    sys.path.insert(0, str(Path(__file__).parent))
    from batch_ops import BatchOperator
    operator = BatchOperator(config_path)

    return operator.batch_create([record])


def main():
    parser = argparse.ArgumentParser(description="快速添加单条记录到飞书")
    parser.add_argument("--config", "-c", required=True, help="飞书配置文件路径")
    parser.add_argument("--name", "-n", required=True, help="原始车型名")
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

    result = quick_add(
        config_path=args.config,
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
