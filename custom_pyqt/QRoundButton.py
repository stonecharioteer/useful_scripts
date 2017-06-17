from PyQt4.QtGui import * 
from PyQt4.QtCore import * 
import sys

class MyRoundWidget(QWidget):
    def __init__(self, master=None):
        super(MyRoundWidget,self).__init__(master)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setWindowTitle("QLinearGradient Vertical Gradient ")
        self.setAttribute(Qt.WA_TranslucentBackground)

    def paintEvent(self, ev):
        painter = QPainter(self)
        painter.begin(self)
        gradient = QLinearGradient(QRectF(self.rect()).topLeft(),QRectF(self.rect()).bottomLeft())
        gradient.setColorAt(0.0, Qt.black)
        gradient.setColorAt(0.4, Qt.gray)
        gradient.setColorAt(0.7, Qt.black)
        painter.setBrush(gradient)
        painter.drawRoundedRect(self.rect(), 10.0, 10.0)
        painter.end()

def main():    
    app     = QApplication(sys.argv)
    widget = MyRoundWidget()
    widget.show()
    widget.raise_()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
    