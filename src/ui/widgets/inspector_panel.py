from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QHBoxLayout, QDoubleSpinBox, 
    QCheckBox, QPushButton, QColorDialog, QGraphicsItem, QGraphicsRectItem
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QBrush
from src.ui.graphics.items import EditablePixmapItem

class InspectorPanel(QWidget):
    def __init__(self, canvas):
        super().__init__()
        self.canvas = canvas
        self.setFixedWidth(210)
        v = QVBoxLayout(self)
        v.setContentsMargins(12, 12, 12, 12)
        v.setSpacing(8)
        t = QLabel("<b>ویژگی‌ها</b>")
        v.addWidget(t)
        self.fields = {}
        grid = QVBoxLayout()
        grid.setSpacing(6)
        for key, label, mx in [('x', 'X', 5000), ('y', 'Y', 5000), ('w', 'عرض', 5000),
                               ('h', 'طول', 5000), ('rot', 'چرخش°', 360)]:
            row = QHBoxLayout()
            lb = QLabel(label)
            lb.setFixedWidth(40)
            lb.setObjectName("dim")
            sp = QDoubleSpinBox()
            sp.setRange(-mx, mx)
            sp.setDecimals(1)
            sp.valueChanged.connect(lambda val, k=key: self._apply(k, val))
            row.addWidget(lb)
            row.addWidget(sp)
            grid.addLayout(row)
            self.fields[key] = sp
        v.addLayout(grid)
        self.lock_chk = QCheckBox("قفل")
        self.lock_chk.toggled.connect(self._apply_lock)
        v.addWidget(self.lock_chk)
        self.color_btn = QPushButton("رنگ")
        self.color_btn.clicked.connect(self._pick_color)
        v.addWidget(self.color_btn)
        v.addStretch()
        self._loading = False
        canvas.scene.selectionChanged.connect(self.reload)
        self.reload()

    def _item(self):
        sel = self.canvas.scene.selectedItems()
        return sel[0] if len(sel) == 1 else None

    def reload(self):
        it = self._item()
        self._loading = True
        en = it is not None
        for sp in self.fields.values():
            sp.setEnabled(en)
        self.lock_chk.setEnabled(en)
        self.color_btn.setEnabled(isinstance(it, QGraphicsRectItem))
        if en:
            base = it.boundingRect()
            s = it.scale()
            self.fields['x'].setValue(it.pos().x())
            self.fields['y'].setValue(it.pos().y())
            self.fields['w'].setValue(base.width() * s)
            self.fields['h'].setValue(base.height() * s)
            self.fields['rot'].setValue(it.rotation())
            if isinstance(it, EditablePixmapItem):
                self.lock_chk.setChecked(it.is_locked())
            else:
                self.lock_chk.setChecked(not bool(it.flags() & QGraphicsItem.ItemIsMovable))
        self._loading = False

    def _apply(self, key: str, val: float):
        if self._loading: return
        it = self._item()
        if not it: return
        if key == 'x': it.setX(val)
        elif key == 'y': it.setY(val)
        elif key == 'rot': it.setRotation(val)
        elif key in ('w', 'h'):
            base = it.boundingRect()
            if isinstance(it, QGraphicsRectItem):
                r = it.rect()
                if key == 'w': r.setWidth(max(1, val))
                else: r.setHeight(max(1, val))
                it.setRect(r)
            else:
                it.setScale(max(0.01, val / (base.width() if key == 'w' else base.height())))
        self.canvas.set_modified()

    def _apply_lock(self, on: bool):
        it = self._item()
        if not it or self._loading: return
        if isinstance(it, EditablePixmapItem):
            it.set_locked(on)
        else:
            it.setFlag(QGraphicsItem.ItemIsMovable, not on)

    def _pick_color(self):
        it = self._item()
        if isinstance(it, QGraphicsRectItem):
            c = QColorDialog.getColor(it.brush().color(), self)
            if c.isValid():
                it.setBrush(QBrush(c))
                self.canvas.set_modified()