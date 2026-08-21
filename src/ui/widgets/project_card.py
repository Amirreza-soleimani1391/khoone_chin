import os
from PyQt5.QtWidgets import QFrame, QHBoxLayout, QVBoxLayout, QLabel, QPushButton, QWidget
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QPixmap
from src.utils.icons import icon
from src.utils.helpers import relative_time, fa
from src.config.theme import ThemeManager

class ProjectCard(QFrame):
    edit_clicked = pyqtSignal(dict)
    delete_clicked = pyqtSignal(dict)
    open_clicked = pyqtSignal(dict)

    def __init__(self, project: dict, parent=None):
        super().__init__(parent)
        self.project = project
        self.setObjectName("projectCard")
        self.setCursor(Qt.PointingHandCursor)
        self.setMinimumHeight(96)
        self._setup_ui()

    def _setup_ui(self):
        h = QHBoxLayout(self)
        h.setContentsMargins(14, 12, 14, 12)
        h.setSpacing(14)
        self.thumb = QLabel()
        self.thumb.setFixedSize(64, 64)
        self.thumb.setAlignment(Qt.AlignCenter)
        self.thumb.setObjectName("thumb")
        self._load_thumb()
        h.addWidget(self.thumb)
        info = QVBoxLayout()
        info.setSpacing(6)
        name_row = QHBoxLayout()
        name = QLabel(self.project.get('name') or "بدون نام")
        name.setObjectName("name")
        name_row.addWidget(name)
        name_row.addStretch()
        time_lbl = QLabel(relative_time(self.project.get('updated_at')))
        time_lbl.setObjectName("time")
        name_row.addWidget(time_lbl)
        info.addLayout(name_row)
        meta = QHBoxLayout()
        meta.setSpacing(8)
        style_text = self.project.get('style') or "بدون سبک"
        badge = QLabel(style_text)
        badge.setObjectName("badge")
        meta.addWidget(badge)
        area = self.project.get('area')
        if area:
            area_lbl = QLabel(fa(f"{area} متر"))
            area_lbl.setObjectName("area")
            meta.addWidget(area_lbl)
        meta.addStretch()
        info.addLayout(meta)
        h.addLayout(info, 1)
        self.actions = QWidget()
        self.actions.setObjectName("actions")
        ah = QHBoxLayout(self.actions)
        ah.setContentsMargins(0, 0, 0, 0)
        ah.setSpacing(4)

        tm = ThemeManager.get_instance()
        
        def _btn(iname, tip, sig, danger=False):
            b = QPushButton()
            b.setIcon(icon(iname, tm.colors['danger'] if danger else tm.colors['dim'], 16))
            b.setToolTip(tip)
            b.setFixedSize(32, 32)
            b.setObjectName("danger" if danger else "tool-btn")
            b.clicked.connect(sig)
            ah.addWidget(b)
            return b

        _btn('pen', 'ویرایش', lambda: self.edit_clicked.emit(self.project))
        _btn('trash', 'حذف', lambda: self.delete_clicked.emit(self.project), danger=True)
        open_btn = QPushButton("طراحی")
        open_btn.setIcon(icon('plus', tm.colors['accent_text'], 14))
        open_btn.setCursor(Qt.PointingHandCursor)
        open_btn.setProperty('primary', 'true')
        open_btn.clicked.connect(lambda: self.open_clicked.emit(self.project))
        ah.addWidget(open_btn)
        h.addWidget(self.actions)
        self.actions.hide()

    def _load_thumb(self):
        path = self.project.get('canvas_file')
        if path:
            thumb_path = path.rsplit('.', 1)[0] + '.thumb.png'
            if os.path.exists(thumb_path):
                px = QPixmap(thumb_path).scaled(60, 60, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.thumb.setPixmap(px)
                return
        tm = ThemeManager.get_instance()
        self.thumb.setPixmap(icon('home', tm.colors['dim'], 28).pixmap(28, 28))

    def enterEvent(self, e):
        self.actions.show()
        super().enterEvent(e)

    def leaveEvent(self, e):
        self.actions.hide()
        super().leaveEvent(e)