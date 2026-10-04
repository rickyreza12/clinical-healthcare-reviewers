import sys
import os
from pathlib import Path
os.environ["SEMANTIC_ENABLED"] = "false"
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
