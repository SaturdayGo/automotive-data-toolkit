"""批量操作脚本：创建/更新/删除飞书记录。"""

import json
import argparse
import csv
from typing import Dict, Any, List

from lark_wrapper import LarkWrapper


class BatchOperator:
    """批量操作器。"""

    def __init__(self, config_path: str):
        with open(config_path, "r", encoding="utf-8") as f:
            self.config = json.load(f)
        self.wrapper = LarkWrapper()

    def create(self, data_path: str) -> List[Dict]:
        """批量创建记录。

        Args:
            data_path: 数据文件路径（JSON）

        Returns:
            创建结果
        """
        with open(data_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        records = data if isinstance(data, list) else data.get("records", [])
        return self.wrapper.batch_create(
            self.config["base_token"],
            self.config["table_id"],
            records
        )

    def update(self, data_path: str) -> List[Dict]:
        """批量更新记录。

        Args:
            data_path: 数据文件路径（JSON）

        Returns:
            更新结果
        """
        with open(data_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        records = data if isinstance(data, list) else data.get("records", [])
        results = []

        for record in records:
            record_id = record.pop("record_id", None)
            if record_id:
                result = self.wrapper.batch_update(
                    self.config["base_token"],
                    self.config["table_id"],
                    [record_id],
                    record
                )
                results.extend(result)

        return results

    def remove_attachment(self, record_id: str, field_id: str, file_token: str) -> Dict:
        """删除附件。

        Args:
            record_id: 记录 ID
            field_id: 字段 ID
            file_token: 文件 token

        Returns:
            删除结果
        """
        return self.wrapper.run(
            "base +record-remove-attachment",
            [
                "--base-token", self.config["base_token"],
                "--table-id", self.config["table_id"],
                "--record-id", record_id,
                "--field-id", field_id,
                "--file-token", file_token,
                "--yes"
            ]
        )


def main():
    parser = argparse.ArgumentParser(description="飞书批量操作工具")
    parser.add_argument("--action", "-a", required=True, choices=["create", "update", "delete"],
                       help="操作类型")
    parser.add_argument("--config", "-c", required=True, help="配置文件路径")
    parser.add_argument("--data", "-d", required=True, help="数据文件路径")

    args = parser.parse_args()

    operator = BatchOperator(args.config)

    if args.action == "create":
        results = operator.create(args.data)
    elif args.action == "update":
        results = operator.update(args.data)
    else:
        print("删除操作请使用 dedup.py")
        return

    print(json.dumps(results, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
