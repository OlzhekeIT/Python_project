# main.py
from __future__ import annotations

import sys
from pathlib import Path

from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtGui import QFont, QIcon

from views.main_window import MainWindow

def load_stylesheet(app: QApplication) -> None:
    """QSS стилін жүктеу."""
    qss_path = Path(__file__).parent / "resources" / "styles.qss"
    if not qss_path.exists():
        print(f"[warn] styles.qss табылмады: {qss_path}")
        return
    try:
        style = qss_path.read_text(encoding="utf-8")
        app.setStyleSheet(style)
        print("[info] Stylesheet loaded successfully.")
    except Exception as e:
        print(f"[error] Stylesheet loading failed: {e}")

def main() -> int:
    app = QApplication(sys.argv)
    
    # Kaspi брендингі
    app.setApplicationName("Kaspi.kz")
    app.setOrganizationName("Kaspi Bank")
    
    # Стандартты шрифт орнату (Segoe UI Windows үшін жақсы)
    default_font = QFont("Segoe UI", 10)
    app.setFont(default_font)
    
    # Стильді жүктеу
    load_stylesheet(app)

    # Негізгі терезе
    try:
        window = MainWindow()
        window.setWindowTitle("Kaspi.kz")
        window.show()
    except Exception as e:
        QMessageBox.critical(None, "Критическая ошибка", f"Қосымшаны іске қосу мүмкін емес:\n{e}")
        return 1

    return app.exec()

if __name__ == "__main__":
    sys.exit(main())


