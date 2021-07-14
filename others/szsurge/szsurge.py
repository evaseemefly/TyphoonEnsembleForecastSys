import numpy as np
from numpy import *
from PyQt5 import QtCore,QtGui,QtWidgets
from PyQt5.QtWidgets import (QTableWidgetItem, QGraphicsScene, QGraphicsPixmapItem,QHeaderView,QApplication,QLabel,QWidget)
from PyQt5.QtGui import (QBrush, QColor, QDrag, QImage, QPainter, QPen, QPixmap, QPainterPath)
from PyQt5.QtCore import QTimer, QDateTime,QEvent
import sys
import os
import winsound
from datetime import *
import time
from PIL import Image
import qtawesome as qta
import pandas as pd
import win32ui
#import openpyxl
import requests
from threading import Timer,Thread
from szsurge_ui import Ui_MainWindow
from craw_typhoon_cma import get_typath_cma
from gen_draw_typath import cal_time_radius_pres, output_pathfiles, gen_draw_typath, output_controlfile,interp6h
from process_result_contourf import draw_maxsurge, draw_prosurge, get_maxsurgedata
from process_result_plot import get_plotdata, plot_surge
from scipy import interpolate

wtime=datetime.now()
wtimes=wtime.strftime('%Y%m%d%H')
wyear=str(wtimes)[0:4]
#
wdir0='D:/szsurge/'
#

#print(tynos)
#
#caseno='TY'+tyno+'_'+wtimes
lonsz=114.0979
latsz=22.6382
#
dhrs=1
#freq=1
wls4s=[[272, 297, 322, 347],  #'汕尾'
       [375, 400, 420, 440],  #'惠州'
       [382, 392, 407, 422],  #'深圳东山'
       [348, 363, 378, 393],  #'深圳南澳'
       [367, 382, 397, 412],  #'盐田'
       [348, 363, 378, 393],   #'大梅沙'
       [443, 463, 488, 513],   #'赤湾H'
       [443, 463, 488, 513],  # '蛇口'
       [395, 420, 440, 460],  # '前海湾'
       [395, 420, 440, 460]]  # '深圳机场'

msl=[141,#'汕尾'
     222,#'惠州'
     58,#'深圳东山'
     61,#'深圳南澳'
     196,#'盐田'
     57,# '大梅沙'
     281,# '赤湾H'
     64, # '蛇口'
     68,# '前海湾'
     65]# '深圳机场'
levs = [0.5, 1.0, 1.5, 2.0, 2.5, 3.0]
levs2 = ['_gt0_5m', '_gt1_0m', '_gt1_5m', '_gt2_0m', '_gt2_5m', '_gt3_0m']
caseno='None'
perc = [[0.622459331201855,0.377540668798145,0,0,0,0,0,0],                                                                  #1Q
        [0.511247316569098,0.361272035812932,0.127480647617970,0,0,0,0,0],                                                    #2Q
        [0.447236368708731,0.346535478033354,0.161205360081582,0.0450227931763340,0,0,0,0],                                   #3Q
        [0.400517551714126,0.329456751386887,0.183370297149815,0.0690578866644997,0.0175975130846732,0,0,0],                  #4Q
        [0.334118261046163,0.294858330470191,0.202652969294367,0.108472317838118,0.0452179894932070,0.0146801318579536,0,0],  #5Q
        [0.286632500828924,0.262800543511864,0.202548363088809,0.131229921447511,0.0714724471890523,0.0327224707706080,0.0125937531632317,0],  #6Q
        [0.250977633593432,0.235471130014034,0.194466864320737,0.141370518440951,0.0904643330162669,0.0509566907449681,0.0252656422414563,0.0110271876281545]]#7Q
perc=np.array(perc)
#
site3=['汕尾','惠州','深圳东山','深圳南澳','盐田','大梅沙','赤湾H','蛇口','前海湾','深圳机场']
site3e=['SHANWEI','HUIZHOU','SZDONGSHAN','SZNANAO','YANTIAN','DAMEISHA','CHIWANH','SHEKOU','QIANHAIWAN','SZJICHANG']
casenum=['145个', '125个', '105个', '85个', '65个', '45个', '25个']
west=110; east=118; south=19; north=24
#
gtwl=[0.5, 1.0, 1.5, 2.0, 2.5, 3.0]
nsta=len(site3)
gtwls=[]
for i in range(len(gtwl)):
    gtwls.append('>'+str(gtwl[i])+'米概率')
