from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QListWidget, QListWidgetItem, 
    QPushButton, QAbstractItemView
)
from PyQt5.QtCore import Qt, pyqtSignal, QSize, QMimeData, QByteArray
from PyQt5.QtGui import QIcon, QPixmap
from src.utils.icons import icon
from src.utils.helpers import fa
from src.utils.assets import asset_path
from src.config.constants import CATALOG

class DraggableList(QListWidget):
    def __init__(self):
        super().__init__()
        self.setViewMode(QListWidget.IconMode)
        self.setIconSize(QSize(56, 56))
        self.setResizeMode(QListWidget.Adjust)
        self.setDragEnabled(True)
        self.setAcceptDrops(False)
        self.setSpacing(4)

    def mimeTypes(self):
        return ['application/x-image-path']

    def mimeData(self, items):
        m = QMimeData()
        if items:
            p = items[0].data(Qt.UserRole)
            if p:
                m.setData('application/x-image-path', QByteArray(p.encode('utf-8')))
        return m

class LibraryPanel(QWidget):
    add_images_clicked = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setFixedWidth(230)
        v = QVBoxLayout(self)
        v.setContentsMargins(12, 12, 12, 12)
        v.setSpacing(8)
        v.addWidget(QLabel("<b>کتابخانه</b>"))
        self.search = QLineEdit()
        self.search.setPlaceholderText("جستجو…")
        self.search.textChanged.connect(self._filter)
        v.addWidget(self.search)
        
        cat_lbl = QLabel("کاتالوگ وسایل (سانتی‌متر)")
        cat_lbl.setObjectName("dim")
        v.addWidget(cat_lbl)
        
        self.catalog = DraggableList()
        self.catalog.setMaximumHeight(190)
        for name, w, h, inner in CATALOG:
            p = asset_path(name, w, h, inner)
            it = QListWidgetItem(QIcon(QPixmap(p)), name)
            it.setData(Qt.UserRole, p)
            it.setToolTip(f"{name} — {fa(w)}×{fa(h)}")
            self.catalog.addItem(it)
        v.addWidget(self.catalog)
        
        user_lbl = QLabel("تصاویر شما")
        user_lbl.setObjectName("dim")
        v.addWidget(user_lbl)
        
        self.user_list = DraggableList()
        self.user_empty = QLabel("هنوز تصویری اضافه نکرده‌اید؛\nفایل را اینجا رها کنید یا + بزنید", self.user_list)
        self.user_empty.setObjectName("dim")
        self.user_empty.setAlignment(Qt.AlignCenter)
        self.user_empty.setGeometry(0, 10, 200, 60)
        self.user_empty.setWordWrap(True)
        v.addWidget(self.user_list, 1)
        
        add = QPushButton("افزودن تصویر")
        add.setIcon(icon('plus', None, 14))
        add.clicked.connect(self.add_images_clicked)
        v.addWidget(add)

    def _filter(self, txt: str):
        for i in range(self.catalog.count()):
            it = self.catalog.item(i)
            it.setHidden(txt not in it.text())

    def add_user_image(self, path: str):
        px = QPixmap(path)
        if px.isNull(): return
        it = QListWidgetItem(QIcon(px.scaled(56, 56, Qt.KeepAspectRatio, Qt.SmoothTransformation)), " ")
        it.setData(Qt.UserRole, path)
        it.setToolTip(path)
        self.user_list.addItem(it)
        self.user_empty.hide()