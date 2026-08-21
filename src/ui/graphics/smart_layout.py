import math
from typing import List, Tuple
from PyQt5.QtCore import QPointF, QRectF
from PyQt5.QtWidgets import QGraphicsScene, QUndoStack, QGraphicsItem, QGraphicsRectItem

from src.core.undo_commands import SmartLayoutCommand
from src.config.constants import TAG_PRESETS

class SmartLayoutEngine:
    @staticmethod
    def execute(scene: QGraphicsScene, undo_stack: QUndoStack) -> bool:
        valid_tags = {key for _, key in TAG_PRESETS}
        tagged = [it for it in scene.items() if it.data(1) in valid_tags]
        if not tagged:
            return False
            
        area_items = [it for it in tagged if it.data(1) == 'area']
        work_items = [it for it in tagged if it.data(1) != 'area']
        if not work_items:
            return False

        if area_items:
            region = QRectF()
            for it in area_items:
                r = it.sceneBoundingRect()
                region = r if region.isNull() else region.united(r)
            region = region.adjusted(40, 40, -40, -40)
        else:
            region = QRectF()
            for it in work_items:
                r = it.sceneBoundingRect()
                region = r if region.isNull() else region.united(r)
            if region.isNull():
                return False
            region = region.adjusted(-250, -250, 250, 250)

        center = region.center()
        changes = []

        def size_of(item: QGraphicsItem) -> Tuple[float, float]:
            br = item.boundingRect()
            s = item.scale() if hasattr(item, "scale") else 1.0
            return br.width() * s, br.height() * s

        def place_center(item: QGraphicsItem, target: QPointF, rot: float = None):
            old_pos = QPointF(item.pos())
            old_rot = item.rotation()
            if rot is not None:
                item.setRotation(rot)
            br = item.sceneBoundingRect()
            delta = target - br.center()
            new_pos = item.pos() + delta
            item.setPos(new_pos)
            changes.append((item, old_pos, QPointF(new_pos), old_rot, item.rotation()))

        def all_tag(tag: str) -> List[QGraphicsItem]:
            return [it for it in work_items if it.data(1) == tag]

        sofas = all_tag("sofa")
        chairs = all_tag("chair")
        tvs = all_tag("tv")
        tables = all_tag("table")
        cabinets = all_tag("cabinet")
        others = all_tag("other")
        
        if len(sofas) > 1: others.extend(sofas[1:])
        if len(tvs) > 1: others.extend(tvs[1:])
        if len(tables) > 1: others.extend(tables[1:])
        if len(cabinets) > 1: others.extend(cabinets[1:])

        sofa = sofas[0] if sofas else None
        tv = tvs[0] if tvs else None
        table = tables[0] if tables else None
        cabinet = cabinets[0] if cabinets else None

        if cabinet:
            w, h = size_of(cabinet)
            place_center(cabinet, QPointF(region.left() + 120 + w / 2, region.top() + 100 + h / 2), 0)

        if sofa:
            sw, sh = size_of(sofa)
            sofa_x = region.left() + max(140, sw / 2 + 90)
            sofa_y = center.y()
            place_center(sofa, QPointF(sofa_x, sofa_y), 0)
            tv_x = None
            tv_w = 0
            if tv:
                tv_w, tv_h = size_of(tv)
                tv_x = region.right() - max(140, tv_w / 2 + 90)
                place_center(tv, QPointF(tv_x, sofa_y), 180)
            if table:
                tw, th = size_of(table)
                table_x = (sofa_x + sw / 2 + tv_x - tv_w / 2) / 2 if tv is not None else sofa_x + sw / 2 + 140 + tw / 2
                place_center(table, QPointF(table_x, sofa_y), 0)
                if chairs:
                    top_y = sofa_y - th / 2 - 95
                    bottom_y = sofa_y + th / 2 + 95
                    top_chairs = chairs[::2]
                    bottom_chairs = chairs[1::2]

                    def place_row(row, y):
                        if not row: return
                        widths = []
                        total = 0
                        for ch in row:
                            cw, _ = size_of(ch)
                            widths.append(cw)
                            total += cw + 60
                        total -= 60
                        x = table_x - total / 2
                        for ch, cw in zip(row, widths):
                            place_center(ch, QPointF(x + cw / 2, y), 0)
                            x += cw + 60

                    place_row(top_chairs, top_y)
                    place_row(bottom_chairs, bottom_y)
            else:
                if chairs:
                    x = sofa_x + sw / 2 + 150
                    for i, ch in enumerate(chairs):
                        cw, chh = size_of(ch)
                        y = sofa_y + (i - (len(chairs) - 1) / 2) * (chh + 60)
                        place_center(ch, QPointF(x, y), 0)
        else:
            base = center
            if table:
                place_center(table, base, 0)
            if tv:
                tv_w, tv_h = size_of(tv)
                place_center(tv, QPointF(region.right() - 120 - tv_w / 2, base.y()), 180)
            if chairs:
                n = len(chairs)
                for i, ch in enumerate(chairs):
                    angle = i * (2 * math.pi / max(1, n))
                    pos = QPointF(base.x() + math.cos(angle) * 230, base.y() + math.sin(angle) * 190)
                    place_center(ch, pos, 0)

        x = region.left() + 120
        y = region.bottom() - 200
        max_h = 0
        for it in others:
            w, h = size_of(it)
            if x + w > region.right() - 120:
                x = region.left() + 120
                y += max_h + 80
                max_h = 0
            place_center(it, QPointF(x + w / 2, y - h / 2), 0)
            x += w + 80
            max_h = max(max_h, h)

        if changes:
            undo_stack.push(SmartLayoutCommand(changes))
            return True
        return False