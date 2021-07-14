import numpy as np
from netCDF4 import Dataset
from numpy import *
from math import *
import os

from datetime import *
import time


wdir0='D:/szsurge/'
#wdir=wdir0+'result/TY1822_2019061010/'

wtime=datetime.now()
wtimes=wtime.strftime('%Y%m%d%H')
tyno='2022'

xx=2
lonsz=114.0979
latsz=22.6382

#caseno='TY'+tyno+'_'+wtimes
caseno='TY'+tyno+'_2021010416'

tcma='2020091517'

st=datetime.strptime(tcma, '%Y%m%d%H') # str==>datetime
stms = datetime.strftime(st, '%Y%m%d%H%M')  # datetime==>str
stm=datetime.strptime(stms, '%Y%m%d%H%M')
#syear=str(st)[0:4]
#
loncma=[119.2,117.6,116.1,114.6,113.1,111.4,109.7,108.1,106.7]
latcma=[18.9,19.8,20.5,21.2,21.9,22.5,23.0,23.4,23.7]
hcma=[0,6,12,18,24,30,36,42,48]
levs = [0.5, 1.0, 1.5, 2.0, 2.5, 3.0]
levs2 = ['_gt0_5m', '_gt1_0m', '_gt1_5m', '_gt2_0m', '_gt2_5m', '_gt3_0m']
west=110; east=118; south=19; north=24
#
def get_maxsurgedata(wdir0,caseno,st):
    syear=str(st)[0:4]
    wdir =wdir0+'result/'+caseno+'/'
    path1 = os.listdir(wdir)
    #nsta=len(site3)
    dflag=0
    dznum = []
    tt1 = time.time()
    for i in range(len(path1)):
        if path1[i][0:8] == 'maxSurge':
            print(path1[i])
            dflag=1

            with open(wdir + path1[i], 'r+') as fi:
                dz0 = fi.readlines()
                for L in dz0:
                    dz1=L.strip('\n').split()
                    dz2=list(map(float,dz1))
                    #dz3=np.flipud(dz2)
                    dznum.append(dz2)
    dznum=np.array(dznum)
    print('Time used: {} sec'.format(time.time() - tt1))
    if dflag==1:
        print(type(dznum),shape(dznum))
        return dznum
    else:
        dznum=[]
        return dznum

def draw_maxsurge(wdir0,caseno,lonsz,latsz,tlon,tlat,st,dznum,west, east, south, north,cmin,cmax):
    from mpl_toolkits.basemap import Basemap
    import matplotlib
    matplotlib.use('Agg')  # 不出现画图的框
    import matplotlib.pyplot as plt
    #
    if dznum==[]:
        disp('Can NOT find maxsurge files!')
        return None, None
    else:
        tt, mm = shape(dznum)
        sur=dznum[0:660,:]
        sur=np.array(sur)
        sur[sur>900]=nan
        sur = flipud(sur)*100
        lon0 = arange(105 + 1 / 120, 123 + 1 / 120, 1 / 60)
        lat0 = arange(15 + 1 / 120, 26 + 1 / 120, 1 / 60)
        lon, lat = meshgrid(lon0, lat0)
        #
        syear = str(st)[0:4]
        print(np.nanmax(sur), np.nanmin(sur))
        if cmax=='默认':
            maxsur = round(np.nanmax(sur)/10* 0.68) *10
            minsur = 0
        else:
            minsur=float(cmin)
            maxsur=float(cmax)

        print(minsur, maxsur)
        #
        if maxsur - minsur >= 400:
            levels = arange(minsur, maxsur, 5)
        elif maxsur - minsur >= 300:
            levels = arange(minsur, maxsur, 4)
        elif maxsur - minsur >= 200:
            levels = arange(minsur, maxsur, 3)
        elif maxsur - minsur >= 100:
            levels = arange(minsur, maxsur, 2)
        else:
            levels = arange(minsur, maxsur, 1)
        #print(levels)
        #
        picname = 'maxSurge_' + caseno + '.png'
        print('Drawing '+picname)
        fig = plt.figure(figsize=(11.8, 8))
        plt.rcParams['font.sans-serif'] = [u'SimHei']
        plt.rcParams['axes.unicode_minus'] = False

        tt1 = time.time()
        plt.plot(lonsz, latsz, color='r', marker='o', markersize=2)
        #
        plt.text(lonsz-0.12, latsz + 0.08, '深圳', fontsize=8, color='r')
        #
        cmap = matplotlib.cm.jet
        norm = matplotlib.colors.Normalize(vmin=minsur, vmax=maxsur)
        cf = plt.contourf(lon, lat, sur, levels=levels, cmap=cmap, norm=norm)#, extend='both'
        #
        cbar = plt.colorbar(cf,  orientation='vertical', fraction=0.03, pad=0.02)  # ticks=levels,
        font = {'family': 'serif',
                'color': 'k',
                'weight': 'normal',
                'size': 10,
                }
        cbar.set_label('cm', fontdict=font)

        plt.plot(tlon, tlat, c='m', ls='--', marker='o', markersize=3, linewidth=1.0)
        plt.title('最大风暴增水分布图（TY'+ tyno+'）', fontsize=12, fontweight='bold', color='k')
        plt.axis('equal')
        xtick = range(104, 124, 1)
        ytick = range(14, 26, 1)
        plt.xticks(xtick)
        plt.yticks(ytick)
        plt.grid(linestyle='--', linewidth=0.5, color='k')
        plt.xlim(west, east)
        plt.ylim(south, north)
        plt.xlabel('Longitude (E)', fontsize=10)
        plt.ylabel('Latitude (N)', fontsize=10)
        # plt.show()
        wdirp = wdir0 + 'pictures/' + caseno + '/'

        if not os.path.exists(wdirp):
            os.makedirs(wdirp)
        plt.savefig(wdirp + picname, dpi=150, bbox_inches='tight')
        plt.clf()
        print('Time used: {} sec'.format(time.time() - tt1))
        plt.close(fig)
        return picname, maxsur

