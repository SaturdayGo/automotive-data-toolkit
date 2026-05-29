"""共享配置加载工具。"""

import json
from pathlib import Path
from typing import Any, Optional

ASSETS_DIR = Path(__file__).parent.parent / "assets"


def load_json_config(filename: str) -> dict:
    """从 assets 目录加载 JSON 配置文件。

    Args:
        filename: 文件名（如 "brands.json"）

    Returns:
        解析后的字典
    """
    path = ASSETS_DIR / filename
    if not path.exists():
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_brands() -> list:
    """加载品牌列表。"""
    data = load_json_config("brands.json")
    return data.get("brands", [])


def load_product_types() -> list:
    """加载产品类型列表。"""
    data = load_json_config("product-types.json")
    return data.get("product_types", [])


def load_variant_map() -> dict:
    """加载品牌变体映射。"""
    data = load_json_config("brands.json")
    return data.get("variant_map", {})
