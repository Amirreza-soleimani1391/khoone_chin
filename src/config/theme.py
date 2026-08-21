import json
import os
from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QApplication
from src.config.settings import get_config_dir

DARK_T = {
    'bg': '#17181c', 'panel': '#1e2026', 'elev': '#262931', 'border': '#343842',
    'text': '#e8eaf0', 'dim': '#98a0ad', 'accent': '#2dd4bf', 'accent_text': '#0b3b36',
    'danger': '#f87171', 'warn': '#fbbf24', 'ok': '#34d399',
}

LIGHT_T = {
    'bg': '#f4f5f7', 'panel': '#ffffff', 'elev': '#eef0f4', 'border': '#d5d9e0',
    'text': '#1f2328', 'dim': '#6b7280', 'accent': '#0ea5a0', 'accent_text': '#ffffff',
    'danger': '#dc2626', 'warn': '#d97706', 'ok': '#059669',
}

class ThemeManager(QObject):
    _instance = None
    theme_changed = pyqtSignal()

    @classmethod
    def get_instance(cls) -> 'ThemeManager':
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        super().__init__()
        self._config_path = os.path.join(get_config_dir(), 'theme.json')
        self._mode = self._load_mode()
        self._colors = DARK_T if self._mode == 'dark' else LIGHT_T
        self._accent = QColor(self._colors['accent'])

    def _load_mode(self) -> str:
        try:
            with open(self._config_path, 'r', encoding='utf-8') as f:
                mode = json.load(f).get('theme', 'dark')
                return mode if mode in ('dark', 'light') else 'dark'
        except Exception:
            return 'dark'

    @property
    def colors(self) -> dict:
        return self._colors.copy()

    @property
    def accent(self) -> QColor:
        return QColor(self._accent)

    def set_theme(self, mode: str, save: bool = True):
        if mode not in ('dark', 'light'):
            return
        self._mode = mode
        self._colors = DARK_T if mode == 'dark' else LIGHT_T
        self._accent = QColor(self._colors['accent'])
        if save:
            try:
                with open(self._config_path, 'w', encoding='utf-8') as f:
                    json.dump({'theme': mode}, f)
            except Exception:
                pass
        self.theme_changed.emit()

    def toggle_theme(self) -> str:
        new_mode = 'light' if self._mode == 'dark' else 'dark'
        self.set_theme(new_mode)
        return new_mode

