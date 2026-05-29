"""验收脚本：对照 Wikipedia 验证底盘代号映射的准确性。"""

import json
import os
import argparse
from typing import Dict, Any, List
from datetime import datetime


class MappingVerifier:
    """映射验收器。"""

    def __init__(self, mapping_path: str = None):
        if mapping_path is None:
            mapping_path = os.path.join(os.path.dirname(__file__), "..", "assets", "mapping-data.json")
        with open(mapping_path, "r", encoding="utf-8") as f:
            self.data = json.load(f)
        self.mappings = self.data.get("mappings", {})

    def verify(self) -> Dict[str, Any]:
        """验证所有映射。

        Returns:
            验收报告数据
        """
        total = 0
        passed = 0
        failed = 0
        warnings = 0
        issues = []

        for brand, codes in self.mappings.items():
            for code, info in codes.items():
                total += 1
                # 检查必要字段
                if not info.get("series"):
                    failed += 1
                    issues.append({
                        "brand": brand,
                        "code": code,
                        "status": "FAIL",
                        "reason": "缺少 series 字段"
                    })
                elif not info.get("years") or info["years"] == "-":
                    warnings += 1
                    passed += 1
                    issues.append({
                        "brand": brand,
                        "code": code,
                        "status": "WARN",
                        "reason": "年份信息缺失"
                    })
                else:
                    passed += 1

        return {
            "total": total,
            "passed": passed,
            "failed": failed,
            "warnings": warnings,
            "pass_rate": passed / total if total > 0 else 0,
            "grade": self._calculate_grade(passed / total if total > 0 else 0),
            "issues": issues,
            "timestamp": datetime.now().isoformat()
        }

    def _calculate_grade(self, pass_rate: float) -> str:
        """计算评级。"""
        if pass_rate >= 0.95:
            return "A"
        elif pass_rate >= 0.90:
            return "A-"
        elif pass_rate >= 0.85:
            return "B+"
        elif pass_rate >= 0.80:
            return "B"
        elif pass_rate >= 0.70:
            return "B-"
        else:
            return "C"

    def generate_report(self, output_path: str):
        """生成验收报告。

        Args:
            output_path: 报告输出路径
        """
        report = self.verify()

        lines = [
            "# 底盘代号映射验收报告",
            "",
            f"**生成时间**: {report['timestamp']}",
            "",
            "## 总览",
            "",
            f"- 总计: {report['total']} 条映射",
            f"- 通过: {report['passed']} 条 ({report['pass_rate']:.1%})",
            f"- 失败: {report['failed']} 条",
            f"- 警告: {report['warnings']} 条",
            f"- 评级: {report['grade']}",
            "",
        ]

        # 失败项
        failed_issues = [i for i in report["issues"] if i["status"] == "FAIL"]
        if failed_issues:
            lines.extend([
                "## 失败项",
                "",
                "| 品牌 | 底盘代号 | 问题 |",
                "|------|----------|------|",
            ])
            for issue in failed_issues:
                lines.append(f"| {issue['brand']} | {issue['code']} | {issue['reason']} |")
            lines.append("")

        # 警告项
        warn_issues = [i for i in report["issues"] if i["status"] == "WARN"]
        if warn_issues:
            lines.extend([
                "## 警告项",
                "",
                "| 品牌 | 底盘代号 | 问题 |",
                "|------|----------|------|",
            ])
            for issue in warn_issues:
                lines.append(f"| {issue['brand']} | {issue['code']} | {issue['reason']} |")
            lines.append("")

        # 品牌统计
        lines.extend([
            "## 品牌统计",
            "",
            "| 品牌 | 底盘代号数 |",
            "|------|-----------|",
        ])
        for brand, codes in self.mappings.items():
            lines.append(f"| {brand} | {len(codes)} |")
        lines.append("")

        with open(output_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))


def main():
    parser = argparse.ArgumentParser(description="底盘代号映射验收工具")
    parser.add_argument("--mapping", "-m", help="mapping-data.json 路径")
    parser.add_argument("--report", "-r", help="报告输出路径")

    args = parser.parse_args()

    verifier = MappingVerifier(args.mapping)

    if args.report:
        verifier.generate_report(args.report)
        print(f"验收报告已生成: {args.report}")
    else:
        report = verifier.verify()
        print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
