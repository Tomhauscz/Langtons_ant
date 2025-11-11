from PySide6.QtWidgets import (
    QDialog,
    QLabel,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QApplication,
    QStyle,
    QSizePolicy
)
from PySide6.QtCore import (
    Qt,
    QSize
)


class WarningDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Warning Dialog Window")

        # --- main vertical layout
        main_layout = QVBoxLayout(self)

        # --- Top layout for warning icon and warning text
        top_layout = QHBoxLayout()
        top_layout.setContentsMargins(0, 0, 20, 20)

        icon_warning = QLabel()
        pixmap = QApplication.style().standardIcon(
            QStyle.StandardPixmap.SP_MessageBoxWarning
        ).pixmap(48, 48)
        icon_warning.setPixmap(pixmap)
        icon_warning.setAlignment(Qt.AlignmentFlag.AlignTop)
        top_layout.addWidget(icon_warning)

        self.label = QLabel("Warning!")
        self.label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        top_layout.addWidget(self.label)

        main_layout.addLayout(top_layout)

        # --- Bottom horizontal layout for button
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        ok_button = QPushButton("OK")
        ok_button.clicked.connect(self.accept)
        button_layout.addWidget(ok_button)

        main_layout.addLayout(button_layout)

        # adjust the dialog size to the content
        self.adjustSize()
        self.setFixedSize(self.sizeHint())

    def setTitle(self, title_msg: str):
        self.setWindowTitle(title_msg)

    def setMessage(self, message: str):
        self.label.setText(message)

