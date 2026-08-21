import os
from PyQt5.QtCore import QByteArray, Qt
from PyQt5.QtGui import QPixmap, QPainter
from PyQt5.QtSvg import QSvgRenderer
from src.config.settings import get_cache_dir

def _cat_svg(inner: str, w: int, h: int) -> str:
    return (f"<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 {w} {h}'>"
            f"<g stroke='#aeb6c4' stroke-width='3' fill='#414a5a'>{inner}</g></svg>")

def asset_path(name: str, w: int, h: int, inner: str) -> str:
    d = os.path.join(get_cache_dir(), 'assets')
    os.makedirs(d, exist_ok=True)
    p = os.path.join(d, f'{name}.png')
    if not os.path.exists(p):
        r = QSvgRenderer(QByteArray(_cat_svg(inner, w, h).encode('utf-8')))
        px = QPixmap(w, h)
        px.fill(Qt.transparent)
        pa = QPainter(px)
        pa.setRenderHint(QPainter.Antialiasing)
        r.render(pa)
        pa.end()
        px.save(p)
    return p

def load_optimized_pixmap(path: str, max_size: int = 1000) -> QPixmap:
    if not path or not os.path.exists(path):
        return QPixmap()
    pixmap = QPixmap(path)
    if pixmap.isNull():
        return pixmap
    if pixmap.width() > max_size or pixmap.height() > max_size:
        pixmap = pixmap.scaled(max_size, max_size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
    return pixmap