import qtawesome as qta
from PyQt5 import QtCore,QtGui,QtWidgets
from PyQt5.QtWidgets import (QTableWidgetItem, QGraphicsScene, QGraphicsPixmapItem,QHeaderView,QApplication,QLabel,QWidget)
from PyQt5.QtGui import (QBrush, QColor, QDrag, QImage, QPainter, QPen, QPixmap, QPainterPath)
from PyQt5.QtCore import QTimer, QDateTime,QEvent
import sys
from szsurge_ui0 import Ui_MainWindow


class MainUi(QtWidgets.QMainWindow,Ui_MainWindow):
    def __init__(self):
        super(MainUi,self).__init__()
        self.setupUi(self)

        fa5_icon = qta.icon('fa5.flag')
        self.pushButton.setIcon(QtWidgets.QPushButton(fa5_icon, 'Font Awesome! (regular)'))
        fa5s_icon = qta.icon('fa5s.flag')
        self.pushButton_2.setIcon(QtWidgets.QPushButton(fa5s_icon, 'Font Awesome! (solid)'))
        fa5b_icon = qta.icon('fa5b.github')
        self.pushButton_3.setIcon( QtWidgets.QPushButton(fa5b_icon, 'Font Awesome! (brands)'))
def main():
    app = QtWidgets.QApplication(sys.argv)
    gui = MainUi()
    #
    gui.show()

    sys.exit(app.exec_())

if __name__ == '__main__':
    main()