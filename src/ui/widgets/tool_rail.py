from PyQt5.QtWidgets import QWidget, QVBoxLayout, QToolButton, QButtonGroup
from PyQt5.QtCore import pyqtSignal, QSize
from src.utils.icons import icon
from src.utils.helpers import fa

class ToolRail(QWidget):
    tool_changed = pyqtSignal(str)
    TOOLS = [('select', 'انتخاب و جابه‌جایی', 'V'), ('pan', 'جابه‌جایی دید (Space)', 'H'),
             ('pen', 'رسم خط / دیوار (Shift=قائمه)', 'P'), ('rect', 'رسم مستطیل', 'R'),
             ('image', 'افزودن تصویر با کلیک', 'I'), ('measure', 'اندازه‌گیری', 'M')]

    def __init__(self):
        super().__init__()
        self.setFixedWidth(52)
        v = QVBoxLayout(self)
        v.setContentsMargins(6, 10, 6, 10)
        v.setSpacing(6)
        self.group = QButtonGroup(self)
        self.group.setExclusive(True)
        self._btns = {}
        for name, tip, key in self.TOOLS:
            b = QToolButton()
            b.setIcon(icon(name))
            b.setIconSize(QSize(20, 20))
            b.setCheckable(True)
            b.setToolTip(f"{tip} — {fa(key)}")
            self.group.addButton(b)
            self._btns[name] = b
            v.addWidget(b)
        self._btns['select'].setChecked(True)
        self.group.buttonClicked.connect(lambda b: self.tool_changed.emit(
            [k for k, v2 in self._btns.items() if v2 == b][0]))

    def set_tool(self, name: str):
        self._btns[name].setChecked(True)