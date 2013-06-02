import numpy as np
import datetime

from matplotlib.collections import PolyCollection
from matplotlib import dates as md
import matplotlib

from mpl_toolkits.basemap import Basemap

import utils

class musicFan(object):
  def __init__(self,dataObject,dataSet='active',time=None,axis=None,fileName=None,scale=None, **kwArgs):
    if fileName != None:
      from matplotlib.backends.backend_agg import FigureCanvasAgg
      from matplotlib.figure import Figure
      if axis==None:
        fig   = Figure()
    else:
      from matplotlib import pyplot as plt
      plt.ion()
      if axis==None:
        fig   = plt.figure()

    #Make some variables easier to get to...
    currentData = getattr(dataObject,dataSet)
    metadata    = currentData.metadata
    latFull     = currentData.fov.latFull
    lonFull     = currentData.fov.lonFull

    coords      = metadata['coords']

    #Translate parameter information from short to long form.
    if    metadata['param'] == 'p_l'  : param = 'power'
    elif  metadata['param'] == 'p_s'  : param = 'power'
    elif  metadata['param'] == 'v'    : param = 'velocity'
    elif  metadata['param'] == 'w_l'  : param = 'width'
    elif  metadata['param'] == 'w_s'  : param = 'width'
    elif  metadata['param'] == 'elv'  : param = 'elevation'
    elif  metadata['param'] == 'phi0' : param = 'phi0'
    else: param = metadata['param']

    #Set colorbar scale if not explicitly defined.
    if(scale == None):
      if(param == 'velocity'): scale=[-200,200]
      elif(param == 'power'): scale=[0,30]
      elif(param == 'width'): scale=[0,150]
      elif(param == 'elevation'): scale=[0,50]
      elif(param == 'phi0'): scale=[-np.pi,np.pi]
      else: scale = [-200,200]

    #See if an axis is provided... if not, set one up!
    if axis==None:
      axis  = fig.add_subplot(111)
    else:
      fig   = axis.get_figure()

    #Figure out which scan we are going to plot...
    if time == None:
      timeInx = 0
    else:
      timeInx = (np.where(currentData.time >= time))[0]
      if np.size(timeInx) == 0:
        timeInx = -1
      else:
        timeInx = int(np.min(timeInx))

    #do some stuff in map projection coords to get necessary width and height of map
    lonFull,latFull = (np.array(lonFull)+360.)%360.,np.array(latFull)
    tmpmap = Basemap(projection='npstere', boundinglat=20,lat_0=90, lon_0=np.mean(lonFull))
    x,y = tmpmap(lonFull,latFull)
    minx = x.min()
    miny = y.min()
    maxx = x.max()
    maxy = y.max()
    width = (maxx-minx)
    height = (maxy-miny)
    cx = minx + width/2.
    cy = miny + height/2.
    lon_0,lat_0 = tmpmap(cx, cy, inverse=True)
    dist = width/50.

    #draw the actual map we want
    m = Basemap(projection='stere',width=width,height=height,lon_0=np.mean(lonFull),lat_0=lat_0)
    m.drawparallels(np.arange(-80.,81.,10.),labels=[1,0,0,0])
    m.drawmeridians(np.arange(-180.,181.,20.),labels=[0,0,0,1])
    if(coords == 'geo'):
      m.drawcoastlines(linewidth=0.5,color='k')
      m.drawmapboundary(fill_color='w')
      m.fillcontinents(color='w', lake_color='w')
    #overlay fields of view, if desired
#    if(fov == 1):
#      for r in rad:
#        pydarn.plotting.overlayRadar(m, codes=r, dateTime=sTime)
#        pydarn.plotting.overlayFov(m, codes=r, dateTime=sTime)

    #Setup the map!!
#    m = Basemap(projection='merc',
#                  lon_0=0,lat_0=0,lat_ts=0,
#                  llcrnrlat=5,urcrnrlat=68,
#                  llcrnrlon=-180,urcrnrlon=-50,
#                  resolution='l',ax=axis,**kwArgs)
#    m.drawcountries(linewidth=1, color='k')
#    m.bluemarble(scale=1)
#    m.drawmapscale(-60, 12, -90, 5, 1000, barstyle='fancy',fontcolor='w')

    #Plot the SuperDARN data!
    ngates = np.shape(currentData.data)[2]
    nbeams = np.shape(currentData.data)[1]
    verts = []
    scan = []
    data  = currentData.data[timeInx,:,:]
    for bm in range(nbeams):
      for rg in range(ngates):
        if np.isnan(data[bm,rg]): continue
        if data[bm,rg] == 0: continue
        scan.append(data[bm,rg])

        x1,y1 = m(lonFull[bm+0,rg+0],latFull[bm+0,rg+0])
        x2,y2 = m(lonFull[bm+1,rg+0],latFull[bm+1,rg+0])
        x3,y3 = m(lonFull[bm+1,rg+1],latFull[bm+1,rg+1])
        x4,y4 = m(lonFull[bm+0,rg+1],latFull[bm+0,rg+1])
        verts.append(((x1,y1),(x2,y2),(x3,y3),(x4,y4),(x1,y1)))

    colors  = 'lasse'
    cmap,norm,bounds = utils.plotUtils.genCmap(param,scale,colors=colors)
    pcoll = PolyCollection(np.array(verts),edgecolors='face',linewidths=0,closed=False,cmap=cmap,norm=norm,zorder=99)
    pcoll.set_array(np.array(scan))
    axis.add_collection(pcoll,autolim=False)

    cbar = fig.colorbar(pcoll,orientation='vertical',shrink=.65,fraction=.1)
    labels = cbar.ax.get_yticklabels()
    labels[-1].set_visible(False)
    plt.show()