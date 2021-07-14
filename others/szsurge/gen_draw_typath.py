"""该程序用于读取cma路径数据，生成145条（可改）路径文件
    绘制台风路径图
"""
import numpy as np
from numpy import *
from math import *
from scipy import interpolate
import time
import pandas as pd
import os
from datetime import *
from geographiclib.geodesic import Geodesic

from matplotlib.patches import Circle
from mpl_toolkits.basemap import Basemap
#from pyecharts import Map, Geo, GeoLines, Style
#
wtime=datetime.now()
wtimes=wtime.strftime('%Y%m%d%H')
wdir0='D:/szsurge/'

#
tyno='2022'
stime='2018091517'

tlon=[119.2,117.6,116.1,114.6,113.1,111.4,109.7,108.1,106.7]
tlat=[18.9,19.8,20.5,21.2,21.9,22.5,23.0,23.4,23.7]
pres=[945, 940, 935, 935, 940, 959, 985,1003,1000]
hrs=[0,6,12,18,24,30,36,42,48]
dR=0
pnum = 145
lonsz=114.0979
latsz=22.6382
#
west = 104 #104
east = 126 #126
south = 14 #14
north = 28 #28
r01 = 60
r02 = 100
r03 = 120
r04 = 150
r05 = 180
st=datetime.strptime(stime,'%Y%m%d%H')
syear=str(st)[0:4]
#caseno='TY'+tyno+'_'+wtimes
caseno='TY'+tyno+'_2020042710'

#interploate the typhoon data

def interp6h(horg,lonorg,latorg,porg):
    h1org=arange(0, horg[-1]+6, 6)
    if len(horg)>=4:
        fx = interpolate.interp1d(horg, lonorg, kind="cubic")  # "quadratic","cubic"
        fy = interpolate.interp1d(horg, latorg, kind="cubic")
        fp = interpolate.interp1d(horg, porg, kind="cubic")
    else:
        fx = interpolate.interp1d(horg, lonorg)  # "quadratic","cubic"
        fy = interpolate.interp1d(horg, latorg)
        fp = interpolate.interp1d(horg, porg)
    lon1org = fx(h1org)
    lat1org = fy(h1org)
    p1org = np.round(fp(h1org))
    return (h1org, lon1org, lat1org, p1org)
#
def cal_time_radius_pres(p1org, storg, dR):
    dorg=[]
    dorg2=[]
    rorg=[]
    korg=len(p1org)
    for i in range(korg):
        if p1org[i] > 1000:
            p1org[i] = 1000
        #
        rorg0=round((1119 * (1010 - p1org[i]) ** -0.805))
        if rorg0 > 80:
            rorg0 = 80
        elif rorg0 <= 20:
            rorg0 = 20
        rorg.append(round(rorg0+dR))
        st2 = storg + timedelta(days=i * 6 / 24)
        dorg.append(st2.strftime('%m%d%H'))
        dorg2.append(st2.strftime('%m/%d/%H'))
        #
        if rorg[i] > 80:
            rorg[i] = 80
        elif rorg[i] <= 20:
            rorg[i] = 20
    return (dorg,dorg2,p1org,rorg,korg)
#

#print(rads)

# Make typhoon path files
#
def output_pathfiles(wdir,filename,caseno,ri,dir,datex,tlonx,tlatx,presx,radsx,label):
    kxi=len(tlonx)
    fn=caseno + '_'+ dir + str(ri) + '_p'+ label
    tyno=caseno[2:6]
    filename.append(fn)
    fi = open(wdir + fn, 'w+')
    fi.write(tyno + '\n')
    fi.write('0\n')
    fi.write(str(kxi) + '\n')
    for i in range(kxi):
        fi.write(datex[i] + ' ' + "{:.1f}".format(tlonx[i]) + ' ' + "{:.1f}".format(tlatx[i]) + ' ' + "{:.0f}".format(presx[i]) + ' ' + "{:.0f}".format(radsx[i]) + '\n')
    fi.close()
    return filename
