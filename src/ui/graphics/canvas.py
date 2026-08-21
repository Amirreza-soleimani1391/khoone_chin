import json
import math
from PyQt5.QtWidgets import (
    QGraphicsView, QGraphicsScene, QGraphicsItem, QGraphicsRectItem, 
    QGraphicsLineItem, QGraphicsItemGroup, QGraphicsSimpleTextItem, QFileDialog
)
from PyQt5.QtCore import Qt, pyqtSignal, QPointF, QRectF, QLineF
from PyQt5.QtWidgets import QUndoStack
from PyQt5.QtGui import QPainter, QPen, QColor, QBrush, QImage

from src.config.theme import ThemeManager
from src.config.constants import TAG_COLORS
from src.core.undo_commands import AddCommand, DeleteCommand, MoveCommand
from src.ui.graphics.items import EditablePixmapItem
from src.ui.graphics.smart_layout import SmartLayoutEngine
from src.ui.widgets.floating_toolbar import FloatingToolbar
from src.utils.helpers import fa
from src.utils.assets import load_optimized_pixmap

class ModernCanvas(QGraphicsView):
    zoom_changed = pyqtSignal(float)
    cursor_moved = pyqtSignal(float, float)
    modified = pyqtSignal()
    item_created = pyqtSignal(object)
    request_tag_for_item = pyqtSignal(object)

    HINTS = {
        'select': "کلیک: انتخاب | درگ: جابه‌جایی | Space یا کلیک وسط: پن | Ctrl+Wheel: زوم",
        'pan': "برای جابه‌جایی دید بکشید",
        'pen': "کلیک و بکشید تا خط رسم شود | Shift: زاویه‌ی قائمه",
        'rect': "برای رسم مستطیل بکشید؛ ابعاد زنده نمایش داده می‌شود",
        'image': "برای قرار دادن تصویر، کلیک کنید",
        'measure': "دو نقطه را کلیک کنید تا فاصله به سانتی‌متر نمایش یابد"
    }

    def __init__(self, undo_stack: QUndoStack):
        super().__init__()
        self.undo_stack = undo_stack
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        self.scene.setSceneRect(-2000, -2000, 4000, 4000)
        self.setRenderHint(QPainter.Antialiasing)
        self.setAcceptDrops(True)
        self.setMouseTracking(True)
        self.setObjectName("ModernCanvas")
        self.tool = 'select'
        self.grid_enabled = True
        self.snap_enabled = True
        self._guides = []
        self._badge = False
        self._space = False
        self._pan_anchor = None
        self._measure_p1 = None
        self._last_cursor = None
        self._move_start = {}
        self._rubber = None
        self._pen_line = None
        self._pen_start = None
        self._rect_start = None
        self.toolbar = FloatingToolbar(self)
        self.scene.selectionChanged.connect(self.toolbar.reposition)
        self.undo_stack.indexChanged.connect(self.toolbar.reposition)

    def _default_cursor(self):
        if self._space or self._pan_anchor is not None or self.tool == 'pan':
            return Qt.OpenHandCursor
        if self.tool in ('pen', 'rect', 'image', 'measure'):
            return Qt.CrossCursor
        return Qt.ArrowCursor

    def set_tool(self, name: str):
        if self._rubber is not None:
            self.scene.removeItem(self._rubber)
            self._rubber = None
        if self._pen_line is not None:
            ln = self._pen_line
            self._pen_line = None
            ln.setFlag(QGraphicsItem.ItemIsSelectable, True)
            ln.setFlag(QGraphicsItem.ItemIsMovable, True)
            self.undo_stack.push(AddCommand(self.scene, ln))
            self.set_modified()
        self._measure_p1 = None
        self._badge = False
        self._guides = []
        self.tool = name
        self.setDragMode(QGraphicsView.ScrollHandDrag if name == 'pan' else QGraphicsView.NoDrag)
        self.setCursor(self._default_cursor())
        self.toolbar.reposition()

    def wheelEvent(self, e):
        if e.modifiers() & Qt.ControlModifier:
            self.zoom_by(1.15 if e.angleDelta().y() > 0 else 1 / 1.15)
        else:
            super().wheelEvent(e)

    def zoom_by(self, f: float):
        z = self.transform().m11()
        if not (0.1 < z * f < 8):
            return
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.scale(f, f)
        self.zoom_changed.emit(self.transform().m11())

    def zoom_fit(self):
        r = self.scene.itemsBoundingRect()
        if r.isNull():
            r = QRectF(-400, -300, 800, 600)
        self.fitInView(r.adjusted(-60, -60, 60, 60), Qt.KeepAspectRatio)
        self.zoom_changed.emit(self.transform().m11())

    def drawBackground(self, p: QPainter, rect: QRectF):
        super().drawBackground(p, rect)
        if not self.grid_enabled:
            return
        z = self.transform().m11()
        step = 25.0
        while step * z < 14: step *= 2
        while step * z > 56: step /= 2
        vr = self.mapToScene(self.viewport().rect()).boundingRect()
        p.setPen(Qt.NoPen)
        p.setBrush(QColor('#3a3e48'))
        r = 1.3 / z
        x0, x1 = math.floor(vr.left() / step) * step, math.ceil(vr.right() / step) * step
        y0, y1 = math.floor(vr.top() / step) * step, math.ceil(vr.bottom() / step) * step
        if (x1 - x0) / step * (y1 - y0) / step > 10000: return
        x = x0
        while x < x1:
            y = y0
            while y < y1:
                p.drawEllipse(QPointF(x, y), r, r)
                y += step
            x += step

    def drawForeground(self, p: QPainter, rect: QRectF):
        super().drawForeground(p, rect)
        t = ThemeManager.get_instance().colors
        z = self.transform().m11()
        if self._guides:
            p.setPen(QPen(ThemeManager.get_instance().accent, 1.2 / z))
            for g in self._guides:
                if g[0] == 'V':
                    p.drawLine(QLineF(g[1], g[2], g[1], g[3]))
                else:
                    p.drawLine(QLineF(g[2], g[1], g[3], g[1]))
        if self._measure_p1 is not None:
            p.setPen(QPen(QColor(t['dim']), 1 / z, Qt.DashLine))
            p.drawLine(self._measure_p1, self._last_cursor or self._measure_p1)
        if self._badge:
            sel = self.scene.selectedItems()
            if len(sel) == 1:
                r = sel[0].sceneBoundingRect()
                txt = fa(f"{r.width():.0f}") + " × " + fa(f"{r.height():.0f}")
                font = p.font()
                font.setPixelSize(int(12 / z))
                p.setFont(font)
                tw = p.fontMetrics().boundingRect(txt).width()
                br = QRectF(r.center().x() - tw / 2 - 8 / z, r.bottom() + 10 / z, tw + 16 / z, 22 / z)
                p.setPen(QPen(QColor(t['border']), 1 / z))
                p.setBrush(QColor(t['elev']))
                p.drawRoundedRect(br, 6 / z, 6 / z)
                p.setPen(QPen(QColor(t['text']), 1 / z))
                p.drawText(br, Qt.AlignCenter, txt)

    def _update_guides(self):
        sel = [i for i in self.scene.selectedItems() if isinstance(i, (EditablePixmapItem, QGraphicsRectItem))]
        others = [i for i in self.scene.items() if i not in sel and isinstance(i, (EditablePixmapItem, QGraphicsRectItem)) and i.isVisible()]
        self._guides = []
        if not sel or not others: return
        sel_rect = QRectF()
        for it in sel:
            sel_rect = it.sceneBoundingRect() if sel_rect.isNull() else sel_rect.united(it.sceneBoundingRect())
        thr = 6.0 / self.transform().m11()
        dx = dy = None
        for o in others:
            q = o.sceneBoundingRect()
            for mv, tv in [(sel_rect.center().x(), q.center().x()), (sel_rect.left(), q.left()), (sel_rect.right(), q.right()), (sel_rect.left(), q.right()), (sel_rect.right(), q.left())]:
                d = tv - mv
                if abs(d) < thr and (dx is None or abs(d) < abs(dx)): dx = d
            for mv, tv in [(sel_rect.center().y(), q.center().y()), (sel_rect.top(), q.top()), (sel_rect.bottom(), q.bottom()), (sel_rect.top(), q.bottom()), (sel_rect.bottom(), q.top())]:
                d = tv - mv
                if abs(d) < thr and (dy is None or abs(d) < abs(dy)): dy = d
        if dx is not None:
            self._guides.append(('V', sel_rect.center().x() + dx, sel_rect.top() - 40, sel_rect.bottom() + 40))
        if dy is not None:
            self._guides.append(('H', sel_rect.center().y() + dy, sel_rect.left() - 40, sel_rect.right() + 40))
        if (dx is not None or dy is not None) and self.snap_enabled:
            for it in sel:
                it.setPos(it.pos() + QPointF(dx if dx is not None else 0, dy if dy is not None else 0))

    def mousePressEvent(self, e):
        if e.button() == Qt.MiddleButton or self._space:
            self._pan_anchor = e.pos()
            self.setCursor(Qt.ClosedHandCursor)
            e.accept()
            return
        if self.tool == 'select' and e.button() == Qt.LeftButton:
            super().mousePressEvent(e)
            self._move_start = {it: QPointF(it.pos()) for it in self.scene.selectedItems()}
            self._badge = True
            return
        if self.tool == 'pen' and e.button() == Qt.LeftButton:
            p = self.mapToScene(e.pos())
            t = ThemeManager.get_instance().colors
            self._pen_start = p
            self._pen_line = self.scene.addLine(p.x(), p.y(), p.x(), p.y(), QPen(QColor(t['warn']), 3))
        elif self.tool == 'rect' and e.button() == Qt.LeftButton:
            self._rect_start = self.mapToScene(e.pos())
            self._rubber = QGraphicsRectItem(0, 0, 0, 0)
            self._rubber.setPen(QPen(ThemeManager.get_instance().accent, 1.5, Qt.DashLine))
            self._rubber.setBrush(QBrush(QColor(45, 212, 191, 35)))
            self.scene.addItem(self._rubber)
        elif self.tool == 'image' and e.button() == Qt.LeftButton:
            path, _ = QFileDialog.getOpenFileName(self, "انتخاب تصویر", "", "Images (*.png *.jpg *.jpeg *.bmp)")
            if path:
                self.add_image(path, self.mapToScene(e.pos()))
        elif self.tool == 'measure' and e.button() == Qt.LeftButton:
            p = self.mapToScene(e.pos())
            if self._measure_p1 is None:
                self._measure_p1 = p
            else:
                self._finish_measure(p)
        super().mousePressEvent(e)

    def mouseMoveEvent(self, e):
        sc = self.mapToScene(e.pos())
        self._last_cursor = sc
        self.cursor_moved.emit(sc.x(), sc.y())
        if self._pan_anchor is not None:
            d = e.pos() - self._pan_anchor
            self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() - d.x())
            self.verticalScrollBar().setValue(self.verticalScrollBar().value() - d.y())
            e.accept()
            return
        if self.tool == 'pen' and self._pen_line:
            end = sc
            if e.modifiers() & Qt.ShiftModifier:
                dx, dy = end.x() - self._pen_start.x(), end.y() - self._pen_start.y()
                ang = round(math.atan2(dy, dx) / (math.pi / 4)) * (math.pi / 4)
                L = math.hypot(dx, dy)
                end = self._pen_start + QPointF(math.cos(ang) * L, math.sin(ang) * L)
            self._pen_line.setLine(self._pen_start.x(), self._pen_start.y(), end.x(), end.y())
        elif self.tool == 'rect' and self._rubber:
            self._rubber.setRect(QRectF(self._rect_start, sc).normalized())
        elif self.tool == 'select' and self._badge:
            super().mouseMoveEvent(e)
            self._update_guides()
            return
        super().mouseMoveEvent(e)

    def mouseReleaseEvent(self, e):
        if self._pan_anchor is not None:
            self._pan_anchor = None
            self.setCursor(self._default_cursor())
        if self.tool == 'select' and self._badge:
            self._badge = False
            self._guides = []
            moves = [(it, old, QPointF(it.pos())) for it, old in self._move_start.items() if old != it.pos()]
            if moves:
                self.undo_stack.push(MoveCommand(moves))
                self.set_modified()
            self.viewport().update()
            self.toolbar.reposition()
        elif self.tool == 'pen' and self._pen_line:
            ln = self._pen_line
            self._pen_line = None
            ln.setFlag(QGraphicsItem.ItemIsSelectable, True)
            ln.setFlag(QGraphicsItem.ItemIsMovable, True)
            self.undo_stack.push(AddCommand(self.scene, ln))
            self.set_modified()
        elif self.tool == 'rect' and self._rubber:
            r = self._rubber.rect()
            self.scene.removeItem(self._rubber)
            self._rubber = None
            if r.width() > 5 and r.height() > 5:
                it = QGraphicsRectItem(0, 0, r.width(), r.height())
                it.setPos(r.topLeft())
                it.setBrush(QBrush(QColor('#414a5a')))
                it.setPen(QPen(QColor('#aeb6c4'), 2))
                it.setFlag(QGraphicsItem.ItemIsSelectable, True)
                it.setFlag(QGraphicsItem.ItemIsMovable, True)
                it.setData(1, 'other')
                self.scene.addItem(it)
                self.undo_stack.push(AddCommand(self.scene, it))
                self.set_modified()
                self.scene.clearSelection()
                it.setSelected(True)
                self.item_created.emit(it)
        super().mouseReleaseEvent(e)

    def keyPressEvent(self, e):
        if e.key() == Qt.Key_Space:
            self._space = True
            self.setCursor(Qt.OpenHandCursor)
        super().keyPressEvent(e)

    def keyReleaseEvent(self, e):
        if e.key() == Qt.Key_Space:
            self._space = False
            self.setCursor(self._default_cursor())
        super().keyReleaseEvent(e)

    def scrollContentsBy(self, dx: int, dy: int):
        super().scrollContentsBy(dx, dy)
        self.toolbar.reposition()

    def resizeEvent(self, e):
        super().resizeEvent(e)
        self.toolbar.reposition()

    @staticmethod
    def _is_locked(it: QGraphicsItem) -> bool:
        if isinstance(it, EditablePixmapItem):
            return it.is_locked()
        return not bool(it.flags() & QGraphicsItem.ItemIsMovable)

    def tag_selected(self):
        sel = self.scene.selectedItems()
        if sel:
            self.request_tag_for_item.emit(sel[0])

    def apply_tag_visual(self, item: QGraphicsItem):
        tag = item.data(1) or 'other'
        if isinstance(item, QGraphicsRectItem):
            color = QColor(TAG_COLORS.get(tag, TAG_COLORS['other']))
            fill = QColor(color)
            fill.setAlpha(70)
            if tag == 'area':
                item.setBrush(QBrush(QColor(45, 212, 191, 25)))
                item.setPen(QPen(QColor(TAG_COLORS['area']), 2, Qt.DashLine))
            else:
                item.setBrush(QBrush(fill))
                item.setPen(QPen(color, 2))

    def smart_layout(self) -> bool:
        if SmartLayoutEngine.execute(self.scene, self.undo_stack):
            self.set_modified()
            self.toolbar.reposition()
            return True
        return False

    def add_image(self, path: str, pos: QPointF = None):
        px = load_optimized_pixmap(path)
        if px.isNull(): return
        it = EditablePixmapItem(px)
        it.setData(0, path)
        self.scene.addItem(it)
        it.setPos(pos or self.mapToScene(self.viewport().rect().center()))
        self.undo_stack.push(AddCommand(self.scene, it))
        self.set_modified()

    def delete_selected(self):
        items = [it for it in self.scene.selectedItems() if not self._is_locked(it)]
        if items:
            self.undo_stack.push(DeleteCommand(self.scene, items))
            self.set_modified()

    def duplicate_selected(self):
        changed = False
        for it in list(self.scene.selectedItems()):
            if self._is_locked(it): continue
            if isinstance(it, EditablePixmapItem):
                d = it.to_dict()
                d['x'] += 20
                d['y'] += 20
                d['z'] = it.zValue() + 1
                new = EditablePixmapItem.from_dict(d, self.scene)
                if new:
                    self.undo_stack.push(AddCommand(self.scene, new))
                    changed = True
            elif isinstance(it, QGraphicsRectItem):
                n = QGraphicsRectItem(it.rect())
                n.setPos(it.pos() + QPointF(20, 20))
                n.setBrush(it.brush())
                n.setPen(it.pen())
                n.setZValue(it.zValue() + 1)
                n.setFlag(QGraphicsItem.ItemIsSelectable, True)
                n.setFlag(QGraphicsItem.ItemIsMovable, True)
                n.setData(1, it.data(1))
                self.scene.addItem(n)
                self.undo_stack.push(AddCommand(self.scene, n))
                changed = True
        if changed:
            self.set_modified()

    def toggle_lock(self):
        for it in self.scene.selectedItems():
            if isinstance(it, EditablePixmapItem):
                it.set_locked(not it.is_locked())
            else:
                it.setFlag(QGraphicsItem.ItemIsMovable, not bool(it.flags() & QGraphicsItem.ItemIsMovable))

    def set_z(self, d: int):
        for it in self.scene.selectedItems():
            it.setZValue(it.zValue() + d)

    def _build_measure(self, p1: QPointF, p2: QPointF) -> QGraphicsItemGroup:
        t = ThemeManager.get_instance().colors
        grp = QGraphicsItemGroup()
        ln = QGraphicsLineItem(p1.x(), p1.y(), p2.x(), p2.y())
        ln.setPen(QPen(QColor(t['dim']), 2, Qt.DashLine))
        txt = QGraphicsSimpleTextItem(fa(int(math.hypot(p2.x() - p1.x(), p2.y() - p1.y()))) + " سانتی‌متر")
        txt.setBrush(QBrush(QColor(t['text'])))
        grp.addToGroup(ln)
        grp.addToGroup(txt)
        txt.setPos(QPointF((p1.x() + p2.x()) / 2, (p1.y() + p2.y()) / 2))
        grp.setFlag(QGraphicsItem.ItemIsSelectable, True)
        grp.setFlag(QGraphicsItem.ItemIsMovable, True)
        return grp

    def _finish_measure(self, p2: QPointF):
        p1 = self._measure_p1
        self._measure_p1 = None
        grp = self._build_measure(p1, p2)
        self.scene.addItem(grp)
        self.undo_stack.push(AddCommand(self.scene, grp))
        self.set_modified()

    def set_modified(self):
        self.modified.emit()

    def dragEnterEvent(self, e):
        if e.mimeData().hasUrls() or e.mimeData().hasFormat('application/x-image-path'):
            e.acceptProposedAction()
        else:
            e.ignore()

    def dragMoveEvent(self, e):
        e.acceptProposedAction()

    def dropEvent(self, e):
        pos = self.mapToScene(e.pos())
        if e.mimeData().hasUrls():
            for u in e.mimeData().urls():
                if u.isLocalFile():
                    self.add_image(u.toLocalFile(), pos)
        elif e.mimeData().hasFormat('application/x-image-path'):
            self.add_image(bytes(e.mimeData().data('application/x-image-path')).decode('utf-8'), pos)
        e.acceptProposedAction()

    def serialize(self) -> list:
        out = []
        for it in self.scene.items():
            if it.parentItem() is not None: continue
            if isinstance(it, EditablePixmapItem):
                out.append(it.to_dict())
            elif isinstance(it, QGraphicsItemGroup):
                ln = next((c for c in it.childItems() if isinstance(c, QGraphicsLineItem)), None)
                if ln is not None:
                    l = ln.line()
                    out.append({'type': 'measure', 'x': it.pos().x(), 'y': it.pos().y(), 'x1': l.x1(), 'y1': l.y1(), 'x2': l.x2(), 'y2': l.y2()})
            elif isinstance(it, QGraphicsRectItem):
                out.append({'type': 'rect', 'x': it.pos().x(), 'y': it.pos().y(), 'w': it.rect().width(), 'h': it.rect().height(), 'color': it.brush().color().name(), 'rotation': it.rotation(), 'z': it.zValue(), 'locked': self._is_locked(it), 'tag': it.data(1) or ''})
            elif isinstance(it, QGraphicsLineItem):
                l = it.line()
                out.append({'type': 'line', 'x1': l.x1(), 'y1': l.y1(), 'x2': l.x2(), 'y2': l.y2(), 'color': it.pen().color().name(), 'width': it.pen().width(), 'z': it.zValue()})
        return out

    def save(self, path: str):
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(self.serialize(), f, ensure_ascii=False)
        self._write_thumb(path)

    def _write_thumb(self, path: str):
        r = self.scene.itemsBoundingRect()
        if r.isNull(): return
        try:
            img = QImage(240, 180, QImage.Format_ARGB32)
            img.fill(Qt.transparent)
            p = QPainter(img)
            p.setRenderHint(QPainter.Antialiasing)
            self.scene.render(p, target=QRectF(img.rect()), source=r.adjusted(-20, -20, 20, 20))
            p.end()
            img.save(path.rsplit('.', 1)[0] + '.thumb.png')
        except Exception:
            pass

    def load(self, path: str) -> bool:
        self.scene.clear()
        self.undo_stack.clear()
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except Exception as ex:
            print(f"Load error: {ex}")
            return False
        for d in data:
            t = d.get('type')
            if t == 'image':
                EditablePixmapItem.from_dict(d, self.scene)
            elif t == 'rect':
                it = QGraphicsRectItem(0, 0, d['w'], d['h'])
                it.setPos(d['x'], d['y'])
                it.setBrush(QBrush(QColor(d['color'])))
                it.setPen(QPen(QColor('#aeb6c4'), 2))
                it.setRotation(d.get('rotation', 0))
                it.setZValue(d.get('z', 0))
                it.setFlag(QGraphicsItem.ItemIsSelectable, True)
                it.setFlag(QGraphicsItem.ItemIsMovable, not d.get('locked', False))
                if d.get('tag'):
                    it.setData(1, d['tag'])
                    self.apply_tag_visual(it)
                self.scene.addItem(it)
            elif t == 'line':
                ln = self.scene.addLine(d['x1'], d['y1'], d['x2'], d['y2'], QPen(QColor(d['color']), d['width']))
                ln.setZValue(d.get('z', 0))
                ln.setFlag(QGraphicsItem.ItemIsSelectable, True)
                ln.setFlag(QGraphicsItem.ItemIsMovable, True)
                self.scene.addItem(ln)
            elif t == 'measure':
                o = QPointF(d.get('x', 0), d.get('y', 0))
                self.scene.addItem(self._build_measure(o + QPointF(d['x1'], d['y1']), o + QPointF(d['x2'], d['y2'])))
        return True

    def export_png(self, path: str) -> bool:
        r = self.scene.itemsBoundingRect()
        if r.isNull(): return False
        r = r.adjusted(-30, -30, 30, 30)
        max_dim = 8000
        if r.width() > max_dim or r.height() > max_dim:
            r = QRectF(r.center().x() - max_dim / 2, r.center().y() - max_dim / 2, max_dim, max_dim)
        img = QImage(r.size().toSize(), QImage.Format_ARGB32)
        img.fill(Qt.transparent)
        p = QPainter(img)
        p.setRenderHint(QPainter.Antialiasing)
        self.scene.render(p, target=QRectF(img.rect()), source=r)
        p.end()
        return img.save(path)