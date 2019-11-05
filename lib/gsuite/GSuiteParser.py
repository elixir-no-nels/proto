from urllib import unquote
from collections import OrderedDict, namedtuple
from cStringIO import StringIO

from gsuite.GSuite import GSuite
from gsuite.GSuiteTrack import GSuiteTrack
from gsuite.GSuiteConstants import HEADER_VAR_DICT, FILE_TYPE_HEADER, \
                                        TEXT, BINARY, PRIMARY, PREPROCESSED, \
                                        ALL_STD_COL_SPECS, OPTIONAL_STD_COL_NAMES, \
                                        ALL_STD_COL_NAMES, URI_COL, \
                                        GENOME_HEADER, MULTIPLE
from proto.CommonConstants import ALLOWED_CHARS
from gsuite.CustomExceptions import InvalidFormatError


#
# Namedtuples
#
from proto.CommonFunctions import urlDecodePhrase, formatPhraseWithCorrectChrUsage

GSuiteContents = namedtuple('GSuiteContents', ['genome', 'colNames', 'headerVars', 'tracks'])


#
# Header lines, e.g.: "##track type: segments"
#

def _parseHeaderLine(line):
    headerLine = line[2:]
    splitLine = headerLine.split(':')

    if len(splitLine) != 2:
        raise InvalidFormatError('Header line not understood: ' + repr(headerLine))

    key, val = splitLine
    key = key.lower()
    val = val.strip()

    if key == GENOME_HEADER:
        val = urlDecodePhrase(val)
    elif key not in HEADER_VAR_DICT:
        if key.endswith(' '):
            raise InvalidFormatError('Header variable "%s" must not end with space.' % key)

        # raise InvalidFormatError('Header variable "%s" is not part of the GSuite format.' % key)
        if urlDecodePhrase(key) != key:
            raise InvalidFormatError('Custom header variable names in GSuite do not support URL '
                                     'escaping. Offending header variable: "{}"'.format(key))
    else:
        val = val.lower()

        if val not in HEADER_VAR_DICT[key].allowed:
            raise InvalidFormatError('Value "%s" is not allowed for header "%s". Allowed values: %s' %
                                     (val, key, ', '.join(HEADER_VAR_DICT[key].allowed)))

        if key == FILE_TYPE_HEADER:
            if val == TEXT:
                val = PRIMARY
            elif val == BINARY:
                val = PREPROCESSED

    return key, val


def _updateHeaderVars(headerVars, key, val):
    if key in headerVars:
        raise InvalidFormatError('Double header lines for header "%s" are not allowed.' % key)

    headerVars[key] = val
    return headerVars


def _setCustomHeaders(gSuite, headerVars):
    for key, val in headerVars.iteritems():
        if key not in HEADER_VAR_DICT:
            gSuite.setCustomHeader(key, val)


def _compareHeaders(headerName, textHeader, trackSummaryHeader):
    if textHeader != trackSummaryHeader:
        raise InvalidFormatError(
            'The global value for GSuite header variable "%s" (%s) '
            % (headerName, textHeader) + 'is not compatible with the combined '
            'value of the corresponding track-specific variables: %s' % trackSummaryHeader
        )


def _compareTextHeadersWithTrackSummaryHeaders(headerVars, gSuite):
    for header in HEADER_VAR_DICT:
        if header in headerVars:
            _compareHeaders(header, headerVars[header],
                            getattr(gSuite, HEADER_VAR_DICT[header].memberName))


# def _updateUnsetHeaderVarsWithDefaultVals(headerVars):
#    for key in HEADER_VAR_DICT:
#        if not key in headerVars:
#            headerVars[key] = HEADER_VAR_DICT[key].default
#
#    return headerVars


#
# Column specification line, e.g.: "###uri\ttitle\tantibody"
#

