"""品牌归一化模块：将品牌变体映射到标准品牌名。"""

import json
import re
from pathlib import Path
from typing import Optional

from config_utils import load_brands, load_variant_map


class BrandNormalizer:
    """品牌归一化器。"""

    # 品牌变体 → 标准品牌名映射（从 assets/brands.json 加载，硬编码作为回退）
    VARIANT_MAP = load_variant_map() or {
        "三菱系列": "三菱",
        "丰田系列": "丰田",
        "奔驰系列": "奔驰",
        "奥迪大灯": "奥迪",
        "福特系列": "福特",
        "铃木系列": "铃木",
    }

    # 已知品牌列表（从 assets/brands.json 加载，硬编码作为回退）
    KNOWN_BRANDS = load_brands() or [
        "宝马", "奔驰", "奥迪", "丰田", "本田", "日产", "马自达",
        "福特", "现代", "雷克萨斯", "雪佛兰", "吉普", "路虎",
        "三菱", "铃木", "大众", "特斯拉", "凯迪拉克", "别克",
        "五菱", "道奇", "起亚", "坦克", "沃尔沃", "标致",
    ]

    def __init__(self):
        """初始化并加载 brand_series_map 和 mappings 用于反向查找。"""
        self._series_to_brand = {}
        mapping_path = Path(__file__).parent.parent / "assets" / "mapping-data.json"
        if mapping_path.exists():
            with open(mapping_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            # 从 brand_series_map 提取（如 "霸道"→"丰田"）
            for key, series in data.get("brand_series_map", {}).items():
                parts = series.split(" ", 1)
                if len(parts) == 2:
                    self._series_to_brand[key] = parts[0]
            # 从 mappings 提取中文车型名（如 "凯美瑞"→"丰田"）
            for brand, models in data.get("mappings", {}).items():
                for model_key, model_info in models.items():
                    if model_key not in self._series_to_brand:
                        # 只提取中文名称（非底盘代号）
                        if any('一' <= c <= '鿿' for c in model_key):
                            self._series_to_brand[model_key] = brand

    def normalize(self, brand: str) -> str:
        """归一化品牌名。

        Args:
            brand: 原始品牌名

        Returns:
            归一化后的品牌名
        """
        brand = brand.strip()
        return self.VARIANT_MAP.get(brand, brand)

    def extract_brand(self, model_name: str) -> Optional[str]:
        """从车型名中提取品牌。

        Args:
            model_name: 原始车型名（如"宝马E90大灯4片"）

        Returns:
            提取到的品牌名，未找到返回 None
        """
        model_name = model_name.strip()

        # 先检查变体
        for variant, standard in self.VARIANT_MAP.items():
            if variant in model_name:
                return standard

        # 再检查标准品牌（带词边界保护）
        # 只阻断已知的复合词误匹配（如"宝马仕"中的"仕"）
        _COMPOUND_CHARS = set('仕')
        for brand in self.KNOWN_BRANDS:
            if brand in model_name:
                idx = model_name.index(brand) + len(brand)
                if idx < len(model_name) and model_name[idx] in _COMPOUND_CHARS:
                    continue
                return brand

        # 最后从 brand_series_map 反向查找（如"凯美瑞"→"丰田"）
        for key, brand in self._series_to_brand.items():
            if key in model_name:
                return brand

        return None


if __name__ == "__main__":
    import sys
    normalizer = BrandNormalizer()
    if len(sys.argv) > 1:
        input_name = sys.argv[1]
        brand = normalizer.extract_brand(input_name)
        if brand:
            print(f"品牌: {brand}")
        else:
            print("未识别到品牌")
