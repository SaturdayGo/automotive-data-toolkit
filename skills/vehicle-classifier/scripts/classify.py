"""主分类脚本：将原始车型名转换为结构化分类。"""

import re
import json
import sys
import argparse
import csv
from typing import Dict, Any, Optional, List

from brand_normalizer import BrandNormalizer
from wikipedia_verifier import WikipediaVerifier


class VehicleClassifier:
    """车辆分类器。"""

    # 产品类型关键词
    PRODUCT_TYPES = [
        "大灯", "尾灯", "贯穿灯", "雾灯", "转向灯", "刹车灯",
        "后杠灯", "叶子板灯", "日行灯", "示宽灯", "倒车灯",
        "前杠灯", "后尾灯", "前大灯", "LED灯", "激光大灯",
    ]

    # 代数映射（日产轩逸等）
    GENERATION_MAP = {
        "轩逸": {
            "14代": {"code": "B18", "years": "2019-2025"},
            "13代": {"code": "B17", "years": "2012-2019"},
        },
        "雅阁": {
            "11代": {"years": "2023-present"},
            "10代": {"years": "2017-2022"},
            "9代": {"years": "2012-2017"},
        },
    }

    def __init__(self, no_wikipedia: bool = False):
        """初始化分类器。

        Args:
            no_wikipedia: 是否跳过 Wikipedia 验证
        """
        self.normalizer = BrandNormalizer()
        self.verifier = WikipediaVerifier()
        self.no_wikipedia = no_wikipedia

    def classify(self, model_name: str) -> Dict[str, Any]:
        """分类车型名。

        Args:
            model_name: 原始车型名

        Returns:
            结构化分类结果
        """
        result = {
            "brand": None,
            "series": None,
            "model": None,
            "product_type": None,
            "year_range": None,
            "wikipedia_verified": False,
            "confidence": 0.0,
        }

        # 1. 提取品牌
        brand = self.normalizer.extract_brand(model_name)
        result["brand"] = brand

        # 2. 提取产品类型
        product_type = self._extract_product_type(model_name)
        result["product_type"] = product_type

        # 3. 提取年款
        year_range = self._extract_year_range(model_name)
        result["year_range"] = year_range

        # 4. 提取核心车型
        model = self._extract_model(model_name, brand)
        result["model"] = model

        # 5. 推断车系
        if brand and model:
            series = self._infer_series(brand, model, model_name)
            result["series"] = series

        # 6. 计算置信度
        result["confidence"] = self._calculate_confidence(result)

        return result

    def _extract_product_type(self, model_name: str) -> Optional[str]:
        """提取产品类型。"""
        for ptype in self.PRODUCT_TYPES:
            if ptype in model_name:
                return ptype
        return None

    def _extract_year_range(self, model_name: str) -> Optional[str]:
        """提取年款范围。"""
        # 匹配 "2012-2019" 或 "2012-2019" 格式
        match = re.search(r'(\d{4})\s*[-–~]\s*(\d{4})', model_name)
        if match:
            return f"{match.group(1)}-{match.group(2)}"

        # 匹配 "03-09款" 格式
        match = re.search(r'(\d{2})\s*[-–]\s*(\d{2})款', model_name)
        if match:
            start = int(match.group(1))
            end = int(match.group(2))
            if start < 50:
                start += 2000
            else:
                start += 1900
            if end < 50:
                end += 2000
            else:
                end += 1900
            return f"{start}-{end}"

        return None

    def _extract_model(self, model_name: str, brand: Optional[str]) -> Optional[str]:
        """提取核心车型。"""
        if not brand:
            return None

        # 移除品牌名
        cleaned = model_name.replace(brand, "").strip()

        # 移除产品类型
        for ptype in self.PRODUCT_TYPES:
            cleaned = cleaned.replace(ptype, "").strip()

        # 移除年款
        cleaned = re.sub(r'\d{4}\s*[-–~]\s*\d{4}', '', cleaned).strip()
        cleaned = re.sub(r'\d{2}\s*[-–]\s*\d{2}款', '', cleaned).strip()

        # 移除数量词
        cleaned = re.sub(r'\d+\s*片', '', cleaned).strip()

        # 移除"款"字
        cleaned = re.sub(r'^款', '', cleaned).strip()

        return cleaned if cleaned else None

    def _infer_series(self, brand: str, model: str, full_name: str) -> Optional[str]:
        """推断车系。"""
        # 1. 先查品牌系列映射表
        series_map = self.verifier.data.get("brand_series_map", {})
        for key, series in series_map.items():
            if key in full_name or key in model:
                return series

        # 2. 查底盘代号映射
        if not self.no_wikipedia:
            verification = self.verifier.verify(brand, model)
            if verification["verified"]:
                return verification["series"]

        # 3. 直接用品牌+车型
        return f"{brand} {model}"

    def _calculate_confidence(self, result: Dict[str, Any]) -> float:
        """计算置信度。"""
        score = 0.0
        if result["brand"]:
            score += 0.3
        if result["series"]:
            score += 0.3
        if result["model"]:
            score += 0.2
        if result["product_type"]:
            score += 0.1
        if result["year_range"]:
            score += 0.1
        return round(score, 2)

    def lookup(self, chassis_code: str) -> Dict[str, Any]:
        """查询底盘代号。"""
        # 遍历所有品牌查找
        for brand, mappings in self.verifier.mappings.items():
            if chassis_code in mappings:
                data = mappings[chassis_code]
                return {
                    "brand": brand,
                    "series": data["series"],
                    "market_name": data["market_name"],
                    "years": data["years"],
                    "body": data["body"],
                }
        return {"error": f"未找到底盘代号: {chassis_code}"}


def main():
    parser = argparse.ArgumentParser(description="汽车车型分类器")
    parser.add_argument("--input", "-i", help="输入文件（CSV）或车型名")
    parser.add_argument("--output", "-o", help="输出文件（CSV）")
    parser.add_argument("--lookup", "-l", help="查询底盘代号")
    parser.add_argument("--no-wikipedia", action="store_true", help="跳过 Wikipedia 验证")

    args = parser.parse_args()

    classifier = VehicleClassifier(no_wikipedia=args.no_wikipedia)

    if args.lookup:
        result = classifier.lookup(args.lookup)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return

    if args.input:
        # 判断是文件还是车型名
        if args.input.endswith(".csv"):
            # 批量处理
            results = []
            with open(args.input, "r", encoding="utf-8-sig") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    model_name = row.get("车型", row.get("model_name", ""))
                    if model_name:
                        result = classifier.classify(model_name)
                        results.append(result)

            if args.output:
                with open(args.output, "w", encoding="utf-8-sig", newline="") as f:
                    writer = csv.DictWriter(f, fieldnames=results[0].keys())
                    writer.writeheader()
                    writer.writerows(results)
                print(f"已处理 {len(results)} 条记录，输出到 {args.output}")
            else:
                print(json.dumps(results, ensure_ascii=False, indent=2))
        else:
            # 单条处理
            result = classifier.classify(args.input)
            print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
