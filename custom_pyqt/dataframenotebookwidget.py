# Set the QT API to PyQt4
import os
os.environ['QT_API'] = 'pyqt'

import random

import sip
sip.setapi("QString", 2)
sip.setapi("QVariant", 2)
from PyQt4.QtGui  import *
from PyQt4.QtCore import *


# Import the console machinery from ipython
from qtconsole.rich_ipython_widget import RichJupyterWidget
from qtconsole.inprocess import QtInProcessKernelManager
from IPython.lib import guisupport

import pandas as pd
import numpy as np

class QIPythonWidget(RichJupyterWidget):
    """ Convenience class for a live IPython console widget. We can replace the standard banner using the customBanner argument"""
    def __init__(self,customBanner=None,*args,**kwargs):
        if customBanner!=None: self.banner=customBanner
        super(QIPythonWidget, self).__init__(*args,**kwargs)
        self.kernel_manager = kernel_manager = QtInProcessKernelManager()
        kernel_manager.start_kernel()
        kernel_manager.kernel.gui = 'qt4'
        self.kernel_client = kernel_client = self._kernel_manager.client()
        kernel_client.start_channels()

        def stop():
            kernel_client.stop_channels()
            kernel_manager.shutdown_kernel()
            guisupport.get_app_qt4().exit()
        self.exit_requested.connect(stop)

    def pushVariables(self,variableDict):
        """ Given a dictionary containing name / value pairs, push those variables to the IPython console widget """
        self.kernel_manager.kernel.shell.push(variableDict)
    def clearTerminal(self):
        """ Clears the terminal """
        self._control.clear()
    def printText(self,text):
        """ Prints some plain text to the console """
        self._append_plain_text(text)
    def executeCommand(self,command):
        """ Execute a command in the frame of the console widget """
        self._execute(command,False)


class ExampleWidget(QWidget):
    """ Main GUI Widget including a button and IPython Console widget inside vertical layout """
    def __init__(self, parent=None):
        super(ExampleWidget, self).__init__(parent)
        layout = QVBoxLayout(self)
        ipyConsole = QIPythonWidget(customBanner="Welcome to the embedded ipython console\n")
        self.df = get_df(5)
        self.dfviewer = QTextEdit()
        self.dfviewer.setReadOnly(True)
        #print(dir(self.dfviewer))
        self.refresh_button = QPushButton("Refresh View")
        self.refresh()
        layout.addWidget(ipyConsole)
        layout.addWidget(self.dfviewer)
        layout.addWidget(self.refresh_button)
        # This allows the variable foo and method print_process_id to be accessed from the ipython console
        ipyConsole.pushVariables({"df":self.df, "viewer":self.dfviewer, "refresh":self.refresh,"display":self.display})
        ipyConsole.printText("The variable 'foo' and the method 'print_process_id()' are available. Use the 'whos' command for information.")
    
    def refresh(self):
        self.display(self.df)
    
    def display(self, obj):
        """Send this function an object with HTML to show it."""
        try:
            html = obj._repr_html_() + ""
        except:
            html = "<b>Unable to retrieve HTML for {}.".format(str(obj))
        self.dfviewer.setHtml(html)

def get_df(n=None):
    if n is None:
        n = 50
    columns = ["age","height","weight","bmi"]
    datamatrix = []
    for i in range(n):
        row = [random.randint(10,99), random.random()+1,  random.randint(50,100), random.random()+2]
        datamatrix.append(row)
    return pd.DataFrame(datamatrix,columns=columns)


def main():
    app  = QApplication([])
    widget = ExampleWidget()
    widget.show()
    app.exec_()

if __name__ == '__main__':
    main()