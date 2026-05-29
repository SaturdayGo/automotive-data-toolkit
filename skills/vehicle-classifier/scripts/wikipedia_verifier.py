"""Wikipedia 验证模块：验证底盘代号映射的准确性。"""

import json
import os
from typing import Optional, Dict, Any


class WikipediaVerifier:
    """Wikipedia 验证器。"""

    def __init__(self, mapping_path: Optional[str] = None):
        """初始化验证器。

        Args:
            mapping_path: mapping-data.json 的路径，默认为 assets/mapping-data.json
        """
        if mapping_path is None:
            mapping_path = os.path.join(os.path.dirname(__file__), "..", "assets", "mapping-data.json")
        with open(mapping_path, "r", encoding="utf-8") as f:
            self.data = json.load(f)
        self.mappings = self.data.get("mappings", {})

    def verify(self, brand: str, chassis_code: str) -> Dict[str, Any]:
        """验证底盘代号。

        Args:
            brand: 品牌名
            chassis_code: 底盘代号

        Returns:
            验证结果，包含 verified, series, years, body 等字段
        """
        # 先查本地缓存
        cached = self.get_cached(brand, chassis_code)
        if cached:
            return {
                "verified": True,
                "source": "local_cache",
                **cached
            }

        # 本地未找到，返回未验证
        return {
            "verified": False,
            "source": "not_found",
            "series": None,
            "years": None,
            "body": None
        }

    def get_cached(self, brand: str, chassis_code: str) -> Optional[Dict[str, str]]:
        """从本地缓存获取映射。

        Args:
            brand: 品牌名
            chassis_code: 底盘代号

        Returns:
            映射数据，未找到返回 None
        """
        brand_mappings = self.mappings.get(brand, {})
        return brand_mappings.get(chassis_code)

    def get_all_for_brand(self, brand: str) -> Dict[str, Dict[str, str]]:
        """获取品牌的所有映射。

        Args:
            brand: 品牌名

        Returns:
            该品牌的所有底盘代号映射
        """
        return self.mappings.get(brand, {})


if __name__ == "__main__":
    import sys
    verifier = WikipediaVerifier()
    if len(sys.argv) >= 3:
        brand = sys.argv[1]
        code = sys.argv[2]
        result = verifier.verify(brand, code)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print("用法: python wikipedia_verifier.py <品牌> <底盘代号>")