#
hrs1, tlon1, tlat1, pres1 = interp6h(hrs, tlon, tlat, pres)
#west=102,east=140,south=8,north=32 r01=60; r02=100; r03=120; r04=150; r05=180
def gen_draw_typath(wdir0,st,dR,caseno,tyno,r01,r02,r03,r04,r05,pnum,west,east,south,north,tlon1,tlat1, pres1,lonsz,latsz):
    import matplotlib
    matplotlib.use('Agg')  # 不出现画图的框
    import matplotlib.pyplot as plt

    pres05 = pres1 + 5
    pres10 = pres1 + 10
    pres_05 = pres1 - 5
    pres_10 = pres1 - 10
    datef, datef2, pres1, rads, kxi = cal_time_radius_pres(pres1, st, dR)
    datef, datef2, pres05, rads05, kxi = cal_time_radius_pres(pres05, st, dR)
    datef, datef2, pres10, rads10, kxi = cal_time_radius_pres(pres10, st, dR)
    datef, datef2, pres_05, rads_05, kxi = cal_time_radius_pres(pres_05, st, dR)
    datef, datef2, pres_10, rads_10, kxi = cal_time_radius_pres(pres_10, st, dR)

    nrr = round((pnum/5-5)/4+1)
    minsp = 12; coef = 0.7

    rrs = np.array([0, r01, r02, r03, r04, r05])
    x =arange(0,120+24,24)
    x2 =arange(0,120+6,6)
    rrmat = np.zeros((nrr, len(x)-1))
    rrmat6 = np.zeros((nrr,len(x2)-1))
    fr = interpolate.interp1d(x,rrs,kind="slinear")
    rrs6 = np.round(fr(x2))
    rrmat[0, :] = rrs[1:]
    rrmat6[0, :] = rrs6[1:]
    #rrmat6=np.round(rrmat6)

    filename=[]
    kk=0
    #
    wdir = wdir0 + 'pathfiles/' + caseno + '/'
    if not os.path.exists(wdir):
        os.mkdir(wdir)
    wdirx = wdir0 + 'result/' + caseno + '/'
    if not os.path.exists(wdirx):
        os.makedirs(wdirx)

    fig=plt.figure(figsize=(11.8,8))
    plt.rcParams['font.sans-serif'] = [u'SimHei']
    plt.rcParams['axes.unicode_minus'] = False
    mp = Basemap(
    llcrnrlon=104,#west, #longitude of lower left hand corner of the desired map domain (degrees).
    llcrnrlat=14,#south,  #latitude of lower left hand corner of the desired map domain (degrees).
    urcrnrlon=126,#east, #longitude of upper right hand corner of the desired map domain (degrees).
    urcrnrlat=28,#north,  #latitude of upper right hand corner of the desired map domain (degrees).
    projection='merc',
    resolution='i',
    lon_0=lonsz,
    lat_0=latsz)
    mp.drawcountries(linewidth=0.5)
    mp.drawmapboundary(fill_color = 'w',linewidth=0.5)
    mp.drawcoastlines(linewidth=0.5)
    mp.fillcontinents(color = 'whitesmoke',lake_color='w')

    for r in range(nrr-1):
        r=r+1
        rrmat[r, :] = np.round(rrmat[0, :] * r / nrr)
        rrmat6[r, :] = np.round(rrmat6[0, :] * r / nrr)
    #print(rrmat6)
    for r in range(nrr):
        #print(r)
        spd0=[]
        dista = []
        angle = []
        tlonl=tlon1.copy();tlatl=tlat1.copy()
        tlonr=tlon1.copy();tlatr=tlat1.copy()
        tlonf=tlon1.copy();tlatf=tlat1.copy()
        tlons=tlon1.copy();tlats=tlat1.copy()

        for j in range(kxi-1):
            #dista.append(geodistance(tlon1[j],tlat1[j],tlon1[j+1],tlat1[j+1]))
            geodict = Geodesic.WGS84.Inverse( tlat1[j], tlon1[j], tlat1[j + 1], tlon1[j + 1] )
            dista.append(geodict['s12']/1000)
            angle.append(geodict['azi1']+360)
            spd0.append(round(dista[j]/6))
            if spd0[j] < minsp:
                rrmat6[r,j] = round(rrmat6[r,j] * coef)
                if j == kxi - 1:
                    rrmat6[r,j+ 1] = round(rrmat6[r,j + 1] * coef)
            # left patb
            geoxyl=Geodesic.WGS84.Direct(tlat1[j+1], tlon1[j+1], angle[j]-360+270, rrmat6[r, j]*1000)
            tlonl[j + 1] = geoxyl['lon2']
            tlatl[j + 1] = geoxyl['lat2']
            # right path
            geoxyr = Geodesic.WGS84.Direct(tlat1[j + 1], tlon1[j + 1], angle[j] - 360 + 90, rrmat6[r, j] * 1000)
            tlonr[j + 1] = geoxyr['lon2']
            tlatr[j + 1] = geoxyr['lat2']
            # fast path
            geoxyf = Geodesic.WGS84.Direct(tlat1[j + 1], tlon1[j + 1], angle[j] - 360, rrmat6[r, j] * 1000)
            tlonf[j + 1] = geoxyf['lon2']
            tlatf[j + 1] = geoxyf['lat2']
            # slow path
            geoxys = Geodesic.WGS84.Direct(tlat1[j + 1], tlon1[j + 1], angle[j] - 360 -180, rrmat6[r, j] * 1000)
            tlons[j + 1] = geoxys['lon2']
            tlats[j + 1] = geoxys['lat2']
            #print([tlonl[j],tlatl[j]])

           # -----------------------------draw circles------------------------------------#
            theta = arange(0, 360+6, 6)
            #xt=np.cos(theta) * rrmat6[r, j] *360/ (6371 *2* pi) + tlon1[j + 1]
            #yt=np.sin(theta) * rrmat6[r, j] *360/ (6371 *2* pi) + tlat1[j + 1]
            xt=[]
            yt=[]
            for i in range(len(theta)):
                geoxya = Geodesic.WGS84.Direct(tlat1[j + 1], tlon1[j + 1], theta[i], rrmat6[r, j] * 1000)
                xt.append(geoxya['lon2'])
                yt.append(geoxya['lat2'])
                xxt,yyt=mp(xt,yt)
            if j==3:
                mp.plot(xxt, yyt, c='lime',ls='--',linewidth=1.0)
            elif j==7:
                mp.plot(xxt, yyt, c='b',ls='--',linewidth=1.0)
            elif j==11:
                mp.plot(xxt, yyt, c='darkorange',ls='--',linewidth=1.0)
            elif j==15:
                mp.plot(xxt, yyt, c='m',ls='--',linewidth=1.0)
            elif j==19:
                mp.plot(xxt, yyt, 'r--',linewidth=1.0)
        # -----------------------------draw paths------------------------------------#

        #plt.plot(tlonl, tlatl, c='m',ls='--')
        #plt.plot(tlonr, tlatr, c='b',ls='--')
        #plt.plot(tlonf, tlatf, c='darkorange',ls='--')
        #plt.plot(tlons, tlats, c='lime',ls='--')
        xx1,yy1=mp(tlon1,tlat1)
        xxl, yyl = mp(tlonl, tlatl)
        xxr, yyr= mp(tlonr, tlatr)
        xxf, yyf = mp(tlonf, tlatf)
        xxs, yys = mp(tlons, tlats)
        if r==0:
            mp.plot(xxl, yyl, c='m', ls='--',label='left path', marker='o',markersize=1,linewidth=1.0)
            mp.plot(xxr, yyr, c='b', ls='--',label='right path', marker='o',markersize=1,linewidth=1.0)
            mp.plot(xxf, yyf, c='darkorange', ls='--',label='fast path', marker='o',markersize=1,linewidth=1.0)
            mp.plot(xxs, yys, c='lime', ls='--',label='slow path', marker='o',markersize=1,linewidth=1.0)

            for i in range(0, len(tlon1), 4):
                plt.text(xxr[i], yyr[i], datef2[i])

        else:
            mp.plot(xxl, yyl, c='m', ls='--', marker='o',markersize=1,linewidth=1.0)
            mp.plot(xxr, yyr, c='b', ls='--', marker='o',markersize=1,linewidth=1.0)
            mp.plot(xxf, yyf, c='darkorange', ls='--', marker='o',markersize=1,linewidth=1.0)
            mp.plot(xxs, yys, c='lime', ls='--', marker='o',markersize=1,linewidth=1.0)

        if r==0:
            # -----------------------------center path------------------------------------#
            filename=output_pathfiles(wdir, filename, caseno, r, 'c', datef, tlon1, tlat1, pres1, rads, '00')
            filename=output_pathfiles(wdir, filename, caseno, r, 'c', datef, tlon1, tlat1, pres05, rads05, '05')
            filename=output_pathfiles(wdir, filename, caseno, r, 'c', datef, tlon1, tlat1, pres10, rads10, '10')
            filename=output_pathfiles(wdir, filename, caseno, r, 'c', datef, tlon1, tlat1, pres_05, rads_05, '_05')
            filename=output_pathfiles(wdir, filename, caseno, r, 'c', datef, tlon1, tlat1, pres_10, rads_10, '_10')

        #-----------------------------right path------------------------------------#
        filename=output_pathfiles(wdir, filename, caseno, r, 'r', datef, tlonr, tlatr, pres1, rads, '00')
        filename=output_pathfiles(wdir, filename, caseno, r, 'r', datef, tlonr, tlatr, pres05, rads05, '05')
        filename=output_pathfiles(wdir, filename, caseno, r, 'r', datef, tlonr, tlatr, pres10, rads10, '10')
        filename=output_pathfiles(wdir, filename, caseno, r, 'r', datef, tlonr, tlatr, pres_05, rads_05, '_05')
        filename=output_pathfiles(wdir, filename, caseno, r, 'r', datef, tlonr, tlatr, pres_10, rads_10, '_10')

        # -----------------------------left path------------------------------------#
        filename=output_pathfiles(wdir, filename,caseno, r, 'l', datef, tlonl, tlatl, pres1, rads, '00')
        filename=output_pathfiles(wdir, filename, caseno, r, 'l', datef, tlonl, tlatl, pres05, rads05, '05')
        filename=output_pathfiles(wdir, filename, caseno, r, 'l', datef, tlonl, tlatl, pres10, rads10, '10')
        filename=output_pathfiles(wdir, filename, caseno, r, 'l', datef, tlonl, tlatl, pres_05, rads_05, '_05')
        filename=output_pathfiles(wdir, filename, caseno, r, 'l', datef, tlonl, tlatl, pres_10, rads_10, '_10')

        # -----------------------------fast path------------------------------------#
        filename=output_pathfiles(wdir, filename, caseno, r, 'f', datef, tlonf, tlatf, pres1, rads, '00')
        filename=output_pathfiles(wdir, filename, caseno, r, 'f', datef, tlonf, tlatf, pres05, rads05, '05')
        filename=output_pathfiles(wdir, filename, caseno, r, 'f', datef, tlonf, tlatf, pres10, rads10, '10')
        filename=output_pathfiles(wdir, filename, caseno, r, 'f', datef, tlonf, tlatf, pres_05, rads_05, '_05')
        filename=output_pathfiles(wdir, filename, caseno, r, 'f', datef, tlonf, tlatf, pres_10, rads_10, '_10')

        # -----------------------------slow path------------------------------------#
        filename=output_pathfiles(wdir, filename, caseno, r, 's', datef, tlons, tlats, pres1, rads, '00')
        filename=output_pathfiles(wdir, filename, caseno, r, 's', datef, tlons, tlats, pres05, rads05, '05')
        filename=output_pathfiles(wdir, filename, caseno, r, 's', datef, tlons, tlats, pres10, rads10, '10')
        filename=output_pathfiles(wdir, filename, caseno, r, 's', datef, tlons, tlats, pres_05, rads_05, '_05')
        filename=output_pathfiles(wdir, filename, caseno, r, 's', datef, tlons, tlats, pres_10, rads_10, '_10')

    #-----------------------------draw Map------------------------------------#

    xtmo=[]
    ytmo=[]

    mp.plot(xx1, yy1, c='r', ls='-', label='CMA path', marker='o', markersize=2, linewidth=1.0)

    for i in range(len(theta)):
        geoxya = Geodesic.WGS84.Direct(latsz, lonsz, theta[i], 400 * 1000)
        xtmo.append(geoxya['lon2'])
        ytmo.append(geoxya['lat2'])
    xxtmo, yytmo = mp(xtmo, ytmo)
    mp.plot(xxtmo,yytmo, color='r', ls='--')

    tx,ty=mp(112,26.1)#112,26.1
    plt.text(tx,ty,'Radius=400km',fontsize=8,color='r')
    xmo, ymo = mp(lonsz, latsz)
    mp.plot(xmo, ymo, color='r', marker='o', markersize=2)
    #
    tx2, ty2 = mp(lonsz - 0.12, latsz + 0.08)
    plt.text(tx2, ty2, '深圳', fontsize=8, color='r')

    #

    #m.readshapefile('CHN_adm_shp/CHN_adm1', 'states', drawbounds=True)
    #m.readshapefile('TWN_adm_shp/TWN_adm0', 'taiwan', drawbounds=True)
    #
    plt.axis('equal')
    xtick = range(100,136,2)
    ytick = range(10,40,2)
    #plt.xticks(xtick)
    #plt.yticks(ytick)
    #plt.grid()

    #plt.xlabel('Longitude (E)', fontsize=10)
    #plt.ylabel('Latitude (N)', fontsize=10)
    plt.title('Typhoon '+tyno, fontsize=14, fontweight='bold', color='k')
    #plt.xlim((106,130))
    #plt.ylim((18,36))
    mp.drawparallels(np.arange(10,50,4),labels=[1,1,0,1], fontsize=8)# 画出纬线， 在北纬10度到90度区间内以20度为单位， 纬度标记在图形左右和下测
    mp.drawmeridians(np.arange(100,140,4),labels=[1,1,0,1], fontsize=8)# 画出经线， 从西经180度到东经180度区间内以30度为单位， 经度标记在图形左右和下测
    plt.legend(loc='best')
    #
    picname = 'typhoon_path_' + caseno + '.png'
    wdirp = wdir0 + 'pictures/' + caseno + '/'
    if not os.path.exists(wdirp):
        os.makedirs(wdirp)
    plt.savefig(wdirp + picname, dpi=150,bbox_inches='tight')
    plt.close(fig)
    #plt.show()
    #print('Path files for Function B are done!')
    return wdirp,picname,filename
