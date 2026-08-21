from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel, QToolButton
from PyQt5.QtCore import pyqtSignal, Qt
from src.utils.icons import icon # تابع آیکون شما

class StatusStrip(QWidget):
    # سیگنال‌هایی که در editor_window.py به آن‌ها نیاز داریم
    grid_toggled = pyqtSignal(bool)
    snap_toggled = pyqtSignal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(32)
        self.setObjectName("StatusStrip")
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 2, 10, 2)
        layout.setSpacing(10)
        
        # نمایش مختصات موس
        self.coords_label = QLabel("X: 0, Y: 0")
        self.coords_label.setMinimumWidth(120)
        self.coords_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        layout.addWidget(self.coords_label)
        
        # متن راهنمای ابزار (Hint)
        self.hint_label = QLabel("آماده")
        self.hint_label.setStyleSheet("color: gray; font-style: italic;")
        self.hint_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.hint_label, 1) # 1 باعث می‌شود فضای خالی را پر کند
        
        # دکمه توری (Grid)
        self.grid_btn = QToolButton()
        try:
            self.grid_btn.setIcon(icon('grid', None, 16))
        except Exception:
            self.grid_btn.setText("Grid")
        self.grid_btn.setToolTip("نمایش خطوط راهنما")
        self.grid_btn.setCheckable(True)
        self.grid_btn.setChecked(True) # به صورت پیش‌فرض روشن
        self.grid_btn.toggled.connect(self.grid_toggled.emit)
        layout.addWidget(self.grid_btn)
        
        # دکمه چسبندگی (Snap)
        self.snap_btn = QToolButton()
        try:
            self.snap_btn.setIcon(icon('magnet', None, 16))
        except Exception:
            self.snap_btn.setText("Snap")
        self.snap_btn.setToolTip("چسبندگی به نقاط و خطوط")
        self.snap_btn.setCheckable(True)
        self.snap_btn.setChecked(True)
        self.snap_btn.toggled.connect(self.snap_toggled.emit)
        layout.addWidget(self.snap_btn)

    def set_coords(self, x, y):
        """نمایش مختصات موس در نوار وضعیت"""
        # فرمت کردن اعداد برای نمایش بهتر (مثلاً ۱۲۳.۴)
        self.coords_label.setText(f"X: {x:.1f}, Y: {y:.1f}")

    def set_hint(self, text):
        """تغییر متن راهنمای ابزار فعلی"""
        self.hint_label.setText(text or "آماده")