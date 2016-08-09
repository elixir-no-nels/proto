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

from gold.result.Presenter import Presenter
from gold.util.CommonFunctions import strWithStdFormatting
from gold.result.GraphicsPresenter import GlobalResultGraphicsMatrixDataFromNumpy, GlobalResultGraphicsMatrixDataFromDictOfDicts, \
    GlobalResultGraphicsMatrixDataFromTableData
from gold.result.HtmlCore import HtmlCore
from gold.result.TextCore import TextCore
from quick.util.CommonFunctions import ensurePathExists, getLoadToGalaxyHistoryURL
from quick.result.model.TableData import TableData
import os
import numpy
from copy import copy


class MatrixGlobalValuePresenter(Presenter):
    FN_SUFFIX = '_table'
    DESCRIPTION = 'Table: effect size'
    HEADER = 'Global result table'
    
    def __init__(self, results, baseDir, header):
        Presenter.__init__(self, results, baseDir)
        
        self._htmlFns = {}
        self._rawFns = {}
        
        for resDictKey in self._getResDictKeys():
            #HTML
            self._htmlFns[resDictKey] = os.sep.join([baseDir, (resDictKey if not resDictKey is None else 'Result')+\
                                                     self.FN_SUFFIX + '.html'])
            self._writeContent(self._htmlFns[resDictKey], resDictKey, header, HtmlCore)
            #Raw text
            self._rawFns[resDictKey] = os.sep.join([baseDir, (resDictKey if not resDictKey is None else 'Result') +\
                                                    self.FN_SUFFIX + '.txt'])
            self._writeContent(self._rawFns[resDictKey], resDictKey, header, TextCore)
    
    def getDescription(self):
        return self.DESCRIPTION
    
    def getReference(self, resDictKey):
        if self._getRawData(resDictKey) is None:
            return 'N/A'

        return str(HtmlCore().link('HTML', self._getRelativeURL(self._htmlFns[resDictKey]))) + \
                '&nbsp;/&nbsp;' + \
                str(HtmlCore().link('Raw&nbsp;text', self._getRelativeURL(self._rawFns[resDictKey])))

    def _writeContent(self, fn, resDictKey, header, coreCls):
        ensurePathExists(fn)
        outFile = open(fn,'w')

        self._writeFile(coreCls, header, outFile, resDictKey)

    def _writeFile(self, coreCls, header, outFile, resDictKey):
        core = coreCls()
        core.begin()
        core = self._writeTable(core, coreCls, header, outFile, resDictKey)
        core.end()
        outFile.write(str(core))
        outFile.close()

    def _writeTable(self, core, coreCls, header, outFile, resDictKey):
        core.bigHeader(header)
        core.header(self.HEADER)
        tableData = self._getRawData(resDictKey)
        assert isinstance(tableData, TableData)
        matrix = tableData.numpyMatrix
        rowNames = tableData.rowNamesAsNumpyArray
        colNames = tableData.columnNamesAsNumpyArray
        rowOrder = tableData.rowOrder
        colOrder = tableData.colOrder
        if rowOrder is not None:
            rowNames = rowNames[rowOrder]
            matrix = matrix[rowOrder]
        if colOrder is not None:
            colNames = colNames[colOrder]
            matrix = matrix[:, colOrder]
        core.tableHeader(
            [''] + [str(coreCls().textWithHelp(baseText, helpText)) for
                    baseText, helpText in \
                    [self._results.getLabelHelpPair(col) for col in colNames]],
            sortable=True)
        for i, row in enumerate(matrix):
            core.tableLine([str(coreCls().textWithHelp(
                *self._results.getLabelHelpPair(rowNames[i])))] + \
                           [str(coreCls().format(row[i])) for i in
                            xrange(len(row))])
            # In order for the memory usage and handling time not to explode for large tables
            outFile.write(str(core))
            core = coreCls()
        core.tableFooter()
        return core

    def _getResDictKeys(self):
        return self._results.getResDictKeys()


class MatrixGlobalValueFromNumpyPresenter(MatrixGlobalValuePresenter,
                                          GlobalResultGraphicsMatrixDataFromNumpy):
    MATRIX_VALUE_KEY = 'Matrix'


class MatrixGlobalValueFromTableDataPresenter(MatrixGlobalValuePresenter,
                                              GlobalResultGraphicsMatrixDataFromTableData):
    pass


class MatrixGlobalValueFromDictOfDictsPresenter(MatrixGlobalValuePresenter,
                                                GlobalResultGraphicsMatrixDataFromDictOfDicts):
    def _getResDictKeys(self):
        return [None]

class MatrixGlobalCountsPresenter(MatrixGlobalValuePresenter,
                                  GlobalResultGraphicsMatrixDataFromNumpy):
    FN_SUFFIX = '_counts_table'
    MATRIX_VALUE_KEY = 'Counts'
    DESCRIPTION = 'Table: counts'
    HEADER = 'Global table of counts'


class MatrixGlobalPvalPresenter(MatrixGlobalValuePresenter,
                                GlobalResultGraphicsMatrixDataFromNumpy):
    FN_SUFFIX = '_pval_table'
    MATRIX_VALUE_KEY = 'Pvals'
    DESCRIPTION = 'Table: p-values'
    HEADER = 'Global table of p-values'


class MatrixGlobalSignificancePresenter(MatrixGlobalValuePresenter,
                                        GlobalResultGraphicsMatrixDataFromNumpy):
    FN_SUFFIX = '_significance_table'
    MATRIX_VALUE_KEY = 'Significance'
    DESCRIPTION = 'Table: significance'
    HEADER = 'Global table of significance'