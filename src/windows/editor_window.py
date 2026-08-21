import os
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QFileDialog, 
    QMessageBox, QShortcut, QApplication, QUndoStack 
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QKeySequence 
from src.ui.widgets.tool_rail import ToolRail
from src.ui.widgets.header_bar import HeaderBar

# اصلاح: import مستقیم و بدون try-except
from src.ui.widgets.status_strip import StatusStrip

from src.ui.widgets.inspector_panel import InspectorPanel
from src.ui.widgets.library_panel import LibraryPanel
from src.ui.widgets.toast import Toast
from src.ui.widgets.command_palette import CommandPalette
from src.ui.dialogs.tag_dialog import TagDialog
from src.ui.graphics.canvas import ModernCanvas
from src.config.theme import ThemeManager, apply_theme_to_app, build_qss

class ModernMainWindow(QMainWindow):
    def __init__(self, canvas_file=None):
        super().__init__()

# اصلاح حیاتی: مدیریت خطای StatusStrip
try:
    from src.ui.widgets.status_strip import StatusStrip
except ImportError:
    import warnings
    warnings.warn("کلاس StatusStrip در فایل status_strip.py یافت نشد. در حال استفاده از کلاس جایگزین (Mock).")
    # کلاس موقتی برای جلوگیری از کرش
    class MockButton:
        def toggle(self): pass

    class StatusStrip(QWidget):
        grid_toggled = pyqtSignal(bool)
        snap_toggled = pyqtSignal(bool)
        def __init__(self, parent=None):
            super().__init__(parent)
            self.grid_btn = MockButton()
            self.snap_btn = MockButton()
            self.grid_enabled = False
            self.snap_enabled = False
        def set_coords(self, *args): pass
        def set_hint(self, *args): pass

from src.ui.widgets.inspector_panel import InspectorPanel
from src.ui.widgets.library_panel import LibraryPanel
from src.ui.widgets.toast import Toast
from src.ui.widgets.command_palette import CommandPalette
from src.ui.dialogs.tag_dialog import TagDialog
from src.ui.graphics.canvas import ModernCanvas
from src.config.theme import ThemeManager, apply_theme_to_app, build_qss

