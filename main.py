import sys
import os

# Ensure the project root is in sys.path for absolute imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QFontDatabase

from src.config.theme import ThemeManager, apply_theme_to_app
from src.windows.manager_window import HouseDesignerApp

def main():
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    app = QApplication(sys.argv)
    app.setOrganizationName("KhooneChin")
    app.setApplicationName("KhooneChin")

    # Initialize Theme Manager
    ThemeManager.get_instance()
    
    # اصلاح: پاس دادن app به تابع تم در صورت نیاز
    try:
        apply_theme_to_app(app)
    except TypeError:
        apply_theme_to_app()

    # Load custom fonts if available
    FONT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts")
    if os.path.isdir(FONT_DIR):
        for f in os.listdir(FONT_DIR):
            if f.endswith(('.ttf', '.otf')):
                QFontDatabase.addApplicationFont(os.path.join(FONT_DIR, f))
    app.setFont(QFont("Vazirmatn", 10))

    window = HouseDesignerApp()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()