"""测试 lark_wrapper.py。"""

import json
import pytest
from unittest.mock import patch, MagicMock

from lark_wrapper import LarkWrapper


class TestLarkWrapper:
    """测试 LarkWrapper。"""

    @patch("subprocess.run")
    def test_find_lark_cli(self, mock_run):
        """测试查找 lark-cli。"""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="/usr/local/bin/lark-cli\n"
        )
        with patch("os.path.exists", return_value=False):
            wrapper = LarkWrapper()
            assert wrapper.cli_path == "/usr/local/bin/lark-cli"

    @patch("os.path.exists")
    def test_init_with_default_path(self, mock_exists):
        """测试默认路径初始化。"""
        mock_exists.return_value = True
        wrapper = LarkWrapper()
        assert wrapper.cli_path == "/Users/aiden/.npm-global/bin/lark-cli"

    @patch("os.path.exists")
    def test_init_file_not_found(self, mock_exists):
        """测试找不到 lark-cli。"""
        mock_exists.return_value = False
        with patch("subprocess.run", return_value=MagicMock(returncode=1, stdout="")):
            with pytest.raises(FileNotFoundError):
                LarkWrapper()

    @patch("os.path.exists")
    @patch("subprocess.run")
    def test_run_success(self, mock_run, mock_exists):
        """测试成功执行。"""
        mock_exists.return_value = True
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout='{"items": []}'
        )
        wrapper = LarkWrapper()
        result = wrapper.run("base +record-list", ["--base-token", "test"])
        assert result == {"items": []}

    @patch("os.path.exists")
    @patch("subprocess.run")
    def test_run_with_stderr(self, mock_run, mock_exists):
        """测试 stderr 警告处理。"""
        mock_exists.return_value = True
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout='{"items": []}',
            stderr="proxy warning"
        )
        wrapper = LarkWrapper()
        result = wrapper.run("base +record-list", ["--base-token", "test"])
        assert result == {"items": []}

    @patch("os.path.exists")
    @patch("subprocess.run")
    def test_run_json_parse_returns_raw(self, mock_run, mock_exists):
        """测试非 JSON 输出返回 raw。"""
        mock_exists.return_value = True
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="not json"
        )
        wrapper = LarkWrapper()
        result = wrapper.run("base +record-list", ["--base-token", "test"])
        assert "raw" in result
        assert result["raw"] == "not json"

    @patch("os.path.exists")
    @patch("subprocess.run")
    def test_run_timeout_retry(self, mock_run, mock_exists):
        """测试超时重试。"""
        import subprocess
        mock_exists.return_value = True
        mock_run.side_effect = [
            subprocess.TimeoutExpired(cmd="test", timeout=60),
            MagicMock(returncode=0, stdout='{"items": []}')
        ]
        wrapper = LarkWrapper()
        result = wrapper.run("base +record-list", ["--base-token", "test"])
        assert result == {"items": []}
        assert mock_run.call_count == 2

    @patch("os.path.exists")
    @patch("subprocess.run")
    def test_batch_create(self, mock_run, mock_exists):
        """测试批量创建。"""
        mock_exists.return_value = True
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout='{"records": []}'
        )
        wrapper = LarkWrapper()
        records = [{"fields": {"name": "test"}}]
        result = wrapper.batch_create("token", "table", records)
        assert len(result) == 1
        assert result[0] == {"records": []}

    @patch("os.path.exists")
    @patch("subprocess.run")
    def test_batch_update(self, mock_run, mock_exists):
        """测试批量更新。"""
        mock_exists.return_value = True
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout='{"records": []}'
        )
        wrapper = LarkWrapper()
        record_ids = ["id1", "id2"]
        patch_data = {"fields": {"name": "updated"}}
        result = wrapper.batch_update("token", "table", record_ids, patch_data)
        assert len(result) == 1

    @patch("os.path.exists")
    def test_clean_records(self, mock_exists):
        """测试清理记录。"""
        mock_exists.return_value = True
        wrapper = LarkWrapper()
        records = [
            {"name": "test", "value": None, "empty": "", "valid": 0},
            {"all_none": None, "also_none": None}
        ]
        cleaned = wrapper._clean_records(records)
        assert len(cleaned) == 1
        assert cleaned[0]["name"] == "test"
        assert cleaned[0]["valid"] == 0
        assert "value" not in cleaned[0]
        assert "empty" not in cleaned[0]
