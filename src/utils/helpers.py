from datetime import datetime, timedelta
from PyQt5.QtWidgets import QFrame

def fa(s: str) -> str:
    """Translate English digits to Persian digits."""
    return str(s).translate(str.maketrans('0123456789', '۰۱۲۳۴۵۶۷۸۹'))

def relative_time(updated_at: str) -> str:
    if not updated_at:
        return "نامشخص"
    try:
        last = datetime.strptime(updated_at, "%Y-%m-%d %H:%M:%S")
    except Exception:
        return "نامشخص"
    delta = datetime.now() - last
    if delta < timedelta(minutes=1):
        return "همین الان"
    if delta < timedelta(hours=1):
        return fa(f"{delta.seconds // 60} دقیقه پیش")
    if delta < timedelta(days=1):
        return fa(f"{delta.seconds // 3600} ساعت پیش")
    if delta < timedelta(days=7):
        return fa(f"{delta.days} روز پیش")
    return last.strftime("%Y/%m/%d")

def create_separator() -> QFrame:
    f = QFrame()
    f.setFrameShape(QFrame.VLine)
    f.setProperty('vline', True)
    f.setFixedWidth(1)
    return f