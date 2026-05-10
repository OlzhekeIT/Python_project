# views/base_view.py
from __future__ import annotations
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QFrame, QLabel, QHBoxLayout, QScrollArea
from PyQt6.QtCore import Qt
from services.localization_service import L

class BaseView(QWidget):
    """Базалық көрініс: Барлық беттер осы кластан мұрагерлік алады."""
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._main_layout = QVBoxLayout(self)
        self._main_layout.setContentsMargins(0, 0, 0, 0)
        self._main_layout.setSpacing(0)
        
        # Header (Optional for views that need it)
        self._header = QFrame()
        self._header.setObjectName("details_header")
        self._header.setFixedHeight(70)
        self._header.setStyleSheet("background: white; border-bottom: 1px solid #EDEDED;")
        self._header_layout = QHBoxLayout(self._header)
        self._header_layout.setContentsMargins(40, 0, 40, 0)
        
        self.title_lbl = QLabel()
        self.title_lbl.setObjectName("header_title")
        self._header_layout.addStretch()
        self._header_layout.addWidget(self.title_lbl)
        self._header_layout.addStretch()
        
        # Scroll Area for content
        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setFrameShape(QFrame.Shape.NoFrame)
        self._scroll.setStyleSheet("background: #F8F9FB;")
        
        self._content_widget = QWidget()
        self._content_layout = QVBoxLayout(self._content_widget)
        self._content_layout.setContentsMargins(40, 30, 40, 40)
        self._content_layout.setSpacing(30)
        
        self._scroll.setWidget(self._content_widget)
        
        # Add to main layout
        self._main_layout.addWidget(self._header)
        self._main_layout.addWidget(self._scroll)
        
        L.lang_changed.connect(self.update_localization)

    def set_title(self, text: str):
        self.title_lbl.setText(text)

    def update_localization(self):
        """Мұрагер кластарда қайта анықталуы керек."""
        pass

    def clear_layout(self, layout):
        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()
                else:
                    sub_layout = item.layout()
                    if sub_layout: self.clear_layout(sub_layout)