#print(gtwls)
#==================================  MainUI==================================#
class MainUi(QtWidgets.QMainWindow,Ui_MainWindow):
    def __init__(self):
        super(MainUi,self).__init__()
        self.setupUi(self)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.currtime)
        self.timer.start(1000)
        #
        self.initUI()
        #
        self.initConnect()
        self.initSet()
        self.initdata()
        self.setWindowTitle('深圳市台风风暴潮集合预报系统')
        self.afterGenerationConfig()
        #
        self.status = self.statusBar()
        #
        self.graphicsView.installEventFilter(self)
        self.graphicsView_2.installEventFilter(self)
        self.graphicsView_3.installEventFilter(self)
        self.graphicsView_4.installEventFilter(self)
        self.graphicsView_5.installEventFilter(self)
        #
        self.graphicsView.scene_img = QGraphicsScene()
        self.graphicsView_2.scene_img = QGraphicsScene()
        self.graphicsView_3.scene_img = QGraphicsScene()
        self.graphicsView_4.scene_img = QGraphicsScene()
        self.graphicsView_5.scene_img = QGraphicsScene()
        #
    def initSet(self):
        #global pnames, hlabel
        self.comboBox.clear()
        self.comboBox_2.clear()
        self.comboBox_3.clear()
        self.comboBox_4.clear()
        self.comboBox_5.clear()
        #
        self.comboBox.addItems(casenum)
        self.comboBox_2.addItems(site3)
        #
        tynos = []
        casedirs = os.listdir(wdir0 + 'pictures/')
        for i in range(len(casedirs)):
            if len(casedirs[i]) == 17 and casedirs[i][0:2] == 'TY':
                tynos.append(casedirs[i][2:6])
        tynos.sort(reverse=True)
        tynos = pd.unique(tynos)
        timstrs = []
        for i in range(len(casedirs)):
            if len(casedirs[i]) == 17 and casedirs[i][2:6] == tynos[0]:
                timstrs.append(casedirs[i][-6:])
        timstrs.sort(reverse=True)
        self.comboBox_3.addItems(tynos)
        self.comboBox_4.addItems(timstrs)
        self.comboBox_5.addItems(gtwls)
        #
    def initdata(self):
        csno = self.comboBox.currentIndex()#集合成员个数
        pnum = casenum[csno][:-1]          #集合成员个数
        r01 = float(self.lineEdit_9.text())
        r02 = float(self.lineEdit_10.text())
        r03 = float(self.lineEdit_11.text())
        r04 = float(self.lineEdit_12.text())
        r05 = float(self.lineEdit_13.text())
        dR  = float(self.lineEdit_14.text())
        tyid = self.lineEdit_15.text()
        #
        west = float(self.lineEdit_3.text())
        east = float(self.lineEdit_4.text())
        south = float(self.lineEdit_5.text())
        north = float(self.lineEdit_6.text())
        #
        cmin = self.lineEdit_7.text()
        cmax = self.lineEdit_8.text()

    def initConnect(self):
        # 槽函數不能加括號
        self.pushButton.clicked.connect(self.pushbutton_task)     # 画图
        self.pushButton_2.clicked.connect(self.pushbutton2_task)  # 启动
        self.pushButton_3.clicked.connect(self.pushbutton3_task)  # 采集
        self.pushButton_4.clicked.connect(self.pushbutton4_task)  # 读取
        self.pushButton_5.clicked.connect(self.pushbutton5_task)  # 上一页
        self.pushButton_6.clicked.connect(self.pushbutton6_task)  # 下一页
        self.pushButton_7.clicked.connect(self.pushbutton7_task)  # 上一页
        self.pushButton_8.clicked.connect(self.pushbutton8_task)  # 下一页
              #
        #
        self.pushButton.pressed.connect(self.press_task)
        self.pushButton_2.pressed.connect(self.press_task2)
        self.pushButton_3.pressed.connect(self.press_task3)
        self.pushButton_4.pressed.connect(self.press_task4)
        self.pushButton_5.pressed.connect(self.press_task5)
        self.pushButton_6.pressed.connect(self.press_task6)
        self.pushButton_7.pressed.connect(self.press_task7)
        self.pushButton_8.pressed.connect(self.press_task8)
        #
        self.comboBox.activated[str].connect(self.combobox_task)
        self.comboBox_2.activated[str].connect(self.combobox2_task)
        self.comboBox_3.activated[str].connect(self.combobox3_task)
        self.comboBox_4.activated[str].connect(self.combobox4_task)
        self.comboBox_5.activated[str].connect(self.combobox5_task)

    def initUI(self):
       #
        #spin_widget = qta.IconWidget()
        self.pushButton.setIcon(qta.icon('fa5s.images', color='black'))  # 画图 ,animation=qta.Spin(spin_widget),active='fa5s.balance-scale'
        self.pushButton_2.setIcon(qta.icon('fa.play', color='black'))  # 啟動,color_active='#D2F6EE'
        self.pushButton_3.setIcon(qta.icon('fa.download', color='black'))     #采集
        self.pushButton_4.setIcon(qta.icon('fa.folder-open', color='black'))     #读取'#1ECD97',color_active='#D2F6EE'

        self.pushButton_5.setIcon(qta.icon('fa5s.arrow-left', color='black'))  # 上一页,color_active='#1ECD97' fa5.arrow-alt-circle-left
        self.pushButton_6.setIcon(qta.icon('fa5s.arrow-right', color='black'))  # 下一页

        self.pushButton_7.setIcon(qta.icon('fa5s.arrow-left', color='black'))  # 上一页,color_active='#1ECD97' fa5.arrow-alt-circle-left
        self.pushButton_8.setIcon(qta.icon('fa5s.arrow-right', color='black'))  # 下一页
        #
        self.pushButton.setStyleSheet(
            '''QPushButton{background:#F0F0F0;border-radius:5px;height:25px;}QPushButton:hover{background:#D8D8D8;font-weight:700;border-left:6px solid #D8D8D8;}
            QPushButton{font: 75 12pt \"微软雅黑\";}''')#画图
        self.pushButton_2.setStyleSheet(
            '''QPushButton{background:#F0F0F0;border-radius:5px;height:25px;}QPushButton:hover{background:#D8D8D8;font-weight:700;border-left:6px solid #D8D8D8;}
            QPushButton{font: 75 12pt \"微软雅黑\";}''')#启动
        self.pushButton_3.setStyleSheet(
            '''QPushButton{background:#F0F0F0;border-radius:5px;height:25px;}QPushButton:hover{background:#D8D8D8;font-weight:700;border-left:6px solid #D8D8D8;}
            QPushButton{font: 75 10pt \"微软雅黑\";}''')#采集
        self.pushButton_4.setStyleSheet(
            '''QPushButton{background:#F0F0F0;border-radius:5px;height:25px;}QPushButton:hover{background:#D8D8D8;font-weight:700;border-left:6px solid #D8D8D8;}
            QPushButton{font: 75 10pt \"微软雅黑\";}''')#读取

        self.pushButton_5.setStyleSheet(
            '''QPushButton{background:#FFFFFF;border-radius:5px;height:25px;}QPushButton:hover{background:#D8D8D8;font-weight:700;border-right:6px solid #D8D8D8;}
            QPushButton{font: 75 10pt \"微软雅黑\";}''')#上一页

        self.pushButton_6.setStyleSheet(
            '''QPushButton{background:#FFFFFF;border-radius:5px;height:25px;}QPushButton:hover{background:#D8D8D8;font-weight:700;border-left:6px solid #D8D8D8;}
            QPushButton{font: 75 10pt \"微软雅黑\";}''')#下一页

        self.pushButton_7.setStyleSheet(
            '''QPushButton{background:#F0F0F0;border-radius:5px;height:25px;}QPushButton:hover{background:#D8D8D8;font-weight:700;border-right:6px solid #D8D8D8;}
            QPushButton{font: 75 10pt \"微软雅黑\";}''')  # 上一页

        self.pushButton_8.setStyleSheet(
            '''QPushButton{background:#F0F0F0;border-radius:5px;height:25px;}QPushButton:hover{background:#D8D8D8;font-weight:700;border-left:6px solid #D8D8D8;}
            QPushButton{font: 75 10pt \"微软雅黑\";}''')  # 下一页

        '''透明的窗口背景会让图形界面有现代感和时尚感，我们来讲图形界面的窗口背景设为透明：'''
        #self.setWindowOpacity(0.95)  # 设置窗口透明度
        #self.setAttribute(QtCore.Qt.WA_TranslucentBackground)  # 设置窗口背景透明
        #self.setWindowFlag(QtCore.Qt.FramelessWindowHint)  # 隐藏边框
        #self.main_layout.setSpacing(0)

    def press_task(self):#画图
        self.pushButton.setIcon(qta.icon('fa5.images', color='#D2F6EE'))  # 画图
        self.pushButton.setStyleSheet(
            '''QPushButton{background:rgb(30,205,151);border-radius:5px;height:25px;border:1px solid #FF0000;}QPushButton:hover{background:rgb(30,205,151);border:1px solid #FF0000;
                font-weight:700;}QPushButton{font: 75 10pt \"微软雅黑\";color:#D2F6EE;}''')
    def press_task2(self):#启动
        self.pushButton_2.setIcon(qta.icon('fa5.play-circle', color='#D2F6EE'))  # 啟動,
        self.pushButton_2.setStyleSheet(
            '''QPushButton{background:rgb(30,205,151);border-radius:5px;height:25px;border:1px solid #FF0000;}QPushButton:hover{background:rgb(30,205,151);border:1px solid #FF0000;
                            font-weight:700;}QPushButton{font: 75 10pt \"微软雅黑\";color:#D2F6EE;}''')
    def press_task3(self):#采集
        self.pushButton_3.setIcon(qta.icon('fa.download', color='#D2F6EE'))  # 采集
        self.pushButton_3.setStyleSheet(
            '''QPushButton{background:rgb(30,205,151);border-radius:5px;height:25px;border:1px solid #FF0000;}QPushButton:hover{background:rgb(30,205,151);border:1px solid #FF0000;
                font-weight:700;}QPushButton{font: 75 10pt \"微软雅黑\";color:#D2F6EE;}''')
    def press_task4(self):#读取
        self.pushButton_4.setIcon(qta.icon('fa.folder-open', color='#D2F6EE'))  # 读取
        self.pushButton_4.setStyleSheet(
            '''QPushButton{background:rgb(30,205,151);border-radius:5px;height:25px;border:1px solid #FF0000;}QPushButton:hover{background:rgb(30,205,151);border:1px solid #FF0000;
                            font-weight:700;}QPushButton{font: 75 10pt \"微软雅黑\";color:#D2F6EE;}''')
    def press_task5(self):#上一页
        self.pushButton_5.setIcon(qta.icon('fa5s.arrow-left', color='#D2F6EE'))
        self.pushButton_5.setStyleSheet(
            '''QPushButton{background:rgb(30,205,151);border-radius:5px;height:25px;border-right:6px solid #1ECD97;}QPushButton:hover{background:rgb(30,205,151);
                                        font-weight:700;border-right:6px solid #1ECD97;}QPushButton{font: 75 10pt \"微软雅黑\";color:#D2F6EE;}''')
    def press_task6(self):#下一页
        self.pushButton_6.setIcon(qta.icon('fa5s.arrow-right', color='#D2F6EE'))  # 下一页
        self.pushButton_6.setStyleSheet(
            '''QPushButton{background:#1ECD97;border-radius:5px;height:25px;border-left:6px solid #1ECD97;}QPushButton:hover{background:rgb(30,205,151);
                                        font-weight:700;border-left:6px solid #1ECD97;}QPushButton{font: 75 10pt \"微软雅黑\";color:#D2F6EE;}''')
    def press_task7(self):#上一页
        self.pushButton_7.setIcon(qta.icon('fa5s.arrow-left', color='#D2F6EE'))
        self.pushButton_7.setStyleSheet(
            '''QPushButton{background:#1ECD97;border-radius:5px;height:25px;border-right:6px solid #1ECD97;}QPushButton:hover{background:rgb(30,205,151);
                                        font-weight:700;border-right:6px solid #1ECD97;}QPushButton{font: 75 10pt \"微软雅黑\";color:#D2F6EE;}''')
    def press_task8(self):#下一页
        self.pushButton_8.setIcon(qta.icon('fa5s.arrow-right', color='#D2F6EE'))  # 下一页
        self.pushButton_8.setStyleSheet(
            '''QPushButton{background:rgb(30,205,151);border-radius:5px;height:25px;border-left:6px solid #1ECD97;}QPushButton:hover{background:rgb(30,205,151);
                                        font-weight:700;border-left:6px solid #1ECD97;}QPushButton{font: 75 10pt \"微软雅黑\";color:#D2F6EE;}''')



    def afterGenerationConfig(self):
        self.graphicsView.setRenderHint(QPainter.Antialiasing)  ##设置视图的抗锯齿渲染模式。
        self.graphicsView_2.setRenderHint(QPainter.Antialiasing)  ##设置视图的抗锯齿渲染模式。
        self.graphicsView_3.setRenderHint(QPainter.Antialiasing)
        self.graphicsView_4.setRenderHint(QPainter.Antialiasing)
        self.graphicsView_5.setRenderHint(QPainter.Antialiasing)
        #self.scene = self.graphicsView.scene()
    def currtime(self):
        self.curr_time = QDateTime.currentDateTime()
        str_date = self.curr_time.toString("yyyy-MM-dd")
        str_time = self.curr_time.toString("hh:mm:ss")
        str_sec=self.curr_time.toString("ss")
        #self.label_19.setText(str_date)
        #self.label_20.setText(str_time)
    #
    def show_surgepic(self):
        wdirp = wdir0 + 'pictures/' + caseno + '/'
        xx = self.comboBox_2.currentIndex()
        surgepic = 'surge_' + caseno + '_'+site3e[xx]+'.png'
        img = Image.open(wdirp + surgepic)
        img.show()
    def show_wlpic(self):
        wdirp = wdir0 + 'pictures/' + caseno + '/'
        xx = self.comboBox_2.currentIndex()
        wlpic= 'wl_' + caseno + '_'+site3e[xx]+'.png'
        img = Image.open(wdirp + wlpic)
        img.show()
    def show_maxsurpic(self):
        wdirp = wdir0 + 'pictures/' + caseno + '/'
        maxsurpic = 'maxSurge_' + caseno + '.png'
        img = Image.open(wdirp + maxsurpic)
        img.show()
    def show_prosurpics(self):
        prono=self.comboBox_5.currentIndex()
        picnames = []
        wdirp = wdir0 + 'pictures/' + caseno + '/'
        for i in range(len(levs)):
            picname = 'proSurge_' + caseno + levs2[i] + '.png'
            picnames.append(picname)
        img = Image.open(wdirp + picnames[prono])
        img.show()
    def show_pathpic(self):
        wdirp = wdir0 + 'pictures/' + caseno + '/'
        pathpic = 'typhoon_path_' + caseno + '.png'
        img = Image.open(wdirp+pathpic)
        img.show()

    #
    def eventFilter(self, watched, event):
        if watched == self.graphicsView and event.type() == QEvent.MouseButtonDblClick:
            thread_01 = Thread(target=self.show_surgepic)
            thread_01.start()
        if watched == self.graphicsView_2 and event.type() == QEvent.MouseButtonDblClick:
            thread_02 = Thread(target=self.show_wlpic)
            thread_02.start()
        if watched == self.graphicsView_3 and event.type() == QEvent.MouseButtonDblClick:
            thread_03 = Thread(target=self.show_maxsurpic)
            thread_03.start()
        if watched == self.graphicsView_4 and event.type() == QEvent.MouseButtonDblClick:
            thread_04 = Thread(target=self.show_prosurpics)
            thread_04.start()
        if watched == self.graphicsView_5 and event.type() == QEvent.MouseButtonDblClick:
            thread_05 = Thread(target=self.show_pathpic)
            thread_05.start()
        return QWidget.eventFilter(self, watched, event)
    #==============================    模拟结果画图    ==============================#
    def pushbutton_task(self):
        self.status.showMessage(" ")
        QApplication.processEvents()
        west, east, south, north=self.get_lonlat()
        cmin = self.lineEdit_7.text()
        cmax = self.lineEdit_8.text()
        wdirp = wdir0 + 'pictures/' + caseno + '/'
        if not os.path.exists(wdirp):
            os.makedirs(wdirp)
        # surge
        self.status.showMessage(' 加载单站风暴增水数据 ... ')
        QApplication.processEvents()
        time.sleep(0.2)
        print(st)
        dzs, wla, tide = get_plotdata(wdir0, site3, site3e, st, hrs1, dhrs, caseno)
        self.status.showMessage(' 绘制单站风暴增水曲线图 ... ')
        QApplication.processEvents()
        time.sleep(0.2)
        wdirp, surpic, wlpic = plot_surge(wdir0, site3, site3e, caseno, dhrs, st, dzs, wla, tide, msl, wls4s, perc,
                                              -1)
        # surge        
        self.imgShow = QPixmap()
        self.imgShow.load(wdirp + surpic)

        self.imgShowItem = QGraphicsPixmapItem()
        self.imgShowItem.setPixmap(QPixmap(self.imgShow))
        # self.imgShowItem.setPixmap(QPixmap(self.imgShow).scaled(8000,  8000))    //自己设定尺寸
        self.graphicsView.scene_img.addItem(self.imgShowItem)
        self.graphicsView.setScene(self.graphicsView.scene_img)
        self.graphicsView.fitInView(QGraphicsPixmapItem(QPixmap(self.imgShow)))  # // 图像自适应大小
        # wl
        self.imgShow = QPixmap()
        self.imgShow.load(wdirp + wlpic)

        self.imgShowItem = QGraphicsPixmapItem()
        self.imgShowItem.setPixmap(QPixmap(self.imgShow))
        # self.imgShowItem.setPixmap(QPixmap(self.imgShow).scaled(8000,  8000))    //自己设定尺寸
        self.graphicsView_2.scene_img.addItem(self.imgShowItem)
        self.graphicsView_2.setScene(self.graphicsView_2.scene_img)
        self.graphicsView_2.fitInView(QGraphicsPixmapItem(QPixmap(self.imgShow)))  # // 图像自适应大小
        #
        #maxsurge
        self.status.showMessage(' 加载最大风暴增水数据 ... ')
        QApplication.processEvents()
        time.sleep(0.2)
        dznum = get_maxsurgedata(wdir0, caseno, st)
        self.status.showMessage(' 绘制最大风暴增水图片 ... ')
        QApplication.processEvents()
        time.sleep(0.2)
        maxpicname,maxsur=draw_maxsurge(wdir0, caseno, lonsz, latsz, tlon1, tlat1, st, dznum, west, east, south, north,cmin,cmax)
        self.lineEdit_8.setText(str(int(maxsur)))
        #prosurge
        self.status.showMessage(' 绘制风暴增水概率图片 ... ')
        QApplication.processEvents()
        time.sleep(0.2)
        propicnames=draw_prosurge(wdir0, caseno, lonsz, latsz, tlon1, tlat1, st, dznum, levs, levs2, west, east, south,
                      north)
        self.maxsurpic = maxpicname
        self.prosurpics = propicnames

        # maxsurge
        self.tabWidget.setCurrentIndex(1)
        self.imgShow = QPixmap()
        self.imgShow.load(wdirp + maxpicname)

        self.imgShowItem = QGraphicsPixmapItem()
        self.imgShowItem.setPixmap(QPixmap(self.imgShow))
        # self.imgShowItem.setPixmap(QPixmap(self.imgShow).scaled(8000,  8000))    //自己设定尺寸
        self.graphicsView_3.scene_img.addItem(self.imgShowItem)
        self.graphicsView_3.setScene(self.graphicsView_3.scene_img)
        self.graphicsView_3.fitInView(QGraphicsPixmapItem(QPixmap(self.imgShow)))  # // 图像自适应大小
        # prosurge
        self.tabWidget.setCurrentIndex(2)
        self.imgShow = QPixmap()
        self.imgShow.load(wdirp + propicnames[0])

        self.imgShowItem = QGraphicsPixmapItem()
        self.imgShowItem.setPixmap(QPixmap(self.imgShow))
        # self.imgShowItem.setPixmap(QPixmap(self.imgShow).scaled(8000,  8000))    //自己设定尺寸
        self.graphicsView_4.scene_img.addItem(self.imgShowItem)
        self.graphicsView_4.setScene(self.graphicsView_4.scene_img)
        self.graphicsView_4.fitInView(QGraphicsPixmapItem(QPixmap(self.imgShow)))  # // 图像自适应大小
        #
        self.tabWidget.setCurrentIndex(0)
        self.status.showMessage('风暴潮集合预报产品制作完成！')
        QApplication.processEvents()
        time.sleep(0.2)
        self.pushButton.setIcon(qta.icon('fa5.images', color='#D2F6EE'))
        self.pushButton.setStyleSheet(
            '''QPushButton{background:rgb(30,205,151);border-radius:5px;height:25px;}QPushButton:hover{background:rgb(30,205,151);border-bottom:6px solid rgb(30,205,151);
            font-weight:700;}QPushButton{font: 75 10pt \"微软雅黑\";color:#D2F6EE;}''')
        # 更新资料目录
        tynos = []
        timstrs = []
        casedirs = os.listdir(wdir0 + 'pictures/')
        for i in range(len(casedirs)):
            if len(casedirs[i]) == 17 and casedirs[i][0:2] == 'TY':
                tynos.append(casedirs[i][2:6])
                timstrs.append(casedirs[i][-6:])
        tynos.sort(reverse=True)
        timstrs.sort(reverse=True)
        tynos = pd.unique(tynos)
        self.comboBox_3.clear()
        self.comboBox_4.clear()
        self.comboBox_3.addItems(tynos)
        self.comboBox_4.addItems(timstrs)
    #==============================    模型启动    ==============================#
    def pushbutton2_task(self):
        self.status.showMessage(" ")
        QApplication.processEvents()
        csno = self.comboBox.currentIndex()
        pnum = int(casenum[csno][:-1])
        print(caseno)
        path0 = os.listdir(wdir0+'pathfiles/' + caseno + '/')
        #
        if len(path0)>=pnum:
            os.startfile(wdir0 + "sz_start_gpu_model.bat")

            filenum = 0
            wdir = wdir0 + 'result/' + caseno + '/'
            if not os.path.exists(wdir):
                os.makedirs(wdir)
            while filenum < pnum * 2:
                path1 = os.listdir(wdir)
                files = []
                for fn in path1:
                    if fn[-4:] == '.dat':
                        files.append(fn)
                filenum = len(files)
                self.status.showMessage(' 模拟进度: ' +str("{:.1f}".format(filenum/(pnum * 2) * 100)) + '% ... ')
                QApplication.processEvents()
                time.sleep(0.2)
            self.status.showMessage('模拟完成! 可点击画图制作产品。')
            QApplication.processEvents()
            time.sleep(1)
            self.pushButton_2.setIcon(qta.icon('fa5.play-circle', color='#D2F6EE'))
            self.pushButton_2.setStyleSheet(
                '''QPushButton{background:rgb(30,205,151);border-radius:5px;height:25px;}QPushButton:hover{background:rgb(30,205,151);border-bottom:6px solid rgb(30,205,151);
                font-weight:700;}QPushButton{font: 75 10pt \"微软雅黑\";color:#D2F6EE;}''')
        else:
            self.status.showMessage('路径文件不存在或缺失！请读取或采集路径数据后再试。')
            QApplication.processEvents()
            time.sleep(1)
            return

    #==============================    台风数据采集    ==============================#
    def pushbutton3_task(self):
        global caseno, syear, tyid, tlon1, tlat1, hrs1, st
        self.status.showMessage(" ")
        QApplication.processEvents()
        wtime = datetime.now()
        wtimes = wtime.strftime('%Y%m%d%H')
        wyear = str(wtimes)[0:4]
        #
        west, east, south, north =self.get_lonlat()
        tyid = self.lineEdit_15.text()
        csno = self.comboBox.currentIndex()  # 集合成员个数
        pnum = int(casenum[csno][:-1])        # 集合成员个数
        r01 = float(self.lineEdit_9.text())
        r02 = float(self.lineEdit_10.text())
        r03 = float(self.lineEdit_11.text())
        r04 = float(self.lineEdit_12.text())
        r05 = float(self.lineEdit_13.text())
        dR = float(self.lineEdit_14.text())
        syear='20'+tyid[0:2]
        #
        if tyid=='':
            print('请先输入需要采集的台风编号！')
            self.pushButton_3.setIcon(qta.icon('fa.download', color='black'))  # 采集
            self.pushButton_3.setStyleSheet(
                '''QPushButton{background:#F0F0F0;border-radius:5px;height:25px;}QPushButton:hover{background:#D8D8D8;font-weight:700;border-left:6px solid #D8D8D8;}
                QPushButton{font: 75 10pt \"微软雅黑\";}''')  # 采集
            self.status.showMessage('请先输入需要采集的台风编号！')
            QApplication.processEvents()
            time.sleep(0.2)
            return
        elif len(tyid)!=4:
            print('请输入正确格式的台风编号！')
            self.pushButton_3.setIcon(qta.icon('fa.download', color='black'))  # 采集
            self.pushButton_3.setStyleSheet(
                '''QPushButton{background:#F0F0F0;border-radius:5px;height:25px;}QPushButton:hover{background:#D8D8D8;font-weight:700;border-left:6px solid #D8D8D8;}
                QPushButton{font: 75 10pt \"微软雅黑\";}''')  # 采集
            self.status.showMessage('请输入正确格式的台风编号！')
            QApplication.processEvents()
            time.sleep(0.2)
            return
        #
        outcma = get_typath_cma(wdir0, tyid)
        if outcma == None:
            print("CMA: 目前西太平洋和南海没有活跃台风。")
            self.pushButton_3.setIcon(qta.icon('fa.download', color='black'))  # 采集
            self.pushButton_3.setStyleSheet(
                '''QPushButton{background:#F0F0F0;border-radius:5px;height:25px;}QPushButton:hover{background:#D8D8D8;font-weight:700;border-left:6px solid #D8D8D8;}
                QPushButton{font: 75 10pt \"微软雅黑\";}''')  # 采集

            self.status.showMessage("CMA: 目前西太平洋和南海没有活跃台风。")
            QApplication.processEvents()
            time.sleep(1.5)
            return
        else:
            filecma = outcma[0]
            tcma = outcma[1]
            loncma = outcma[2]
            latcma = outcma[3]
            pcma = outcma[4]
            spdcma = outcma[5]
            idcma = outcma[6]
            tyname = outcma[-1]
            # 判断是否在区域内
            tyflag = 0
            tlon = []
            tlat = []
            pres = []
            for i in range(len(loncma)):
                lon = float(loncma[i])
                lat = float(latcma[i])
                pp = float(pcma[i])
                tlon.append(lon)
                tlat.append(lat)
                pres.append(pp)
                if lon <= east and lon >= west and lat <= north and lat >= south:
                    tyflag = 1

            #
            if tyflag == 1:
                caseno = 'TY' + idcma + '_' + wtimes
                strcma =tcma[0]
                print(
                    "CMA: 发现活跃台风 (编号" + tyid + ")，案例编号设为：" + caseno + "。")
                self.status.showMessage(
                    "CMA: 发现活跃台风 (编号" + tyid + ")，案例编号设为：" + caseno + "。")
                time.sleep(0.5)
                print("台风路径数据已读取，制作并绘制集合预报成员中...")
                self.status.showMessage("台风路径数据已读取，制作并绘制集合预报成员中...")
                QApplication.processEvents()
                time.sleep(0.2)
                # spdorgs.append(spdcma)
                sth = []
                hrs = []
                for i in range(len(tcma)):
                    sth.append(datetime.strptime(tcma[i], '%Y%m%d%H'))
                    dday = (sth[i] - sth[0]).days
                    dsec = (sth[i] - sth[0]).seconds
                    hrs.append(round(dsec / 3600 + dday * 24))
                #winsound.Beep(500, 2000)
                #绘制集合成员图
                st = datetime.strptime(strcma, '%Y%m%d%H')
                hrs1, tlon1, tlat1, pres1 = interp6h(hrs, tlon, tlat, pres)
                wdirp, picname, filename = gen_draw_typath(wdir0, st, dR, caseno, tyid, r01, r02, r03, r04, r05, pnum,
                                                           west, east, south, north, tlon1, tlat1, pres1, lonsz, latsz)
                output_controlfile(wdir0, filename)
                self.wdirp=wdirp
                self.pathpic=picname
                #
                self.tabWidget.setCurrentIndex(0)
                self.imgShow = QPixmap()
                self.imgShow.load(wdirp + picname)

                self.imgShowItem = QGraphicsPixmapItem()
                self.imgShowItem.setPixmap(QPixmap(self.imgShow))
                # self.imgShowItem.setPixmap(QPixmap(self.imgShow).scaled(8000,  8000))    //自己设定尺寸
                self.graphicsView_5.scene_img.addItem(self.imgShowItem)
                self.graphicsView_5.setScene(self.graphicsView_5.scene_img)
                self.graphicsView_5.fitInView(QGraphicsPixmapItem(QPixmap(self.imgShow)))  # // 图像自适应大小
                #更新资料目录
                tynos = []
                timstrs = []
                casedirs = os.listdir(wdir0 + 'pictures/')
                for i in range(len(casedirs)):
                    if len(casedirs[i]) == 17 and casedirs[i][0:2] == 'TY':
                        tynos.append(casedirs[i][2:6])
                        timstrs.append(casedirs[i][-6:])
                self.comboBox_3.clear()
                self.comboBox_4.clear()
                tynos.sort(reverse=True)
                timstrs.sort(reverse=True)
                tynos = pd.unique(tynos)
                self.comboBox_3.addItems(tynos)
                self.comboBox_4.addItems(timstrs)
                #
                print(
                    "台风集合预报成员制作完成，可点击启动进行模拟。")
                self.status.showMessage(
                    "台风集合预报成员制作完成，可点击启动进行模拟。")
                QApplication.processEvents()
                time.sleep(0.2)
                self.pushButton_3.setIcon(qta.icon('fa.download', color='#D2F6EE'))  # 采集
                self.pushButton_3.setStyleSheet(
                    '''QPushButton{background:rgb(30,205,151);border-radius:5px;height:25px;}QPushButton:hover{background:rgb(30,205,151);border-bottom:6px solid rgb(30,205,151);
                    font-weight:700;}QPushButton{font: 75 10pt \"微软雅黑\";color:#D2F6EE;}''')
            else:
                print(
                    "CMA: 发现活跃台风 (编号" + tyid + ")，但不在关注区域内，忽略之。")
                self.pushButton_3.setIcon(qta.icon('fa.download', color='black'))  # 采集
                self.pushButton_3.setStyleSheet(
                    '''QPushButton{background:#F0F0F0;border-radius:5px;height:25px;}QPushButton:hover{background:#D8D8D8;font-weight:700;border-left:6px solid #D8D8D8;}
                    QPushButton{font: 75 10pt \"微软雅黑\";}''')  # 采集
                self.status.showMessage(
                    "CMA: 发现活跃台风 (编号" + tyid + ")，但不在关注区域内，忽略之。",
                    1500)
                QApplication.processEvents()
                time.sleep(1.5)
                return

    #==============================    读取台风路径文件    ==============================#
    def pushbutton4_task(self):
        global caseno, syear, tyid, tlon1, tlat1, hrs1, st
        wtime = datetime.now()
        wtimes = wtime.strftime('%Y%m%d%H')
        wyear = str(wtimes)[0:4]
        self.status.showMessage(" ")
        QApplication.processEvents()
        #
        west, east, south, north=self.get_lonlat()
        csno = self.comboBox.currentIndex()  # 集合成员个数
        pnum = int(casenum[csno][:-1])  # 集合成员个数
        r01 = float(self.lineEdit_9.text())
        r02 = float(self.lineEdit_10.text())
        r03 = float(self.lineEdit_11.text())
        r04 = float(self.lineEdit_12.text())
        r05 = float(self.lineEdit_13.text())
        dR = float(self.lineEdit_14.text())
        #
        # 打开路径文件，读取数据
        dlg = win32ui.CreateFileDialog(1)  # 1表示打开文件对话框
        wdir = wdir0 + 'pathfiles/'
        #
        dlg.SetOFNInitialDir(wdir)  # 设置打开文件对话框中的初始显示目录
        dlg.DoModal()
        filename = dlg.GetPathName()  # 获取选择的文件名称
        print(filename)
        if filename=='':
            self.pushButton_4.setIcon(qta.icon('fa.folder-open', color='black'))  # 读取
            self.pushButton_4.setStyleSheet(
                '''QPushButton{background:#F0F0F0;border-radius:5px;height:25px;}QPushButton:hover{background:#D8D8D8;font-weight:700;border-left:6px solid #D8D8D8;}
                QPushButton{font: 75 10pt \"微软雅黑\";}''')  # 读取
            return

        dirp = filename.split('\\')
        #fl_name = wdir + filename
        # ascii_fl = loadtxt(fl_name, delimiter=' ',dtype=float)
        with open(filename, 'r+') as fi:
            tyli = fi.readlines()
            tylines = []
            for L in tyli:
                tyli0= L.strip('\n').split()
                tylines.append(tyli0)
                #dznum.append(list(map(float, dz3)))
            #ascii_fl = np.array(dznum)
            #print(tylines)
        tyid=''.join(tylines[0])
        syear='20'+tyid[0:2]
        #print(tyid,syear)
        #
        loncma=[]
        latcma=[]
        pcma=[]
        tcma = []
        for i in range(len(tylines)-3):
            loncma.append(tylines[i+3][1])
            latcma.append(tylines[i+3][2])
            pcma.append(tylines[i+3][3])
            tt=tylines[i+3][0]
            if len(tt)==5:
                tcma.append(syear + '0'+tt)
            elif len(tt)==6:
                tcma.append(syear + tt)
            else:
                print('台风径文件格式有误！')
                self.pushButton_4.setIcon(qta.icon('fa.folder-open', color='black'))  # 读取
                self.pushButton_4.setStyleSheet(
                    '''QPushButton{background:#F0F0F0;border-radius:5px;height:25px;}QPushButton:hover{background:#D8D8D8;font-weight:700;border-left:6px solid #D8D8D8;}
                    QPushButton{font: 75 10pt \"微软雅黑\";}''')  # 读取
                self.status.showMessage("台风路径文件格式有误！")
                QApplication.processEvents()
                time.sleep(0.5)
                return
        #print(loncma,latcma,pcma)
        self.lineEdit_15.setText(tyid)
        #
        # 判断是否在区域内
        tyflag = 0
        tlon = []
        tlat = []
        pres = []

        for i in range(len(loncma)):
            lon = float(loncma[i])
            lat = float(latcma[i])
            pp = float(pcma[i])
            tlon.append(lon)
            tlat.append(lat)
            pres.append(pp)
            if lon <= east and lon >= west and lat <= north and lat >= south:
                tyflag = 1
        #
        if tyflag == 1:
            caseno = 'TY' + tyid + '_' + wtimes
            strcma = tcma[0]
            print(
                "读取台风 (编号" + tyid + ")路径数据，案例编号设为：" + caseno + "。")
            self.status.showMessage(
                "读取台风 (编号" + tyid + ")路径数据，案例编号设为：" + caseno + "。")
            time.sleep(0.5)
            # spdorgs.append(spdcma)
            sth = []
            hrs = []
            for i in range(len(tcma)):
                sth.append(datetime.strptime(tcma[i], '%Y%m%d%H'))
                dday = (sth[i] - sth[0]).days
                dsec = (sth[i] - sth[0]).seconds
                hrs.append(round(dsec / 3600 + dday * 24))


            # winsound.Beep(500, 2000)
            #
            print("台风路径数据已读取，制作并绘制集合预报成员中...")
            self.status.showMessage("台风路径数据已读取，制作并绘制集合预报成员中...")
            QApplication.processEvents()
            time.sleep(0.2)
            st = datetime.strptime(strcma, '%Y%m%d%H')
            hrs1, tlon1, tlat1, pres1 = interp6h(hrs, tlon, tlat, pres)
            wdirp, picname, filename = gen_draw_typath(wdir0, st, dR, caseno, tyid, r01, r02, r03, r04, r05, pnum,
                                                       west, east, south, north, tlon1, tlat1, pres1, lonsz, latsz)
            output_controlfile(wdir0, filename)
            self.wdirp = wdirp
            self.pathpic = picname
            #
            self.tabWidget.setCurrentIndex(0)
            self.imgShow = QPixmap()
            self.imgShow.load(wdirp + picname)

            self.imgShowItem = QGraphicsPixmapItem()
            self.imgShowItem.setPixmap(QPixmap(self.imgShow))
            # self.imgShowItem.setPixmap(QPixmap(self.imgShow).scaled(8000,  8000))    //自己设定尺寸
            self.graphicsView_5.scene_img.addItem(self.imgShowItem)
            self.graphicsView_5.setScene(self.graphicsView_5.scene_img)
            self.graphicsView_5.fitInView(QGraphicsPixmapItem(QPixmap(self.imgShow)))  # // 图像自适应大小

            # 更新资料目录
            tynos=[]
            timstrs=[]
            casedirs = os.listdir(wdir0 + 'pictures/')
            for i in range(len(casedirs)):
                if len(casedirs[i]) == 17 and casedirs[i][0:2] == 'TY':
                    tynos.append(casedirs[i][2:6])
                    timstrs.append(casedirs[i][-6:])
            tynos.sort(reverse=True)
            timstrs.sort(reverse=True)
            tynos = pd.unique(tynos)
            self.comboBox_3.clear()
            self.comboBox_4.clear()
            self.comboBox_3.addItems(tynos)
            self.comboBox_4.addItems(timstrs)
            #
            print(
                "台风集合预报成员制作完成，可点击启动进行模拟。")
            self.status.showMessage(
                "台风集合预报成员制作完成，可点击启动进行模拟。")
            QApplication.processEvents()
            time.sleep(0.2)
            #
            self.pushButton_4.setIcon(qta.icon('fa.folder-open', color='#D2F6EE'))  # 读取
            self.pushButton_4.setStyleSheet(
                '''QPushButton{background:rgb(30,205,151);border-radius:5px;height:25px;}QPushButton:hover{background:rgb(30,205,151);border-bottom:6px solid rgb(30,205,151);
                font-weight:700;}QPushButton{font: 75 10pt \"微软雅黑\";color:#D2F6EE;}''')
        else:
            print(
                "台风 (编号" + tyid + ")不在关注区域内，忽略之。")
            self.pushButton_4.setIcon(qta.icon('fa.folder-open', color='black'))  # 读取
            self.pushButton_4.setStyleSheet(
                '''QPushButton{background:#F0F0F0;border-radius:5px;height:25px;}QPushButton:hover{background:#D8D8D8;font-weight:700;border-left:6px solid #D8D8D8;}
                QPushButton{font: 75 10pt \"微软雅黑\";}''')  # 读取
            self.status.showMessage(
                "台风 (编号" + tyid + ")不在关注区域内，忽略之。")
            QApplication.processEvents()
            time.sleep(1.5)
            return

    # ==============================    概率分布 上一页 & 下一页   ==============================#
    def pushbutton5_task(self):
        prono = self.comboBox_5.currentIndex()
        wdirp = wdir0 + 'pictures/' + caseno + '/'
        if prono - 1 >= 0:
            self.comboBox_5.setCurrentIndex(prono - 1)
            picnames = []
            for i in range(len(levs)):
                picname = 'proSurge_' + caseno + levs2[i] + '.png'
                picnames.append(picname)
            if not os.path.exists(wdirp + picnames[prono - 1]):
                # self.graphicsView.scene_img = QGraphicsScene()
                self.graphicsView_4.scene_img.clear()
                print(wdirp + picnames[prono - 1] + ' 不存在！')
                self.status.showMessage(wdirp + picnames[prono - 1] + ' 不存在！')
                QApplication.processEvents()
                time.sleep(0.5)
            else:
                self.imgShow = QPixmap()
                self.imgShow.load(wdirp + picnames[prono - 1])

                self.imgShowItem = QGraphicsPixmapItem()
                self.imgShowItem.setPixmap(QPixmap(self.imgShow))
                # self.imgShowItem.setPixmap(QPixmap(self.imgShow).scaled(8000,  8000))    //自己设定尺寸
                self.graphicsView_4.scene_img.addItem(self.imgShowItem)
                self.graphicsView_4.setScene(self.graphicsView_4.scene_img)
                self.graphicsView_4.fitInView(QGraphicsPixmapItem(QPixmap(self.imgShow)))  # // 图像自适应大小
        self.pushButton_5.setIcon(qta.icon('fa5s.arrow-left', color='black'))  # 上一页
        self.pushButton_5.setStyleSheet(
            '''QPushButton{background:#FFFFFF;border-radius:5px;height:25px;}QPushButton:hover{background:#D8D8D8;font-weight:700;border-right:6px solid #D8D8D8;}
            QPushButton{font: 75 10pt \"微软雅黑\";}''')  # 上一页

    def pushbutton6_task(self):
        prono = self.comboBox_5.currentIndex()
        wdirp = wdir0 + 'pictures/' + caseno + '/'
        if prono + 1 <= len(levs) - 1:
            self.comboBox_5.setCurrentIndex(prono + 1)
            picnames = []
            for i in range(len(levs)):
                picname = 'proSurge_' + caseno + levs2[i] + '.png'
                picnames.append(picname)
            if not os.path.exists(wdirp + picnames[prono + 1]):
                # self.graphicsView.scene_img = QGraphicsScene()
                self.graphicsView_4.scene_img.clear()
                print(wdirp + picnames[prono + 1] + ' 不存在！')
                self.status.showMessage(wdirp + picnames[prono + 1] + ' 不存在！')
                QApplication.processEvents()
                time.sleep(0.5)
            else:
                self.imgShow = QPixmap()
                self.imgShow.load(wdirp + picnames[prono + 1])

                self.imgShowItem = QGraphicsPixmapItem()
                self.imgShowItem.setPixmap(QPixmap(self.imgShow))
                # self.imgShowItem.setPixmap(QPixmap(self.imgShow).scaled(8000,  8000))    //自己设定尺寸
                self.graphicsView_4.scene_img.addItem(self.imgShowItem)
                self.graphicsView_4.setScene(self.graphicsView_4.scene_img)
                self.graphicsView_4.fitInView(QGraphicsPixmapItem(QPixmap(self.imgShow)))  # // 图像自适应大小
        self.pushButton_6.setIcon(qta.icon('fa5s.arrow-right', color='black'))  # 下一页
        self.pushButton_6.setStyleSheet(
            '''QPushButton{background:#FFFFFF;border-radius:5px;height:25px;}QPushButton:hover{background:#D8D8D8;font-weight:700;border-left:6px solid #D8D8D8;}
            QPushButton{font: 75 10pt \"微软雅黑\";}''')  # 下一页

    # ==============================    单站增水 上一页 & 下一页   ==============================#
    def pushbutton7_task(self):
        stano = self.comboBox_2.currentIndex()
        wdirp = wdir0 + 'pictures/' + caseno + '/'
        if stano - 1 >= 0:
            self.comboBox_2.setCurrentIndex(stano - 1)
            picnames = []
            picname2s = []
            for i in range(len(site3e)):
                picname = 'surge_' + caseno +'_'+ site3e[i] + '.png'
                picname2 = 'wl_' + caseno +'_'+ site3e[i] + '.png'
                picnames.append(picname)
                picname2s.append(picname2)
            if not os.path.exists(wdirp + picnames[stano - 1]):
                self.label_2.setText('风暴增水过程曲线图')

                # self.graphicsView.scene_img = QGraphicsScene()
                self.graphicsView.scene_img.clear()
                print(wdirp + picnames[stano - 1] + ' 不存在！')
                self.status.showMessage(wdirp + picnames[stano - 1] + ' 不存在！')
                QApplication.processEvents()
                time.sleep(0.5)
            else:
                self.label_2.setText('风暴增水过程曲线图（' + site3[stano - 1] + '站)')

                self.imgShow = QPixmap()
                self.imgShow.load(wdirp + picnames[stano - 1])

                self.imgShowItem = QGraphicsPixmapItem()
                self.imgShowItem.setPixmap(QPixmap(self.imgShow))
                # self.imgShowItem.setPixmap(QPixmap(self.imgShow).scaled(8000,  8000))    //自己设定尺寸
                self.graphicsView.scene_img.addItem(self.imgShowItem)
                self.graphicsView.setScene(self.graphicsView.scene_img)
                self.graphicsView.fitInView(QGraphicsPixmapItem(QPixmap(self.imgShow)))  # // 图像自适应大小
            #
            if not os.path.exists(wdirp + picname2s[stano - 1]):
                # self.graphicsView.scene_img = QGraphicsScene()
                self.label_3.setText('总潮位过程曲线图')
                self.graphicsView_2.scene_img.clear()
                print(wdirp + picname2s[stano - 1] + ' 不存在！')
                self.status.showMessage(wdirp + picname2s[stano - 1] + ' 不存在！')
                QApplication.processEvents()
                time.sleep(0.5)
            else:
                self.label_3.setText('总潮位过程曲线图（' + site3[stano - 1] + '站)')
                self.imgShow = QPixmap()
                self.imgShow.load(wdirp + picname2s[stano - 1])

                self.imgShowItem = QGraphicsPixmapItem()
                self.imgShowItem.setPixmap(QPixmap(self.imgShow))
                # self.imgShowItem.setPixmap(QPixmap(self.imgShow).scaled(8000,  8000))    //自己设定尺寸
                self.graphicsView_2.scene_img.addItem(self.imgShowItem)
                self.graphicsView_2.setScene(self.graphicsView_2.scene_img)
                self.graphicsView_2.fitInView(QGraphicsPixmapItem(QPixmap(self.imgShow)))  # // 图像自适应大小
        self.pushButton_7.setIcon(qta.icon('fa5s.arrow-left', color='black'))  # 上一页
        self.pushButton_7.setStyleSheet(
            '''QPushButton{background:#F0F0F0;border-radius:5px;height:25px;}QPushButton:hover{background:#D8D8D8;font-weight:700;border-right:6px solid #D8D8D8;}
            QPushButton{font: 75 10pt \"微软雅黑\";}''')  # 上一页

    def pushbutton8_task(self):
        stano = self.comboBox_2.currentIndex()
        wdirp = wdir0 + 'pictures/' + caseno + '/'
        if stano + 1 <= len(site3e) - 1:
            self.comboBox_2.setCurrentIndex(stano + 1)
            picnames = []
            picname2s = []
            for i in range(len(site3e)):
                picname = 'Surge_' + caseno +'_'+ site3e[i] + '.png'
                picname2 = 'wl_' + caseno +'_'+ site3e[i] + '.png'
                picnames.append(picname)
                picname2s.append(picname2)
            if not os.path.exists(wdirp + picnames[stano + 1]):
                self.label_2.setText('风暴增水过程曲线图')
                # self.graphicsView.scene_img = QGraphicsScene()
                self.graphicsView.scene_img.clear()
                print(wdirp + picnames[stano + 1] + ' 不存在！')
                self.status.showMessage(wdirp + picnames[stano + 1] + ' 不存在！')
                QApplication.processEvents()
                time.sleep(0.5)
            else:
                self.label_2.setText('风暴增水过程曲线图（' + site3[stano + 1] + '站)')
                self.imgShow = QPixmap()
                self.imgShow.load(wdirp + picnames[stano + 1])

                self.imgShowItem = QGraphicsPixmapItem()
                self.imgShowItem.setPixmap(QPixmap(self.imgShow))
                # self.imgShowItem.setPixmap(QPixmap(self.imgShow).scaled(8000,  8000))    //自己设定尺寸
                self.graphicsView.scene_img.addItem(self.imgShowItem)
                self.graphicsView.setScene(self.graphicsView.scene_img)
                self.graphicsView.fitInView(QGraphicsPixmapItem(QPixmap(self.imgShow)))  # // 图像自适应大小
            #
            if not os.path.exists(wdirp + picname2s[stano + 1]):
                # self.graphicsView.scene_img = QGraphicsScene()
                self.label_3.setText('总潮位过程曲线图')
                self.graphicsView_2.scene_img.clear()
                print(wdirp + picname2s[stano + 1] + ' 不存在！')
                self.status.showMessage(wdirp + picname2s[stano + 1] + ' 不存在！')
                QApplication.processEvents()
                time.sleep(0.5)
            else:
                self.label_3.setText('总潮位过程曲线图（' + site3[stano + 1] + '站)')
                self.imgShow = QPixmap()
                self.imgShow.load(wdirp + picname2s[stano + 1])

                self.imgShowItem = QGraphicsPixmapItem()
                self.imgShowItem.setPixmap(QPixmap(self.imgShow))
                # self.imgShowItem.setPixmap(QPixmap(self.imgShow).scaled(8000,  8000))    //自己设定尺寸
                self.graphicsView_2.scene_img.addItem(self.imgShowItem)
                self.graphicsView_2.setScene(self.graphicsView_2.scene_img)
                self.graphicsView_2.fitInView(QGraphicsPixmapItem(QPixmap(self.imgShow)))  # // 图像自适应大小
        self.pushButton_8.setIcon(qta.icon('fa5s.arrow-right', color='black'))  # 下一页
        self.pushButton_8.setStyleSheet(
            '''QPushButton{background:#F0F0F0;border-radius:5px;height:25px;}QPushButton:hover{background:#D8D8D8;font-weight:700;border-left:6px solid #D8D8D8;}
            QPushButton{font: 75 10pt \"微软雅黑\";}''')  # 下一页
    # ==============================    选择集合成员个数    ==============================#
    def combobox_task(self):
        csno = self.comboBox.currentIndex()  # 集合成员个数
        pnum = casenum[csno][:-1]  # 集合成员个数
        print('已选'+pnum+'台风集合成员。')
        self.status.showMessage(
            '已选'+pnum+'台风集合成员。', 1500)
        QApplication.processEvents()
        time.sleep(0.5)
        pass

    # ==============================    选择单站    ==============================#
    def combobox2_task(self):
        self.status.showMessage('')
        QApplication.processEvents()
        time.sleep(0.1)
        xx = self.comboBox_2.currentIndex()
        print(xx, site3[xx])
        self.label_2.setText('风暴增水过程曲线图（' + site3[xx] + '站)')
        self.label_3.setText('总潮位过程曲线图（' + site3[xx] + '站)')
        wdirp = wdir0 + 'pictures/' +  caseno + '/'
        picname = 'surge_' + caseno + '_' + site3e[xx] + '.png'
        picname2 = 'wl_' + caseno + '_' + site3e[xx] + '.png'
        self.wdirp=wdirp
        self.surgepic=picname
        self.wlpic=picname2
        #
        tt1 = time.time()
        if not os.path.exists(wdirp + picname):
            # self.graphicsView.scene_img = QGraphicsScene()
            self.graphicsView.scene_img.clear()
            print(wdirp + picname + ' 不存在！')
            self.status.showMessage(wdirp + picname + ' 不存在！')
            QApplication.processEvents()
            time.sleep(0.5)
        else:
            # self.graphicsView.scene_img = QGraphicsScene()
            self.imgShow = QPixmap()
            self.imgShow.load(wdirp + picname)

            self.imgShowItem = QGraphicsPixmapItem()
            self.imgShowItem.setPixmap(QPixmap(self.imgShow))
            # self.imgShowItem.setPixmap(QPixmap(self.imgShow).scaled(8000,  8000))    //自己设定尺寸
            self.graphicsView.scene_img.addItem(self.imgShowItem)
            self.graphicsView.setScene(self.graphicsView.scene_img)
            self.graphicsView.fitInView(QGraphicsPixmapItem(QPixmap(self.imgShow)))  # // 图像自适应大小
        #
        if not os.path.exists(wdirp + picname2):
            # self.graphicsView_3.scene_img = QGraphicsScene()
            self.graphicsView_2.scene_img.clear()
            print(wdirp + picname2 + ' 不存在！')
            self.status.showMessage(wdirp + picname2 + ' 不存在！')
            QApplication.processEvents()
            time.sleep(0.5)
        else:
            # self.graphicsView_2.scene_img = QGraphicsScene()
            self.imgShow = QPixmap()
            self.imgShow.load(wdirp + picname2)

            self.imgShowItem = QGraphicsPixmapItem()
            self.imgShowItem.setPixmap(QPixmap(self.imgShow))
            # self.imgShowItem.setPixmap(QPixmap(self.imgShow).scaled(8000,  8000))    //自己设定尺寸
            self.graphicsView_2.scene_img.addItem(self.imgShowItem)
            self.graphicsView_2.setScene(self.graphicsView_2.scene_img)
            self.graphicsView_2.fitInView(QGraphicsPixmapItem(QPixmap(self.imgShow)))  # // 图像自适应大小
        print('Time used: {} sec'.format(time.time() - tt1))

    # ==============================    选择台风编号    ==============================#
    def combobox3_task(self):
        ftyno = self.comboBox_3.currentText()
        self.lineEdit_15.setText(ftyno)
        casedirs = os.listdir(wdir0 + 'pictures/')
        timstrs=[]
        self.comboBox_4.clear()
        for i in range(len(casedirs)):
            if len(casedirs[i]) == 17 and casedirs[i][2:6] == ftyno:
                timstrs.append(casedirs[i][-6:])
        if timstrs!=[]:
            self.comboBox_4.addItems(timstrs)
        else:
            self.comboBox_4.addItems('None')

    # ==============================    选择操作时间    ==============================#
    def combobox4_task(self):
        global caseno, st,hrs1,tlon1,tlat1
        self.status.showMessage(" ")
        QApplication.processEvents()
        ftyno = self.comboBox_3.currentText()
        ftimstr= self.comboBox_4.currentText()
        self.lineEdit_15.setText(ftyno)
        casedirs = os.listdir(wdir0 + 'pictures/')
        for i in range(len(casedirs)):
            if casedirs[i][-6:] == ftimstr and casedirs[i][2:6] == ftyno and len(casedirs[i]) == 17:
                scaseno=casedirs[i]
        caseno = scaseno
        #  ================加载台风路径文件 ================#
        #  #D:\szsurge\pathfiles\TY2022_2021010416\TY2022_2021010416_c0_p00
        filename= wdir0 + 'pathfiles/' + caseno + '/'+caseno+'_c0_p00'
        with open(filename, 'r+') as fi:
            tyli = fi.readlines()
            tylines = []
            for L in tyli:
                tyli0= L.strip('\n').split()
                tylines.append(tyli0)
        tyid=''.join(tylines[0])
        syear='20'+tyid[0:2]

        loncma = []
        latcma = []
        pcma = []
        tcma = []
        for i in range(len(tylines) - 3):
            loncma.append(tylines[i + 3][1])
            latcma.append(tylines[i + 3][2])
            pcma.append(tylines[i + 3][3])
            tt = tylines[i + 3][0]
            if len(tt) == 5:
                tcma.append(syear + '0' + tt)
            elif len(tt) == 6:
                tcma.append(syear + tt)
        tlon = []
        tlat = []
        pres = []
        for i in range(len(loncma)):
            lon = float(loncma[i])
            lat = float(latcma[i])
            pp = float(pcma[i])
            tlon.append(lon)
            tlat.append(lat)
            pres.append(pp)
        sth = []
        hrs = []
        for i in range(len(tcma)):
            sth.append(datetime.strptime(tcma[i], '%Y%m%d%H'))
            dday = (sth[i] - sth[0]).days
            dsec = (sth[i] - sth[0]).seconds
            hrs.append(round(dsec / 3600 + dday * 24))
        hrs1, tlon1, tlat1, pres1 = interp6h(hrs, tlon, tlat, pres)
        stime=tcma[0]
        st = datetime.strptime(stime, '%Y%m%d%H')
        print(stime,st)
        #  =================================================#
        #
        #xx = self.comboBox_2.currentIndex()
        self.combobox2_task()# 加载单站图片
        wdirp = wdir0 + 'pictures/' + caseno + '/'
        # 加载路径图片
        pathpic = 'typhoon_path_' + caseno + '.png'
        if not os.path.exists(wdirp + pathpic):
            # self.graphicsView_3.scene_img = QGraphicsScene()
            self.graphicsView_5.scene_img.clear()
            print(wdirp + pathpic + ' 不存在！')
            self.status.showMessage(wdirp + pathpic + ' 不存在！')
            QApplication.processEvents()
            time.sleep(0.5)
        else:
            self.tabWidget.setCurrentIndex(0)
            self.imgShow = QPixmap()
            self.imgShow.load(wdirp + pathpic)

            self.imgShowItem = QGraphicsPixmapItem()
            self.imgShowItem.setPixmap(QPixmap(self.imgShow))
            # self.imgShowItem.setPixmap(QPixmap(self.imgShow).scaled(8000,  8000))    //自己设定尺寸
            self.graphicsView_5.scene_img.addItem(self.imgShowItem)
            self.graphicsView_5.setScene(self.graphicsView_5.scene_img)
            self.graphicsView_5.fitInView(QGraphicsPixmapItem(QPixmap(self.imgShow)))  # // 图像自适应大小

        # 加载最大风暴增水图片
        maxpicname = 'maxSurge_' + caseno + '.png'
        if not os.path.exists(wdirp + maxpicname):
            # self.graphicsView_3.scene_img = QGraphicsScene()
            self.graphicsView_3.scene_img.clear()
            print(wdirp + pathpic + ' 不存在！')
            self.status.showMessage(wdirp + pathpic + ' 不存在！')
            QApplication.processEvents()
            time.sleep(0.5)
        else:
            self.tabWidget.setCurrentIndex(1)
            self.imgShow = QPixmap()
            self.imgShow.load(wdirp + maxpicname)

            self.imgShowItem = QGraphicsPixmapItem()
            self.imgShowItem.setPixmap(QPixmap(self.imgShow))
            # self.imgShowItem.setPixmap(QPixmap(self.imgShow).scaled(8000,  8000))    //自己设定尺寸
            self.graphicsView_3.scene_img.addItem(self.imgShowItem)
            self.graphicsView_3.setScene(self.graphicsView_3.scene_img)
            self.graphicsView_3.fitInView(QGraphicsPixmapItem(QPixmap(self.imgShow)))  # // 图像自适应大小
        #
        # 加载风暴增水概率分布图片
        propicnames = []
        for i in range(len(levs)):
            picname = 'proSurge_' + caseno + levs2[i] + '.png'
            propicnames.append(picname)
        if not os.path.exists(wdirp + maxpicname):
            # self.graphicsView_3.scene_img = QGraphicsScene()
            self.graphicsView_4.scene_img.clear()
            print(wdirp + pathpic + ' 不存在！')
            self.status.showMessage(wdirp + pathpic + ' 不存在！')
            QApplication.processEvents()
            time.sleep(0.5)
        else:
            self.tabWidget.setCurrentIndex(2)
            self.imgShow = QPixmap()
            self.imgShow.load(wdirp + propicnames[0])

            self.imgShowItem = QGraphicsPixmapItem()
            self.imgShowItem.setPixmap(QPixmap(self.imgShow))
            # self.imgShowItem.setPixmap(QPixmap(self.imgShow).scaled(8000,  8000))    //自己设定尺寸
            self.graphicsView_4.scene_img.addItem(self.imgShowItem)
            self.graphicsView_4.setScene(self.graphicsView_4.scene_img)
            self.graphicsView_4.fitInView(QGraphicsPixmapItem(QPixmap(self.imgShow)))  # // 图像自适应大小
        #
        self.tabWidget.setCurrentIndex(0)
    # ==============================    选择>?米概率分布    ==============================#
    def combobox5_task(self):
        wdirp = wdir0 + 'pictures/' + caseno + '/'
        prono = self.comboBox_5.currentIndex()
        picnames=[]
        for i in range(len(levs)):
            picname = 'proSurge_' + caseno+ levs2[i] + '.png'
            picnames.append(picname)
        self.imgShow = QPixmap()
        self.imgShow.load(wdirp + picnames[prono])

        self.imgShowItem = QGraphicsPixmapItem()
        self.imgShowItem.setPixmap(QPixmap(self.imgShow))
        # self.imgShowItem.setPixmap(QPixmap(self.imgShow).scaled(8000,  8000))    //自己设定尺寸
        self.graphicsView_4.scene_img.addItem(self.imgShowItem)
        self.graphicsView_4.setScene(self.graphicsView_4.scene_img)
        self.graphicsView_4.fitInView(QGraphicsPixmapItem(QPixmap(self.imgShow)))  # // 图像自适应大小
    #
    def get_lonlat(self):
        west = float(self.lineEdit_3.text())
        east = float(self.lineEdit_4.text())
        south = float(self.lineEdit_5.text())
        north = float(self.lineEdit_6.text())
        if west >= east or south >= north:
            print('请输入正确的画图区域！')
            self.status.showMessage('请输入正确的画图区域！')
            QApplication.processEvents()
            time.sleep(0.2)
            return
        if west < 105:
            west = 105
        if east > 123:
            east = 123
        if south < 15:
            south = 15
        if north > 26:
            north = 26
        return west, east, south, north
def main():
    app = QtWidgets.QApplication(sys.argv)
    gui = MainUi()
    #
    gui.show()

    sys.exit(app.exec_())

if __name__ == '__main__':
    main()