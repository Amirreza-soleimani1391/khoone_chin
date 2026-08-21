from PyQt5.QtCore import QByteArray, Qt
from PyQt5.QtGui import QPixmap, QIcon, QPainter
from PyQt5.QtSvg import QSvgRenderer
from src.config.theme import ThemeManager

_SVG_PATHS = {
    'select': "<path d='M4 3l7.5 17 2.3-7.2L21 10.5z'/>",
    'pan': "<path d='M12 2v20M2 12h20M12 2l-3 3m3-3l3 3M12 22l-3-3m3 3l3-3M2 12l3-3m-3 3l3 3M22 12l-3-3m3 3l-3 3'/>",
    'pen': "<path d='M17 3a2.8 2.8 0 1 1 4 4L7.5 20.5 2 22l1.5-5.5z'/>",
    'rect': "<rect x='4' y='6' width='16' height='12' rx='1.5'/>",
    'image': "<rect x='3' y='5' width='18' height='14' rx='2'/><circle cx='9' cy='10' r='1.6'/><path d='M5 19l6-6 4 4 3-3 3 3'/>",
    'measure': "<path d='M21.3 8.7l-6-6L2.7 15.3l6 6zM7.5 10.5l2 2M10.5 7.5l2 2M13.5 4.5l2 2'/>",
    'undo': "<path d='M9 14L4 9l5-5M4 9h10a6 6 0 0 1 0 12h-3'/>",
    'redo': "<path d='M15 14l5-5-5-5M20 9H10a6 6 0 0 0 0 12h3'/>",
    'plus': "<path d='M12 5v14M5 12h14'/>",
    'minus': "<path d='M5 12h14'/>",
    'fit': "<path d='M8 3H5a2 2 0 0 0-2 2v3M16 3h3a2 2 0 0 1 2 2v3M8 21H5a2 2 0 0 1-2-2v-3M16 21h3a2 2 0 0 0 2-2v-3'/>",
    'export': "<path d='M12 3v12m0 0l-4-4m4 4l4-4M4 19h16'/>",
    'trash': "<path d='M4 7h16M9 7V5a1 1 0 0 1 1-1h4a1 1 0 0 1 1 1v2m-11 0l1 13h10l1-13'/>",
    'copy': "<rect x='9' y='9' width='11' height='11' rx='2'/><path d='M5 15V5a2 2 0 0 1 2-2h10'/>",
    'lock': "<rect x='5' y='11' width='14' height='9' rx='2'/><path d='M8 11V8a4 4 0 0 1 8 0v3'/>",
    'front': "<path d='M12 3l9 5-9 5-9-5zM3 14l9 5 9-5'/>",
    'back': "<path d='M12 11l9 5-9 5-9-5zM3 5l9 5 9-5'/>",
    'grid': "<path d='M3 9h18M3 15h18M9 3v18M15 3v18'/>",
    'magnet': "<path d='M6 3v8a6 6 0 0 0 12 0V3M6 3h4v8M14 3h4v8'/>",
    'search': "<circle cx='11' cy='11' r='7'/><path d='M20 20l-3.5-3.5'/>",
    'check': "<path d='M4 12l5 5L20 7'/>",
    'project': "<path d='M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z'/><path d='M14 2v6h6M16 13H8M16 17H8M10 9H8'/>",
    'chart': "<path d='M3 3v18h18'/><path d='M7 14l3-3 4 4 6-6'/>",
    'clock': "<circle cx='12' cy='12' r='10'/><path d='M12 6v6l4 2'/>",
    'settings': "<circle cx='12' cy='12' r='3'/><path d='M19.4 15a1.7 1.7 0 0 0 .3 1.8l.1.1a2 2 0 1 1-2.8 2.8l-.1-.1a1.7 1.7 0 0 0-1.8-.3 1.7 1.7 0 0 0-1 1.5V21a2 2 0 1 1-4 0v-.1a1.7 1.7 0 0 0-1.1-1.5 1.7 1.7 0 0 0-1.8.3l-.1.1a2 2 0 1 1-2.8-2.8l.1-.1a1.7 1.7 0 0 0 .3-1.8 1.7 1.7 0 0 0-1.5-1H3a2 2 0 1 1 0-4h.1a1.7 1.7 0 0 0 1.5-1.1 1.7 1.7 0 0 0-.3-1.8l-.1-.1a2 2 0 1 1 2.8-2.8l.1.1a1.7 1.7 0 0 0 1.8.3H9a1.7 1.7 0 0 0 1-1.5V3a2 2 0 1 1 4 0v.1a1.7 1.7 0 0 0 1 1.5 1.7 1.7 0 0 0 1.8-.3l.1-.1a2 2 0 1 1 2.8 2.8l-.1.1a1.7 1.7 0 0 0-.3 1.8V9a1.7 1.7 0 0 0 1.5 1H21a2 2 0 1 1 0 4h-.1a1.7 1.7 0 0 0-1.5 1z'/>",
    'info': "<circle cx='12' cy='12' r='10'/><path d='M12 16v-4M12 8h.01'/>",
    'backup': "<path d='M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4'/><path d='M7 10l5 5 5-5M12 15V3'/>",
    'restore': "<path d='M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4'/><path d='M17 8l-5-5-5 5M12 3v12'/>",
    'home': "<path d='M3 12l9-9 9 9'/><path d='M5 10v10a1 1 0 0 0 1 1h3v-6h6v6h3a1 1 0 0 0 1-1V10'/>",
    'folder': "<path d='M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z'/>",
    'star': "<polygon points='12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2'/>",
    'theme': "<path d='M21 12.8A9 9 0 1 1 11.2 3 7 7 0 0 0 21 12.8z'/>",
}

def icon(name: str, color: str = None, size: int = 20) -> QIcon:
    tm = ThemeManager.get_instance()
    if color is None:
        color = tm.colors['dim']
    elif color == 'accent':
        color = tm.colors['accent']
        
    inner = _SVG_PATHS.get(name, '')
    svg = (f"<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='{color}' "
           f"stroke-width='1.8' stroke-linecap='round' stroke-linejoin='round'>{inner}</svg>")
    r = QSvgRenderer(QByteArray(svg.encode('utf-8')))
    px = QPixmap(size * 2, size * 2)
    px.fill(Qt.transparent)
    p = QPainter(px)
    p.setRenderHint(QPainter.Antialiasing)
    r.render(p)
    p.end()
    return QIcon(px)