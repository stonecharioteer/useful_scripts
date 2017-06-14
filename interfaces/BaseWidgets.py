#!/usr/env python3
"""
BaseWidgets.py
This file contains the code for reusable widgets.
Code history:
1 - 2016-4-20 - Still no version control.
0 - 2016-03-31 - Initial Code Base
"""
import os
import sys
import glob
import datetime
import multiprocessing

import numpy as np
import pandas as pd
import scipy
# import sklearn
import statsmodels

from PyQt4 import QtCore
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from PyQt4.QtCore import Qt

from gkngui.Constants import getColor
from gkngui.PathMethods import getImage

try:
    from gkngui.FileListerMethods import *
except:
    path_to_algorithms = os.path.abspath(os.path.join("..","Algorithms"))
    if os.path.exists(path_to_algorithms):
        sys.path.append(path_to_algorithms)
        from FileListerMethods import *

    
class BaseWidget(QWidget):
    def __init__(self, *args, **kwargs):
        super(BaseWidget, self).__init__(*args, **kwargs)

    def alert(self, title, message):
        QMessageBox.about(self, title, message)

class Label(QLabel):
    def __init__(self, *args, **kwargs):
        super(Label, self).__init__(*args, **kwargs)
        self.setStyleSheet("font-weight: bold;")

class PushButton(QPushButton):
    def __init__(self, *args, **kwargs):
        super(PushButton, self).__init__(*args, **kwargs)
        #self.setStyleSheet("font-weight: bold;")

class PlaceholderWidget(QLabel):
    def __init__(self, *args, **kwargs):
        super(PlaceholderWidget, self).__init__(*args, **kwargs)
        self.setStyleSheet("border: 1px solid black;")
        self.setText("Placeholder")
        self.setGeometry(100,100,100,100)
        self.setToolTip("Placeholder!")

class DirectoryWidget(BaseWidget):
    directoryChanged = pyqtSignal(str)
    def __init__(self, label, directory=None, *args, **kwargs):
        super(DirectoryWidget, self).__init__()
        self.directory = directory if directory is not None else os.getcwd()
        self.label = Label(label)
        self.line_edit = LineEdit(self.directory)
        self.browse_button = IconButton("Browse", getImage("Browse"))
        self.layout = QHBoxLayout()
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.line_edit)
        self.layout.addWidget(self.browse_button)
        self.layout.setContentsMargins(QMargins(0,0,0,0))
        self.setLayout(self.layout)
        self.browse_button.clicked.connect(self.browse)
        #self.line_edit.editingFinished.connect(self.pasteLocation)
        self.line_edit.returnPressed.connect(self.pasteLocation)
        
    def browse(self):
        directory = QFileDialog.getExistingDirectory(
                                                self, 
                                                "Select the %s directory: "%self.label.text(), 
                                                os.getcwd()
                                                )

        if not(directory is None or directory.strip() == ""):
            if os.path.exists(directory):
                self.directory = directory
                self.line_edit.setText(directory)
                self.directoryChanged.emit(self.directory)

    def pasteLocation(self):
        directory = self.line_edit.text().strip()
        if not(directory is None or directory.strip() == ""):
            if os.path.exists(directory):
                self.directory = directory
                self.line_edit.setText(directory)
                self.directoryChanged.emit(self.directory)
        else:
            self.alert("Error","%s is not a valid directory. The directory will be reset to the last known value."%directory)
            self.line_edit.setText(self.directory)
            

class NumLineEdit(QSpinBox, BaseWidget):
    def __init__(self, *args,**kwargs):
        super(NumLineEdit, self).__init__(*args, **kwargs)
        self.setRange(0,10**7)
    def setValue(self, value):
        if self.maximum() < value:
            self.alert("Error", "The value you tried to use is larger than the maximum permissible value right now. This program will use the maximum possible value instead.")
            value = self.maximum()
        super(NumLineEdit, self).setValue(value)
        
class LineEdit(QLineEdit):
    def __init__(self, *args, **kwargs):
        super(LineEdit, self).__init__(*args, **kwargs)

class StatusLineEdit(LineEdit):
    def __init__(self, *args, **kwargs):
        super(StatusLineEdit, self).__init__()
        self.setStyleSheet("border: 0; background-color: lightgray;")
        self.setReadOnly(True)
        #self.setEnabled(False)
        
    def showStatus(self, message):
        super(StatusLineEdit, self).setText(message)

