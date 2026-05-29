"""测试配置。"""

import sys
from pathlib import Path

# 添加 scripts 目录到路径
scripts_dir = str(Path(__file__).parent.parent / "scripts")
if scripts_dir not in sys.path:
    sys.path.insert(0, scripts_dir)
