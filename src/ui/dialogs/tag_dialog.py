from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QComboBox, QHBoxLayout, QPushButton
from src.config.constants import TAG_PRESETS

class TagDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("انتخاب تگ")
        self.setModal(True)
        self.setMinimumWidth(280)
        v = QVBoxLayout(self)
        v.addWidget(QLabel("این آیتم چه چیزی است؟"))
        self.combo = QComboBox()
        for text, key in TAG_PRESETS:
            self.combo.addItem(text, key)
        v.addWidget(self.combo)
        btns = QHBoxLayout()
        btns.addStretch()
        cancel = QPushButton("لغو")
        cancel.clicked.connect(self.reject)
        btns.addWidget(cancel)
        ok = QPushButton("تایید")
        ok.clicked.connect(self.accept)
        btns.addWidget(ok)
        v.addLayout(btns)

    def selected_tag(self) -> str:
        return self.combo.currentData()