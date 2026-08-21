import os
from PyQt5.QtCore import QStandardPaths

def get_app_data_dir() -> str:
    """Returns the application data directory, creating it if it doesn't exist."""
    path = QStandardPaths.writableLocation(QStandardPaths.AppDataLocation)
    app_dir = os.path.join(path, "KhooneChin")
    os.makedirs(app_dir, exist_ok=True)
    return app_dir

def get_config_dir() -> str:
    """Returns the application config directory, creating it if it doesn't exist."""
    path = QStandardPaths.writableLocation(QStandardPaths.ConfigLocation)
    app_dir = os.path.join(path, "KhooneChin")
    os.makedirs(app_dir, exist_ok=True)
    return app_dir

def get_cache_dir() -> str:
    """Returns the application cache directory, creating it if it doesn't exist."""
    path = QStandardPaths.writableLocation(QStandardPaths.CacheLocation)
    app_dir = os.path.join(path, "KhooneChin")
    os.makedirs(app_dir, exist_ok=True)
    return app_dir