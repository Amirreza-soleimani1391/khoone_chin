import os  # اصلاح: اضافه شدن ماژول os
import json
import time
from collections import Counter
from datetime import datetime
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QScrollArea,
    QLabel, QLineEdit, QPushButton, QToolButton, QFileDialog, QMessageBox, QDialog
)
from PyQt5.QtCore import Qt, QTimer, QSize
from src.core.database import ProjectDB
from src.models.project import Project
from src.ui.widgets.stat_card import StatCard
from src.ui.widgets.project_card import ProjectCard
from src.ui.widgets.toast import Toast
from src.ui.widgets.command_palette import CommandPalette
from src.ui.dialogs.project_dialog import ProjectDialog
from src.utils.icons import icon
from src.utils.helpers import fa, relative_time
from src.config.theme import ThemeManager, apply_theme_to_app, build_qss
from src.config.settings import get_app_data_dir
from src.windows.editor_window import ModernMainWindow

class HouseDesignerApp(QMainWindow):
    def __init__(self, home_page=None):
        super().__init__()
        self.home_page = home_page
        self.db = ProjectDB()
        self.all_projects = []
        self.setWindowTitle("خونه‌چین — پروژه‌های من")
        self.resize(1100, 720)
        self.setLayoutDirection(Qt.RightToLeft)
        self.setStyleSheet(build_qss())
        self.start_time = datetime.now()
        self.session_timer = QTimer(self)
        self.session_timer.timeout.connect(self._update_session)
        self.session_timer.start(1000)
        self._build_ui()
        self.toast = Toast(self.centralWidget())
        self.palette = CommandPalette(self._palette_actions(), self)
        self.refresh_list()

    def _build_ui(self):
        root = QWidget()
        self.setCentralWidget(root)
        main = QVBoxLayout(root)
        main.setContentsMargins(0, 0, 0, 0)
        main.setSpacing(0)
        main.addWidget(self._build_header())
        body = QWidget()
        body.setObjectName("MainBody")
        bv = QVBoxLayout(body)
        bv.setContentsMargins(24, 20, 24, 16)
        bv.setSpacing(20)
        bv.addWidget(self._build_stats())
        bv.addWidget(self._build_search_bar())
        bv.addWidget(self._build_project_list(), 1)
        main.addWidget(body, 1)

    def _build_header(self):
        header_bar = QWidget()
        header_bar.setFixedHeight(56)
        header_bar.setObjectName("HeaderBar")
        hb = QHBoxLayout(header_bar)
        hb.setContentsMargins(20, 0, 20, 0)
        hb.setSpacing(10)
        logo = QWidget()
        logo.setFixedSize(24, 24)
        logo.setObjectName("logo")
        hb.addWidget(logo)
        title = QLabel("<b style='font-size:16px'>خونه‌چین</b>")
        hb.addWidget(title)
        hb.addStretch()

        tm = ThemeManager.get_instance()

        def tb(name, tip, fn):
            b = QToolButton()
            b.setIcon(icon(name, tm.colors['dim'], 18))
            b.setToolTip(tip)
            b.setIconSize(QSize(18, 18))
            b.clicked.connect(fn)
            hb.addWidget(b)
            return b

        tb('info', 'درباره', self._show_about)
        tb('settings', 'تنظیمات', lambda: self.toast.show_message("تنظیمات به‌زودی…", tm.colors['dim']))
        tb('theme', 'تغییر تم روز/شب', self._toggle_theme)
        add_btn = QPushButton("پروژه جدید")
        add_btn.setCursor(Qt.PointingHandCursor)
        add_btn.setIcon(icon('plus', tm.colors['accent_text'], 15))
        add_btn.setProperty('primary', 'true')
        add_btn.clicked.connect(self.add_new_house)
        hb.addWidget(add_btn)
        return header_bar

    def _build_stats(self):
        grid = QGridLayout()
        grid.setSpacing(12)
        for c in range(3):
            grid.setColumnStretch(c, 1)
        cards = [
            ("تعداد پروژه‌ها", 'project'),
            ("میانگین متراژ", 'chart'),
            ("محبوب‌ترین سبک", 'star'),
            ("آخرین ویرایش", 'clock'),
            ("پروژه‌های بی‌نام", 'folder'),
            ("زمان استفاده", 'clock'),
        ]
        self.stats_cards = {}
        for i, (title, ic) in enumerate(cards):
            card = StatCard(title, ic)
            grid.addWidget(card, i // 3, i % 3)
            self.stats_cards[title] = card
        wrap = QWidget()
        wrap.setLayout(grid)
        return wrap

    def _build_search_bar(self):
        bar = QWidget()
        h = QHBoxLayout(bar)
        h.setContentsMargins(0, 0, 0, 0)
        h.setSpacing(10)
        searchWrap = QWidget()
        searchWrap.setObjectName("SearchWrap")
        sh = QHBoxLayout(searchWrap)
        sh.setContentsMargins(10, 0, 10, 0)
        sh.setSpacing(8)
        tm = ThemeManager.get_instance()
        s_icon = QLabel()
        s_icon.setPixmap(icon('search', tm.colors['dim'], 16).pixmap(16, 16))
        sh.addWidget(s_icon)
        self.search = QLineEdit()
        self.search.setPlaceholderText("جستجو در پروژه‌ها… (نام، سبک، متراژ)")
        self.search.textChanged.connect(self._filter_list)
        sh.addWidget(self.search)
        h.addWidget(searchWrap, 1)

        def tool_btn(name, tip, fn):
            b = QToolButton()
            b.setIcon(icon(name, tm.colors['dim'], 16))
            b.setToolTip(tip)
            b.setIconSize(QSize(16, 16))
            b.setObjectName("tool-btn")
            b.clicked.connect(fn)
            h.addWidget(b)
            return b

        tool_btn('backup', 'پشتیبان‌گیری (Export)', self.export_to_file)
        tool_btn('restore', 'بازیابی (Import)', self.import_from_file)
        return bar

    def _build_project_list(self):
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setObjectName("ProjectScroll")
        self.list_container = QWidget()
        self.list_container.setObjectName("ListContainer")
        self.list_layout = QVBoxLayout(self.list_container)
        self.list_layout.setContentsMargins(0, 0, 0, 0)
        self.list_layout.setSpacing(8)
        self.list_layout.addStretch()
        self.scroll.setWidget(self.list_container)
        self.empty_state = QWidget()
        ev = QVBoxLayout(self.empty_state)
        ev.setAlignment(Qt.AlignCenter)
        ev.setSpacing(12)
        ic = QLabel()
        tm = ThemeManager.get_instance()
        ic.setPixmap(icon('home', tm.colors['dim'], 64).pixmap(64, 64))
        ic.setAlignment(Qt.AlignCenter)
        ev.addWidget(ic)
        t1 = QLabel("هنوز پروژه‌ای نساخته‌اید")
        t1.setObjectName("empty-title")
        t1.setAlignment(Qt.AlignCenter)
        ev.addWidget(t1)
        t2 = QLabel("با دکمه «پروژه جدید» اولین چیدمان خود را بسازید")
        t2.setObjectName("empty-desc")
        t2.setAlignment(Qt.AlignCenter)
        ev.addWidget(t2)
        wrap = QWidget()
        wrap_l = QVBoxLayout(wrap)
        wrap_l.setContentsMargins(0, 0, 0, 0)
        wrap_l.setSpacing(0)
        wrap_l.addWidget(self.scroll)
        wrap_l.addWidget(self.empty_state)
        self.empty_state.hide()
        return wrap

    def refresh_list(self):
        self.all_projects = self.db.get_all_projects()
        self._filter_list()
        self._update_stats()

    def _filter_list(self):
        q = self.search.text().strip().lower()
        filtered = [p for p in self.all_projects if (
            q in (p.name or '').lower() or
            q in (p.style or '').lower() or
            q in (p.area or '').lower()
        )]
        while self.list_layout.count() > 1:
            item = self.list_layout.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()
        self.empty_state.setVisible(not filtered)
        self.scroll.setVisible(bool(filtered))
        for p in filtered:
            # Convert Project dataclass to dict for compatibility with ProjectCard
            p_dict = {
                'id': p.id, 'name': p.name, 'style': p.style, 'area': p.area,
                'canvas_file': p.canvas_file, 'created_at': p.created_at, 'updated_at': p.updated_at
            }
            card = ProjectCard(p_dict)
            card.edit_clicked.connect(self.edit_project)
            card.delete_clicked.connect(self.delete_project)
            card.open_clicked.connect(self.goto_canvas_for_project)
            self.list_layout.insertWidget(self.list_layout.count() - 1, card)

    def _update_stats(self):
        total = len(self.all_projects)
        self.stats_cards["تعداد پروژه‌ها"].set_value(fa(total))
        areas = []
        for p in self.all_projects:
            try:
                if p.area:
                    areas.append(float(p.area))
            except ValueError:
                pass
        if areas:
            self.stats_cards["میانگین متراژ"].set_value(fa(f"{sum(areas) / len(areas):.0f} متر"))
        else:
            self.stats_cards["میانگین متراژ"].set_value("—")
        styles = [(p.style or '').strip() for p in self.all_projects if (p.style or '').strip()]
        if styles:
            most = Counter(styles).most_common(1)[0]
            self.stats_cards["محبوب‌ترین سبک"].set_value(most[0])
        else:
            self.stats_cards["محبوب‌ترین سبک"].set_value("—")
            
        # اصلاح: مدیریت خطای احتمالی دسترسی به کانکشن دیتابیس
        try:
            cursor = self.db.conn.cursor()
            cursor.execute("SELECT updated_at FROM projects ORDER BY updated_at DESC LIMIT 1")
            row = cursor.fetchone()
            if row and row[0]:
                self.stats_cards["آخرین ویرایش"].set_value(relative_time(row[0]))
            else:
                self.stats_cards["آخرین ویرایش"].set_value("—")
        except Exception:
            self.stats_cards["آخرین ویرایش"].set_value("—")
            
        unnamed = sum(1 for p in self.all_projects
                      if not (p.name or '').strip() or p.name == "بدون نام")
        self.stats_cards["پروژه‌های بی‌نام"].set_value(fa(unnamed))

    def _update_session(self):
        delta = int((datetime.now() - self.start_time).total_seconds())
        h = delta // 3600
        m = (delta % 3600) // 60
        s = delta % 60
        self.stats_cards["زمان استفاده"].set_value(fa(f"{h:02d}:{m:02d}:{s:02d}"))

    def _toggle_theme(self):
        ThemeManager.get_instance().toggle_theme()
        apply_theme_to_app()
        if hasattr(self, 'toast'):
            self.toast.show_message("تم تغییر کرد")

    def add_new_house(self):
        tm = ThemeManager.get_instance()
        dlg = ProjectDialog("پروژه جدید", self)
        if dlg.exec_() == QDialog.Accepted:
            vals = dlg.get_values()
            if not vals['name']:
                self.toast.show_message("نام پروژه نمی‌تواند خالی باشد", tm.colors['danger'])
                return
            base_dir = get_app_data_dir()
            canvas_dir = os.path.join(base_dir, 'canvases')
            os.makedirs(canvas_dir, exist_ok=True)
            filename = os.path.join(canvas_dir, f"project_{int(time.time())}.json")
            self.db.add_project(vals['name'], vals['style'], vals['area'], filename)
            self.refresh_list()
            self.toast.show_message("✓ پروژه جدید ایجاد شد")

    def edit_project(self, project: dict):
        tm = ThemeManager.get_instance()
        dlg = ProjectDialog("ویرایش پروژه", self, default=project)
        if dlg.exec_() == QDialog.Accepted:
            vals = dlg.get_values()
            if not vals['name']:
                self.toast.show_message("نام پروژه نمی‌تواند خالی باشد", tm.colors['danger'])
                return
            self.db.update_project(project['id'], vals['name'], vals['style'], vals['area'])
            self.refresh_list()
            self.toast.show_message("✓ اطلاعات به‌روز شد")

    def delete_project(self, project: dict):
        reply = QMessageBox.question(
            self, "حذف پروژه",
            f"آیا از حذف پروژه «{project.get('name')}» اطمینان دارید؟",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.db.delete_project(project['id'])
            self.refresh_list()
            self.toast.show_message("پروژه حذف شد", ThemeManager.get_instance().colors['danger'])

    def goto_canvas_for_project(self, project: dict):
        self.canvas_window = ModernMainWindow(canvas_file=project.get('canvas_file'))
        self.canvas_window.project_id = project['id']
        self.canvas_window.db = self.db
        self.canvas_window.header.name_edit.setText(project.get('name') or "طرح بدون نام")
        self.canvas_window.setAttribute(Qt.WA_DeleteOnClose, True)
        self.canvas_window.destroyed.connect(self._on_canvas_closed)
        self.canvas_window.show()
        self.hide()

    def _on_canvas_closed(self, *args):
        self.refresh_list()
        self.show()
        self.activateWindow()

    def export_to_file(self):
        tm = ThemeManager.get_instance()
        path, _ = QFileDialog.getSaveFileName(self, "پشتیبان‌گیری", "houses_backup.json", "JSON (*.json)")
        if not path: return
        try:
            data = []
            for p in self.db.get_all_projects():
                data.append({
                    'id': p.id, 'name': p.name, 'style': p.style, 'area': p.area,
                    'canvas_file': p.canvas_file, 'created_at': p.created_at, 'updated_at': p.updated_at
                })
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            self.toast.show_message("✓ پشتیبان ذخیره شد")
        except Exception as e:
            self.toast.show_message(f"خطا: {e}", tm.colors['danger'])

    def import_from_file(self):
        tm = ThemeManager.get_instance()
        path, _ = QFileDialog.getOpenFileName(self, "بازیابی", "", "JSON (*.json);;همه فایل‌ها (*)")
        if not path: return
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            count = 0
            for p in data:
                self.db.add_project(
                    p.get('name', ''), p.get('style', ''),
                    p.get('area', ''), p.get('canvas_file', '')
                )
                count += 1
            self.refresh_list()
            self.toast.show_message(f"✓ {fa(count)} پروژه بازیابی شد")
        except Exception as e:
            self.toast.show_message(f"خطا: {e}", tm.colors['danger'])

    def _show_about(self):
        self.toast.show_message("خونه‌چین — سازندگان: تیم حلی ۵")

    def _palette_actions(self):
        return [
            ("پروژه: جدید", self.add_new_house),
            ("فایل: پشتیبان‌گیری", self.export_to_file),
            ("فایل: بازیابی", self.import_from_file),
            ("تم: روز/شب", self._toggle_theme),
            ("جستجو: تمرکز روی فیلد", self.search.setFocus),
            ("نمایش: درباره", self._show_about),
        ]

    def keyPressEvent(self, e):
        if e.key() == Qt.Key_Escape:
            self.close()
        elif e.modifiers() == Qt.ControlModifier and e.key() == Qt.Key_N:
            self.add_new_house()
        elif e.modifiers() == Qt.ControlModifier and e.key() == Qt.Key_K:
            self.palette.exec_()
        elif e.modifiers() == Qt.ControlModifier and e.key() == Qt.Key_F:
            self.search.setFocus()
        else:
            super().keyPressEvent(e)

    def closeEvent(self, e):
        try:
            self.db.close()
        except Exception:
            pass
        super().closeEvent(e)