class TextEdit(QTextEdit):
    def __init__(self, *args, **kwargs):
        super(TextEdit, self).__init__(*args, **kwargs)

class LogViewer(TextEdit):
    def __init__(self, *args, **kwargs):
        super(LogViewer, self).__init__(*args, **kwargs)
        self.setReadOnly(True)
        self.setToolTip("Log: Right click to save.")
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.__contextMenu)
    
    def saveLog(self):
        path_to_txt = QFileDialog.getSaveFileName(self, "Log File", os.getcwd(), ("Log Files (*.log)"))[0]
        if path_to_txt is not None and path_to_txt.strip() != "":
            with open(path_to_txt, "wb") as logfile:
                logfile.write(str(self.toPlainText()).strip().encode("utf-8"))
                
    def clrLog(self):
        self.clear()

    def __contextMenu(self):
        self._normalMenu = self.createStandardContextMenu()
        self._addCustomMenuItems(self._normalMenu)
        self._normalMenu.exec_(QCursor.pos())

    def _addCustomMenuItems(self, menu):
        menu.addSeparator()
        menu.addAction(QIcon(getImage("save")), "Save to File", self.saveLog, QKeySequence(Qt.CTRL + Qt.Key_S))
        menu.addAction(QIcon(getImage("clear")), "Clear Log", self.clrLog)
        
    def record(self, message, mode=None):
        if mode is None:
            mode = "message"
        self.append(str(message))

class ResettableComboBox(QComboBox, BaseWidget):
    def __init__(self, *args, **kwargs):
        super(ResettableComboBox, self).__init__()
        #print("Custom Combo Box!")
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.showMenu)
        self.installEventFilter(self)

    def eventFilter(self, target, event):
        if(event.type()== QtCore.QEvent.KeyPress):
            self.keyPressEvent(event)
            return True
        return False

    def showMenu(self, pos):
        menu = QMenu()
        clear_action = menu.addAction(QIcon(getImage("clear")), "Clear Selection", self.clearSelection)
        action = menu.exec_(self.mapToGlobal(pos))
        menu.show()

    def keyPressEvent(self, event):
        #print(event.key())
        if event.key() == 16777219:
            self.clearSelection()
        QComboBox.keyPressEvent(self, event)

    def clearSelection(self):
        self.setCurrentIndex(-1)
       #self.alert("Success!","Cleared the selection")

