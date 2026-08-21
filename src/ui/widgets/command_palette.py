from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLineEdit, QListWidget, QAbstractItemView

class CommandPalette(QDialog):
    def __init__(self, actions, parent):
        super().__init__(parent)
        self.actions = actions
        self.setWindowTitle("فرمان‌ها")
        self.setFixedWidth(420)
        v = QVBoxLayout(self)
        self.edit = QLineEdit()
        self.edit.setPlaceholderText("تایپ کنید… (مثلاً «خروجی»)")
        self.list = QListWidget()
        self.list.setEditTriggers(QAbstractItemView.NoEditTriggers)
        v.addWidget(self.edit)
        v.addWidget(self.list)
        self.edit.textChanged.connect(self._fill)
        self.edit.returnPressed.connect(self._run)
        self.list.itemDoubleClicked.connect(lambda *a: self._run())
        self._fill("")

    def _fill(self, txt: str):
        self.list.clear()
        for name, _ in self.actions:
            if txt in name:
                self.list.addItem(name)
        if self.list.count():
            self.list.setCurrentRow(0)

    def _run(self):
        cur = self.list.currentItem()
        if not cur: return
        for name, fn in self.actions:
            if name == cur.text():
                self.hide()
                fn()
                return