#-----------------------------output control file------------------------------------#
# output gpus_path_list.bat
def output_controlfile(wdir0,filename):
    fi = open(wdir0 + 'sz_gpus_path_list.bat', 'w+')
    fi.write('@echo off'+ '\n')
    fi.write('set date1=%date%'+ '\n')
    fi.write('set startmonth=%date:~5,2%'+ '\n')
    fi.write('set startday=%date:~8,2%'+ '\n')
    fi.write('set starthour=%time:~0,2%'+ '\n')
    fi.write('set startmin=%time:~3,2%'+ '\n')
    fi.write('set startsec=%time:~6,2%'+ '\n')
    fi.write('echo StartDate %date1%'+ '\n')
    fi.write('echo StartTime %time1%'+ '\n')
    for i in range(len(filename)):
        fi.write('echo '+filename[i] +'|CTSgpu_sz.exe'+ '\n')
    fi.write('set time2=%time%'+ '\n')
    fi.write('set date2=%date%'+ '\n')

    fi.write('set endmonth=%date:~5,2%'+ '\n')
    fi.write('set endday=%date:~8,2%'+ '\n')
    fi.write('set endhour=%time:~0,2%'+ '\n')
    fi.write('set endmin=%time:~3,2%'+ '\n')
    fi.write('set endsec=%time:~6,2%'+ '\n')
    fi.write('echo EndDate %date2%'+ '\n')
    fi.write('echo EndTime %time2%'+ '\n')

    fi.write('set intday=0'+ '\n')
    fi.write('set inthour=0'+ '\n')
    fi.write('set intmin=0'+ '\n')
    fi.write('set inttime=0'+ '\n')

    fi.write('if %endday% EQU %startday% (call:calc1 & goto :finalresult)'+ '\n')

    fi.write(':finalresult'+ '\n')
    fi.write('echo Elapsed time: %inttime%'+ '\n')
    fi.write('exit /b'+ '\n')

    fi.write(':calc1'+ '\n')
    fi.write('if /i %endsec% LSS %startsec% (set /a intsec=%endsec%+60-%startsec% & set /a endmin-=1) else (set /a intsec=%endsec%-%startsec%)'+ '\n')
    fi.write('if /i %endmin% LSS %startmin% (set /a intmin=%endmin%+60-%startmin% & set /a endhour-=1) else (set /a intmin=%endmin%-%startmin%)'+ '\n')
    fi.write('set /a inthour=%endhour%-%starthour%'+ '\n')
    fi.write('set /a intday=%endday%-%startday%'+ '\n')
    fi.write('set inttime=%intday% day %inthour% hours %intmin% min %intsec% sec'+ '\n')
    fi.close()
    #
    fi = open(wdir0 + 'sz_start_gpu_model.bat', 'w+')
    fi.write('@echo off' + '\n')
    fi.write('set PGI=C:\\PROGRA~1\\PGI' + '\n')
    fi.write('set PATH=C:\\Program Files\\Java\\jre1.8.0_112\\bin;%PATH%' + '\n')
    fi.write('set PATH=C:\\Program Files\\PGI\\flexlm;%PATH%' + '\n')
    fi.write('set PATH=%PGI%\\win64\\2019\\cuda\\9.2\\bin;%PATH%' + '\n')
    fi.write('set PATH=%PGI%\\win64\\2019\\cuda\\10.0\\bin;%PATH%' + '\n')
    fi.write('set PATH=%PGI%\\win64\\2019\\cuda\\10.1\\bin;%PATH%' + '\n')
    fi.write('set PATH=C:\\Program Files (x86)\\Windows Kits\\10\\bin\\x64;%PATH%' + '\n')
    fi.write(
        'set PATH=C:\\Program Files (x86)\\Microsoft Visual Studio\\2019\\Community\\VC\\Tools\\MSVC\\14.21.27702\\bin\\Hostx64\\x64;%PATH%' + '\n')
    fi.write('set PATH=%PGI%\\win64\\19.9\\bin;%PATH%' + '\n')
    fi.write('set PATH=%PATH%;.' + '\n')
    fi.write('set FLEXLM_BATCH=1' + '\n')
    fi.write('title PGI 19.9' + '\n')
    fi.write('set TMP=C:\\temp' + '\n')
    fi.write('set PS1=PGI$' + '\n')
    fi.write('echo PGI 19.9' + '\n')

    fi.write('cmd /k "cd /d D:\\szsurge\\ && call sz_gpus_path_list.bat && exit"' + '\n')
    fi.close()

    #print('Control files for Function B are done!')

if __name__ == '__main__':

    wdirp,picname,filename=gen_draw_typath(wdir0,st,dR,caseno,tyno,r01,r02,r03,r04,r05,pnum,west,east,south,north,tlon1,tlat1, pres1,lonsz,latsz)
    output_controlfile(wdir0, filename)














