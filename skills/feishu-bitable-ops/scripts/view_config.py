"""视图配置脚本：排序/分组/字段可见性。"""

import json
import argparse
from typing import Dict, List, Any

from lark_wrapper import LarkWrapper


class ViewConfigurator:
    """视图配置器。"""

    def __init__(self, config_path: str):
        with open(config_path, "r", encoding="utf-8") as f:
            self.config = json.load(f)
        self.wrapper = LarkWrapper()

    def set_sort(self, sort_config: List[Dict[str, str]], view_id: str = None) -> Dict:
        """设置排序。

        Args:
            sort_config: 排序配置列表，如 [{"field": "车系", "order": "asc"}]
            view_id: 视图 ID

        Returns:
            配置结果
        """
        field_mapping = self.config.get("field_mapping", {})
        sort_data = []
        for item in sort_config:
            field_id = field_mapping.get(item["field"], item["field"])
            sort_data.append({
                "field_id": field_id,
                "desc": item.get("order", "asc") == "desc"
            })

        args = [
            "--base-token", self.config["base_token"],
            "--table-id", self.config["table_id"],
            "--json", json.dumps({"sort": sort_data}, ensure_ascii=False)
        ]
        if view_id:
            args.extend(["--view-id", view_id])

        return self.wrapper.run("base +view-set-sort", args)

    def set_group(self, group_config: List[Dict[str, Any]], view_id: str = None) -> Dict:
        """设置分组。

        Args:
            group_config: 分组配置列表，如 [{"field": "车系", "order": "asc"}]
            view_id: 视图 ID

        Returns:
            配置结果
        """
        field_mapping = self.config.get("field_mapping", {})
        group_data = []
        for item in group_config:
            field_id = field_mapping.get(item["field"], item["field"])
            group_data.append({
                "field_id": field_id,
                "desc": item.get("order", "asc") == "desc"
            })

        args = [
            "--base-token", self.config["base_token"],
            "--table-id", self.config["table_id"],
            "--json", json.dumps({"group": group_data}, ensure_ascii=False)
        ]
        if view_id:
            args.extend(["--view-id", view_id])

        return self.wrapper.run("base +view-set-group", args)

    def set_visible_fields(self, fields: List[str], view_id: str = None) -> Dict:
        """设置可见字段。

        Args:
            fields: 可见字段名列表
            view_id: 视图 ID

        Returns:
            配置结果
        """
        field_mapping = self.config.get("field_mapping", {})
        field_ids = [field_mapping.get(f, f) for f in fields]

        args = [
            "--base-token", self.config["base_token"],
            "--table-id", self.config["table_id"],
            "--json", json.dumps({"visible_field_ids": field_ids}, ensure_ascii=False)
        ]
        if view_id:
            args.extend(["--view-id", view_id])

        return self.wrapper.run("base +view-set-visible-fields", args)


def main():
    parser = argparse.ArgumentParser(description="飞书视图配置工具")
    parser.add_argument("--config", "-c", required=True, help="配置文件路径")
    parser.add_argument("--sort", help="排序配置（JSON）")
    parser.add_argument("--group", help="分组配置（JSON）")
    parser.add_argument("--fields", help="可见字段（JSON）")
    parser.add_argument("--view-id", help="视图 ID")

    args = parser.parse_args()

    configurator = ViewConfigurator(args.config)

    if args.sort:
        sort_config = json.loads(args.sort)
        result = configurator.set_sort(sort_config, args.view_id)
        print("排序配置完成:")
        print(json.dumps(result, ensure_ascii=False, indent=2))

    if args.group:
        group_config = json.loads(args.group)
        result = configurator.set_group(group_config, args.view_id)
        print("分组配置完成:")
        print(json.dumps(result, ensure_ascii=False, indent=2))

    if args.fields:
        fields = json.loads(args.fields)
        result = configurator.set_visible_fields(fields, args.view_id)
        print("可见字段配置完成:")
        print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
