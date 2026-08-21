from PyQt5.QtWidgets import QWidget, QHBoxLayout, QToolButton
from PyQt5.QtCore import QPointF
from src.utils.icons import icon
from src.config.theme import ThemeManager

class FloatingToolbar(QWidget):
    def __init__(self, canvas):
        super().__init__(canvas)
        self.canvas = canvas
        h = QHBoxLayout(self)
        h.setContentsMargins(4, 4, 4, 4)
        h.setSpacing(2)
        self.setObjectName("FloatingToolbar")

        tm = ThemeManager.get_instance()
        
        def b(name, tip, fn):
            bt = QToolButton()
            bt.setIcon(icon(name, tm.colors['text'], 15))
            bt.setToolTip(tip)
            bt.clicked.connect(fn)
            h.addWidget(bt)
            return bt

        b('copy', 'کپی (Ctrl+D)', canvas.duplicate_selected)
        b('lock', 'قفل/بازکردن', canvas.toggle_lock)
        b('front', 'آوردن به رو', lambda: canvas.set_z(+1))
        b('back', 'بردن به زیر', lambda: canvas.set_z(-1))
        b('settings', 'تگ', canvas.tag_selected)
        b('trash', 'حذف (Delete)', canvas.delete_selected)
        self.hide()

    def reposition(self):
        sel = self.canvas.scene.selectedItems()
        if not sel or self.canvas.tool == 'pan':
            self.hide()
            return
        r = None
        for it in sel:
            r = it.sceneBoundingRect() if r is None else r.united(it.sceneBoundingRect())
        p = self.canvas.mapFromScene(QPointF(r.center().x(), r.top()))
        self.show()
        self.move(int(p.x() - self.width() / 2), max(4, p.y() - self.height() - 10))