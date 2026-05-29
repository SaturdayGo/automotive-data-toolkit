"""pipeline.py 测试。"""

import json
import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path


def test_pipeline_init_with_config(tmp_path):
    """测试 Pipeline 初始化带配置文件。"""
    config = {"base_token": "test", "table_id": "test"}
    config_file = tmp_path / "config.json"
    config_file.write_text(json.dumps(config), encoding="utf-8")

    from pipeline import Pipeline
    p = Pipeline(str(config_file))
    assert p.config == config


def test_pipeline_init_without_config():
    """测试 Pipeline 初始化不带配置文件。"""
    from pipeline import Pipeline
    p = Pipeline()
    assert p.config is None


def test_classify_input_csv(tmp_path):
    """测试 CSV 分类输入。"""
    csv_file = tmp_path / "test.csv"
    csv_file.write_text("车型名\n宝马E90大灯\n丰田凯美瑞尾灯\n", encoding="utf-8-sig")

    from pipeline import Pipeline
    p = Pipeline()

    with patch("classify.VehicleClassifier") as MockClassifier:
        MockClassifier.return_value.classify.return_value = {
            "brand": "宝马", "series": None, "model": "E90",
            "product_type": "大灯", "year_range": None,
            "wikipedia_verified": False, "confidence": 0.5
        }
        results = p.classify_input(str(csv_file))

    assert len(results) == 2
    assert results[0]["brand"] == "宝马"


def test_classify_input_empty_csv(tmp_path):
    """测试空 CSV 文件。"""
    csv_file = tmp_path / "empty.csv"
    csv_file.write_text("车型名\n", encoding="utf-8-sig")

    from pipeline import Pipeline
    p = Pipeline()
    results = p.classify_input(str(csv_file))
    assert len(results) == 0


def test_classify_input_output(tmp_path):
    """测试分类结果输出到文件。"""
    csv_file = tmp_path / "test.csv"
    csv_file.write_text("车型名\n宝马E90大灯\n", encoding="utf-8-sig")
    output_file = tmp_path / "output.csv"

    from pipeline import Pipeline
    p = Pipeline()

    with patch("classify.VehicleClassifier") as MockClassifier:
        MockClassifier.return_value.classify.return_value = {
            "brand": "宝马", "series": None, "model": "E90",
            "product_type": "大灯", "year_range": None,
            "wikipedia_verified": False, "confidence": 0.5
        }
        p.classify_input(str(csv_file), str(output_file))

    assert output_file.exists()
    content = output_file.read_text(encoding="utf-8-sig")
    assert "宝马" in content
