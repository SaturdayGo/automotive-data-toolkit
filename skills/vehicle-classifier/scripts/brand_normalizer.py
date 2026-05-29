"""品牌归一化模块：将品牌变体映射到标准品牌名。"""

import re
from typing import Optional


class BrandNormalizer:
    """品牌归一化器。"""

    # 品牌变体 → 标准品牌名映射
    VARIANT_MAP = {
        "三菱系列": "三菱",
        "丰田系列": "丰田",
        "奔驰系列": "奔驰",
        "奥迪大灯": "奥迪",
        "福特系列": "福特",
        "铃木系列": "铃木",
    }

    # 已知品牌列表（用于从车型名中提取品牌）
    KNOWN_BRANDS = [
        "宝马", "奔驰", "奥迪", "丰田", "本田", "日产", "马自达",
        "福特", "现代", "雷克萨斯", "雪佛兰", "吉普", "路虎",
        "三菱", "铃木", "大众", "特斯拉", "凯迪拉克", "别克",
        "五菱", "道奇", "起亚", "坦克", "沃尔沃", "标致",
    ]

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

        # 再检查标准品牌
        for brand in self.KNOWN_BRANDS:
            if brand in model_name:
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
