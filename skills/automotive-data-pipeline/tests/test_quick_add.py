"""quick_add.py 测试。"""

import json
import pytest
from unittest.mock import patch, mock_open, MagicMock
from pathlib import Path


def test_resolve_config_default_table(tmp_path):
    """测试默认表解析。"""
    tables = {
        "default": "灯具表",
        "tables": {
            "灯具表": "configs/灯具表.json",
            "配件表": "configs/配件表.json"
        }
    }
    tables_file = tmp_path / "tables.json"
    tables_file.write_text(json.dumps(tables, ensure_ascii=False), encoding="utf-8")

    config_dir = tmp_path / "configs"
    config_dir.mkdir()
    config_file = config_dir / "灯具表.json"
    config_file.write_text('{"base_token": "test", "table_id": "test"}', encoding="utf-8")

    import quick_add as qa
    with patch.object(qa, 'TABLES_REGISTRY', tables_file), \
         patch.object(qa, 'SKILL_DIR', tmp_path):
        result = qa.resolve_config()
        assert result == str(config_file)


def test_resolve_config_specific_table(tmp_path):
    """测试指定表名解析。"""
    tables = {
        "default": "灯具表",
        "tables": {
            "灯具表": "configs/灯具表.json",
            "配件表": "configs/配件表.json"
        }
    }
    tables_file = tmp_path / "tables.json"
    tables_file.write_text(json.dumps(tables, ensure_ascii=False), encoding="utf-8")

    config_dir = tmp_path / "configs"
    config_dir.mkdir()
    config_file = config_dir / "配件表.json"
    config_file.write_text('{"base_token": "test", "table_id": "test"}', encoding="utf-8")

    import quick_add as qa
    with patch.object(qa, 'TABLES_REGISTRY', tables_file), \
         patch.object(qa, 'SKILL_DIR', tmp_path):
        result = qa.resolve_config("配件表")
        assert result == str(config_file)


def test_resolve_config_unknown_table(tmp_path):
    """测试未知表名抛出异常。"""
    tables = {
        "default": "灯具表",
        "tables": {"灯具表": "configs/灯具表.json"}
    }
    tables_file = tmp_path / "tables.json"
    tables_file.write_text(json.dumps(tables, ensure_ascii=False), encoding="utf-8")

    import quick_add as qa
    with patch.object(qa, 'TABLES_REGISTRY', tables_file), \
         patch.object(qa, 'SKILL_DIR', tmp_path):
        with pytest.raises(ValueError, match="未找到表"):
            qa.resolve_config("不存在的表")


def test_resolve_config_missing_registry():
    """测试 tables.json 不存在时的回退逻辑。"""
    import quick_add as qa
    with patch.object(qa, 'TABLES_REGISTRY', Path("/nonexistent/tables.json")):
        with pytest.raises(FileNotFoundError):
            qa.resolve_config()


def test_list_tables(capsys, tmp_path):
    """测试列出已注册的表。"""
    tables = {
        "default": "灯具表",
        "tables": {
            "灯具表": "configs/灯具表.json",
            "配件表": "configs/配件表.json"
        }
    }
    tables_file = tmp_path / "tables.json"
    tables_file.write_text(json.dumps(tables, ensure_ascii=False), encoding="utf-8")

    import quick_add as qa
    with patch.object(qa, 'TABLES_REGISTRY', tables_file):
        qa.list_tables()

    captured = capsys.readouterr()
    assert "灯具表" in captured.out
    assert "配件表" in captured.out
    assert "(默认)" in captured.out


def test_build_record_fields():
    """测试记录构建包含所有字段。"""
    mock_result = [{"record_id": "rec123"}]

    with patch("classify.VehicleClassifier") as MockClassifier:
        MockClassifier.return_value.classify.return_value = {
            "brand": "丰田",
            "series": "丰田 凯美瑞",
            "model": "凯美瑞",
            "product_type": "尾灯",
            "year_range": None,
        }
        with patch("batch_ops.BatchOperator") as MockOperator:
            MockOperator.return_value.batch_create.return_value = mock_result
            from quick_add import quick_add
            result = quick_add(
                config_path="/fake/config.json",
                name="丰田凯美瑞尾灯",
                size="50*30*20cm",
                weight="5kg"
            )

    call_args = MockOperator.return_value.batch_create.call_args
    record = call_args[0][0][0]
    assert record["原始车型名"] == "丰田凯美瑞尾灯"
    assert record["尺寸"] == "50*30*20cm"
    assert record["重量"] == "5kg"
