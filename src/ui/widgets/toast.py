from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel, QGraphicsOpacityEffect
from PyQt5.QtCore import QTimer, Qt
from src.config.theme import ThemeManager

class Toast(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.setAttribute(Qt.WA_ShowWithoutActivating, True)
        self.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        h = QHBoxLayout(self)
        self.label = QLabel()
        h.addWidget(self.label)
        self._eff = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self._eff)
        self._timer = QTimer(self)
        self._timer.setSingleShot(True)
        self._timer.timeout.connect(self.hide)

    def show_message(self, text: str, color: str = None):
        t = ThemeManager.get_instance().colors
        c = color or t['ok']
        self.label.setText(text)
        self.setStyleSheet(f"background:{t['elev']}; border:1px solid {c}; border-radius:10px; padding:2px;")
        self.label.setStyleSheet(f"color:{t['text']}; padding:6px 16px;")
        self.adjustSize()
        self._place()
        self.show()
        self.raise_()
        self._eff.setOpacity(1.0)
        self._timer.start(2000)

    def _place(self):
        p = self.parentWidget()
        if p:
            self.move((p.width() - self.width()) // 2, p.height() - self.height() - 60)