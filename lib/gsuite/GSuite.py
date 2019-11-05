from collections import OrderedDict
from gsuite.CustomExceptions import InvalidFormatError, NotSupportedError, ArgumentValueError
from gsuite.GSuiteConstants import HEADER_VAR_DICT, LOCATION_HEADER, FILE_FORMAT_HEADER, \
                                        TRACK_TYPE_HEADER, GENOME_HEADER, LOCATION_MEMBER, \
                                        FILE_FORMAT_MEMBER, TRACK_TYPE_MEMBER, GENOME_MEMBER, \
                                        UNKNOWN, MULTIPLE, LOCAL, PREPROCESSED
from proto.CommonFunctions import urlDecodePhrase


class GSuite(object):
    def __init__(self, trackList=[], customHeaders=OrderedDict()):
        self._trackList = []
        self._titleToTrackDict = {}
        self._updatedHeaders = False
        self.customHeaders = customHeaders

        self.addTracks(trackList)

    @property
    def location(self):
        return self._location

    def _updateLocation(self):
        self._location = self._getCombinedHeaderValue(LOCATION_HEADER, LOCATION_MEMBER,
                                                      self._combineEqualVals)

    @property
    def fileFormat(self):
        return self._fileFormat

    def _updateFileFormat(self):
        self._fileFormat = self._getCombinedHeaderValue(FILE_FORMAT_HEADER, FILE_FORMAT_MEMBER,
                                                        self._combineEqualVals)

    @property
    def trackType(self):
        return self._trackType

    def _updateTrackType(self):
        self._trackType = self._getCombinedHeaderValue(TRACK_TYPE_HEADER, TRACK_TYPE_MEMBER,
                                                       self._combineTrackTypeVals)

    @property
    def genome(self):
        return self._genome

    def _updateGenome(self):
        self._genome = self._getCombinedHeaderValue(GENOME_HEADER, GENOME_MEMBER,
                                                    self._combineEqualVals)

    def _getCombinedHeaderValue(self, key, member, combineValPairFunc):
        valPerTrack = [getattr(track, member) for track in self._trackList]
        if len(valPerTrack) == 0:
            curVal = HEADER_VAR_DICT[key].default
        else:
            curVal = valPerTrack[0]
            for nextVal in valPerTrack[1:]:
                curVal = self._combineTrackValPair(curVal, nextVal, combineValPairFunc)

        return curVal

    @staticmethod
    def _combineTrackValPair(curVal, nextVal, combineValPairFunc):
        try:
            return combineValPairFunc(curVal, nextVal)
        except (InvalidFormatError, NotSupportedError):
            if UNKNOWN in (curVal, nextVal):
                return UNKNOWN
            else:
                return MULTIPLE

    @staticmethod
    def _combineEqualVals(curVal, nextVal):
        if curVal == nextVal:
            return curVal
        raise InvalidFormatError('%s != %s' % (curVal, nextVal))

    def _combineTrackTypeVals(self, curVal, nextVal):
        try:
            return self._combineEqualVals(curVal, nextVal)
        except InvalidFormatError:
            from gold.track.TrackFormat import TrackFormatReq
            curReq = TrackFormatReq(name=curVal)
            nextReq = TrackFormatReq(name=nextVal)

            maxCommonCoreType = TrackFormatReq.maxCommonCoreFormat(curReq, nextReq)
            if maxCommonCoreType is not None:
                return maxCommonCoreType.getFormatName().lower()

            raise InvalidFormatError('Track types "%s" and "%s" are not possible to combine. '
                                     % (curVal, nextVal))

    @property
    def customHeaders(self):
        return self._customHeaders

    @customHeaders.setter
    def customHeaders(self, customHeaders):
        self._customHeaders = OrderedDict()

        for key, val in customHeaders.iteritems():
            if val is not None:
                if val == '':
                    raise InvalidFormatError('Empty header values not allowed. '
                                             'Please use ".", the period character, to '
                                             'indicate missing values')

                if key.lower() in self._customHeaders:
                    raise ArgumentValueError('Custom header "{}" appears multiple times in the '
                                             'header list. Note that custom headers are case '
                                             'insensitive (e.g., "ABC" and "abc" is the same '
                                             'header).'.format(key))
                self.setCustomHeader(key, val)

    def setCustomHeader(self, headerName, headerVal):
        headerName = headerName.lower()
        self._customHeaders[headerName] = urlDecodePhrase(headerVal)

    def getCustomHeader(self, headerName):
        if headerName in self._customHeaders:
            return self._customHeaders[headerName]

    @property
    def attributes(self):
        allAttributes = OrderedDict()

        for track in self._trackList:
            for attribute in track.attributes:
                allAttributes[attribute] = True

        return allAttributes.keys()
    
    def isPreprocessed(self):
        return self.location == LOCAL and self.fileFormat == PREPROCESSED

    def hasCustomTitles(self):
        return any(track.title != track.uri for track in self.allTracks())

    def addTrack(self, track, allowDuplicateTitles=True):
        if track.title in self._titleToTrackDict:
            if allowDuplicateTitles:
                for i in range(self.numTracks()):
                    candTitle = track.title + ' (%s)' % (i+2)
                    if candTitle not in self._titleToTrackDict:
                        track.title = candTitle
                        break
            else:
                raise InvalidFormatError('Multiple tracks with the same title is not allowed: ' +
                                         track.title)

        self._updatedHeaders = False
        self._titleToTrackDict[track.title] = track
        self._trackList.append(track)

    def addTracks(self, trackList, allowDuplicateTitles=True):
        for track in trackList:
            self.addTrack(track, allowDuplicateTitles=allowDuplicateTitles)

        self._updateGSuiteHeaders()

    def _updateGSuiteHeaders(self):
        self._updateLocation()
        self._updateFileFormat()
        self._updateTrackType()
        self._updateGenome()
        
        self._updatedHeaders = True

    def numTracks(self):
        return len(self._trackList)

    def allTracks(self):
        for track in self._trackList:
            yield track

    def allTrackTitles(self):
        return [gsTrack.title for gsTrack in self._trackList]

    def allTrackTypes(self):
        return list(sorted(set(x.trackType for x in self.allTracks())))
    
    def getTrackFromIndex(self, index):
        return self._trackList[index]

    def getTrackFromTitle(self, title):
        return self._titleToTrackDict[title]

    def setGenomeOfAllTracks(self, genome):
        for track in self.allTracks():
            track.genome = genome
        self._updateGenome()
        
    def __str__(self):
        import gsuite.GSuiteComposer as GSuiteComposer
        return GSuiteComposer.composeToString(self)
    
    def __len__(self):
        return self.numTracks()

    def isEmpty(self):
        return len(list(self.allTracks())) == 0
    
    def getAttributeValueList(self, attrName):
        assert attrName in self.attributes, attrName
        return [x.getAttribute(attrName) for x in self.allTracks()]

    def __getattribute__(self, attr):
        if not object.__getattribute__(self, '_updatedHeaders') and \
                not attr.startswith('_') and \
                attr not in ('addTrack', 'addTracks'):
            self._updateGSuiteHeaders()
        return object.__getattribute__(self, attr)

    def __getattr__(self, item):
        try:
            return self.__dict__['_customHeaders'][item]
        except KeyError:
            raise AttributeError("Member '%s' not found in class '%s'" %
                                 (item, self.__class__.__name__))
