import sys
import threading
from pathlib import Path

import PyQt5
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QApplication, QLineEdit, QWidget, QFormLayout, QPushButton, QLabel, QGroupBox, \
    QHBoxLayout
from pytube import YouTube


class MyRadioButton(PyQt5.QtWidgets.QRadioButton):
    def __init__(self):
        super(MyRadioButton, self).__init__()
        self.value = -1

    def SetValue(self, val):
        self.value = val

    def GetValue(self):
        return self.value


class App(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        # data
        self.videoTargetValue = 0
        self.list_radButton = []
        self.yt_obj = None

        self.horizontalGroupBox = QGroupBox("Video quality")
        self.horizontalButton = QGroupBox("Action")
        self.horizontalGroupBox.hide()

        self.dirPath = QLabel(self)
        self.title = 'Youtube Video Download'
        self.left = 800
        self.top = 300
        self.width = 600
        self.height = 250
        self.file = open("userCurrentDownloadLocation.txt", "r")

        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        self.dirSelected = QLineEdit(self)
        self.dirSelected.move(20, 20)
        self.dirSelected.resize(280, 25)
        self.dirSelected.setReadOnly(True)

        if self.file != 0:
            self.dirSelected.setText(self.file.read())
            self.file.close()
        else:
            downloads_path = str(Path.home() / "Downloads")
            self.dirSelected.setText(downloads_path)
            self.file.close()

        self.input_VideoUrl = QLineEdit(self)
        self.input_VideoUrl.move(50, 20)
        self.input_VideoUrl.resize(280, 25)

        self.btn_GetData = QPushButton('Get Video Data', self)
        self.btn_GetData.move(10, 170)
        # connect button to function on_click
        self.btn_GetData.clicked.connect(self.onClick_GetData)

        self.btn_Download = QPushButton('Download')
        self.btn_Download.move(10, 170)
        self.btn_Download.clicked.connect(self.onCLick_Download)
        self.btn_Download.setDisabled(True)

        self.btn_Reset = QPushButton("Reset")
        self.btn_Reset.clicked.connect(self.onClick_Reset)

        self.btnLocation = QPushButton("Location", self)
        self.btnLocation.clicked.connect(self.onClick_btnLocation)

        self.status = QLabel(self)

        self.control_ui = QFormLayout()
        # self.control_ui.addRow(self.btnLocation)
        self.control_ui.addRow("Location:", self.dirSelected)
        self.control_ui.addRow("Youtube Url: ", self.input_VideoUrl)
        self.control_ui.addWidget(self.horizontalGroupBox)

        action_Layout = QHBoxLayout()
        action_Layout.addWidget(self.btn_GetData)
        action_Layout.addWidget(self.btn_Download)
        action_Layout.addWidget(self.btn_Reset)
        action_Layout.addWidget(self.btnLocation)

        self.horizontalButton.setLayout(action_Layout)
        self.control_ui.addWidget(self.horizontalButton)
        self.control_ui.addRow(self.status)
        self.control_ui.addRow(self.dirPath)

        self.setLayout(self.control_ui)
        self.show()

    # def GetDataVideo_NewThread(self):
    #     thread_data = threading.Thread(target=self.onClick_GetData)
    #     thread_data.start()

    @pyqtSlot()
    def onClick_GetData(self):

        self.status.setText("")
        self.dirPath.setText("")
        radioButton_Layout = QHBoxLayout()
        try:
            self.yt_obj = YouTube(self.input_VideoUrl.text())
            available_res = []

            for item in self.yt_obj.streams:
                if item.resolution in available_res:
                    continue
                elif not item.resolution is None and item.resolution[0].isdigit():
                    available_res.append(item.resolution)

                    radioButton = MyRadioButton()
                    radioButton.setText(item.resolution)

                    value = self.yt_obj.streams.index(item)

                    radioButton.SetValue(value)
                    radioButton.setChecked(False)

                    # radioButton.clicked().connect(self.onClickRadioButton(self,value))
                    # radioButton.clicked.connect(lambda: self.onClickRadioButton(radioButton.GetValue()))

                    self.list_radButton.append(radioButton)

                else:
                    pass

            for rad in self.list_radButton:
                # print("rad ", rad.GetValue())
                rad.clicked.connect(lambda: self.onClickRadioButton())
                radioButton_Layout.addWidget(rad)
                # if rad.isChecked():
                #     self.videoTargetValue = rad.GetValue()

            self.horizontalGroupBox.setLayout(radioButton_Layout)
            self.horizontalGroupBox.show()

            self.btn_Download.setDisabled(False)

            # yt_obj.streams.first().download(output_path, filename=yt_obj.title)

        except Exception as e:
            print(e)
            self.status.setText('Cannot download your video, Please try again')
            self.status.setStyleSheet('color: red')

    @pyqtSlot()
    def onClick_btnLocation(self):
        dir_ = PyQt5.QtWidgets.QFileDialog.getExistingDirectory(None, 'Select project folder:', 'D:\\',
                                                                PyQt5.QtWidgets.QFileDialog.ShowDirsOnly)
        self.dirSelected.setText(dir_)
        self.file = open("userCurrentDownloadLocation.txt", "w")
        self.file.write(dir_)
        self.file.close()

    def DownloadVideo_NewThread(self):
        thread = threading.Thread(target=self.onCLick_Download)
        thread.start()
        thread.join()

    @pyqtSlot()
    def onCLick_Download(self):
        output_path = self.dirSelected.text()
        try:
            # self.yt_obj = YouTube(self.input_VideoUrl.text())
            self.yt_obj.streams[self.videoTargetValue].download(output_path, filename=self.yt_obj.title)
            self.status.setText('YouTube video downloaded successfully')
            self.status.setStyleSheet('color: green')
            self.status.move(50, 200)
            self.dirPath.setText("Video saved in : " + output_path)
            self.dirPath.move(50, 220)
            self.dirPath.setStyleSheet('color: green')
        except Exception as e:
            print(e)
            self.status.setText('Can not download your video, Please try again')
            self.status.setStyleSheet('color: red')

    @pyqtSlot()
    def onClick_Reset(self):
        self.dirPath.setText("")
        self.status.setText("")
        self.input_VideoUrl.setText("")
        self.btn_Download.setDisabled(True)

    @pyqtSlot()
    def onClickRadioButton(self):
        # self.videoTargetValue = value
        for radButton in self.list_radButton:
            if radButton.isChecked():
                self.videoTargetValue = radButton.GetValue()
        # print("select value: ", self.videoTargetValue)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    # print(PyQt5.QtWidgets.QStyleFactory.keys())
    win = App()
    win.show()
    sys.exit(app.exec_())
