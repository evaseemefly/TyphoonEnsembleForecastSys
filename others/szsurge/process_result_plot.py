import numpy as np
from numpy import *
import os
from math import *

from datetime import *
#import bokeh.palettes as bp
#from bokeh.plotting import figure, output_file, show
#from bokeh.io import output_notebook
from io import BytesIO
import base64
import pandas as pd
import time

#from flask import Flask,  render_template

#app = Flask(__name__)

wdir0='D:/szsurge/'
#wdir=wdir0+'result/TY1822_2019061010/'
stime='2020091517'
hcma=[0,6,12,18,24,30,36,42,48]

wtime=datetime.now()
wtimes=wtime.strftime('%Y%m%d%H')
tyno='2022'
dhrs=1
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
xx=2
perc = [[0.622459331201855,0.377540668798145,0,0,0,0,0,0],                                                                  #1Q
        [0.511247316569098,0.361272035812932,0.127480647617970,0,0,0,0,0],                                                    #2Q
        [0.447236368708731,0.346535478033354,0.161205360081582,0.0450227931763340,0,0,0,0],                                   #3Q
        [0.400517551714126,0.329456751386887,0.183370297149815,0.0690578866644997,0.0175975130846732,0,0,0],                  #4Q
        [0.334118261046163,0.294858330470191,0.202652969294367,0.108472317838118,0.0452179894932070,0.0146801318579536,0,0],  #5Q
        [0.286632500828924,0.262800543511864,0.202548363088809,0.131229921447511,0.0714724471890523,0.0327224707706080,0.0125937531632317,0],  #6Q
        [0.250977633593432,0.235471130014034,0.194466864320737,0.141370518440951,0.0904643330162669,0.0509566907449681,0.0252656422414563,0.0110271876281545]]#7Q
perc=np.array(perc)
#caseno='TY'+tyno+'_'+wtimes
#caseno='TY'+tyno+'_2020042710'
caseno='TY'+tyno+'_2021010416'
site3=['汕尾','惠州','深圳东山','深圳南澳','盐田','大梅沙','赤湾H','蛇口','前海湾','深圳机场']
site3e=['SHANWEI','HUIZHOU','SZDONGSHAN','SZNANAO','YANTIAN','DAMEISHA','CHIWANH','SHEKOU','QIANHAIWAN','SZJICHANG']