class CheckableComboBox(QComboBox):
    changedSelection = QtCore.pyqtSignal(bool)
    def __init__(self, label):
        super(CheckableComboBox, self).__init__()
        self.label = label
        self.view().pressed.connect(self.handleItemPressed)
        self.clear()
        self.setCurrentIndex(0)
        self.installEventFilter(self)
        self.currentIndexChanged.connect(self.reset)

    def eventFilter(self, target, event):
        if(event.type()== QtCore.QEvent.Wheel):
            #wheel event is blocked here
            return True
        return False

    def handleItemPressed(self, index):
        item = self.model().itemFromIndex(index)
        if "---" not in item.text():
            if item.checkState() == QtCore.Qt.Checked:
                item.setCheckState(QtCore.Qt.Unchecked)
            else:
                item.setCheckState(QtCore.Qt.Checked)
            self.changedSelection.emit(True)

    def reset(self):
        checked_items = len(self.getCheckedItems())
        if checked_items > 0:
            self.model().item(0).setText("----%s : %d options selected----"%(self.label, checked_items))
            self.setCurrentIndex(0)
        else:
            self.setItemText(0,"----%s----"%(self.label))
        if self.currentIndex() != 0:
            self.setCurrentIndex(0)

    def getCheckedItems(self):
        rows = self.model().rowCount()
        checked_items = []
        for item_index in range(rows)[1:]:
            item = self.model().item(item_index)
            if item.checkState() == QtCore.Qt.Checked:
                checked_items.append(str(item.text()))
        return checked_items

    def clear(self):
        super(CheckableComboBox,self).clear()
        firstItem = QStandardItem("----%s----"%self.label)
        firstItem.setBackground(QBrush(QColor(200, 200, 200)))
        firstItem.setSelectable(False)
        self.setModel(QStandardItemModel(self))
        self.model().setItem(0, 0, firstItem)
        self.model().item(0).setText("----%s----"%(self.label))
    
    def addItems(self,items_list):
        base_index = self.__len__()
        for item_index in range(len(items_list)):
            item_object = items_list[item_index]
            if item_object is not None:
                self.addItem(str(items_list[item_index]))
                item = self.model().item(item_index+base_index, 0)
                item.setCheckState(QtCore.Qt.Unchecked)
        self.reset()

    def select(self, query, mute=None):
        if mute is None:
            mute = False
        if type(query) == str:
            rows = self.model().rowCount()
            found_item = False
            for item_index in range(rows)[1:]:
                if not found_item:
                    item = self.model().item(item_index)
                    item_text = str(item.text())
                    if (item_text == query):
                        found_item = True
                        if (item.checkState() != QtCore.Qt.Checked):
                            item.setCheckState(QtCore.Qt.Checked)
                else:
                    break
            if found_item and not(mute):
                self.reset()
                self.changedSelection.emit(True)

        elif type(query) == list:
            for query_item in query:
                self.select(query_item, True)
            self.reset()
            self.changedSelection.emit(True)

    def selectIfTextFound(self, query_string):
        rows = self.model().rowCount()
        found_item = False
        for item_index in range(rows)[1:]:
            item = self.model().item(item_index)
            item_text = str(item.text())
            if (query_string in item_text):
                found_item = True
                if (item.checkState() != QtCore.Qt.Checked):
                    item.setCheckState(QtCore.Qt.Checked)
        if found_item:
            self.reset()
            self.changedSelection.emit(True)

    def selectAll(self):
        rows = self.model().rowCount()
        for item_index in range(rows)[1:]:
            item = self.model().item(item_index)
            if (item.checkState() != QtCore.Qt.Checked):
                item.setCheckState(QtCore.Qt.Checked)
        self.reset()
        self.changedSelection.emit(True)

    def clearSelection(self):
        rows = self.model().rowCount()
        for item_index in range(rows)[1:]:
            item = self.model().item(item_index)
            if (item.checkState() == QtCore.Qt.Checked):
                item.setCheckState(QtCore.Qt.Unchecked)
        self.reset()
        self.changedSelection.emit(True)

class ComboBox(QComboBox):
    def __init__(self, *args, **kwargs):
        super(ComboBox, self).__init__(*args, **kwargs)

class ProgressBar(QProgressBar):
    def __init__(self, *args, **kwargs):
        super(ProgressBar, self).__init__(*args, **kwargs)

class DateEdit(QDateTimeEdit):
    def __init__(self, *args, **kwargs):
        super(DateEdit, self).__init__(*args, **kwargs)
        self.setDisplayFormat("ddd, dd-MMM-yyyy") 
        self.setDate(datetime.date.today())
        self.setCalendarPopup(True) 
        
class DateTimeEdit(QDateTimeEdit):
    def __init__(self, *args, **kwargs):
        super(DateTimeEdit, self).__init__(*args, **kwargs)
        self.setDateTime(datetime.datetime.now())

class TimeEdit(QDateTimeEdit):
    def __init__(self, *args, **kwargs):
        super(TimeEdit, self).__init__(*args, **kwargs)
        self.setDateTime(datetime.datetime.now())

class SpinBox(QSpinBox):
    def __init__(self, *args, **kwargs):
        super(SpinBox, self).__init__(*args, **kwargs)

class DoubleSpinBox(QDoubleSpinBox):
    def __init__(self, *args, **kwargs):
        super(DoubleSpinBox, self).__init__(*args, **kwargs)

