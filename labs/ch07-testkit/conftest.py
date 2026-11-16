import sys
from pathlib import Path

# 让 `pytest labs` 从仓库根跑时也能 import testkit
sys.path.insert(0, str(Path(__file__).resolve().parent))