#
st=datetime.strptime(stime,'%Y%m%d%H')
#print(str(st))
#
def get_plotdata(wdir0,site3,site3e,st,hcma,dhrs,caseno):
    #wdir =wdir0+'result/'+caseno
    tt1 = time.time()
    syear = str(st)[0:4]
    tymm = int(str(st)[5:7])
    tydd = int(str(st)[8:10])
    tyhh = int(str(st)[11:13])
    #print(tymm,tydd,tyhh)
    wdir = wdir0 + 'result/'+caseno+'/'
    path1 = os.listdir(wdir)
    nsta=len(site3)
    # identify whether the year is a leap year or not
    mon1 = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    mon2 = [31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    if int(syear) % 4 != 0:
        days = 365
        mon = mon1
    elif int(syear) % 100 != 0:
        days = 366
        mon = mon2
    elif int(syear) % 400 == 0:
        days = 366
        mon = mon2
    else:
        days = 365
        mon = mon1
    day=np.cumsum(mon)
    if tymm != 1:
        tyhrs = (day[tymm - 1]+ tydd - 1) * 24 + tyhh + 1
    else:
        tyhrs = (tydd - 1) * 24 + tyhh + 1

    # load tide
    ehrs=int(hcma[-1])
    #print(tyhrs,ehrs,type(ehrs))
    #
    tide = np.zeros((round(ehrs/dhrs)+1, nsta))
    for i in range(len(site3)):#
        #
        tfile = wdir0 + 'tide/'+syear+'/' + site3e[i] + syear
        with open(tfile, 'r+') as fi:
            tideli = fi.readlines()
            tidelines = []
            for L in tideli:
                tideli0= L.strip('\n').split()
                tidelines.append(tideli0)
        #
        tt=np.array(tidelines)

        #print(tt,type(tt),mm,nn)
        tt2=tt[:, 0:24]
        mm, nn = shape(tt2)
        tt2=np.array(tt2)
        tt3=tt2.reshape(mm*nn)
        tide[:,i]=tt3[tyhrs+hcma[0]-1:tyhrs+ehrs]
    #print(tide)
    #
    dzs=[]
    wla=[]
    cnum=[]
    for i in range(len(path1)):
        if path1[i][0:5]=='Surge':
            fi = open(wdir + path1[i], 'r+')
            cnum.append(path1[i][24:26])
            #print(' Reading '+ path1[i] + '...')
            dz=fi.read()
            dzz=dz.split('\n')
            dz2=dz.split()
            #print(len(dz2))
            dznum = np.zeros((int(len(dz2)/nsta),nsta))

            #dz2=reshape(dzz,len(dzz)/41,41)
            for j in range(len(dzz)):
                if len(dzz[j])>0:
                    dzzline=dzz[j].split()
                    for k in range(len(dzzline)):
                        dznum[j, k]=float(dzzline[k])
            dzs.append(dznum)

            wl = dznum + tide
            wla.append(wl)
    if dzs==[]:
        return None,None,None,None
    else:
        #dzs wla 路徑*時次*站位
        print(' The Plot Data is loaded.')
        print('Time used: {} sec'.format(time.time() - tt1))
        cnum = pd.unique(cnum)
        #print(cnum)
        return dzs,wla,tide,cnum


#========== 利用bokeh畫圖 ==========#
'''
output_file(wdir0+'/fb_plot.html')
p=figure(plot_width = 800, plot_height = 400, # 图表宽度、高度
           tools = 'pan,wheel_zoom,box_zoom,save,reset,help',  # 设置工具栏，默认全部显示
           toolbar_location='above',     # 工具栏位置："above"，"below"，"left"，"right"
           x_axis_label = '時間', y_axis_label = '潮位/cm',    # X,Y轴label
           #x_range = [-3,3], y_range = [-3,3],        # X,Y轴范围
           title="测试图表"                          # 设置图表title
          )
tt=range(49)

hhst=np.array(hhs).T
mm,nn=shape(hhst)
color=bp.Viridis256
print(color,shape(color))
random.shuffle(color)

for i in range(nn):
    if i==0:
        p.line(tt,hhst[:,i],line_width=2.0,color='red')
    else:
        p.line(tt, hhst[:, i], line_width=1.0,color=color[floor(i*len(color)/nn)])

show(p)
'''

#========== 利用matplotlib畫圖 ==========#
#@app.route('/')
def plot_surge(wdir0,site3,site3e,caseno,dhrs,st,dzs,wla,tide,cnum,msl,wls4s,perc,xxlabel):
    import matplotlib
    matplotlib.use('Agg')  # 不出现画图的框
    import matplotlib.pyplot as plt

    if dzs==None:
        disp('Can NOT find surge files!')
        return None,None,None
    else:
        tt1 = time.time()
        syear = str(st)[0:4]
        dzsx = np.array(dzs)
        wlax = np.array(wla)
        #
        #print(len(dzsx))
        dz, dx, dy = shape(dzsx)#路徑條數，時次，站位數
        colors = ['r', 'm', 'darkorange', 'b', 'lime', 'k']
        wlcolor = [(0.1922, 0.5333, 0.9490), (0.9529, 0.9176, 0.1882), (1, 0.5, 0), (0.7569, 0.0235, 0.0431)]
        wlevs = [50, 75, 100, 125, 150, 200, 250, 300, 350, 400]

        #
        datef=[]
        di=[]
        for i in range(dx):
            st2 = st + timedelta(days=i * dhrs / 24)
            HH=st2.strftime('%H%M')
            #print(HH,HH[0:2],HH[2:])
            if dx>60/dhrs:
                if HH=='0000':
                    datef.append(st2.strftime('%m/%d'))
                    di.append(i)
                elif HH[2:]=='00' and (HH[0:2]=='06' or HH[0:2]=='12' or HH[0:2]=='18'):
                    datef.append(st2.strftime('%H:00'))
                    di.append(i)
            else:
                if HH=='0000':
                    datef.append(st2.strftime('%m/%d'))
                    di.append(i)
                elif HH[2:]=='00' and (HH[0:2]=='03' or HH[0:2]=='06' or HH[0:2]=='09' or HH[0:2]=='12' or HH[0:2]=='15' or HH[0:2]=='18' or HH[0:2]=='21'):
                    datef.append(st2.strftime('%H:00'))
                    di.append(i)

        #print(datef)
        plt.rcParams['font.sans-serif'] = [u'SimHei']
        plt.rcParams['axes.unicode_minus'] = False

        if xxlabel==-1:
            xxs=range(len(site3))
        else:
            xxs=range(xxlabel,xxlabel+1)
        #print(xxs)
        #
        fig = plt.figure(figsize=(13.5, 6))
        for xx in xxs:
            wls4 = wls4s[xx]
            ax = plt.subplot(111)
            hhs = []
            wws = []
            for i in range(dz):
                dzsx2 = dzsx[i][:][:]
                wlax2 = wlax[i][:][:]

                hhs.append(dzsx2[:, xx])
                wws.append(wlax2[:, xx])
            hhst = np.array(hhs).T
            wwst = np.array(wws).T
            mm, nn = shape(hhst)
            #
            hhsx = cal_ensemble_surge(hhst, perc,cnum)
            wwsx = cal_ensemble_surge(wwst, perc,cnum)
            # ======================= surge =======================#
            tide2=tide[:,xx]-msl[xx]

            plt.plot(hhst,linewidth=1.0)
            plt.plot(hhst[:,0], linewidth=2.0, color='r',label='确定性预报')
            plt.plot(tide2,'-o', linewidth=2.0, color='k',markerfacecolor=[0,1,0],label='天文潮')
            plt.plot(hhsx, linewidth=2.0, color=[0, 1, 0], label='集合预报')
            psur = []
            for i in range(len(wlevs)):
                psur.append(cal_surge_pro(hhst, wlevs[i]))
            #print(psur[5],wlevs[5])


            maxlim=ceil(max([np.max(hhst),np.max(tide2)])/10)*10#np.max([np.max(wwst),wls4[-1]])
            minlim=floor(min([np.min(hhst),np.min(tide2)])/10)*10
            #
            for i in range(len(psur)):
                if wlevs[i] == 75 or wlevs[i] == 125:
                    if psur[i] != 0 and psur[i] != 100 and psur[5] == 0:
                        plt.plot([0, dx], [wlevs[i], wlevs[i]], linewidth=1.0, ls='-', color='m')
                        plt.text(round(dx * 0.02), wlevs[i]+abs(floor((maxlim-minlim)*0.01)),
                                 '>=' + str(wlevs[i]) + 'cm ' + str("{:.1f}".format(psur[i])) + '%', fontsize=10,
                                 color='k', fontweight='bold')
                else:
                    if psur[i] != 0 and psur[i] != 100:
                        plt.plot([0, dx], [wlevs[i], wlevs[i]], linewidth=1.0, ls='-', color='m')
                        plt.text(round(dx * 0.02), wlevs[i]+abs(floor((maxlim-minlim)*0.01)),
                                 '>=' + str(wlevs[i]) + 'cm ' + str("{:.1f}".format(psur[i])) + '%', fontsize=10,
                                 color='k', fontweight='bold')

            if maxlim-minlim>100:
                ytick = arange(minlim, maxlim, round((maxlim-minlim)/100)*10)
            elif maxlim-minlim>50:
                ytick = arange(minlim, maxlim, 10)
            else:
                ytick = arange(minlim, maxlim, 5)
            plt.xticks(di,datef)
            plt.yticks(ytick)

            plt.xlim((0, mm-1))
            #plt.ylim((18,36))
            plt.grid()
            plt.xlabel('时间', fontsize=10)
            plt.ylabel('水位/cm', fontsize=10)
            plt.legend(loc='upper right',frameon=False,ncol=3)
            plt.title(site3[xx], fontsize=12, fontweight='bold', color='k')
            plt.text(round(mm*0.02), maxlim-abs(floor((maxlim-minlim)*0.95)), '起算时间: '+str(st), fontsize=10, color='k',fontweight='bold')
            #
            picname = 'surge_' + caseno + '_'+site3e[xx]+'.png'
            print(' Drawing '+picname,'...')
            wdirp = wdir0 + 'pictures/' + caseno + '/'
            if not os.path.exists(wdirp):
                os.makedirs(wdirp)
            plt.savefig(wdirp + picname,dpi=150, bbox_inches='tight')
            plt.clf()
            #
            # ======================= WL =======================#
            tide3=tide[:, xx]
            plt.plot(wwst, linewidth=1.0)
            plt.plot(wwst[:, 0], linewidth=2.0, color='r', label='确定性预报')
            plt.plot(tide3, '-o', linewidth=2.0, color='k',markerfacecolor=[0,1,0],label='天文潮')
            plt.plot(wwsx, linewidth=2.0, color=[0, 1, 0], label='集合预报')
            #
            maxlim = ceil(max([np.max(wwst), np.max(tide3),wls4[-1]]) /10) * 10  # np.max([np.max(wwst),wls4[-1]])
            minlim = floor(min([np.min(wwst), np.min(tide3)]) / 10) * 10
            #
            for i in range(len(wls4)):
                pwl = cal_surge_pro(wwst, wls4[i])
                plt.plot([0, dx], [wls4[i], wls4[i]], linewidth=1.0, ls='-', color=wlcolor[i])
                if pwl != 0 and pwl != 100:
                    plt.text(round(dx * 0.02), wls4[i]+abs(floor((maxlim-minlim)*0.01)), '>=' + str(wls4[i]) + 'cm ' + str("{:.1f}".format(pwl)) + '%', fontsize=10, color='k', fontweight='bold')
                else:
                    plt.text(round(dx * 0.02), wls4[i] + abs(floor((maxlim - minlim) * 0.01)),
                              str(wls4[i]) + 'cm ' , fontsize=10, color='k', fontweight='bold')

            if maxlim - minlim > 100:
                ytick = arange(minlim, maxlim, round((maxlim - minlim) /100) *10)
            elif maxlim - minlim > 50:
                ytick = arange(minlim, maxlim,10)
            else:
                ytick = arange(minlim, maxlim, 5)
            plt.xticks(di, datef)
            plt.yticks(ytick)

            plt.xlim((0, mm - 1))
            # plt.ylim((18,36))
            plt.grid()
            plt.xlabel('时间', fontsize=10)
            plt.ylabel('水位/cm', fontsize=10)
            plt.legend(loc='upper right',frameon=False, ncol=3)
            plt.title(site3[xx], fontsize=12, fontweight='bold', color='k')
            plt.text(round(mm * 0.02), maxlim - abs(floor((maxlim - minlim) * 0.95)), '起算时间: ' + str(st),
                     fontsize=10, color='k', fontweight='bold')
            #
            picname2 = 'wl_' + caseno + '_' + site3e[xx] + '.png'
            print(' Drawing ' + picname2, '...')
            wdirp = wdir0 + 'pictures/' + caseno + '/'
            if not os.path.exists(wdirp):
                os.makedirs(wdirp)
            plt.savefig(wdirp + picname2, dpi=150, bbox_inches='tight')
            plt.clf()
            #plt.show()
        plt.close(fig)
        print('Time used: {} sec'.format(time.time() - tt1))
        return wdirp,picname,picname2

def cal_surge_pro(hhst,wlev):
    mhhs=np.max(hhst,axis=0)
    phhs=(mhhs>=wlev).sum()/len(mhhs)*100
    return phhs

def cal_ensemble_surge(hhst, perc, cnum):
    mm, nn = shape(hhst)
    qn = int((nn / 5 - 1) / 4)
    #
    hhsm=[]
    for i in range(int(nn/5)):
        dhh = hhst[:,i*5:(i+1)*5]
        hhsm.append(np.mean(dhh, axis=1))
    hhsm=np.array(hhsm)
    #print(hhsm,shape(hhsm))
    #
    for j in range(len(cnum)):
        if cnum[j]=='c0':
            hhsm[j, :] = hhsm[j, :] * perc[qn-1, 0]
        else:
            qnno=int(cnum[j][-1])
            hhsm[j, :] = hhsm[j, :] * perc[qn-1, qnno+1] / 4
    hhsx = np.sum(hhsm, axis=0)
    #print(hhsm,shape(hhsm),hhsx)
    return hhsx
if __name__ == '__main__':

    dzs,wla,tide,cnum = get_plotdata(wdir0,site3,site3e,st,hcma,dhrs,caseno)
    wdirp,picname,picname2=plot_surge(wdir0,site3,site3e,caseno,dhrs,st,dzs,wla,tide,cnum,msl,wls4s,perc,-1)
    #app.run(debug=True)