class TreeWidget(QTreeWidget, BaseWidget):
    def __init__(self, *args, **kwargs):
        super(TreeWidget, self).__init__(*args, **kwargs)
        
    def showDataFrame(self, dataframe, highlight_rules=None):
        if dataframe is not None:
            row_count = dataframe.shape[0]
            column_count = dataframe.shape[1]
            self.setRowCount(row_count)
            self.setColumnCount(column_count)
            for row_index in range(row_count):
                match = False
                color = getColor("white")
                if highlight_rules is not None:
                    for highlight_rule in highlight_rules:
                        matches = []
                        counter =0
                        for column in highlight_rule["Columns"]:
                            deciding_value = highlight_rule["Values"][counter]
                            value_in_dataframe = dataframe[column][row_index]
                            if type(deciding_value) == list:
                                if deciding_value[0] <= value_in_dataframe < deciding_value[1]:
                                    matches.append(True)
                                else:
                                    matches.append(False)
                            elif type(deciding_value) == str:
                                if value_in_dataframe == deciding_value:
                                    matches.append(True)
                                else:
                                    matches.append(False)
                            else:
                                matches.append(False)
                            counter +=1
                        if len(matches)>0 and False not in matches:
                            match = True
                        else:
                            match = False
                        if match:
                            # print ["%s=%s"%(x, y) for x,y in zip(highlight_rule["Columns"], highlight_rule["Values"])], " matched for row %d."%row_index
                            color = highlight_rule["Color"]
                for col_index in range(column_count):
                    widget_item = QTreeWidgetItem(str(dataframe.iat[row_index, col_index]))
                    widget_item.setBackground(QBrush(QColor(color)))
                    self.setItem(row_index, col_index, widget_item)
                    

            self.setHorizontalHeaderLabels([str(x) for x in list(dataframe.columns)])
            #self.setVerticalHeaderLabels(list(dataframe.index))
            self.verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
            self.verticalHeader().setStretchLastSection(False)
            self.verticalHeader().setVisible(True)

            self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
            self.horizontalHeader().setStretchLastSection(True)
            self.horizontalHeader().setVisible(True)
        else:
            self.setRowCount(0)


class DirectoryViewer(TreeWidget):
    selectedPath = pyqtSignal(str)
    def __init__(self, directory=None, *args, **kwargs):
        super(DirectoryViewer, self).__init__()
        self.directory = os.getcwd() if directory is None else directory
        self.itemActivated.connect(self.getSelectedPath)
        
    def getSelectedPath(self, item):
        this_item = item
        this_item_text = item.text(0)
        parents = []
        while True:
            try:
                parent = item.parent()
                if parent is not None:
                    parents.append(parent.text(0))
                    item = parent
                else:
                    break
            except Exception as e:
                print(repr(e))
                break
        children = []
        item = this_item
        while True:
            i = 0
            try:
                child = item.child(i)
                if child is None: 
                    break
                else:
                    i += 1
                    children.append(child.text(0))
                    item = child
            except Exception as e:
                print(repr(e))
                break
        parents_rev = list(reversed(parents))
        if len(parents_rev) > 0:
            parent_path = os.path.join(*parents_rev)
        if len(children) > 0:
            child_path = os.path.join(*children)
        if len(children) > 0 and len(parents_rev) > 0:
            path = os.path.join(parent_path, this_item_text, child_path)
        elif len(parents_rev)> 0 and len(children) == 0:
            path = os.path.join(parent_path, this_item_text)
        elif len(parents_rev) == 0 and len(children) >0:
            path = os.path.join(this_item_text, child_path)
        else:
            path = this_item_text
        self.selectedPath.emit(path)
        
    def setDirectory(self, directory):
        from pathlib import PurePath
        self.clear()
        self.directory = directory
        self.directory_contents = [PurePath(x).parts for x in getDirectoryContents(directory)]
        self.displayDirectory(self.directory_contents)
        self.alert("Done!", "Retrieved %d files!"%len(self.directory_contents))
    
    def displayDirectory(self, directory_contents):
        self.setColumnCount(2)#max([len(x) for x in directory_contents]))
        l = []
        for row in directory_contents:
            precedent = QTreeWidgetItem(self, [row[0]])
            full_path  = os.path.join(*row)
            is_file = os.path.isfile(full_path)
            counter = 0
            for item in row[1:]:
                counter+=1
                if is_file and item == row[-1]:
                    extension = os.path.splitext(full_path)[1]
                    if extension == "":
                        extension = "File"
                    else:
                        extension = "%s file"%extension
                    this_item = QTreeWidgetItem(precedent, [item, extension])
                    this_item.setFlags(Qt.ItemIsUserCheckable | this_item.flags())
                else:
                    this_item = QTreeWidgetItem(precedent, [item])
                precedent = this_item

