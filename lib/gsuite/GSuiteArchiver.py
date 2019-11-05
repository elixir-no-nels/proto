import os
import tarfile

from abc import ABCMeta, abstractmethod
from collections import OrderedDict
from zipfile import ZipFile

from gsuite.GSuite import GSuite
# from gold.gsuite.GSuiteConstants import ARCHIVE_SUFFIXES
from gsuite.GSuiteTrack import GSuiteTrack, GalaxyGSuiteTrack
from gsuite.CustomExceptions import NotSupportedError
from proto.CommonFunctions import ensurePathExists


class ArchivedFileInfo(object):
    def __init__(self, internalFn):
        head, tail = os.path.split(internalFn)
        dirs = head.split(os.path.sep)

        self.path = internalFn

        self.directories = dirs if dirs != [''] else []
        if '' in self.directories:
            raise NotSupportedError('Absolute paths (starting with "/") or empty directory '
                                    'names not supported for internal file names in archive.')

        self.baseFileName = tail


class ArchiveReader(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def __init__(self, archiveFn):
        pass

    @abstractmethod
    def __iter__(self):
        pass

    @abstractmethod
    def openFile(self, internalFn):
        pass


class ZipArchiveReader(ArchiveReader):
    def __init__(self, archiveFn):
        self._archive = ZipFile(archiveFn)

    def __iter__(self):
        for internalFn in self._archive.namelist():
            if not internalFn.endswith(os.path.sep):  # not directory
                yield ArchivedFileInfo(internalFn)

    def openFile(self, internalFn):
        return self._archive.open(internalFn, 'r')


class TarArchiveReader(ArchiveReader):
    def __init__(self, archiveFn):
        self._archive = tarfile.open(archiveFn, 'r')

    def __iter__(self):
        for tarinfo in self._archive:
            if tarinfo.isfile():
                yield ArchivedFileInfo(tarinfo.name)

    def openFile(self, internalFn):
        return self._archive.extractfile(internalFn)


class ArchiveToGalaxyGSuiteTrackIterator(object):
    def __init__(self, archive, galaxyFn, storeHierarchy=False):
        self._archive = archive
        self._galaxyFn = galaxyFn
        # self._titleToGalaxyFnDict = titleToGalaxyFnDict
        self._storeHierarchy = storeHierarchy

    def __iter__(self):
        for archivedFileInfo in self._archive:
            # galaxyFn = self._titleToGalaxyFnDict.get(archivedFileInfo.title)
            # if not galaxyFn:
            #     raise ShouldNotOccurError('Galaxy filename not found for file with title: ' +
            #                               archivedFile.title)

            extraFileName = os.sep.join((archivedFileInfo.directories
                                         if self._storeHierarchy else []) +
                                        [archivedFileInfo.baseFileName])

            if self._storeHierarchy:
                attributeList = OrderedDict([('dir_level_%s' % (i+1), directory)
                                             for i, directory in
                                             enumerate(archivedFileInfo.directories)])
            else:
                attributeList = OrderedDict()
            
            uri = GalaxyGSuiteTrack.generateURI(self._galaxyFn, extraFileName=extraFileName)
            gSuiteTrack = GSuiteTrack(uri, title=archivedFileInfo.baseFileName,
                                      attributes=attributeList)

            outFn = gSuiteTrack.path
            ensurePathExists(outFn)
            with open(outFn, 'w') as outFile:
                inFile = self._archive.openFile(archivedFileInfo.path)
                outFile.write(inFile.read())
                inFile.close()

            yield gSuiteTrack


def convertArchiveToGSuite(archiveToGSuiteIterator, progressViewer=None):
    gSuite = GSuite()
    for gSuiteTrack in archiveToGSuiteIterator:
        gSuite.addTrack(gSuiteTrack)
        if progressViewer:
                progressViewer.update()
    
    return gSuite