class ModernMainWindow(QMainWindow):
    def __init__(self, canvas_file=None):
        super().__init__()
        self.setLayoutDirection(Qt.RightToLeft)
        self.setWindowTitle("چیدمان — ویرایشگر چیدمان خانه")
        self.resize(1280, 800)
        self.setStyleSheet(build_qss())
        self.canvas_file = canvas_file
        self.project_id = None
        self.db = None
        self.undo_stack = QUndoStack(self)
        self._dirty = False
        root = QWidget()
        vbox = QVBoxLayout(root)
        vbox.setContentsMargins(0, 0, 0, 0)
        vbox.setSpacing(0)
        self.header = HeaderBar()
        vbox.addWidget(self.header)
        body = QHBoxLayout()
        body.setSpacing(0)
        self.rail = ToolRail()
        self.library = LibraryPanel()
        self.canvas = ModernCanvas(self.undo_stack)
        self.inspector = InspectorPanel(self.canvas)
        body.addWidget(self.rail)
        body.addWidget(self.library)
        body.addWidget(self.canvas, 1)
        body.addWidget(self.inspector)
        vbox.addLayout(body)
        self.strip = StatusStrip()
        vbox.addWidget(self.strip)
        self.setCentralWidget(root)
        self.toast = Toast(self.centralWidget())
        self.palette = CommandPalette(self._palette_actions(), self)
        self.undo_stack.cleanChanged.connect(lambda c: self.header.set_saved(c))
        self.undo_stack.indexChanged.connect(self.inspector.reload)
        self.rail.tool_changed.connect(self._tool_changed)
        self.header.undo_clicked.connect(self.undo_stack.undo)
        self.header.redo_clicked.connect(self.undo_stack.redo)
        self.header.zoom_in.connect(lambda: self.canvas.zoom_by(1.2))
        self.header.zoom_out.connect(lambda: self.canvas.zoom_by(1 / 1.2))
        self.header.zoom_fit.connect(self.canvas.zoom_fit)
        self.header.export_clicked.connect(self.export_png)
        self.header.name_changed.connect(lambda n: self.setWindowTitle(f"چیدمان — {n}"))
        self.header.smart_clicked.connect(self.smart_layout_action)
        self.header.theme_toggled.connect(self._toggle_theme)
        self.strip.grid_toggled.connect(lambda on: setattr(self.canvas, 'grid_enabled', on) or self.canvas.viewport().update())
        self.strip.snap_toggled.connect(lambda on: setattr(self.canvas, 'snap_enabled', on))
        self.canvas.zoom_changed.connect(self.header.set_zoom)
        self.canvas.cursor_moved.connect(self.strip.set_coords)
        self.canvas.modified.connect(self._on_modified)
        self.library.add_images_clicked.connect(self.browse_images)
        self.canvas.item_created.connect(self._ask_item_tag)
        self.canvas.request_tag_for_item.connect(self._ask_item_tag)

        def guarded(fn):
            def wrapper():
                fw = QApplication.focusWidget()
                if fw is not None and fw.inherits('QLineEdit'):
                    return
                fn()
            return wrapper

        for key, name in [('V', 'select'), ('H', 'pan'), ('P', 'pen'), ('R', 'rect'),
                          ('I', 'image'), ('M', 'measure')]:
            sc = QShortcut(QKeySequence(key), self)
            sc.activated.connect(guarded(lambda n=name: self._tool_changed(n)))
        sc = QShortcut(QKeySequence("Ctrl+Z"), self)
        sc.activated.connect(guarded(self.undo_stack.undo))
        sc = QShortcut(QKeySequence("Ctrl+Y"), self)
        sc.activated.connect(guarded(self.undo_stack.redo))
        sc = QShortcut(QKeySequence("Delete"), self)
        sc.activated.connect(guarded(self.canvas.delete_selected))
        sc = QShortcut(QKeySequence("Ctrl+D"), self)
        sc.activated.connect(guarded(self.canvas.duplicate_selected))
        sc = QShortcut(QKeySequence("Ctrl+S"), self)
        sc.activated.connect(self.save_design)
        sc = QShortcut(QKeySequence("Ctrl+K"), self)
        sc.activated.connect(self.palette.exec_)
        if canvas_file and os.path.exists(canvas_file):
            self.canvas.load(canvas_file)
            self.undo_stack.setClean()

    def _toggle_theme(self):
        ThemeManager.get_instance().toggle_theme()
        apply_theme_to_app()
        self.canvas.viewport().update()
        self.toast.show_message("تم تغییر کرد")

    def _tool_changed(self, name: str):
        self.rail.set_tool(name)
        self.canvas.set_tool(name)
        self.strip.set_hint(self.canvas.HINTS.get(name, ""))

    def _on_modified(self):
        self._dirty = True
        self.header.set_saved(False)

    def browse_images(self):
        files, _ = QFileDialog.getOpenFileNames(self, "انتخاب تصاویر", "", "Images (*.png *.jpg *.jpeg *.bmp)")
        for f in files:
            self.library.add_user_image(f)

    def _ask_item_tag(self, item):
        dlg = TagDialog(self)
        if dlg.exec_() == TagDialog.Accepted:
            tag = dlg.selected_tag()
            item.setData(1, tag)
            self.canvas.apply_tag_visual(item)
            self.canvas.set_modified()

    def smart_layout_action(self):
        tm = ThemeManager.get_instance()
        if self.canvas.smart_layout():
            self.toast.show_message("✓ چیدمان هوشمند انجام شد.")
        else:
            self.toast.show_message("آیتم تگ‌دار یا محدوده‌ای برای چیدمان پیدا نشد.", tm.colors['warn'])

    def save_design(self) -> bool:
        tm = ThemeManager.get_instance()
        if not self.canvas_file:
            path, _ = QFileDialog.getSaveFileName(self, "ذخیره طرح", "طرح.json", "JSON (*.json)")
            if not path:
                return False
            self.canvas_file = path
        try:
            self.canvas.save(self.canvas_file)
        except Exception as ex:
            self.toast.show_message(f"خطا در ذخیره: {ex}", tm.colors['danger'])
            return False
        self._dirty = False
        self.undo_stack.setClean()
        self.header.set_saved(True)
        if self.db and self.project_id:
            p = self.db.get_project(self.project_id)
            if p:
                name = self.header.name_edit.text().strip() or p.name
                self.db.update_project(self.project_id, name, p.style, p.area, self.canvas_file)
        self.toast.show_message("✓ طرح ذخیره شد")
        return True

    def export_png(self):
        path, _ = QFileDialog.getSaveFileName(self, "خروجی تصویر", "چیدمان.png", "PNG (*.png)")
        if path and self.canvas.export_png(path):
            self.toast.show_message("✓ خروجی تصویر ذخیره شد")

    def _palette_actions(self):
        return [
            ("ابزار: انتخاب", lambda: self._tool_changed('select')),
            ("ابزار: رسم مستطیل", lambda: self._tool_changed('rect')),
            ("ابزار: قلم", lambda: self._tool_changed('pen')),
            ("ابزار: اندازه‌گیری", lambda: self._tool_changed('measure')),
            ("چیدمان: هوشمند", self.smart_layout_action),
            ("تم: روز/شب", self._toggle_theme),
            ("نمایش: توری روشن/خاموش", self.strip.grid_btn.toggle),
            ("نمایش: چسبندگی روشن/خاموش", self.strip.snap_btn.toggle),
            ("بزرگ‌نمایی: کل صفحه", self.canvas.zoom_fit),
            ("فایل: ذخیره", self.save_design),
            ("فایل: خروجی PNG", self.export_png),
            ("ویرایش: واگرد", self.undo_stack.undo),
            ("ویرایش: حذف انتخاب‌شده‌ها", self.canvas.delete_selected),
        ]

    def closeEvent(self, e):
        if self._dirty or not self.undo_stack.isClean():
            r = QMessageBox.question(self, "ذخیره‌نشده", "تغییرات ذخیره‌نشده دارید. ذخیره شود؟",
                                     QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel)
            if r == QMessageBox.Cancel:
                e.ignore()
                return
            if r == QMessageBox.Save and not self.save_design():
                e.ignore()
                return
        e.accept()