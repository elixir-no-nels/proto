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

from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import Statistic, StatisticSplittable
from gold.statistic.RawDataStat import RawDataStat
from gold.track.TrackFormat import TrackFormatReq

class TemporaryGETestStat(MagicStatFactory):
    '''
    To be deleted after testing..
    '''
    pass



class TemporaryGETestStatUnsplittable(Statistic):
    def _compute(self): 
        from gold.origdata.GenomeElement import GenomeElement
        ge = GenomeElement(start=0, end=1)
        ge2 = GenomeElement(start=10, end=11)
        return [ge,ge2]
                
    def _createChildren(self):
        self._addChild( RawDataStat(self._region, self._track, TrackFormatReq() ) )