from PyQt5.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel
from PyQt5.QtCore import Qt
from src.utils.icons import icon
from src.config.theme import ThemeManager

class StatCard(QFrame):
    def __init__(self, title: str, icon_name: str, parent=None):
        super().__init__(parent)
        self.setObjectName("StatCard")
        self.setMinimumHeight(92)
        self.setCursor(Qt.PointingHandCursor)
        v = QVBoxLayout(self)
        v.setContentsMargins(16, 14, 16, 14)
        v.setSpacing(8)
        top = QHBoxLayout()
        top.setSpacing(8)
        self.icon_label = QLabel()
        self.icon_label.setFixedSize(28, 28)
        self.icon_label.setAlignment(Qt.AlignCenter)
        self.icon_label.setObjectName("icon-box")
        
        tm = ThemeManager.get_instance()
        self.icon_label.setPixmap(icon(icon_name, tm.colors['accent'], 16).pixmap(16, 16))
        top.addWidget(self.icon_label)
        self.title_label = QLabel(title)
        self.title_label.setObjectName("title")
        top.addWidget(self.title_label)
        top.addStretch()
        v.addLayout(top)
        self.value_label = QLabel("—")
        self.value_label.setObjectName("value")
        v.addWidget(self.value_label)
        v.addStretch()

    def set_value(self, value: str):
        self.value_label.setText(str(value))