class TableWidget(QTableWidget):
    def __init__(self, *args, **kwargs):
        super(TableWidget, self).__init__(*args, **kwargs)
        self.setStyleSheet("gridline-color: rgb(0, 0, 0)")
        self.clip = QApplication.clipboard()

    def keyPressEvent(self, e):
        if (e.modifiers() & QtCore.Qt.ControlModifier):
            if e.key() == QtCore.Qt.Key_C:
                selected = self.selectedRanges()
                s = '\t'+"\t".join([str(self.horizontalHeaderItem(i).text()) for i in range(selected[0].leftColumn(), selected[0].rightColumn()+1)])
                s = s + '\n'
                for r in range(selected[0].topRow(), selected[0].bottomRow()+1):
                    s += str(r+1) + '\t' 
                    for c in range(selected[0].leftColumn(), selected[0].rightColumn()+1):
                        try:
                            s += str(self.item(r,c).text()) + "\t"
                        except AttributeError:
                            s += "\t"
                    s = s[:-1] + "\n" #eliminate last '\t'
                self.clip.setText(s)
            else:
                super(TableWidget, self).keyPressEvent(e)
        else:
            super(TableWidget, self).keyPressEvent(e)
            
    def showDataFrame(self, dataframe, highlight_rules=None):
        if dataframe is not None:
            row_count = dataframe.shape[0]
            column_count = dataframe.shape[1]
            self.setRowCount(row_count)
            self.setColumnCount(column_count)
            for row_index in range(row_count):
                match = False
                color = getColor("white")
                if highlight_rules is not None:
                    for highlight_rule in highlight_rules:
                        matches = []
                        counter =0
                        for column in highlight_rule["Columns"]:
                            deciding_value = highlight_rule["Values"][counter]
                            value_in_dataframe = dataframe[column][row_index]
                            if type(deciding_value) == list:
                                if deciding_value[0] <= value_in_dataframe < deciding_value[1]:
                                    matches.append(True)
                                else:
                                    matches.append(False)
                            elif type(deciding_value) == str:
                                if value_in_dataframe == deciding_value:
                                    matches.append(True)
                                else:
                                    matches.append(False)
                            else:
                                matches.append(False)
                            counter +=1
                        if len(matches)>0 and False not in matches:
                            match = True
                        else:
                            match = False
                        if match:
                            # print ["%s=%s"%(x, y) for x,y in zip(highlight_rule["Columns"], highlight_rule["Values"])], " matched for row %d."%row_index
                            color = highlight_rule["Color"]
                for col_index in range(column_count):
                    widget_item = QTableWidgetItem(str(dataframe.iat[row_index, col_index]))
                    widget_item.setBackground(QBrush(QColor(color)))
                    self.setItem(row_index, col_index, widget_item)
                    

            self.setHorizontalHeaderLabels([str(x) for x in list(dataframe.columns)])
            #self.setVerticalHeaderLabels(list(dataframe.index))
            self.verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
            self.verticalHeader().setStretchLastSection(False)
            self.verticalHeader().setVisible(True)

            self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
            self.horizontalHeader().setStretchLastSection(True)
            self.horizontalHeader().setVisible(True)
        else:
            self.setRowCount(0)

    def adjustToColumns(self):
        self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        self.horizontalHeader().setStretchLastSection(False)
        self.horizontalHeader().setVisible(True)


class PushButton(QPushButton):
    def __init__(self, *args, **kwargs):
        super(PushButton, self).__init__(*args, **kwargs)

class ImageButton(QPushButton):
    def __init__(self, image_path, size_tuple=None, height=None, *args, **kwargs):
        super(ImageButton, self).__init__(*args, **kwargs)
        self.setIcon(QIcon(image_path))
        if size_tuple is not None:
            self.setIconSize(QtCore.QSize(size_tuple[0],size_tuple[1]))
            
class IconButton(QPushButton):
    def __init__(self, label, image_path, size_tuple=None, *args, **kwargs):
        super(IconButton, self).__init__(*args, **kwargs)
        self.setIcon(QIcon(image_path))
        self.setText(label)
        if size_tuple is not None:
            self.setIconSize(QtCore.QSize(size_tuple[0],size_tuple[1]))
        # self.setFlat(True)

class ListWidget(QListWidget):
    def __init__(self, *args, **kwargs):
        super(ListWidget, self).__init__(*args, **kwargs)
