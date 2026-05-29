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