def draw_prosurge(wdir0,caseno,lonsz,latsz,tlon,tlat,st,dznum,levs,levs2,west, east, south, north):
    from mpl_toolkits.basemap import Basemap
    import matplotlib
    matplotlib.use('Agg')  # 不出现画图的框
    import matplotlib.pyplot as plt
    #
    if dznum == []:
        disp('Can NOT find maxsurge files!')
        return
    else:
        tt, mm = shape(dznum)
        sur = dznum[0:660, :]
        sur = np.array(sur)
        sur = flipud(sur)
        dznum[dznum>900]=0
        lon0 = arange(105 + 1 / 120, 123 + 1 / 120, 1 / 60)
        lat0 = arange(15 + 1 / 120, 26 + 1 / 120, 1 / 60)
        lon, lat = meshgrid(lon0, lat0)
        #
        syear = str(st)[0:4]
        #
        fig = plt.figure(figsize=(11.8, 8))
        plt.rcParams['font.sans-serif'] = [u'SimHei']
        plt.rcParams['axes.unicode_minus'] = False

        picnames=[]

        for i in range(len(levs)):
            pps = cal_pro(dznum, levs[i])
            pps = flipud(pps)
            pps[sur>900]=nan
            picname = 'proSurge_' + caseno+ levs2[i] + '.png'
            picnames.append(picname)
            #
            tt1 = time.time()
            print('Drawing ' + picname)
            plt.plot(lonsz, latsz, color='r', marker='o', markersize=2)
            #
            plt.text(lonsz - 0.12, latsz + 0.08, '深圳', fontsize=8, color='r')
            #
            minsur = 0
            maxsur = 100 + 1
            levels = arange(minsur, maxsur, 1)
            cmap = matplotlib.cm.cool
            norm = matplotlib.colors.Normalize(vmin=minsur, vmax=maxsur)

            if np.nanmax(pps)>0:
                cf = plt.contourf(lon, lat, pps,  cmap=cmap, norm=norm, levels=levels)#, extend='both'
            else:
                sur2=sur.copy()
                sur2[sur2>900]=nan
                cf = plt.contourf(lon, lat, sur2, cmap=cmap, norm=norm, levels=levels)
                plt.text(112.5, 20.5, '此种情况下风暴增水概率为零！', fontsize=18, color='r', fontweight='bold')
            #
            cbar = plt.colorbar(cf,  orientation='vertical', fraction=0.03, pad=0.02, ticks=arange(minsur, maxsur, 10))  # ticks=levels,
            font = {'family': 'serif',
                    'color': 'k',
                    'weight': 'normal',
                    'size': 10,
                    }
            cbar.set_label('%', fontdict=font)
            plt.plot(tlon, tlat, c='m', ls='--', marker='o', markersize=3, linewidth=1.0)
            plt.title('风暴增水大于' +str(levs[i])+'米概率分布（TY'+tyno+'）', fontsize=12, fontweight='bold', color='k')
            plt.axis('equal')
            xtick = range(104, 124, 1)
            ytick = range(14, 26, 1)
            plt.xticks(xtick)
            plt.yticks(ytick)
            plt.grid(linestyle='--', linewidth=0.5, color='k')
            plt.xlim(west, east)
            plt.ylim(south, north)
            plt.xlabel('Longitude (E)', fontsize=10)
            plt.ylabel('Latitude (N)', fontsize=10)
            # plt.show()
            wdirp = wdir0 + 'pictures/' + caseno + '/'

            if not os.path.exists(wdirp):
                os.makedirs(wdirp)
            plt.savefig(wdirp + picname, dpi=150, bbox_inches='tight')
            plt.clf()
            print('Time used: {} sec'.format(time.time() - tt1))
        plt.close(fig)
    return picnames

def cal_pro(dznum,levs):
    pp = dznum.copy()
    pp[pp >= levs] = 1
    pp[pp < levs] = 0
    tt, mm = shape(dznum)
    pps = np.zeros((660,mm))
    for i in range(int(tt/660)):
        pps = pps+pp[i*660:(i+1)*660,:]
    pps=pps/int(tt/660)*100
    return pps

        #return picname
if __name__ == '__main__':
    dznum=get_maxsurgedata(wdir0,caseno,st)
    draw_maxsurge(wdir0,caseno,lonsz,latsz,loncma,latcma,st,dznum, west, east, south, north,'0','默认')
    draw_prosurge(wdir0,caseno,lonsz,latsz,loncma,latcma,st,dznum,levs,levs2, west, east, south, north)