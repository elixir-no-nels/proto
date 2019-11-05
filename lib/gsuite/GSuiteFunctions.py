import os

from gsuite.GSuiteConstants import LOCAL, REMOTE, UNKNOWN, PRIMARY, COMPRESSION_SUFFIXES, \
    PREPROCESSED
from gsuite.GSuiteRequirements import GSuiteRequirements
from gsuite.GSuiteTrack import GSuiteTrack, SearchQueryForSuffixGSuiteTrack
from proto.CommonFunctions import getFileSuffix, stripFileSuffix


def splitTitleIfDuplicate(title):
    import re
    duplicateMatch = re.match('.*( \([0-9]+\))$', title)
    if duplicateMatch:
        duplicateStr = duplicateMatch.groups()[0]
        title = title[:-len(duplicateStr)]
        return title, duplicateStr
    else:
        return title, ''


def getDuplicateIdx(title):
    duplicateStr = splitTitleIfDuplicate(title)[1]
    if duplicateStr:
        import re
        countMatch = re.match(' \(([0-9])+\)$', duplicateStr)
        return int(countMatch.groups()[0])
    else:
        return 1


def renameBaseFileNameWithDuplicateIdx(baseFileName, duplicateIdx):
    if duplicateIdx == 1:
        return baseFileName
    else:
        suffixes = []
        while True:
            suffix = getFileSuffix(baseFileName)
            if suffix:
                suffixes.insert(0, suffix)
                baseFileName = baseFileName[:-len('.' + suffix)]
            else:
                break

        return baseFileName + '_%s' % duplicateIdx + \
            (('.' + '.'.join(suffixes)) if suffixes else '')


def changeSuffixIfPresent(text, oldSuffix=None, newSuffix=None):
    assert newSuffix
    prefix, suffix = os.path.splitext(text)

    if suffix and (oldSuffix is None or suffix == '.' + oldSuffix):
        return prefix + '.' + newSuffix
    else:
        return text


def getTitleSuffix(title):
    return getFileSuffix(splitTitleIfDuplicate(title)[0])


def getTitleWithSuffixReplaced(title, newSuffix):
    titleSuffix = getTitleSuffix(title)
    if titleSuffix:
        rawTitle, duplicateStr = splitTitleIfDuplicate(title)
        rawTitle = stripFileSuffix(rawTitle) + (('.' + newSuffix) if newSuffix else '')
        title = rawTitle + duplicateStr

    return title


def getTitleAndSuffixWithCompressionSuffixesRemoved(gSuiteTrack):
    gSuiteReq = GSuiteRequirements(allowedLocations=[LOCAL, REMOTE],
                                   allowedFileFormats=[PREPROCESSED, PRIMARY, UNKNOWN])
    gSuiteReq.check(gSuiteTrack)

    title, suffix, path = gSuiteTrack.title, gSuiteTrack.suffix, gSuiteTrack.path

    if suffix:
        for compSuffix in COMPRESSION_SUFFIXES:
            reduceLen = len(compSuffix)+1

            if suffix.lower() == compSuffix:
                if path.endswith('.' + compSuffix):
                    path = path[:-reduceLen]
                    suffix = getFileSuffix(path)
                else:
                    if isinstance(gSuiteTrack, SearchQueryForSuffixGSuiteTrack):
                        tempGSuiteTrack = \
                            GSuiteTrack(gSuiteTrack.uri.replace('.' + compSuffix, ''), title='')
                        suffix = tempGSuiteTrack.suffix
                    else:
                        suffix = None  # Impossible to find uncompressed suffix
            elif suffix.lower().endswith('.' + compSuffix):
                suffix = suffix[:-reduceLen]  # e.g. suffix = 'bed.gz' -> 'bed'
            else:
                continue

            title = getTitleWithSuffixReplaced(title, '')
            break

    return title, suffix


def getTitleWithCompressionSuffixesRemoved(gSuiteTrack):
    return getTitleAndSuffixWithCompressionSuffixesRemoved(gSuiteTrack)[0]


def getSuffixWithCompressionSuffixesRemoved(gSuiteTrack):
    return getTitleAndSuffixWithCompressionSuffixesRemoved(gSuiteTrack)[1]
