'''
Created on Mar 10, 2015

@author: boris
'''

import time
from datetime import timedelta

from proto.HtmlCore import HtmlCore

UNKNOWN_TIME_REMAINING = 'Unknown'
RELOAD_TIME = 5 # 15


class ProgressViewer(object):
    '''
    HTML generator for the progress page.
    '''

    def __init__(self, processList, filePath):
        '''
        Constructor
        processList - is a list of 2-tupples (name, elementCount),
        e.g. ("Download tracks", 12) for a GSuite of 12 tracks.
        filePath - path to the output file
        '''
        self._processList = processList
        self._progressObjList = []

        for process in self._processList:
            self.addProgressObject(process[0], int(process[1]))

        self._processIndex = 0
        self._filePath = filePath
        self._startTime = time.time()
        self._refreshOutput(done=len(self._processList) == 0)

    def _addProgressObject(self, progressObject):
        self._progressObjList.append(progressObject)

    def addProgressObject(self, name, elementCount):
        ''' add progress object with given name and element count'''
        self._addProgressObject(ProgressObject(name, int(elementCount)))

    def updateProgressObjectElementCount(self, name, newElementCount):
        for progressObject in self._progressObjList:
            if progressObject.name == name:
                progressObject.elementCount = newElementCount
                return True

        return False

    def _refreshOutput(self, done):
        html = self._buildHtml(done)

        with file(self._filePath, 'w') as f:
            f.write(str(html))
            f.flush()

    @property
    def processCount(self):
        return len(self._processList)

    def _estimateRemainingTime(self):
        fullTimeElapsed = 0
        unknown = False

        for i in range(self.processCount):
            if self._estimateProcessRemainingTime(i) == UNKNOWN_TIME_REMAINING:
                unknown = True
            else:
                fullTimeElapsed += self._estimateProcessRemainingTime(i)

        return fullTimeElapsed, unknown

    def _estimateProcessRemainingTime(self, processIndex):
        progressObj = self._progressObjList[processIndex]
        return progressObj.estimateRemainingTime()

    def _getEstimatedTimeRemainingStr(self, estimatedRemainingTime, unknown):
        if unknown:
            estRemainingTimeStr = UNKNOWN_TIME_REMAINING
        else:
            estRemainingTimeStr = self._getTimeStr(estimatedRemainingTime)

        return "Estimated time remaining: " + estRemainingTimeStr

    def _getTimeStr(self, timeVal):
        timeDelta = timedelta(seconds=timeVal)
        minutes, seconds = divmod(timeDelta.seconds, 60)
        hours, minutes = divmod(minutes, 60)
        timeStr = "%sd:%sh:%sm:%ss" % (
            timeDelta.days, hours, minutes, seconds)
        return timeStr

    def _getRunningTimeStr(self):
        return "Running time for finished tasks: %s" % \
               self._getTimeStr(time.time() - self._startTime)

    def _buildHtml(self, done):
        htmlCore = HtmlCore()
        htmlCore.begin(reloadTime=RELOAD_TIME)
        htmlCore.divBegin(divId='progress')

        runningTimeStr = self._getRunningTimeStr()
        htmlCore.header(runningTimeStr)

        remainingTime, unknown = self._estimateRemainingTime()
        timeRemainingStr = self._getEstimatedTimeRemainingStr(remainingTime, unknown)

        if unknown:
            if remainingTime > 0:
                timeRemainingStr += '+'

        htmlCore.header(timeRemainingStr)

        nameCellColSpan = 4 #colspan for the first cell that displays the process name

        for progressObj in self._progressObjList:
            htmlCore.tableHeader([], tableClass='progress')
            htmlCore.tableRowBegin(rowClass='progressRow')
            htmlCore.tableCell(progressObj.name, colSpan=nameCellColSpan)

#             for i in range(progressObj.status):
#                 content = ''
#                 if i == int(progressObj.elementCount / 2):
#                     content = "%0.2f" % float(progressObj.status) / progressObj.elementCount  * 100
#                 if i == int(progressObj.elementCount / 2 + 1):
#                     content = '%'
#                 htmlCore.tableCell(content, cellClass='progressCellDone')
#
#             for i in range(progressObj.status, progressObj.elementCount):
#                 content = ''
#                 if i == int(progressObj.elementCount / 2):
#                     content = "%0.2f" % float(progressObj.status) / progressObj.elementCount  * 100
#                 if i == int(progressObj.elementCount / 2 + 1):
#                     content = '%'
#                 htmlCore.tableCell(content, cellClass='progressCell')

            for i in range(progressObj.elementCount):
                content = ''
                if i == int(progressObj.elementCount / 2):
                    content = "%0.2f" % (float(progressObj.status) / progressObj.elementCount  * 100)
                if i == int(progressObj.elementCount / 2 + 1):
                    content = '%'
                cellCls = 'progressCellDone' if i < progressObj.status else 'progressCell'
                htmlCore.tableCell(content, cellClass=cellCls)


            htmlCore.tableRowEnd()
            htmlCore.tableFooter()

            estimatedRemainingTime = progressObj.estimateRemainingTime()
            unknown = estimatedRemainingTime == UNKNOWN_TIME_REMAINING
            progressObjInfo = self._getEstimatedTimeRemainingStr(estimatedRemainingTime, unknown)
            htmlCore.paragraph(progressObjInfo)

        htmlCore.divEnd()
        htmlCore.end(stopReload=done)
        return htmlCore

    def update(self):
        '''
        Return false if all processes are finished.
        Update status counts for progress viewer and current progress object, rebuild html,
        and return True if there are unfinished progress objects, else return False.
        '''
        if self._processIndex >= len(self._progressObjList):
            #LOG: inconsistent usage of ProgressViewer
            return False

        currentProgressObj = self._progressObjList[self._processIndex]

        if not currentProgressObj.update():#if last progressObject switch to next process
            self._processIndex += 1

            done = self._processIndex == len(self._progressObjList)
            self._refreshOutput(done)

            if not done:
                self._progressObjList[self._processIndex].resetStartTime()

            return False
        else:
            self._refreshOutput(done=False)
            return True


class ProgressObject(object):

    def __init__(self, name, elementCount):
        self._name = name
        self._elementCount = elementCount
        self._status = 0
        self._startTime = time.time()

    def update(self):
#         if self.status == 0:
#             self.resetStartTime()
        self._status += 1

        if self.status == self.elementCount:
            return False
        else:
            return True

    @property
    def status(self):
        return self._status

    @property
    def elementCount(self):
        return self._elementCount

    @elementCount.setter
    def elementCount(self, value):
        self._elementCount = value

    @property
    def name(self):
        return self._name

    def resetStartTime(self):
        self._startTime = time.time()

    def estimateRemainingTime(self):
        if self.status == 0:
            return UNKNOWN_TIME_REMAINING
        return 1.0 * (self.elementCount - self.status) * (time.time() - self._startTime) / self.status
