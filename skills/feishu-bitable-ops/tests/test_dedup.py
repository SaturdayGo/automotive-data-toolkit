"""dedup.py 测试。"""

import json
import pytest
from unittest.mock import patch, mock_open, MagicMock


def test_dedup_init():
    """测试 Deduplicator 初始化。"""
    config = {"base_token": "test", "table_id": "test", "field_mapping": {"图片": "fld123"}}

    with patch("builtins.open", mock_open(read_data=json.dumps(config))):
        with patch("dedup.LarkWrapper") as MockWrapper:
            from dedup import Deduplicator
            dedup = Deduplicator("/fake/config.json")
            assert dedup.config == config


def test_find_duplicates_no_dupes():
    """测试无重复记录。"""
    config = {"base_token": "test", "table_id": "test", "field_mapping": {}}

    records = [
        {"record_id": "rec1", "fields": {"车型": "宝马E90"}},
        {"record_id": "rec2", "fields": {"车型": "丰田凯美瑞"}},
    ]

    with patch("builtins.open", mock_open(read_data=json.dumps(config))):
        with patch("dedup.LarkWrapper"):
            from dedup import Deduplicator
            dedup = Deduplicator("/fake/config.json")
            result = dedup.find_duplicates(records, "车型")

    assert len(result) == 0


def test_find_duplicates_with_dupes():
    """测试有重复记录。"""
    config = {"base_token": "test", "table_id": "test", "field_mapping": {}}

    records = [
        {"record_id": "rec1", "fields": {"车型": "宝马E90"}},
        {"record_id": "rec2", "fields": {"车型": "宝马E90"}},
        {"record_id": "rec3", "fields": {"车型": "丰田凯美瑞"}},
    ]

    with patch("builtins.open", mock_open(read_data=json.dumps(config))):
        with patch("dedup.LarkWrapper"):
            from dedup import Deduplicator
            dedup = Deduplicator("/fake/config.json")
            result = dedup.find_duplicates(records, "车型")

    assert len(result) == 1
    assert result[0]["value"] == "宝马E90"
    assert result[0]["keep"] == "rec1"
    assert result[0]["remove"] == ["rec2"]


def test_find_duplicates_with_attachment():
    """测试附件字段去重。"""
    config = {"base_token": "test", "table_id": "test", "field_mapping": {}}

    records = [
        {"record_id": "rec1", "fields": {"图片": [{"file_token": "tok123"}]}},
        {"record_id": "rec2", "fields": {"图片": [{"file_token": "tok123"}]}},
    ]

    with patch("builtins.open", mock_open(read_data=json.dumps(config))):
        with patch("dedup.LarkWrapper"):
            from dedup import Deduplicator
            dedup = Deduplicator("/fake/config.json")
            result = dedup.find_duplicates(records, "图片")

    assert len(result) == 1
    assert result[0]["value"] == "tok123"


def test_remove_duplicate_attachments_dry_run():
    """测试预览模式（不执行删除）。"""
    config = {"base_token": "test", "table_id": "test", "field_mapping": {"图片": "fld123"}}

    duplicates = [
        {"value": "tok123", "keep": "rec1", "remove": ["rec2"]}
    ]

    with patch("builtins.open", mock_open(read_data=json.dumps(config))):
        with patch("dedup.LarkWrapper") as MockWrapper:
            from dedup import Deduplicator
            dedup = Deduplicator("/fake/config.json")
            result = dedup.remove_duplicate_attachments(duplicates, "图片", dry_run=True)

    assert len(result) == 1
    assert result[0]["action"] == "would_remove"
    assert result[0]["record_id"] == "rec2"
    # dry_run 模式不应调用 API
    MockWrapper.return_value.run.assert_not_called()
