"""Repository paths used by the course validation tools."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VAULT = ROOT / "数学软件个人学习档案"
PROCESS = VAULT / "05-过程记录"
WEEK01_SOURCE = VAULT / "01-GeoGebra" / "第01周" / "week01-basic-objects.ggb"
WEEK01_PREVIEWS = VAULT / "04-展示材料" / "第01周" / "图片"
WEEK01_EVIDENCE = PROCESS / "成果" / "第01周" / "核验附件"
