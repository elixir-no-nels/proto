# Copyright (C) 2009, Geir Kjetil Sandve, Sveinung Gundersen and Morten Johansen
# This file is part of The Genomic HyperBrowser.
#
#    The Genomic HyperBrowser is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    The Genomic HyperBrowser is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with The Genomic HyperBrowser.  If not, see <http://www.gnu.org/licenses/>.
from numpy import float64
'''
Created on Feb 12, 2015

@author: boris
'''

def drawLineplot(plotDataDict, mainTitle, xLabels, maxPercentage, xTitle, yTitle):
    from gold.application.RSetup import robjects

    matplot = robjects.r.matplot
    cbind = robjects.r.cbind
    matplot(cbind(*plotDataDict.values()), type='b', axes=False, ann=False)
    axis = robjects.r.axis
    axis(1, at=[x + 1 for x in range(len(xLabels))], labels=xLabels, las=2)
    axis(2, at=range(int(maxPercentage) + 2), las=1)
    title = robjects.r.title
    title(main=mainTitle)
    title(xlab=xTitle)
    title(ylab=yTitle)

def drawVioplot(plotDataMatrix, xlabels, mainTitle, 
                xTitle, yTitle, vioplotColor, 
                xAxisAt, xLimMin, xLimMax, xLas, 
                yAxisAt, yLimMin, yLimMax, yLas):
    from gold.application.RSetup import robjects
    
    convertedData = [robjects.FloatVector(x) for x in plotDataMatrix]
    rplot = robjects.r.plot 
    axis = robjects.r.axis
    from rpy2.robjects.packages import importr
    vioplot = importr("vioplot")
    rplot([1], [1], type='n', xlim=robjects.FloatVector([xLimMin, xLimMax]), ylim=robjects.FloatVector([yLimMin, yLimMax]), 
          axes=False, ann=False)
    vioplot.vioplot(col=vioplotColor, add=True, *convertedData)
    axis(1, at=xAxisAt, labels=xlabels, las=xLas)
    axis(2, at=yAxisAt, las=yLas)
    title = robjects.r.title
    title(main=mainTitle)
    title(xlab=xTitle)
    title(ylab=yTitle)

    

def dataIntoBins(xData, yData, xLimMax, bins):
    from numpy import ceil
    dataBinnedDict = dict()
    binSize = xLimMax / bins
    for x, y in zip(xData, yData):
        binVal = ceil(x / binSize) * binSize
        if not binVal in dataBinnedDict:
            dataBinnedDict[binVal] = []
        dataBinnedDict[binVal].append(y)
    
    return dataBinnedDict


def drawSmoothedLinePlot(xData, yData, colors, smoothingParameter, displayPoints):
    from gold.application.RSetup import robjects

    smoothSpline = robjects.r['smooth.spline']
    lines = robjects.r.lines
    sl = smoothSpline(xData, yData, spar=smoothingParameter)
    lines(sl, col=colors)
    if displayPoints:
        points = robjects.r.points
        points(xData, yData, col=colors)

def drawBinnedSmoothedLinePlot(xData, yData, col, bins=20, xLimMax = 100, displayPoints=False, spar=0.6):
    from numpy import mean
    dataBinnedDict = dataIntoBins(xData, yData, xLimMax, bins)
    
    xBinnedData = []
    yBinnedData = []
    for x in sorted(dataBinnedDict.keys()):
        xBinnedData.append(x)
        yBinnedData.append(mean(dataBinnedDict[x], dtype=float64))
    drawSmoothedLinePlot(xBinnedData, yBinnedData, col, spar, displayPoints)
     


def sortDataByX(xData, yData, descending=False):
    dataDict = dict(zip(xData, yData))
    xSorted = sorted(dataDict.keys(), reverse=descending)
    ySorted = [dataDict[x] for x in xSorted]
    return xSorted, ySorted

