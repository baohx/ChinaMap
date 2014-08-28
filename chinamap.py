# -*- coding: utf-8 -*-
import shapefile
import copy
from pandas import Series
import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
import matplotlib as mpl
from matplotlib.collections import LineCollection
from matplotlib import cm
from pandas import concat


def getPointArray(conshpfn):
    conShp = shapefile.Reader(conshpfn)
    conShapes = conShp.shapes()
    conShapeArray = []
    for conShape in conShapes:
        numOfShapePoints = len(conShape.points)
        conShapePartArray = copy.deepcopy(conShape.parts)
        conShapePartArray.append(numOfShapePoints)
        partPointsArray = []
        for partIndex in range(len(conShape.parts)):
            partPointsArray.append(conShape.points[conShapePartArray[partIndex]:conShapePartArray[partIndex+1]])
        partPointsSeries = Series(partPointsArray)
        numOfPartPointsSeries = partPointsSeries.apply(lambda x: len(x))
        numOfPartPointsSeries = numOfPartPointsSeries.rank(method = 'first')
        rankDic = {}
        for i,numOfPartPointsSeriesItem in enumerate(numOfPartPointsSeries):
            rankDic[numOfPartPointsSeriesItem] = partPointsSeries[i]
        rankDicKeys = rankDic.keys()
        rankDicKeys.sort(reverse=True)
        sortedPartPointsArray = []
        for rankDicKey in rankDicKeys:
            sortedPartPointsArray.append(rankDic[rankDicKey])
        conShapeArray.append(sortedPartPointsArray)
    return conShapeArray

def drawShape(m, ax, paraTable):
    for conshpfn in paraTable["ShapeFile"].unique():
        for i, conShape in enumerate(getPointArray(conshpfn)):
            tempParaTable = concat([paraTable[paraTable["ShapeFile"]==conshpfn]], ignore_index = True)
            partLimit = tempParaTable.ix[i,"PartLimit"]
            normal = tempParaTable.ix[i,"Normal"]
            shpsegs = []
            for j, conShapePart in enumerate(conShape):
                if j < partLimit:
                    lons, lats = zip(*conShapePart)
                    x, y = m(lons, lats)
                    shpsegs.append(zip(x,y))
                    lines = LineCollection(shpsegs,antialiaseds=(1,))
                    lines.set_facecolors(cm.gray(1 - normal))
                    lines.set_linewidth(0.01)
                    ax.add_collection(lines)

mpl.rcParams['font.size'] = 10.
mpl.rcParams['font.family'] = 'Comic Sans MS'
mpl.rcParams['axes.labelsize'] = 8.
mpl.rcParams['xtick.labelsize'] = 6.
mpl.rcParams['ytick.labelsize'] = 6.

fig = plt.figure(figsize=(11.7,8.3))
plt.subplots_adjust(left=0.05,right=0.95,top=0.90,bottom=0.05,wspace=0.15,hspace=0.05)
ax = plt.subplot(111)
m = Basemap(llcrnrlon=70, llcrnrlat=0, urcrnrlon=140, urcrnrlat=60, projection='mill',lon_0=180)
#m.drawcountries(linewidth=0.5)
#m.drawcoastlines(linewidth=0.5)
m.drawmapboundary(fill_color='#FFDEAD')
#m.drawmapboundary(fill_color='white')

paraFileName = r'chinamap.xlsx'
paraFile = pd.ExcelFile(paraFileName)
paraTable = paraFile.parse(sheetname = 'Sheet1', header = 0)
paraTable['Normal'] = paraTable['Data']/max(paraTable['Data'])
drawShape(m, ax, paraTable)

fig.savefig('china.png')
plt.show()