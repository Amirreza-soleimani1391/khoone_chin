from PyQt5.QtWidgets import QGraphicsPixmapItem, QGraphicsItem, QGraphicsScene
from PyQt5.QtCore import Qt, QPointF
from PyQt5.QtGui import QPixmap
from src.utils.assets import load_optimized_pixmap

class EditablePixmapItem(QGraphicsPixmapItem):
    def __init__(self, pixmap: QPixmap, parent=None):
        super().__init__(pixmap, parent)
        self.setFlags(
            QGraphicsItem.ItemIsMovable |
            QGraphicsItem.ItemIsSelectable |
            QGraphicsItem.ItemSendsScenePositionChanges
        )
        self.setTransformationMode(Qt.SmoothTransformation)
        self._locked = False

    def is_locked(self) -> bool:
        return self._locked

    def set_locked(self, locked: bool):
        self._locked = locked
        flags = self.flags()
        if locked:
            flags &= ~QGraphicsItem.ItemIsMovable
        else:
            flags |= QGraphicsItem.ItemIsMovable
        self.setFlags(flags)

    def rotate_item(self, angle: float):
        if not self._locked:
            self.setRotation(self.rotation() + angle)

    def scale_item(self, factor: float):
        if not self._locked:
            self.setScale(self.scale() * factor)

    def to_dict(self) -> dict:
        return {
            'type': 'image', 'path': self.data(0),
            'x': self.pos().x(), 'y': self.pos().y(),
            'rotation': self.rotation(), 'scale': self.scale(),
            'locked': self.is_locked(), 'z': self.zValue()
        }

    @classmethod
    def from_dict(cls, data: dict, scene: QGraphicsScene):
        path = data.get('path')
        if not path:
            return None
        pixmap = load_optimized_pixmap(path)
        if pixmap.isNull():
            return None
        item = cls(pixmap)
        item.setData(0, path)
        item.setPos(QPointF(data.get('x', 0), data.get('y', 0)))
        item.setRotation(data.get('rotation', 0))
        item.setScale(data.get('scale', 1.0))
        item.set_locked(data.get('locked', False))
        item.setZValue(data.get('z', 0))
        scene.addItem(item)
        return item