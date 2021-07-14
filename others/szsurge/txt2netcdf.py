from netCDF4 import Dataset
import os
import numpy as np
from numpy import *
from datetime import *
import time

tyno='2022'
caseno='TY'+tyno+'_2021010416'
tcma='2018091517'




sth=datetime.strptime(tcma, '%Y%m%d%H')  # str==>datetime
stms = datetime.strftime(sth, '%Y%m%d%H%M')  # datetime==>str
stm=datetime.strptime(stms, '%Y%m%d%H%M')
syear=str(sth)[0:4]

wdir0='D:/szsurge/'
#
def txt2nc(wdir0, caseno, stm):
    wdir = wdir0 + 'result/' + caseno + '/'
    path1 = os.listdir(wdir)
    fl_name=None
    fl_name2=None
    tt1 = time.time()
    for i in range(len(path1)):
        if path1[i][0:5] == 'field' and path1[i][-10:] == 'c0_p00.dat':


            # Read ASCII File
            ''''''
            fl_name  = wdir + path1[i]
            #ascii_fl = loadtxt(fl_name, delimiter=' ',dtype=float)
            with open(fl_name, 'r+') as fi:
                dz1 = fi.readlines()
                dznum=[]
                for L in dz1:
                    dz3=L.strip('\n').split()
                    dznum.append(list(map(float,dz3)))
                ascii_fl=np.array(dznum)
            #print(ascii_fl)
    #
        if path1[i][0:8] == 'maxSurge' and path1[i][-10:] == 'c0_p00.dat':
            fl_name2 = wdir + path1[i]
            # ascii_fl = loadtxt(fl_name, delimiter=' ',dtype=float)
            with open(fl_name2, 'r+') as fi:
                dz1 = fi.readlines()
                dznum2 = []
                for L in dz1:
                    dz3 = L.strip('\n').split()
                    dznum2.append(list(map(float, dz3)))
                max_surge = np.array(dznum2)
    #
    yy = np.arange(15 + 1 / 120, 26 + 1 / 120, 1 / 60)
    xx = np.arange(105 + 1 / 120, 123 + 1 / 120, 1 / 60)
    if fl_name != None:
        print(type(ascii_fl),shape(ascii_fl))
        tt,mm = shape(ascii_fl)
        #print(stm.strftime('%Y-%m-%d-%H'))
        timestr=[]
        hours=[]
        timenum=[]
        dnum = stm.toordinal()
        HH=str(stm.strftime('%H'))
        for i in range(int(tt / 660)):
            st2 = stm + timedelta(hours=i + 1)
            timenum.append(dnum+(float(HH)+i+1)/24)
            #print(type(dnum),dnum,timenum)
            timestr.append(str(st2))
            hours.append(i+1)

        ascii_fl2 = reshape(ascii_fl, (len(timestr),len(yy),len(xx)))

        # Initialize nc file
        out_nc = fl_name[:-4]+'.nc'
        print('output ' +out_nc)
        nc_data  = Dataset(out_nc, 'w', format='NETCDF4')
        nc_data.description = 'Storm Surge Field'
        #print('Storm Surge Field, starting time： '+str(stm.strftime('%Y-%m-%d-%H')))

        # dimensions
        lat=nc_data.createDimension('lat', len(yy))
        lon=nc_data.createDimension('lon', len(xx))
        times=nc_data.createDimension('times',len(timestr))#round(tt/660)

        # Populate and output nc file
        # variables
        lat  = nc_data.createVariable('latitude', 'f4', ('lat',))
        lon = nc_data.createVariable('longitude', 'f4', ('lon',))
        times = nc_data.createVariable('times', 'f4', ('times',))
        surge = nc_data.createVariable('surge', 'f4', ('times','lat','lon',), fill_value=-9999.0)
        #print(shape(lon),shape(lat))
        #print(shape(xx), shape(yy))

        surge.units = 'm'
        lat.units = 'N'
        lon.units = 'E'
        times.units='days since 0001-1-0'

        # set the variables we know first
        lat[:]  = yy
        lon[:]  = xx
        times[:] = timenum
        surge[::]= ascii_fl2  ### THIS LINE IS NOT WORKING!!!!!!!
        nc_data.close()
        print('Time used: {} sec'.format(time.time() - tt1))
    else:
        print('Storm Surge Field files can NOT be found!')
        print('Time used: {} sec'.format(time.time() - tt1))

    if fl_name2 != None:
        print(shape(max_surge))
        out_nc2 = fl_name2[:-4] + '.nc'
        print('output ' + out_nc2)
        nc_data2 = Dataset(out_nc2, 'w', format='NETCDF4')
        nc_data2.description = 'Maximum Storm Surge'
        # print('Storm Surge Field, starting time： '+str(stm.strftime('%Y-%m-%d-%H')))

        # dimensions
        lat = nc_data2.createDimension('lat', len(yy))
        lon = nc_data2.createDimension('lon', len(xx))

        # Populate and output nc file
        # variables
        lat = nc_data2.createVariable('latitude', 'f4', ('lat',))
        lon = nc_data2.createVariable('longitude', 'f4', ('lon',))

        maxsurge = nc_data2.createVariable('max_surge', 'f4', ('lat', 'lon',), fill_value=999.0)
        #print(shape(lon), shape(lat))
        #print(shape(xx), shape(yy))

        maxsurge.units = 'm'
        lat.units = 'N'
        lon.units = 'E'

        # set the variables we know first
        lat[:] = yy
        lon[:] = xx
        maxsurge[::] = max_surge
        nc_data2.close()
        print('Time used: {} sec'.format(time.time() - tt1))
    else:
        print('The maximum Storm Surge files can NOT be found!')
        print('Time used: {} sec'.format(time.time() - tt1))
if __name__ == '__main__':
    txt2nc(wdir0,caseno, stm)