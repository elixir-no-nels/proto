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
from gold.gsuite import GSuiteFunctions
'''
Created on Nov 26, 2015

@author: boris
'''

from quick.webtools.GeneralGuiTool import GeneralGuiTool


class BasicModeAnalysisInfoMixin(object):
    '''
    classdocs
    
    '''
    @staticmethod
    def getInputBoxNamesForAnalysisInfo():
        return [
                ('Basic mode question ID', 'bmQid'),
                ('Analysis info', 'analysisInfo')]
    
    @staticmethod
    def getOptionsBoxBmQid():
        return '__hidden__', None
     
    @staticmethod

    def getOptionsBoxAnalysisInfo(prevChoices):
        if prevChoices.bmQid and prevChoices.bmQid not in ('None', '', None):
            htmlCore = GSuiteFunctions.getAnalysisQuestionInfoHtml(prevChoices.bmQid)
            return '__rawstr__', str(htmlCore)