def _parseColumnSpecLine(line):
    colNames = line[3:].lower().split('\t')

    # if any(' ' in colName for colName in colNames):
    #    raise InvalidFormatError('Error in column specification line: %s ' % repr(line) +
    #                             'Please separate columns by tab, not space.')

    colNames = [(col if col not in ALL_STD_COL_NAMES else col)
                for col in colNames]

    for colName in colNames:
        if colNames.count(colName) > 1:
            raise InvalidFormatError('Column "%s" appears multiple times in the ' % colName +
                                     'column specification line.')

    if colNames[0] == '':
        raise InvalidFormatError('Column specification line requires at least one'
                                 'column (the "uri" column), but none is specified.')

    if colNames[0] != URI_COL:
        raise InvalidFormatError('The first column must be "%s", not "%s".' %
                                 (URI_COL, colNames[0]))

    if any(colName.strip() == '' for colName in colNames):
        raise InvalidFormatError('Empty column names are not allowed.')

    curOptStdColIdx = -1
    nonStdColsFound = []
    for colName in colNames[1:]:
        if colName in OPTIONAL_STD_COL_NAMES:
            nextOptStdColIdx = OPTIONAL_STD_COL_NAMES.index(colName)

            if nonStdColsFound:
                raise InvalidFormatError('Non-standard columns "%s" ' % ', '.join(nonStdColsFound)
                                         + 'encountered before standard column "%s".' % colName)
            elif nextOptStdColIdx <= curOptStdColIdx:
                raise InvalidFormatError('Standard columns are not in the correct order: '
                                         '%s.' % ', '.join('"%s"' % col for col in
                                                           OPTIONAL_STD_COL_NAMES))

            curOptStdColIdx = nextOptStdColIdx
        else:
            if urlDecodePhrase(colName) != colName:
                raise InvalidFormatError('Column names in GSuite do not support URL escaping. '
                                         'Offending column name: "{}"'.format(colName))
            nonStdColsFound.append(colName)

    return colNames


def _getDefaultColNames():
    return [URI_COL]


#
# Genome specification line, e.g.: "####genome=hg18"
#
# Deprecated, but kept for backwards compability
#

def _parseGenomeLine(line):
    genomeLine = line[4:]
    splitLine = genomeLine.split('=')

    if len(splitLine) != 2:
        raise InvalidFormatError('Genome line not understood: ' + repr(genomeLine))

    key, genome = [_.strip() for _ in splitLine]
    genome = urlDecodePhrase(genome)
    key = key.lower()

    if key != 'genome':
        raise InvalidFormatError('Key in genome line is not "genome": ' + key)

    return genome


#
# Track line, e.g.: "http://server/file.bed\tMy track title\tcMyb"
#

def _popValueFromColValsAndNamesIfPresent(colVals, colNames, colName):
    if colName in colNames:
        retVal = colVals.pop(colNames.index(colName))
        colNames.remove(colName)
        return retVal


def _parseTrackLine(trackLine, colNames, headerVars):
    colVals = trackLine.split('\t')

    if len(colVals) != len(colNames):
        raise InvalidFormatError('The number of columns in track line: %s ' % (repr(trackLine)) +
                                 'is not equal to the number of columns in the '
                                 'column specification line (%s != %s)' %
                                 (len(colVals), len(colNames)))

    from copy import copy
    remainingColNames = copy(colNames)

    assert colNames[0] == URI_COL
    kwArgs = {}
    for colSpec in ALL_STD_COL_SPECS:
        val = _popValueFromColValsAndNamesIfPresent(colVals, remainingColNames, colSpec.colName)
        if val is not None:
            kwArgs[colSpec.memberName] = val
        elif colSpec.headerName in headerVars:
            if headerVars[colSpec.headerName] != MULTIPLE:
                kwArgs[colSpec.memberName] = headerVars[colSpec.headerName]

    attributes = OrderedDict(zip(remainingColNames, colVals))
    for key, val in attributes.iteritems():
        if val == '.':
            del attributes[key]
    kwArgs['attributes'] = attributes

    try:
        track = GSuiteTrack(**kwArgs)
    except InvalidFormatError as e:
        errorMsg = 'Error in track line %s:\n' % repr(trackLine) + e.message
        raise InvalidFormatError(errorMsg)

    return track


#
# Helper functions
#

def _setLevelAndCheckOrder(oldLevel, newLevel):
    if newLevel < oldLevel:
        if oldLevel == 5:
            raise InvalidFormatError('Header line after data line is not allowed.')
        else:
            raise InvalidFormatError('Header type "%s" after type "%s" is not allowed.' %
                                     ('#' * newLevel, '#' * oldLevel))

    if newLevel == oldLevel == 4:
        raise InvalidFormatError('Double genome lines are not allowed.')

    if newLevel == oldLevel == 3:
        raise InvalidFormatError('Double column specification lines are not allowed.')

    return newLevel