def drawMovingAvgSmoothedLinePlot(xData, yData, col, displayPoints=False, spar=0.6):
    from numpy import mean
    xSorted, ySorted = sortDataByX(xData, yData)
     
    xSmoothed = []
    ySmoothed = []
    for i in range(len(xSorted)):
        if i+4 < len(xSorted):
            newX = mean(xSorted[i:i+5], dtype=float64)
             
            newY = mean(ySorted[i:i+5], dtype=float64)
        else: 
            newX = mean(xSorted[i:], dtype=float64)
            newY = mean(ySorted[i:], dtype=float64)
        xSmoothed.append(newX)
        ySmoothed.append(newY)
        
    drawSmoothedLinePlot(xSmoothed, ySmoothed, col, spar, displayPoints)


def drawHeatmap(heatmapPlotData, rowLabels, colLabels, mainTitle, symm=True):
    from gold.application.RSetup import robjects

    from numpy import matrix
    heatmap = robjects.r.heatmap
    rmatrix = robjects.r.matrix
    flatData = matrix(heatmapPlotData).flatten().tolist()[0]
    data = robjects.FloatVector(flatData)
    heatmap(rmatrix(data, nrow=len(rowLabels)), labRow=rowLabels, labCol=colLabels, main=mainTitle, symm=symm)
    
def getRainbowColors(nrColors):
    from gold.application.RSetup import robjects

    rainbow = robjects.r.rainbow
    colors = rainbow(nrColors)
    return colors

def drawHistogram(data, mainTitle, xTitle, yTitle, xLim, yLim=None, color='cadetblue2'):
    from gold.application.RSetup import robjects

    hist = robjects.r.hist
    if yLim:
        hist(robjects.FloatVector(data), main=mainTitle, xlab=xTitle, ylab=yTitle, 
             xlim=robjects.FloatVector(xLim), ylim = robjects.FloatVector(yLim), col=color)
    else:
        hist(robjects.FloatVector(data), main=mainTitle, xlab=xTitle, ylab=yTitle, 
             xlim=robjects.FloatVector(xLim), col=color)

def drawMultiHistogram(data, mainTitle, xTitle, yTitle, names=None, colors=None, hasLegend = False):
    from gold.application.RSetup import robjects

    from rpy2.robjects.packages import importr
    plotrix = importr('plotrix')
    multhist = plotrix.multhist
    
    legend = robjects.r.legend

    plotData = [robjects.FloatVector(x) for x in data]
    multhist(plotData, col=colors, main=mainTitle, beside=True, xlab=xTitle, ylab=yTitle)   
    if hasLegend:
        legend('topleft', legend=names, pch=15, col=colors, bty='n')


def drawVerticalLine(verticalLine):
    from gold.application.RSetup import robjects

    abline = robjects.r.abline
    abline(v=verticalLine)


def drawBarplot(data, mainTitle, xTitle, yTitle, names, col):
    from gold.application.RSetup import robjects

    barplot = robjects.r.barplot
    barplot(robjects.FloatVector(data), main=mainTitle, xlab=xTitle, ylab=yTitle,
             names = names, col=col)

def drawXYPlot(xData, yData, plotType, xLim, yLim, mainTitle, xTitle, yTitle):
    from gold.application.RSetup import robjects

    rPlot = robjects.r.plot
    rPlot(xData, yData, type=plotType, xlim=robjects.FloatVector(xLim), ylim=robjects.FloatVector(yLim), 
          main = mainTitle, xlab=xTitle, ylab=yTitle)
    
def addNoiseUniform(data, noise):
    from random import uniform
    for i in range(len(data)):
        data[i] = data[i] + uniform(-noise, noise)
        
def drawEmptyPlot(xTitle, yTitle, mainTitle, xLim, yLim):
    drawXYPlot([1], [1], 'n', xLim, yLim, mainTitle, xTitle, yTitle)

def drawLegend(position, names, colors):
    from gold.application.RSetup import robjects

    legend = robjects.r.legend
    legend(position, legend=names, lty=1, col=colors, bty='n', cex=0.75)

def rDevOff():
    from gold.application.RSetup import r
    r('dev.off()')
