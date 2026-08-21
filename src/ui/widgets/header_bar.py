from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel, QLineEdit, QToolButton, QPushButton
# اصلاح: اضافه شدن QSize به importها
from PyQt5.QtCore import pyqtSignal, Qt, QSize 
from src.utils.icons import icon
from src.utils.helpers import create_separator
from src.config.theme import ThemeManager

class HeaderBar(QWidget):
    undo_clicked = pyqtSignal()
    redo_clicked = pyqtSignal()
    export_clicked = pyqtSignal()
    name_changed = pyqtSignal(str)
    zoom_in = pyqtSignal()
    zoom_out = pyqtSignal()
    zoom_fit = pyqtSignal()
    smart_clicked = pyqtSignal()
    theme_toggled = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setFixedHeight(52)
        h = QHBoxLayout(self)
        h.setContentsMargins(12, 6, 12, 6)
        h.setSpacing(8)
        logo = QWidget()
        logo.setFixedSize(18, 18)
        logo.setObjectName("logo")
        h.addWidget(logo)
        h.addWidget(QLabel("<b style='font-size:15px'>چیدمان</b>"))
        self.name_edit = QLineEdit("طرح بدون نام")
        self.name_edit.setObjectName("projectName")
        self.name_edit.setFixedWidth(170)
        self.name_edit.editingFinished.connect(lambda: self.name_changed.emit(self.name_edit.text()))
        h.addWidget(self.name_edit)
        self.saved_label = QLabel("✓ ذخیره شده")
        self.saved_label.setObjectName("saved")
        h.addWidget(self.saved_label)
        h.addStretch()

        def ibtn(name, tip, sig=None):
            b = QToolButton()
            b.setIcon(icon(name))
            b.setIconSize(QSize(18, 18))
            b.setToolTip(tip)
            if sig: b.clicked.connect(sig)
            h.addWidget(b)
            return b

        self.undo_btn = ibtn('undo', 'واگرد (Ctrl+Z)', self.undo_clicked)
        self.redo_btn = ibtn('redo', 'ازنو (Ctrl+Y)', self.redo_clicked)
        h.addWidget(create_separator())
        ibtn('minus', 'کوچک‌نمایی', self.zoom_out)
        self.zoom_label = QLabel("٪۱۰۰")
        self.zoom_label.setFixedWidth(52)
        self.zoom_label.setAlignment(Qt.AlignCenter)
        h.addWidget(self.zoom_label)
        ibtn('plus', 'بزرگ‌نمایی (Ctrl+Wheel)', self.zoom_in)
        ibtn('fit', 'اندازه‌ی کل صفحه', self.zoom_fit)
        h.addWidget(create_separator())
        
        tm = ThemeManager.get_instance()
        self.smart_btn = QPushButton("چیدمان هوشمند")
        self.smart_btn.setProperty('primary', 'true')
        self.smart_btn.setIcon(icon('star', tm.colors['accent_text'], 15))
        self.smart_btn.clicked.connect(self.smart_clicked)
        h.addWidget(self.smart_btn)
        
        self.theme_btn = QToolButton()
        self.theme_btn.setIcon(icon('theme', tm.colors['text'], 18))
        self.theme_btn.setToolTip('تغییر تم روز/شب')
        self.theme_btn.clicked.connect(self.theme_toggled)
        h.addWidget(self.theme_btn)
        
        self.export_btn = QPushButton("خروجی")
        self.export_btn.setProperty('primary', 'true')
        self.export_btn.setIcon(icon('export', tm.colors['accent_text'], 16))
        self.export_btn.clicked.connect(self.export_clicked)
        h.addWidget(self.export_btn)

    def set_saved(self, saved: bool):
        if saved:
            self.saved_label.setText("✓ ذخیره شده")
            self.saved_label.setObjectName("saved")
        else:
            self.saved_label.setText("● ذخیره‌نشده")
            self.saved_label.setObjectName("saved_warn")
        self.saved_label.style().unpolish(self.saved_label)
        self.saved_label.style().polish(self.saved_label)

    def set_zoom(self, z: float):
        self.zoom_label.setText("٪" + str(int(z * 100)))