def build_qss() -> str:
    t = ThemeManager.get_instance().colors
    return f"""
    * {{ font-family: 'Vazirmatn', 'Segoe UI', Tahoma; }}
    QMainWindow, QWidget {{ background: {t['bg']}; color: {t['text']}; }}
    QWidget#MainBody, QWidget#ListContainer {{ background: {t['bg']}; }}
    QLabel {{ background: transparent; }}
    QLabel.dim, QLabel#dim {{ color: {t['dim']}; }}
    QLabel#saved {{ color: {t['dim']}; }}
    QLabel#saved_warn {{ color: {t['warn']}; }}
    QLabel#empty-title {{ color: {t['text']}; font-size: 16px; font-weight: 600; }}
    QLabel#empty-desc {{ color: {t['dim']}; font-size: 13px; }}
    
    QPushButton {{ background: {t['elev']}; border: 1px solid {t['border']}; border-radius: 8px; padding: 6px 14px; color: {t['text']}; }}
    QPushButton:hover {{ background: {t['border']}; }}
    QPushButton:pressed {{ background: {t['bg']}; }}
    QPushButton[primary="true"] {{ background: {t['accent']}; border: none; color: {t['accent_text']}; font-weight: 700; }}
    QPushButton[primary="true"]:hover {{ opacity: 0.9; }}
    QPushButton#cancel {{ background: {t['elev']}; color: {t['text']}; border: 1px solid {t['border']}; border-radius: 8px; padding: 8px 18px; font-size: 13px; }}
    QPushButton#cancel:hover {{ background: {t['border']}; }}
    QPushButton#ok {{ background: {t['accent']}; color: {t['accent_text']}; border: none; border-radius: 8px; padding: 8px 18px; font-weight: 600; font-size: 13px; }}
    
    QToolButton {{ background: transparent; border: none; border-radius: 8px; color: {t['dim']}; padding: 6px; }}
    QToolButton:hover {{ background: {t['elev']}; color: {t['text']}; }}
    QToolButton:checked {{ background: {t['elev']}; color: {t['accent']}; }}
    QToolButton#tool-btn {{ background: {t['panel']}; border: 1px solid {t['border']}; border-radius: 10px; padding: 8px; }}
    QToolButton#tool-btn:hover {{ background: {t['elev']}; border-color: {t['accent']}; }}
    
    QLineEdit, QSpinBox, QDoubleSpinBox {{ background: {t['panel']}; border: 1px solid {t['border']}; border-radius: 8px; padding: 5px 8px; color: {t['text']}; selection-background-color: {t['accent']}; }}
    QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus {{ border-color: {t['accent']}; }}
    QLineEdit#projectName {{ background: transparent; border: none; font-size: 14px; font-weight: 600; }}
    QLineEdit#projectName:focus {{ background: {t['panel']}; border: 1px solid {t['border']}; }}
    
    QListWidget {{ background: {t['panel']}; border: 1px solid {t['border']}; border-radius: 10px; outline: none; }}
    QListWidget::item:selected {{ background: {t['elev']}; border: 1px solid {t['accent']}; border-radius: 6px; }}
    
    QScrollBar:vertical {{ background: transparent; width: 10px; }}
    QScrollBar::handle:vertical {{ background: {t['border']}; border-radius: 5px; min-height: 30px; }}
    QScrollBar:horizontal {{ background: transparent; height: 10px; }}
    QScrollBar::handle:horizontal {{ background: {t['border']}; border-radius: 5px; min-width: 30px; }}
    QScrollBar::add-line, QScrollBar::sub-line {{ height: 0; width: 0; }}
    
    QMenu {{ background: {t['panel']}; border: 1px solid {t['border']}; border-radius: 8px; padding: 4px; }}
    QMenu::item {{ padding: 6px 24px; border-radius: 5px; }}
    QMenu::item:selected {{ background: {t['elev']}; }}
    
    QToolTip {{ background: {t['elev']}; border: 1px solid {t['border']}; color: {t['text']}; padding: 4px 8px; border-radius: 6px; }}
    
    QFrame[vline="true"] {{ color: {t['border']}; }}
    
    QComboBox {{ background: {t['panel']}; border: 1px solid {t['border']}; border-radius: 8px; padding: 5px 8px; color: {t['text']}; }}
    QComboBox:focus {{ border-color: {t['accent']}; }}
    QComboBox QAbstractItemView {{ background: {t['panel']}; border: 1px solid {t['border']}; color: {t['text']}; selection-background-color: {t['accent']}; }}
    
    QDialog {{ background: {t['panel']}; border-radius: 12px; }}
    QDialog QLabel#head {{ color: {t['text']}; background: transparent; font-size: 16px; font-weight: 600; }}
    QDialog QLabel#field-label {{ color: {t['dim']}; font-size: 12px; }}
    QDialog QLineEdit {{ background: {t['bg']}; border: 1px solid {t['border']}; border-radius: 8px; padding: 9px 12px; color: {t['text']}; font-size: 14px; }}
    QDialog QLineEdit:focus {{ border: 1px solid {t['accent']}; }}
    QDialog QPushButton#cancel {{ background: {t['elev']}; color: {t['text']}; border: 1px solid {t['border']}; border-radius: 8px; padding: 8px 18px; font-size: 13px; }}
    QDialog QPushButton#cancel:hover {{ background: {t['border']}; }}
    QDialog QPushButton#ok {{ background: {t['accent']}; color: {t['accent_text']}; border: none; border-radius: 8px; padding: 8px 18px; font-weight: 600; font-size: 13px; }}
    
    QWidget#logo {{ background: {t['accent']}; border-radius: 5px; }}
    QWidget#HeaderBar {{ background: {t['panel']}; border-bottom: 1px solid {t['border']}; }}
    QWidget#SearchWrap {{ background: {t['panel']}; border: 1px solid {t['border']}; border-radius: 10px; }}
    QWidget#actions {{ background: transparent; }}
    
    StatusStrip {{ background: {t['panel']}; border-top: 1px solid {t['border']}; }}
    
    QFrame#StatCard {{ background: {t['panel']}; border: 1px solid {t['border']}; border-radius: 14px; }}
    QFrame#StatCard:hover {{ background: {t['elev']}; border: 1px solid {t['accent']}; }}
    QLabel#icon-box {{ background: {t['elev']}; border-radius: 8px; }}
    QLabel#title {{ color: {t['dim']}; font-size: 12px; background: transparent; }}
    QLabel#value {{ color: {t['text']}; font-size: 19px; font-weight: 700; background: transparent; }}
    
    QFrame#projectCard {{ background: {t['panel']}; border: 1px solid {t['border']}; border-radius: 12px; }}
    QFrame#projectCard:hover {{ background: {t['elev']}; border: 1px solid {t['accent']}; }}
    QLabel#thumb {{ background: {t['elev']}; border-radius: 10px; border: 1px solid {t['border']}; }}
    QLabel#name {{ color: {t['text']}; font-size: 15px; font-weight: 600; background: transparent; }}
    QLabel#time {{ color: {t['dim']}; font-size: 11px; background: transparent; }}
    QLabel#badge {{ background: {t['accent']}; color: {t['accent_text']}; padding: 2px 10px; border-radius: 10px; font-size: 11px; font-weight: 600; }}
    QLabel#area {{ color: {t['dim']}; font-size: 12px; background: transparent; }}
    QFrame#projectCard QPushButton {{ background: transparent; border: none; border-radius: 6px; }}
    QFrame#projectCard QPushButton:hover {{ background: {t['elev']}; }}
    QFrame#projectCard QPushButton[primary="true"] {{ background: {t['accent']}; border: none; color: {t['accent_text']}; font-weight: 600; font-size: 12px; border-radius: 8px; padding: 7px 14px; }}
    QFrame#projectCard QPushButton[primary="true"]:hover {{ opacity: 0.9; }}
    
    QScrollArea#ProjectScroll {{ border: none; background: {t['bg']}; }}
    QScrollArea#ProjectScroll > QWidget {{ background: {t['bg']}; }}
    
    ModernCanvas {{ background: {t['bg']}; border: none; }}
    FloatingToolbar {{ background: {t['elev']}; border: 1px solid {t['border']}; border-radius: 10px; }}
    """

def apply_theme_to_app():
    app = QApplication.instance()
    if app is None:
        return
    qss = build_qss()
    app.setStyleSheet(qss)
    for w in app.topLevelWidgets():
        w.setStyleSheet(qss)
        w.update()