from PyQt4.QtGui import QProgressBar

class ProgressBar(QProgressBar):
    def __init__(self):
        super(ProgressBar,self).__init__()
        progress_bar_style = """
            QProgressBar {
                 border: 0.5px solid black;
                 border-radius: 5px;
                 text-align: center;
             }

            QProgressBar::chunk {
                 background-color: #0088D6;
                 width: 20px;
             }""" #05B8CC
        self.setStyleSheet(progress_bar_style)
    
    def setColor(self, hex_code):
        progress_bar_style = """
            QProgressBar {
                 border: 0.5px solid black;
                 border-radius: 5px;
                 text-align: center;
             }

            QProgressBar::chunk {
                 background-color: %s;
                 width: 20px;
             }"""%hex_code
        self.setStyleSheet(progress_bar_style)

    def showETA(self, eta):
        """Need to use this to show Estimated Time of Arrival."""
        pass
