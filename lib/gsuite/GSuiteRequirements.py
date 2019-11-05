from collections import OrderedDict
from gsuite.CustomExceptions import InvalidFormatError
from gsuite.GSuiteConstants import HEADER_VAR_DICT, LOCATION_HEADER, \
                                        FILE_FORMAT_HEADER, TRACK_TYPE_HEADER


class GSuiteRequirements(object):
    def __init__(self, allowedLocations=None, allowedFileFormats=None, allowedTrackTypes=None):
        # A parameter value of None means that all values are allowed
        # If the parameter value is a list, the contents of the list are the allowed values

        assert allowedFileFormats or allowedLocations or allowedTrackTypes

        self._requirements = OrderedDict()

        for header, allowedVals in [(LOCATION_HEADER, allowedLocations),
                                    (FILE_FORMAT_HEADER, allowedFileFormats),
                                    (TRACK_TYPE_HEADER, allowedTrackTypes)]:
            if allowedVals is not None:
                assert all(val in HEADER_VAR_DICT[header].allowed for val in allowedVals)
                self._requirements[header] = allowedVals

    @staticmethod
    def _getMemberValue(gSuiteOrTrack, header):
        return getattr(gSuiteOrTrack, HEADER_VAR_DICT[header].memberName)

    def check(self, gSuiteOrTrack):
        for header, allowedVals in self._requirements.iteritems():
            if self._getMemberValue(gSuiteOrTrack, header) not in allowedVals:
                errorString = '\'%s\' is not a supported GSuite %s for this tool. ' \
                              'Supported file types are [%s]' % \
                              (self._getMemberValue(gSuiteOrTrack, header), header,
                               ', '.join(self._requirements[header]))
                raise InvalidFormatError(errorString)
