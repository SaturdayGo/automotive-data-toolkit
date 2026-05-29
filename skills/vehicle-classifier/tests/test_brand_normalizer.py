import pytest
from brand_normalizer import BrandNormalizer


def test_normalize_variant_brands():
    normalizer = BrandNormalizer()
    assert normalizer.normalize("三菱系列") == "三菱"
    assert normalizer.normalize("丰田系列") == "丰田"
    assert normalizer.normalize("奥迪大灯") == "奥迪"
    assert normalizer.normalize("福特系列") == "福特"
    assert normalizer.normalize("铃木系列") == "铃木"


def test_normalize_standard_brands():
    normalizer = BrandNormalizer()
    assert normalizer.normalize("宝马") == "宝马"
    assert normalizer.normalize("奔驰") == "奔驰"
    assert normalizer.normalize("丰田") == "丰田"


def test_normalize_with_whitespace():
    normalizer = BrandNormalizer()
    assert normalizer.normalize("  宝马  ") == "宝马"


def test_extract_brand_from_model_name():
    normalizer = BrandNormalizer()
    assert normalizer.extract_brand("宝马E90大灯4片") == "宝马"
    assert normalizer.extract_brand("丰田 凌放XU60 2012-2019") == "丰田"
    assert normalizer.extract_brand("03-09款丰田超霸大灯") == "丰田"


def test_extract_brand_boundary_protection():
    """词边界保护：防止复合词误匹配。"""
    normalizer = BrandNormalizer()
    # "宝马仕"是复合词，不应匹配"宝马"
    assert normalizer.extract_brand("宝马仕大灯") is None
    # 正常品牌匹配不受影响
    assert normalizer.extract_brand("宝马E90大灯") == "宝马"
    assert normalizer.extract_brand("宝马X5尾灯") == "宝马"


def test_extract_brand_reverse_lookup():
    """反向查找：从车系名推断品牌。"""
    normalizer = BrandNormalizer()
    # "凯美瑞"不在 KNOWN_BRANDS 中，但 brand_series_map 有映射
    assert normalizer.extract_brand("凯美瑞大灯") == "丰田"
    assert normalizer.extract_brand("轩逸尾灯") == "日产"
    assert normalizer.extract_brand("途乐大灯") == "日产"


def test_extract_brand_none_input():
    """空字符串处理。"""
    normalizer = BrandNormalizer()
    assert normalizer.extract_brand("") is None
    assert normalizer.extract_brand("   ") is None


def test_extract_brand_english_only():
    """纯英文输入。"""
    normalizer = BrandNormalizer()
    # 英文品牌名不在中文品牌列表中
    assert normalizer.extract_brand("BMW E90 headlight") is None


def test_extract_brand_mixed_language():
    """混合语言输入。"""
    normalizer = BrandNormalizer()
    assert normalizer.extract_brand("BMW宝马E90大灯") == "宝马"
    assert normalizer.extract_brand("Toyota丰田凯美瑞") == "丰田"


def test_extract_brand_special_chars():
    """特殊字符输入。"""
    normalizer = BrandNormalizer()
    assert normalizer.extract_brand("宝马/E90/大灯") == "宝马"
    assert normalizer.extract_brand("丰田（凯美瑞）尾灯") == "丰田"
