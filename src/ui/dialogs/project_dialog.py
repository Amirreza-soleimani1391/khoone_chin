from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QFormLayout, QLineEdit, QHBoxLayout, QPushButton
from PyQt5.QtCore import Qt

class ProjectDialog(QDialog):
    def __init__(self, title: str, parent=None, default=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self.setMinimumWidth(420)
        self.setObjectName("ProjectDialog")
        v = QVBoxLayout(self)
        v.setContentsMargins(24, 22, 24, 22)
        v.setSpacing(12)
        head = QLabel(title)
        head.setObjectName("head")
        v.addWidget(head)
        form = QFormLayout()
        form.setSpacing(10)
        form.setLabelAlignment(Qt.AlignRight)
        self.fields = {}
        for key, label, placeholder in [
            ('name', 'نام پروژه', 'مثلاً: خانه پدری'),
            ('style', 'سبک', 'مدرن، کلاسیک، مینیمال…'),
            ('area', 'متراژ (متر)', 'مثلاً: ۱۲۰'),
        ]:
            lb = QLabel(label)
            lb.setObjectName("field-label")
            ed = QLineEdit()
            ed.setPlaceholderText(placeholder)
            if default and key in default:
                ed.setText(str(default[key] or ''))
            self.fields[key] = ed
            form.addRow(lb, ed)
        v.addLayout(form)
        v.addSpacing(6)
        btns = QHBoxLayout()
        btns.addStretch()
        cancel = QPushButton("لغو")
        cancel.setObjectName("cancel")
        cancel.setCursor(Qt.PointingHandCursor)
        cancel.clicked.connect(self.reject)
        btns.addWidget(cancel)
        ok = QPushButton("ذخیره")
        ok.setObjectName("ok")
        ok.setCursor(Qt.PointingHandCursor)
        ok.clicked.connect(self.accept)
        btns.addWidget(ok)
        v.addLayout(btns)
        self.fields['name'].setFocus()

    def get_values(self) -> dict:
        return {k: e.text().strip() for k, e in self.fields.items()}