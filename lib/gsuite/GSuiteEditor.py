from copy import copy
from collections import OrderedDict
from gsuite.GSuite import GSuite


def selectRowsFromGSuiteByIndex(gSuite, idxList):
    trackList = list(gSuite.allTracks())
    reducedTrackList = [trackList[i] for i in idxList]
    reducedGSuite = GSuite(trackList=reducedTrackList)
    return reducedGSuite


def selectRowsFromGSuiteByTitle(gSuite, titleList):
    reducedTrackList = [gSuite.getTrackFromTitle(title) for title in titleList]
    reducedGSuite = GSuite(trackList=reducedTrackList)
    return reducedGSuite


def selectColumnsFromGSuite(gSuite, selectedAttributes, selectTitle=True):
    reducedGSuite = GSuite()

    for attribute in selectedAttributes:
        if attribute not in gSuite.attributes:
            raise KeyError('Attribute "%s" is not defined in the GSuite file' % attribute)

    for track in gSuite.allTracks():
        reducedTrack = copy(track)
        reducedTrack.attributes = \
            OrderedDict([(key, reducedTrack.attributes[key]) for key in selectedAttributes
                         if key in reducedTrack.attributes])
        if not selectTitle:
            reducedTrack.title = reducedTrack.uri

        reducedGSuite.addTrack(reducedTrack)

    return reducedGSuite


def concatenateGSuites(gSuiteList):
    concatenatedGSuite = GSuite()

    for gSuite in gSuiteList:
        concatenatedGSuite.addTracks(gSuite.allTracks())

    return concatenatedGSuite


def concatenateGSuitesAddingCategories(gSuiteList, categoryColumnTitle, categoryList):
    concatenatedGSuite = GSuite()

    assert len(gSuiteList) == len(categoryList)
    for i, gSuite in enumerate(gSuiteList):
        tracksToAdd = [track for track in gSuite.allTracks()]

        for track in tracksToAdd:
            track.setAttribute(categoryColumnTitle, categoryList[i])

        concatenatedGSuite.addTracks(tracksToAdd)

    return concatenatedGSuite
