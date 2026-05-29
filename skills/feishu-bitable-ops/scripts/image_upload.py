"""图片上传脚本：批量上传图片到飞书。"""

import json
import argparse
import os
from typing import Dict, List, Optional

from lark_wrapper import LarkWrapper


class ImageUploader:
    """图片上传器。"""

    SUPPORTED_FORMATS = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp"}

    def __init__(self, config_path: str):
        with open(config_path, "r", encoding="utf-8") as f:
            self.config = json.load(f)
        self.wrapper = LarkWrapper()

    def scan_directory(self, directory: str) -> List[str]:
        """扫描目录中的图片文件。

        Args:
            directory: 目录路径

        Returns:
            图片文件路径列表
        """
        images = []
        for filename in os.listdir(directory):
            ext = os.path.splitext(filename)[1].lower()
            if ext in self.SUPPORTED_FORMATS:
                images.append(os.path.join(directory, filename))
        return sorted(images)

    def upload(self, image_path: str, record_id: str, field_id: str) -> Dict:
        """上传单张图片。

        Args:
            image_path: 图片路径
            record_id: 记录 ID
            field_id: 字段 ID

        Returns:
            上传结果
        """
        return self.wrapper.run(
            "base +record-upload-attachment",
            [
                "--base-token", self.config["base_token"],
                "--table-id", self.config["table_id"],
                "--record-id", record_id,
                "--field-id", field_id,
                "--file", image_path
            ]
        )

    def batch_upload(self, directory: str, mapping: Dict[str, str]) -> List[Dict]:
        """批量上传图片。

        Args:
            directory: 图片目录
            mapping: 图片文件名到记录 ID 的映射

        Returns:
            上传结果列表
        """
        images = self.scan_directory(directory)
        field_id = self.config["field_mapping"].get("图片")
        results = []

        for image_path in images:
            filename = os.path.basename(image_path)
            record_id = mapping.get(filename)
            if record_id and field_id:
                result = self.upload(image_path, record_id, field_id)
                results.append({
                    "filename": filename,
                    "record_id": record_id,
                    "result": result
                })

        return results


def main():
    parser = argparse.ArgumentParser(description="飞书图片上传工具")
    parser.add_argument("--config", "-c", required=True, help="配置文件路径")
    parser.add_argument("--images", "-i", required=True, help="图片目录路径")
    parser.add_argument("--mapping", "-m", required=True, help="图片映射文件路径")

    args = parser.parse_args()

    uploader = ImageUploader(args.config)

    with open(args.mapping, "r", encoding="utf-8") as f:
        mapping = json.load(f)

    results = uploader.batch_upload(args.images, mapping)
    print(f"已上传 {len(results)} 张图片")
    print(json.dumps(results, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
