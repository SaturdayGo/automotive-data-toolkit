import sys
from pathlib import Path

# 添加本 Skill 的 scripts 目录
scripts_dir = str(Path(__file__).parent.parent / "scripts")
if scripts_dir not in sys.path:
    sys.path.insert(0, scripts_dir)

# 添加依赖 Skill 的 scripts 目录（classify, batch_ops 等）
skills_root = Path(__file__).parent.parent.parent
for dep in ["vehicle-classifier/scripts", "feishu-bitable-ops/scripts"]:
    dep_dir = str(skills_root / dep)
    if dep_dir not in sys.path:
        sys.path.insert(0, dep_dir)
