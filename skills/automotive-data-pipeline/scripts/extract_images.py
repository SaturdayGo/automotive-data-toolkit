"""Excel 图片提取工具：从 .xlsx 文件中提取嵌入图片。"""

import os
import argparse
import zipfile
from pathlib import Path
from typing import Dict, List, Optional
from xml.etree import ElementTree


class ImageExtractor:
    """Excel 图片提取器。"""

    def __init__(self, xlsx_path: str):
        self.xlsx_path = xlsx_path
        self.images: Dict[int, List[str]] = {}

    def extract(self, output_dir: str) -> Dict[int, List[str]]:
        """提取图片。

        Args:
            output_dir: 输出目录

        Returns:
            行号 → 图片路径列表的映射
        """
        os.makedirs(output_dir, exist_ok=True)

        with zipfile.ZipFile(self.xlsx_path, "r") as zf:
            # 提取所有图片
            image_files = [f for f in zf.namelist() if f.startswith("xl/media/")]

            for img_file in image_files:
                # 生成输出路径
                img_name = os.path.basename(img_file)
                output_path = os.path.join(output_dir, img_name)

                # 写入文件
                with open(output_path, "wb") as f:
                    f.write(zf.read(img_file))

                print(f"提取: {img_name}")

            # 尝试从 xl/drawings/ 中解析图片与行的对应关系
            self._parse_drawings(zf, output_dir)

        return self.images

    def _parse_drawings(self, zf: zipfile.ZipFile, output_dir: str):
        """解析绘图文件，建立图片与行的对应关系。"""
        drawing_files = [f for f in zf.namelist() if f.startswith("xl/drawings/") and f.endswith(".xml")]

        for drawing_file in drawing_files:
            try:
                content = zf.read(drawing_file)
                root = ElementTree.fromstring(content)

                # 解析 anchor 元素
                ns = {
                    "xdr": "http://schemas.openxmlformats.org/drawingml/2006/spreadsheetDrawing",
                    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
                }

                for anchor in root.findall(".//xdr:twoCellAnchor", ns):
                    # 获取行号
                    from_elem = anchor.find(".//xdr:from", ns)
                    if from_elem is not None:
                        row_elem = from_elem.find("xdr:row", ns)
                        if row_elem is not None:
                            row = int(row_elem.text) + 1  # Excel 行号从 1 开始

                            # 获取图片引用
                            pic = anchor.find(".//xdr:pic", ns)
                            if pic is not None:
                                blip = pic.find(".//a:blip", {"a": "http://schemas.openxmlformats.org/drawingml/2006/main"})
                                if blip is not None:
                                    embed = blip.get("{http://schemas.openxmlformats.org/officeDocument/2006/relationships}embed")
                                    if embed:
                                        if row not in self.images:
                                            self.images[row] = []
                                        self.images[row].append(embed)
            except Exception as e:
                print(f"解析绘图文件失败 {drawing_file}: {e}")


def main():
    parser = argparse.ArgumentParser(description="Excel 图片提取工具")
    parser.add_argument("--input", "-i", required=True, help="Excel 文件路径")
    parser.add_argument("--output", "-o", required=True, help="输出目录")

    args = parser.parse_args()

    if not os.path.exists(args.input):
        print(f"文件不存在: {args.input}")
        return

    extractor = ImageExtractor(args.input)
    images = extractor.extract(args.output)

    print(f"\n提取完成:")
    print(f"  图片总数: {sum(len(v) for v in images.values())}")
    print(f"  关联行数: {len(images)}")


if __name__ == "__main__":
    main()
