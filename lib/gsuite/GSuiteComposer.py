from collections import OrderedDict
from cStringIO import StringIO

from gsuite.GSuiteConstants import HEADER_VAR_DICT, URI_COL_SPEC, TITLE_COL, \
                                        OPTIONAL_STD_COL_SPECS
from proto.CommonFunctions import ensurePathExists, formatPhraseWithCorrectChrUsage


def _composeHeaders(gSuite, out):
    for headerKey, headerVal in _getAllHeadersToPrint(gSuite):
        print >> out, '##%s: %s' % (headerKey, formatPhraseWithCorrectChrUsage(headerVal))


def _getAllHeadersToPrint(gSuite):
    for headerKey, headerSpec in HEADER_VAR_DICT.iteritems():
        if not headerSpec.deprecated:
            headerVal = getattr(gSuite, headerSpec.memberName)
            yield (headerKey, headerVal)
    for headerKey, headerVal in gSuite.customHeaders.iteritems():
        yield (headerKey, headerVal)


def _findAllCols(gSuite):
    # Both colSpecs and attributes are used as ordered sets
    colSpecs = OrderedDict([(URI_COL_SPEC, None)])
    attributes = OrderedDict()

    for colSpec in OPTIONAL_STD_COL_SPECS:
        if not colSpec.deprecated:
            for track in gSuite.allTracks():
                trackColVal = getattr(track, colSpec.memberName)
                if colSpec.colName == TITLE_COL:
                    colSpecs[colSpec] = None
                else:  # Only headers left
                    if trackColVal != HEADER_VAR_DICT[colSpec.headerName].default \
                            and trackColVal != getattr(gSuite, colSpec.memberName) \
                            and colSpec not in colSpecs:
                        colSpecs[colSpec] = None
                        break

                attributes.update(track.attributes)

    return colSpecs, attributes.keys()


def _composeColSpecLine(colSpecs, attributes, out):
    allCols = [colSpec.colName for colSpec in colSpecs] + attributes
    if len(allCols) > 1:
        print >>out, '###' + '\t'.join(allCols)


def _composeTrackLines(gSuite, colSpecs, attributes, out):
    for track in gSuite.allTracks():
        if track.comment:
            print >>out, '#' + track.comment
        
        cells = [formatPhraseWithCorrectChrUsage(getattr(track, colSpec.memberName))
                 for colSpec in colSpecs]
        for attribute in attributes:
            if attribute in track.attributes:
                cells.append(formatPhraseWithCorrectChrUsage(track.attributes[attribute]))
            else:
                cells.append('.')

        print >>out, '\t'.join(cells)


def _composeCommon(gSuite, out):
    _composeHeaders(gSuite, out)

    colSpecs, attributes = _findAllCols(gSuite)
    _composeColSpecLine(colSpecs, attributes, out)
    _composeTrackLines(gSuite, colSpecs, attributes, out)

    return True


def composeToString(gSuite):
    memFile = StringIO()
    _composeCommon(gSuite, memFile)
    return memFile.getvalue()


def composeToFile(gSuite, outFileName):
    ensurePathExists(outFileName)
    with open(outFileName, 'w') as out:
        ok = _composeCommon(gSuite, out)

    return ok
