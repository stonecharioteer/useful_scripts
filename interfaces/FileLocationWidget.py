import os
import datetime

from PyQt4.QtGui import QPushButton, QLabel, QLineEdit, QWidget
from PyQt4.QtGui import QGridLayout, QPixmap, QIcon, QFileDialog
from PyQt4.QtGui import QMessageBox
from PyQt4 import QtCore
from PyQt4.QtCore import QSize, Qt
from gkngui.IconButton import IconButton
from algorithms.PathMethods import get_image_path

class FileLocationWidget(QWidget):
    changedPath = QtCore.pyqtSignal(object)
    def __init__(self, name, default_path=None, location_type=None, file_extension=None):
        super(FileLocationWidget,self).__init__()
        self.name = name
        if (location_type is None) or location_type not in [0,1,2]:
            #0 is folder location
            #1 is existing file location
            #2 is new file location
            self.location_type = 0 
        else:
            self.location_type = location_type

        if self.location_type in [1,2]:
            if file_extension is None:
                self.file_extension = "*"
            else:
                self.file_extension = file_extension
        else:
            self.file_extension = None

        self.createUI()
        self.setPath(default_path)
        self.mapEvents()

    def getItemDescription(self):
        if self.location_type == 0:
            item_description = self.name + " Folder Location:"
        elif self.location_type == 1:
            item_description = self.name + " Open Location:"
        elif self.location_type == 2:
            item_description = self.name + " Save Location:"
        return item_description
    
    def createUI(self):
        self.label = QLabel(self.getItemDescription())
        self.line_edit = QLineEdit()
        self.line_edit.setReadOnly(True)
        self.browse_button = IconButton("Browse",get_image_path("folder"), height=15, width=15)
        self.browse_button.setToolTip("Click this to change the location")
        layout = QGridLayout()
        layout.addWidget(self.label,0,0,1,1,Qt.AlignLeft)
        layout.addWidget(self.line_edit,0,1,1, 3)
        layout.addWidget(self.browse_button,0,4,1,1,Qt.AlignHCenter)
        self.setLayout(layout)
    
    def setPath(self,path):
        if path is None:
            if self.location_type == 0:
                self.current_path = os.getcwd()
            else:
                extension = "" if self.file_extension == "*" else ".{}".format(self.file_extension)
                default_file_name = self.name +datetime.datetime.now().strftime("_%Y%m%d_%H%M%S")+ extension
                self.current_path = os.path.join(os.getcwd(), default_file_name)
        else:
            self.current_path = path
            if not os.path.exists(self.current_path):
                try:
                    os.makedirs(self.current_path)
                except PermissionError:
                    message =("Since the path {} doesn't exist, the "
                            "program tried to create it, but could not "
                            "because of insufficient rights. The program "
                            "will not work as expected.").format(self.current_path)
                    self.alert_message("Permission Error!", message)
                    pass

        self.line_edit.setText(self.current_path)
        self.changedPath.emit(self.current_path)
        message = "Currently pointing to: %s.\nClick the browse button to change this."%self.current_path
        self.line_edit.setToolTip(message)

    def selectNewPath(self):
        instruction = "Select the %s"%(self.getItemDescription())
        if self.location_type == 2:
            new_path = QFileDialog.getSaveFileName(self, instruction, 
                                            self.current_path,
                                             ("(*.{})".format(self.file_extension)))

        elif self.location_type == 1:
            new_path = QFileDialog.getOpenFileName(self, instruction, 
                                            self.current_path,
                                            ("(*.{})".format(self.file_extension))
                                            )
        else:
            new_path = QFileDialog.getExistingDirectory(self, instruction, 
                                            self.current_path,
                                            QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks
                                            )
        if new_path:
            self.setPath(new_path)

    def mapEvents(self):
        self.browse_button.clicked.connect(self.selectNewPath)

    def getPath(self):
        return os.path.normpath(self.current_path)
    
    def alert_message(self, title, message):
        QMessageBox.about(self, title, message)
