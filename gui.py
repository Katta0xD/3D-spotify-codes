#!/usr/bin/env python3
import sys
import logic
from PySide6 import QtCore, QtWidgets, QtGui
from PySide6.QtWidgets import QApplication, QVBoxLayout, QWidget


def btnSearch(searchTerm):
    print()


# def btnSend(reference, URI):
def btnSend():
    logic.send(main.referenceInput.text(), main.URIInput.text(), 1)


class Window(QWidget):
    def __init__(self):
        super().__init__()

        self.title = QtWidgets.QLabel("Spotify 3D codes")
        self.URILabel = QtWidgets.QLabel("URI: ")
        self.URIInput = QtWidgets.QLineEdit()
        self.referenceLabel = QtWidgets.QLabel("reference: ")
        self.referenceInput = QtWidgets.QLineEdit()
        self.button = QtWidgets.QPushButton("Send")
        self.button.clicked.connect(btnSend)

        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.addWidget(self.title)
        self.main_layout.addWidget(self.URILabel)
        self.main_layout.addWidget(self.URIInput)
        self.main_layout.addWidget(self.referenceLabel)
        self.main_layout.addWidget(self.referenceInput)
        self.main_layout.addWidget(self.button)
        self.setLayout(self.main_layout)


app = QApplication(sys.argv)
main = Window()
main.show()

sys.exit(app.exec())
