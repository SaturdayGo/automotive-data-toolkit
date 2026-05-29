"""测试 view_config.py。"""

import json
import pytest
from unittest.mock import patch, MagicMock

from view_config import ViewConfigurator


class TestViewConfigurator:
    """测试 ViewConfigurator。"""

    @patch("lark_wrapper.os.path.exists", return_value=True)
    def test_init(self, mock_exists, tmp_path):
        """测试初始化。"""
        config = {
            "base_token": "test_token",
            "table_id": "test_table",
            "field_mapping": {"车系": "fld1", "核心车型": "fld2"}
        }
        config_path = tmp_path / "config.json"
        config_path.write_text(json.dumps(config))

        configurator = ViewConfigurator(str(config_path))
        assert configurator.config == config

    @patch("lark_wrapper.os.path.exists", return_value=True)
    @patch("lark_wrapper.subprocess.run")
    def test_set_sort(self, mock_run, mock_exists, tmp_path):
        """测试设置排序。"""
        config = {
            "base_token": "test_token",
            "table_id": "test_table",
            "field_mapping": {"车系": "fld1", "核心车型": "fld2"}
        }
        config_path = tmp_path / "config.json"
        config_path.write_text(json.dumps(config))

        mock_run.return_value = MagicMock(
            returncode=0,
            stdout='{}'
        )

        configurator = ViewConfigurator(str(config_path))
        sort_config = [
            {"field": "车系", "order": "asc"},
            {"field": "核心车型", "order": "desc"}
        ]
        result = configurator.set_sort(sort_config)

        mock_run.assert_called_once()
        # 验证传递的 JSON 参数
        call_args = mock_run.call_args
        cmd = call_args[0][0]
        assert "view-set-sort" in " ".join(cmd)

    @patch("lark_wrapper.os.path.exists", return_value=True)
    @patch("lark_wrapper.subprocess.run")
    def test_set_group(self, mock_run, mock_exists, tmp_path):
        """测试设置分组。"""
        config = {
            "base_token": "test_token",
            "table_id": "test_table",
            "field_mapping": {"车系": "fld1"}
        }
        config_path = tmp_path / "config.json"
        config_path.write_text(json.dumps(config))

        mock_run.return_value = MagicMock(
            returncode=0,
            stdout='{}'
        )

        configurator = ViewConfigurator(str(config_path))
        group_config = [{"field": "车系", "order": "asc"}]
        result = configurator.set_group(group_config)

        mock_run.assert_called_once()

    @patch("lark_wrapper.os.path.exists", return_value=True)
    @patch("lark_wrapper.subprocess.run")
    def test_set_visible_fields(self, mock_run, mock_exists, tmp_path):
        """测试设置可见字段。"""
        config = {
            "base_token": "test_token",
            "table_id": "test_table",
            "field_mapping": {"车系": "fld1", "核心车型": "fld2", "图片": "fld3"}
        }
        config_path = tmp_path / "config.json"
        config_path.write_text(json.dumps(config))

        mock_run.return_value = MagicMock(
            returncode=0,
            stdout='{}'
        )

        configurator = ViewConfigurator(str(config_path))
        fields = ["车系", "核心车型", "图片"]
        result = configurator.set_visible_fields(fields)

        mock_run.assert_called_once()

    @patch("lark_wrapper.os.path.exists", return_value=True)
    @patch("lark_wrapper.subprocess.run")
    def test_set_sort_with_view_id(self, mock_run, mock_exists, tmp_path):
        """测试带视图 ID 的排序。"""
        config = {
            "base_token": "test_token",
            "table_id": "test_table",
            "field_mapping": {"车系": "fld1"}
        }
        config_path = tmp_path / "config.json"
        config_path.write_text(json.dumps(config))

        mock_run.return_value = MagicMock(
            returncode=0,
            stdout='{}'
        )

        configurator = ViewConfigurator(str(config_path))
        sort_config = [{"field": "车系", "order": "asc"}]
        result = configurator.set_sort(sort_config, view_id="view123")

        mock_run.assert_called_once()
        call_args = mock_run.call_args
        cmd = call_args[0][0]
        assert "view-set-sort" in " ".join(cmd)
