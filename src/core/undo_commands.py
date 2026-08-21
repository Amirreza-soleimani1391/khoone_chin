from PyQt5.QtWidgets import QUndoCommand, QGraphicsScene, QGraphicsItem
from PyQt5.QtCore import QPointF
from typing import List, Tuple

class AddCommand(QUndoCommand):
    def __init__(self, scene: QGraphicsScene, item: QGraphicsItem):
        super().__init__("افزودن")
        self.scene = scene
        self.item = item
        self.z_value = item.zValue()

    def undo(self):
        if self.item.scene() is not None:
            self.scene.removeItem(self.item)

    def redo(self):
        if self.item.scene() is None:
            self.scene.addItem(self.item)
            self.item.setZValue(self.z_value)

class DeleteCommand(QUndoCommand):
    def __init__(self, scene: QGraphicsScene, items: List[QGraphicsItem]):
        super().__init__("حذف")
        self.scene = scene
        self.items = list(items)
        self.z_values = [i.zValue() for i in self.items]
        self.positions = [i.pos() for i in self.items]

    def undo(self):
        for i, z, p in zip(self.items, self.z_values, self.positions):
            if i.scene() is None:
                self.scene.addItem(i)
                i.setZValue(z)
                i.setPos(p)

    def redo(self):
        for i in self.items:
            if i.scene() is not None:
                self.scene.removeItem(i)

class MoveCommand(QUndoCommand):
    def __init__(self, moves: List[Tuple[QGraphicsItem, QPointF, QPointF]]):
        super().__init__("جابه‌جایی")
        self.moves = moves

    def undo(self):
        for it, old, _ in self.moves:
            it.setPos(old)

    def redo(self):
        for it, _, new in self.moves:
            it.setPos(new)

class SmartLayoutCommand(QUndoCommand):
    def __init__(self, changes: List[Tuple[QGraphicsItem, QPointF, QPointF, float, float]]):
        super().__init__("چیدمان هوشمند")
        self.changes = changes

    def undo(self):
        for item, old_pos, new_pos, old_rot, new_rot in self.changes:
            item.setPos(old_pos)
            item.setRotation(old_rot)

    def redo(self):
        for item, old_pos, new_pos, old_rot, new_rot in self.changes:
            item.setPos(new_pos)
            item.setRotation(new_rot)