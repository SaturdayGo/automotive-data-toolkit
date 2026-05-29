import pytest
from classify import VehicleClassifier


def test_classify_bmw_e90():
    classifier = VehicleClassifier(no_wikipedia=True)
    result = classifier.classify("宝马E90大灯4片")
    assert result["brand"] == "宝马"
    assert result["product_type"] == "大灯"
    # model 提取依赖品牌移除后的正则
    assert result["model"] is not None


def test_classify_toyota_camry():
    classifier = VehicleClassifier(no_wikipedia=True)
    result = classifier.classify("凯美瑞尾灯")
    # "凯美瑞" 本身不是品牌，需要包含品牌名
    # 这个测试验证分类器对无品牌前缀的处理
    assert result["product_type"] == "尾灯"


def test_classify_toyota_with_brand():
    classifier = VehicleClassifier(no_wikipedia=True)
    result = classifier.classify("丰田凯美瑞尾灯")
    assert result["brand"] == "丰田"
    assert result["product_type"] == "尾灯"


def test_classify_with_year_range():
    classifier = VehicleClassifier(no_wikipedia=True)
    result = classifier.classify("丰田 凌放XU60 2012-2019")
    assert result["brand"] == "丰田"
    assert result["year_range"] == "2012-2019"


def test_classify_nissan_sylphy():
    classifier = VehicleClassifier(no_wikipedia=True)
    result = classifier.classify("日产轩逸 14代 大灯")
    assert result["brand"] == "日产"
    assert result["product_type"] == "大灯"


def test_lookup_chassis_code():
    classifier = VehicleClassifier(no_wikipedia=True)
    result = classifier.lookup("E60")
    assert "series" in result
    assert "宝马" in result.get("series", "") or "5系" in result.get("series", "")


def test_classify_empty():
    classifier = VehicleClassifier(no_wikipedia=True)
    result = classifier.classify("")
    assert result["brand"] is None
    assert result["confidence"] == 0.0


def test_confidence_score():
    classifier = VehicleClassifier(no_wikipedia=True)
    result = classifier.classify("宝马E90大灯4片")
    assert 0.0 <= result["confidence"] <= 1.0


def test_classify_multiple_brands():
    """测试多种品牌识别。"""
    classifier = VehicleClassifier(no_wikipedia=True)

    test_cases = [
        ("宝马E90大灯", "宝马"),
        ("奔驰W204尾灯", "奔驰"),
        ("丰田LC76大灯", "丰田"),
        ("日产途乐Y61尾灯", "日产"),
        ("路虎揽运大灯", "路虎"),
    ]

    for name, expected_brand in test_cases:
        result = classifier.classify(name)
        assert result["brand"] == expected_brand, f"Failed for {name}: expected {expected_brand}, got {result['brand']}"


def test_classify_none_input():
    """None 或空输入处理。"""
    classifier = VehicleClassifier(no_wikipedia=True)
    result = classifier.classify("")
    assert result["brand"] is None
    assert result["confidence"] == 0.0


def test_classify_generation_map():
    """代数映射测试（14代→年款）。"""
    classifier = VehicleClassifier(no_wikipedia=True)
    result = classifier.classify("日产轩逸 14代 大灯")
    assert result["brand"] == "日产"
    assert result["year_range"] == "2019-2025"
    assert result["product_type"] == "大灯"


def test_classify_reverse_lookup_brand():
    """反向查找品牌（凯美瑞→丰田）。"""
    classifier = VehicleClassifier(no_wikipedia=True)
    result = classifier.classify("凯美瑞尾灯")
    assert result["brand"] == "丰田"
    assert result["product_type"] == "尾灯"


def test_confidence_with_mapping_hit():
    """映射表命中时置信度更高。"""
    classifier = VehicleClassifier(no_wikipedia=True)
    # 有映射表命中的分类
    result_mapped = classifier.classify("宝马E90大灯")
    # 无品牌的分类
    result_no_brand = classifier.classify("大灯")
    assert result_mapped["confidence"] > result_no_brand["confidence"]
