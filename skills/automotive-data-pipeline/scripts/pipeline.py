"""全链路管道：Excel → 分类 → 飞书导入。"""

import json
import argparse
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional

# 添加父目录到路径以便导入同级模块
sys.path.insert(0, str(Path(__file__).parent))


class Pipeline:
    """数据管道。"""

    def __init__(self, config_path: str = None):
        self.config = None
        if config_path:
            with open(config_path, "r", encoding="utf-8") as f:
                self.config = json.load(f)

    def classify_input(self, input_path: str, output_path: str = None, wikipedia_verify: bool = True) -> List[Dict]:
        """分类输入数据。

        Args:
            input_path: 输入文件路径（CSV 或 Excel）
            output_path: 输出文件路径
            wikipedia_verify: 是否进行 Wikipedia 验证

        Returns:
            分类结果列表
        """
        import pandas as pd

        # 读取输入
        if input_path.endswith(".xlsx") or input_path.endswith(".xls"):
            df = pd.read_excel(input_path)
        else:
            df = pd.read_csv(input_path, encoding="utf-8-sig")

        # 调用分类器
        from classify import VehicleClassifier
        classifier = VehicleClassifier()

        results = []
        for _, row in df.iterrows():
            name = row.get("车型名", row.get("name", ""))
            if name:
                result = classifier.classify(str(name))
                results.append(result)

        # 输出
        if output_path:
            result_df = pd.DataFrame(results)
            result_df.to_csv(output_path, index=False, encoding="utf-8-sig")
            print(f"分类结果已保存到 {output_path}")

        return results

    def import_to_feishu(self, input_path: str, config_path: str) -> Dict:
        """导入数据到飞书。

        Args:
            input_path: 输入文件路径（CSV 或 JSON）
            config_path: 飞书配置文件路径

        Returns:
            导入结果
        """
        import pandas as pd

        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)

        # 读取输入
        if input_path.endswith(".json"):
            with open(input_path, "r", encoding="utf-8") as f:
                records = json.load(f)
        else:
            df = pd.read_csv(input_path, encoding="utf-8-sig")
            records = df.to_dict(orient="records")

        # 调用批量操作
        from batch_ops import BatchOperator
        operator = BatchOperator(config_path)

        return operator.batch_create(records)

    def sort_records(self, config_path: str) -> Dict:
        """排序飞书记录。

        Args:
            config_path: 飞书配置文件路径

        Returns:
            排序结果
        """
        from view_config import ViewConfigurator
        configurator = ViewConfigurator(config_path)

        sort_config = [
            {"field": "车系", "order": "asc"},
            {"field": "核心车型", "order": "asc"},
            {"field": "产品类型", "order": "asc"},
            {"field": "年款", "order": "asc"}
        ]

        return configurator.set_sort(sort_config)

    def run_full_pipeline(self, input_path: str, config_path: str, output_path: str = None) -> Dict:
        """运行完整管道。

        Args:
            input_path: 输入文件路径
            config_path: 飞书配置文件路径
            output_path: 中间文件输出路径

        Returns:
            执行结果
        """
        results = {
            "classify": None,
            "import": None,
            "sort": None
        }

        # Step 1: 分类
        print("Step 1: 分类数据...")
        classified_path = output_path or "classified_output.csv"
        results["classify"] = self.classify_input(input_path, classified_path)
        print(f"  分类完成: {len(results['classify'])} 条记录")

        # Step 2: 导入
        print("Step 2: 导入飞书...")
        results["import"] = self.import_to_feishu(classified_path, config_path)
        print(f"  导入完成")

        # Step 3: 排序
        print("Step 3: 排序优化...")
        results["sort"] = self.sort_records(config_path)
        print(f"  排序完成")

        return results


def main():
    parser = argparse.ArgumentParser(description="汽车产品数据全链路管道")
    parser.add_argument("--input", "-i", help="输入文件路径")
    parser.add_argument("--config", "-c", help="飞书配置文件路径")
    parser.add_argument("--output", "-o", help="输出文件路径")
    parser.add_argument("--classify", action="store_true", help="执行分类")
    parser.add_argument("--import", dest="do_import", action="store_true", help="导入飞书")
    parser.add_argument("--sort", action="store_true", help="排序优化")
    parser.add_argument("--full", action="store_true", help="运行完整管道")

    args = parser.parse_args()

    pipeline = Pipeline(args.config)

    if args.full:
        if not args.input or not args.config:
            print("完整管道需要 --input 和 --config")
            return
        results = pipeline.run_full_pipeline(args.input, args.config, args.output)
        print("\n执行结果:")
        print(json.dumps(results, ensure_ascii=False, indent=2))
    elif args.classify:
        if not args.input:
            print("分类需要 --input")
            return
        results = pipeline.classify_input(args.input, args.output)
        print(f"分类完成: {len(results)} 条记录")
    elif args.do_import:
        if not args.input or not args.config:
            print("导入需要 --input 和 --config")
            return
        results = pipeline.import_to_feishu(args.input, args.config)
        print("导入完成")
    elif args.sort:
        if not args.config:
            print("排序需要 --config")
            return
        results = pipeline.sort_records(args.config)
        print("排序完成")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
