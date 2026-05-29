"""lark-cli 封装层：统一处理路径、参数、错误、重试。"""

import subprocess
import json
import os
import time
from typing import Dict, Any, Optional, List


class LarkWrapper:
    """lark-cli 封装器。"""

    def __init__(self, cli_path: Optional[str] = None):
        self.cli_path = cli_path or self._find_lark_cli()
        if not self.cli_path:
            raise FileNotFoundError("lark-cli not found")

    def _find_lark_cli(self) -> Optional[str]:
        """查找 lark-cli 路径。"""
        # 常见路径
        paths = [
            "/Users/aiden/.npm-global/bin/lark-cli",
            "/usr/local/bin/lark-cli",
            os.path.expanduser("~/.npm-global/bin/lark-cli"),
        ]
        for path in paths:
            if os.path.exists(path):
                return path

        # 尝试 which
        try:
            result = subprocess.run(["which", "lark-cli"], capture_output=True, text=True)
            if result.returncode == 0:
                return result.stdout.strip()
        except:
            pass

        return None

    def run(self, command: str, args: List[str] = None, retry: int = 3) -> Dict[str, Any]:
        """执行 lark-cli 命令。

        Args:
            command: 命令（如 "base +record-list"）
            args: 命令参数
            retry: 重试次数

        Returns:
            命令输出（JSON 解析后）
        """
        cmd = [self.cli_path] + command.split()
        if args:
            cmd.extend(args)

        for attempt in range(retry):
            try:
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=60
                )

                # 抑制 stderr（proxy 警告等）
                stdout = result.stdout

                # 尝试解析 JSON
                try:
                    return json.loads(stdout)
                except json.JSONDecodeError:
                    # 如果不是 JSON，返回原始文本
                    return {"raw": stdout, "returncode": result.returncode}

            except subprocess.TimeoutExpired:
                if attempt < retry - 1:
                    time.sleep(2 ** attempt)  # 指数退避
                    continue
                raise

        return {"error": "Max retries exceeded"}

    def batch_create(self, base_token: str, table_id: str, records: List[Dict], batch_size: int = 500) -> List[Dict]:
        """批量创建记录。

        Args:
            base_token: 飞书 base token
            table_id: 表格 ID
            records: 记录列表
            batch_size: 每批大小

        Returns:
            创建结果列表
        """
        results = []
        for i in range(0, len(records), batch_size):
            batch = records[i:i + batch_size]
            # 过滤 null 值
            cleaned_batch = self._clean_records(batch)
            data = json.dumps({"records": cleaned_batch}, ensure_ascii=False)
            result = self.run(
                "base +record-batch-create",
                ["--base-token", base_token, "--table-id", table_id, "--json", data]
            )
            results.append(result)
        return results

    def batch_update(self, base_token: str, table_id: str, record_ids: List[str], patch: Dict, batch_size: int = 500) -> List[Dict]:
        """批量更新记录。

        Args:
            base_token: 飞书 base token
            table_id: 表格 ID
            record_ids: 记录 ID 列表
            patch: 更新数据
            batch_size: 每批大小

        Returns:
            更新结果列表
        """
        results = []
        for i in range(0, len(record_ids), batch_size):
            batch_ids = record_ids[i:i + batch_size]
            data = json.dumps({"record_id_list": batch_ids, "patch": patch}, ensure_ascii=False)
            result = self.run(
                "base +record-batch-update",
                ["--base-token", base_token, "--table-id", table_id, "--json", data]
            )
            results.append(result)
        return results

    def _clean_records(self, records: List[Dict]) -> List[Dict]:
        """清理记录，过滤 null 值。"""
        cleaned = []
        for record in records:
            cleaned_record = {}
            for key, value in record.items():
                if value is not None and value != "" and value != "None":
                    cleaned_record[key] = value
            if cleaned_record:
                cleaned.append(cleaned_record)
        return cleaned


if __name__ == "__main__":
    wrapper = LarkWrapper()
    print(f"lark-cli path: {wrapper.cli_path}")
