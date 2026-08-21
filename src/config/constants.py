from typing import List, Tuple, Dict

# Tag definitions for smart layout and categorization
TAG_PRESETS: List[Tuple[str, str]] = [
    ("مبل", "sofa"), ("صندلی", "chair"), ("تلویزیون", "tv"),
    ("میز", "table"), ("کمد", "cabinet"), ("سایر", "other"), ("محدوده", "area"),
]

TAG_COLORS: Dict[str, str] = {
    "sofa": "#3b82f6", "chair": "#8b5cf6", "tv": "#f59e0b",
    "table": "#22c55e", "cabinet": "#ef4444", "other": "#6b7280", "area": "#2dd4bf",
}

# Catalog items (Name, Width, Height, SVG Inner Path)
CATALOG: List[Tuple[str, int, int, str]] = [
    ('مبل دونفره', 180, 90, "<rect x='4' y='4' width='172' height='82' rx='14'/><rect x='4' y='4' width='172' height='26' rx='13' fill='#333a47'/>"),
    ('تخت دونفره', 200, 160, "<rect x='4' y='4' width='192' height='152' rx='10'/><rect x='16' y='14' width='76' height='40' rx='8' fill='#333a47'/><rect x='108' y='14' width='76' height='40' rx='8' fill='#333a47'/>"),
    ('میز غذاخوری', 160, 90, "<rect x='6' y='6' width='148' height='78' rx='10'/>"),
    ('میز گرد', 120, 120, "<circle cx='60' cy='60' r='54'/>"),
    ('یخچال', 70, 70, "<rect x='4' y='4' width='62' height='62' rx='6'/><line x1='4' y1='26' x2='66' y2='26'/>"),
    ('فرش', 300, 200, "<rect x='4' y='4' width='292' height='192' rx='6' fill='none' stroke-dasharray='10 8'/>"),
]