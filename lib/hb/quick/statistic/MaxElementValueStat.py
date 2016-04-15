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
from gold.statistic.Statistic import Statistic, StatisticSumResSplittable, StatisticSplittable
from gold.statistic.RawDataStat import RawDataStat
from gold.track.TrackFormat import TrackFormatReq

class MaxElementValueStat(MagicStatFactory):
    "Takes the maximum value of elements inside the bin"
    pass

class MaxElementValueStatSplittable(StatisticSplittable):
    def _combineResults(self):
        self._result = max(self._childResults)


class MaxElementValueStatUnsplittable(Statistic):
    def _compute(self):
        rawData = self._children[0].getResult()
        vals = rawData.valsAsNumpyArray()
        return vals.max()   

    def _createChildren(self):
        self._addChild( RawDataStat(self._region, self._track, TrackFormatReq(allowOverlaps=True)) )
        #self._addChild( RawDataStat(self._region, self._track, TrackFormatReq(val='number', allowOverlaps=self._configuredToAllowOverlaps(strict=False))) )
