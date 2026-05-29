"""测试 batch_ops.py。"""

import json
import pytest
from unittest.mock import patch, MagicMock

from batch_ops import BatchOperator


class TestBatchOperator:
    """测试 BatchOperator。"""

    def test_init(self, tmp_path):
        """测试初始化。"""
        config = {
            "base_token": "test_token",
            "table_id": "test_table",
            "field_mapping": {"name": "fld1"}
        }
        config_path = tmp_path / "config.json"
        config_path.write_text(json.dumps(config))

        with patch("lark_wrapper.os.path.exists", return_value=True):
            operator = BatchOperator(str(config_path))
            assert operator.config == config

    @patch("lark_wrapper.os.path.exists", return_value=True)
    @patch("lark_wrapper.subprocess.run")
    def test_create(self, mock_run, mock_exists, tmp_path):
        """测试批量创建。"""
        config = {
            "base_token": "test_token",
            "table_id": "test_table",
            "field_mapping": {"name": "fld1"}
        }
        config_path = tmp_path / "config.json"
        config_path.write_text(json.dumps(config))

        mock_run.return_value = MagicMock(
            returncode=0,
            stdout='{"records": []}'
        )

        # 创建数据文件
        data = [{"name": "test1"}, {"name": "test2"}]
        data_path = tmp_path / "data.json"
        data_path.write_text(json.dumps(data))

        operator = BatchOperator(str(config_path))
        result = operator.create(str(data_path))

        mock_run.assert_called_once()
        assert len(result) == 1

    @patch("lark_wrapper.os.path.exists", return_value=True)
    @patch("lark_wrapper.subprocess.run")
    def test_update(self, mock_run, mock_exists, tmp_path):
        """测试批量更新。"""
        config = {
            "base_token": "test_token",
            "table_id": "test_table",
            "field_mapping": {"name": "fld1"}
        }
        config_path = tmp_path / "config.json"
        config_path.write_text(json.dumps(config))

        mock_run.return_value = MagicMock(
            returncode=0,
            stdout='{"records": []}'
        )

        # 创建数据文件
        data = [{"record_id": "rec1", "name": "updated"}]
        data_path = tmp_path / "data.json"
        data_path.write_text(json.dumps(data))

        operator = BatchOperator(str(config_path))
        result = operator.update(str(data_path))

        mock_run.assert_called_once()

    @patch("lark_wrapper.os.path.exists", return_value=True)
    @patch("lark_wrapper.subprocess.run")
    def test_remove_attachment(self, mock_run, mock_exists, tmp_path):
        """测试删除附件。"""
        config = {
            "base_token": "test_token",
            "table_id": "test_table",
            "field_mapping": {"图片": "fld1"}
        }
        config_path = tmp_path / "config.json"
        config_path.write_text(json.dumps(config))

        mock_run.return_value = MagicMock(
            returncode=0,
            stdout='{}'
        )

        operator = BatchOperator(str(config_path))
        result = operator.remove_attachment("rec1", "fld1", "tok123")

        mock_run.assert_called_once()
