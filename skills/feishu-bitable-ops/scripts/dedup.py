"""去重工具：按字段去重飞书记录。"""

import json
import argparse
from typing import Dict, List, Any
from collections import defaultdict

from lark_wrapper import LarkWrapper


class Deduplicator:
    """去重器。"""

    def __init__(self, config_path: str):
        with open(config_path, "r", encoding="utf-8") as f:
            self.config = json.load(f)
        self.wrapper = LarkWrapper()

    def fetch_all_records(self) -> List[Dict]:
        """获取所有记录。"""
        result = self.wrapper.run(
            "base +record-list",
            [
                "--base-token", self.config["base_token"],
                "--table-id", self.config["table_id"],
                "--page-size", "500"
            ]
        )
        return result.get("items", [])

    def find_duplicates(self, records: List[Dict], field: str) -> List[Dict]:
        """查找重复记录。

        Args:
            records: 记录列表
            field: 去重字段

        Returns:
            重复记录组
        """
        # 按字段值分组
        groups = defaultdict(list)
        for record in records:
            fields = record.get("fields", {})
            value = fields.get(field)
            if value:
                # 对于附件字段，使用 file_token
                if isinstance(value, list) and len(value) > 0:
                    token = value[0].get("file_token", "")
                    if token:
                        groups[token].append(record["record_id"])
                else:
                    groups[str(value)].append(record["record_id"])

        # 找出有重复的组
        duplicates = []
        for value, ids in groups.items():
            if len(ids) > 1:
                duplicates.append({
                    "value": value,
                    "keep": ids[0],
                    "remove": ids[1:]
                })

        return duplicates

    def remove_duplicate_attachments(self, duplicates: List[Dict], field: str, dry_run: bool = True) -> List[Dict]:
        """清除重复记录的附件（不删除记录本身）。

        Args:
            duplicates: 重复记录组
            field: 去重字段
            dry_run: 是否只预览不执行

        Returns:
            清除结果
        """
        results = []
        for group in duplicates:
            for record_id in group["remove"]:
                if dry_run:
                    results.append({
                        "action": "would_remove",
                        "record_id": record_id,
                        "value": group["value"]
                    })
                else:
                    # 获取字段 ID
                    field_id = self.config.get("field_mapping", {}).get(field)
                    if field_id:
                        # 删除附件
                        result = self.wrapper.run(
                            "base +record-remove-attachment",
                            [
                                "--base-token", self.config["base_token"],
                                "--table-id", self.config["table_id"],
                                "--record-id", record_id,
                                "--field-id", field_id,
                                "--file-token", group["value"],
                                "--yes"
                            ]
                        )
                        results.append({
                            "action": "removed",
                            "record_id": record_id,
                            "result": result
                        })

        return results


def main():
    parser = argparse.ArgumentParser(description="飞书去重工具")
    parser.add_argument("--config", "-c", required=True, help="配置文件路径")
    parser.add_argument("--field", "-f", required=True, help="去重字段")
    parser.add_argument("--dry-run", action="store_true", help="只预览不执行")

    args = parser.parse_args()

    dedup = Deduplicator(args.config)
    records = dedup.fetch_all_records()
    duplicates = dedup.find_duplicates(records, args.field)

    if not duplicates:
        print("未发现重复记录")
        return

    print(f"发现 {len(duplicates)} 组重复记录:")
    for group in duplicates:
        print(f"  值: {group['value']}, 保留: {group['keep']}, 删除: {group['remove']}")

    if args.dry_run:
        print("\n预览模式，未执行删除")
    else:
        results = dedup.remove_duplicate_attachments(duplicates, args.field, dry_run=False)
        print(f"\n已清除 {len(results)} 条重复记录的附件")


if __name__ == "__main__":
    main()
