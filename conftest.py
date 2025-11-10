import os
import sys

# Добавляем каталог service/ в PYTHONPATH, чтобы импорты apps работали из корня
PROJECT_ROOT = os.path.dirname(__file__)
SERVICE_DIR = os.path.join(PROJECT_ROOT, "service")
if SERVICE_DIR not in sys.path:
    sys.path.insert(0, SERVICE_DIR)