def _checkCharUsageOfPhrase(phrase):
    for char in phrase:
        if char not in ALLOWED_CHARS:
            raise InvalidFormatError("Error: Character %s is not allowed in GSuite file. " %
                                     repr(char) + "Offending phrase: %s" % repr(phrase))


#
# GSuiteParser
#

def parseLines(gSuiteLines, allowTrackSummaryToOverrideHeaders=True):
    """
    :return GSuite:
    """
    colNames = None
    headerVars = {}

    gSuite = GSuite()

    trackLines = []
    level = 0
    for line in gSuiteLines:

        line = line.rstrip(' \t\r\n')

        _checkCharUsageOfPhrase(line)

        if line.startswith('####'):  # Deprecated, but kept for backwards compatibility
            level = _setLevelAndCheckOrder(level, 4)
            headerVars[GENOME_HEADER] = _parseGenomeLine(line)
        elif line.startswith('###'):
            level = _setLevelAndCheckOrder(level, 3)
            colNames = _parseColumnSpecLine(line)
        elif line.startswith('##'):
            level = _setLevelAndCheckOrder(level, 2)
            key, val = _parseHeaderLine(line)
            headerVars = _updateHeaderVars(headerVars, key, val)
        elif line == '' or line.startswith('#'):
            pass
        else:
            level = _setLevelAndCheckOrder(level, 5)
            trackLines.append(line)

    # headerVars = _updateUnsetHeaderVarsWithDefaultVals(headerVars)
    if not colNames:
        colNames = _getDefaultColNames()

    for trackLine in trackLines:
        gSuite.addTrack(_parseTrackLine(trackLine, colNames, headerVars),
                        allowDuplicateTitles=False)

    _setCustomHeaders(gSuite, headerVars)

    if not allowTrackSummaryToOverrideHeaders:
        _compareTextHeadersWithTrackSummaryHeaders(headerVars, gSuite)

    return gSuite


def parseFromString(gSuiteStr, allowTrackSummaryToOverrideHeaders=True):
    """
    :return GSuite:
    """
    return parseLines(gSuiteStr.split('\n'), allowTrackSummaryToOverrideHeaders)


def parse(gSuiteFileName, allowTrackSummaryToOverrideHeaders=True):
    """
    :return GSuite:
    """
    with open(gSuiteFileName) as gSuiteFileHandle:
        gSuite = parseLines(gSuiteFileHandle, allowTrackSummaryToOverrideHeaders)

    return gSuite


def validateLines(gSuiteLines, outFile=None, printHelpText=True,
                  allowTrackSummaryToOverrideHeaders=False):
    """
    :return bool: True if GSuite file is valid, else False
    """
    out = outFile if outFile is not None else StringIO()

    if printHelpText:
        print >>out, 'Validating GSuite file...'
        print >>out, '-----------------'

    try:
        parseLines(gSuiteLines, allowTrackSummaryToOverrideHeaders)
        valid = True
        print >>out, 'GSuite file is valid'

    except Exception, e:
        if printHelpText:
            print >>out, e
            print >>out, '-----------------'
            print >>out, 'GSuite file is invalid'
        else:
            print >>out, 'GSuite file is invalid. Error: ', e
        valid = False

    if outFile is None:
        print out.getvalue()

    return valid


def validateFromString(gSuiteStr, outFile=None, printHelpText=True,
                       allowTrackSummaryToOverrideHeaders=False):
    """
    :return bool: True if GSuite file is valid, else False
    """
    valid = validateLines(
        gSuiteStr.split('\n'), outFile,
        printHelpText=printHelpText,
        allowTrackSummaryToOverrideHeaders=allowTrackSummaryToOverrideHeaders)

    return valid


def validate(gSuiteFileName, outFile=None, printHelpText=True,
             allowTrackSummaryToOverrideHeaders=False):
    """
    :return bool: True if GSuite file is valid, else False
    """
    with open(gSuiteFileName) as gSuiteFileHandle:
        valid = validateLines(
            gSuiteFileHandle, outFile,
            printHelpText=printHelpText,
            allowTrackSummaryToOverrideHeaders=allowTrackSummaryToOverrideHeaders)

    return valid
