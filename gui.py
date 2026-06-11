#!/usr/bin/env python3
import logic
import sys
from PySide6 import QtCore, QtWidgets, QtGui
from PySide6.QtWidgets import QApplication, QVBoxLayout, QWidget, QMessageBox


def btnSearch(searchTerm):
    print()


# def btnSend(reference, URI):
def btnSend():

    try:
        if main.styleComboBox.currentText() == "All in one":
            style = 1
        elif main.styleComboBox.currentText() == "Logo and barcode":
            style = 2
        else:
            raise UnboundLocalError("noStyleSelected")

        logic.send(main.referenceInput.text(), main.uriInput.text(), style)

    except Exception as exception:
        msg = QMessageBox()
        msg.setWindowTitle("Something went wrong")
        msg.setStandardButtons(QMessageBox.StandardButton.Ok)
        if str(exception) == "Bad link":
            msg.setText(
                f"Your link: [{main.uriInput.text()}]\ndoesn't seem to be a valid Spotify link.\n ingress a valid link and try again"
            )
        elif str(exception) == "Bad reference":
            msg.setText(
                f"""Your reference: [{main.referenceInput.text()}]\ndoesn't seem valid.
                \n If you are on Windows remember that it can't include any of the next characters:
                < > : " \\ | / ? * \nsince it will be used as a filename for your model"""
            )
        elif str(exception) == "noStyleSelected":
            msg.setText("You must select a style for your 3D model")

        msg.exec()


def showStyle():
    if main.styleComboBox.currentText() == "All in one":
        main.styleImage.load("./Examples/All in one.png")
    elif main.styleComboBox.currentText() == "Logo and barcode":
        main.styleImage.load("./Examples/Logo and barcode.png")

    main.styleViewer.setPixmap(main.styleImage)


class Window(QWidget):
    def __init__(self):
        super().__init__()
        # Components
        self.title = QtWidgets.QLabel("Spotify 3D codes")

        self.uriLabel = QtWidgets.QLabel("URI: ")
        self.uriInput = QtWidgets.QLineEdit()

        self.referenceLabel = QtWidgets.QLabel("reference: ")
        self.referenceInput = QtWidgets.QLineEdit()

        self.styleComboBox = QtWidgets.QComboBox()
        self.styleComboBox.setPlaceholderText("")
        self.styleComboBox.addItems(["All in one", "Logo and barcode"])
        self.styleComboBox.setCurrentIndex(-1)
        self.styleComboBox.activated.connect(showStyle)

        self.styleImage = QtGui.QPixmap()
        self.styleViewer = QtWidgets.QLabel()
        self.styleViewer.setFixedSize(216, 53)
        self.styleViewer.setScaledContents(True)

        self.sendButton = QtWidgets.QPushButton("Send")
        self.sendButton.clicked.connect(btnSend)

        # Layouts
        self.horizontalLayout1 = QtWidgets.QHBoxLayout()

        self.verticalLayout1 = QtWidgets.QVBoxLayout()
        self.verticalLayout1.addWidget(self.title)
        self.verticalLayout1.addWidget(self.uriLabel)
        self.verticalLayout1.addWidget(self.uriInput)
        self.verticalLayout1.addWidget(self.referenceLabel)
        self.verticalLayout1.addWidget(self.referenceInput)

        self.verticalLayout2 = QtWidgets.QVBoxLayout()
        self.verticalLayout2.addWidget(self.styleComboBox)
        self.verticalLayout2.addWidget(self.styleViewer)

        self.mainLayout = QtWidgets.QVBoxLayout()
        self.mainLayout.insertLayout(0, self.horizontalLayout1)
        self.horizontalLayout1.insertLayout(0, self.verticalLayout1)
        self.horizontalLayout1.insertLayout(1, self.verticalLayout2)
        self.mainLayout.addWidget(self.sendButton)
        self.setLayout(self.mainLayout)


app = QApplication(sys.argv)
main = Window()
main.setBaseSize(620, 185)
main.setFixedSize(620, 185)
main.show()

sys.exit(app.exec())
