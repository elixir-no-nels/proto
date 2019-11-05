import os
import re
import urllib
from collections import OrderedDict
from numbers import Number

from proto.CommonConstants import THOUSANDS_SEPARATOR, ALLOWED_CHARS
from proto.config.Config import OUTPUT_PRECISION
from proto.config.Security import galaxySecureEncodeId, galaxySecureDecodeId, \
    GALAXY_SECURITY_HELPER_OBJ

"""
Note on datasetInfo and datasetId (used in several functions):

DatasetInfo is an especially coded list of strings, used mainly to process
files from galaxy history, but can also be used otherwise. Structure is:
['galaxy', fileEnding, datasetFn, name]. The first element is used for
assertion. The second element contains the file format (as galaxy force
the ending '.dat'). datasetFn is the dataset file name, typically ending
with 'XXX/dataset_YYYY.dat', where XXX and YYYY are numbers which may be
extracted and used as a datasetId in the form [XXX, YYYY]. The last element
is the name of the history element, mostly used for presentation purposes.
"""


def getFileSuffix(fn):
    return os.path.splitext(fn)[1].replace('.', '')


def stripFileSuffix(fn):
    suffix = getFileSuffix(fn)
    return fn[:-len(suffix)-1]


def ensurePathExists(fn):
    "Assumes that fn consists of a basepath (folder) and a filename, and ensures that the folder exists."
    path = os.path.split(fn)[0]

    if not os.path.exists(path):
        #oldMask = os.umask(0002)
        os.makedirs(path)
        #os.umask(oldMask)


def extractIdFromGalaxyFn(fn):
    '''
    Extracts the Galaxy history ID from a history file path, e.g.:

    '/path/to/001/dataset_00123.dat' -> ['001', '00123']

    For files related to a Galaxy history (e.g. dataset_00123_files):

    '/path/to/001/dataset_00123_files/myfile/myfile.bed' -> ['001', '00123', 'myfile']

    Also, if the input is a run-specific file, the history and batch ID, is also extracted, e.g.:

    '/path/to/dev2/001/00123/0/somefile.bed' -> ['001', '00123', '0']
    '''
    #'''For temporary Galaxy files:
    #
    #/path/to/tmp/primary_49165_wgEncodeUmassDekker5CEnmPrimer.doc.tgz_visible_.doc.tgz -> '49165'
    #'''

    pathParts = fn.split(os.sep)
    assert len(pathParts) >= 2, pathParts

    if fn.endswith('.dat'):
        id1 = pathParts[-2]
        id2 = re.sub('[^0-9]', '', pathParts[-1])
        id = [id1, id2]
    elif any(part.startswith('dataset_') and part.endswith('_files') for part in pathParts):
        extraIds = []
        for i in range(len(pathParts)-1, 0, -1):
            part = pathParts[i-1]
            if part.startswith('dataset_') and part.endswith('_files'):
                id2 = re.sub('[^0-9]', '', part)
                id1 = pathParts[i-2]
                break
            else:
                extraIds = [part] + extraIds
        id = [id1, id2] + extraIds
    #elif os.path.basename(fn).startswith('primary'):
    #    basenameParts = os.path.basename(fn).split('_')
    #    assert len(basenameParts) >= 2
    #    id = basenameParts[1] # id does not make sense. Removed for now, revise if needed.
    else: #For run-specific files
        for i in range(len(pathParts)-2, 0, -1):
            if not pathParts[i].isdigit():
                id = pathParts[i+1:-1]
                assert len(id) >= 2, 'Could not extract id from galaxy filename: ' + fn
                break

    return id


def createFullGalaxyIdFromNumber(num):
    num = int(num)
    id2 = str(num)
    id1 =  '%03d' % (num / 1000)
    return [id1, id2]


def getGalaxyFnFromDatasetId(num, galaxyFilePath=None):
    if not galaxyFilePath:
        from proto.config.Config import GALAXY_FILE_PATH
        galaxyFilePath = GALAXY_FILE_PATH

    id1, id2 = createFullGalaxyIdFromNumber(num)
    return os.path.join(galaxyFilePath, id1, 'dataset_%s.dat' % id2)


def getEncodedDatasetIdFromPlainGalaxyId(plainId):
    return galaxySecureEncodeId(plainId)


def getEncodedDatasetIdFromGalaxyFn(galaxyFn):
    plainId = extractIdFromGalaxyFn(galaxyFn)[1]
    return getEncodedDatasetIdFromPlainGalaxyId(plainId)


def getGalaxyFnFromEncodedDatasetId(encodedId, galaxyFilePath=None):
    plainId = galaxySecureDecodeId(encodedId)
    return getGalaxyFnFromDatasetId(plainId, galaxyFilePath=galaxyFilePath)


def getGalaxyFnFromAnyDatasetId(id, galaxyFilePath=None):
    try:
        return getGalaxyFnFromEncodedDatasetId(id,
                                               galaxyFilePath=galaxyFilePath)
    except:
        return getGalaxyFnFromDatasetId(id, galaxyFilePath=galaxyFilePath)


def getGalaxyFilesDir(galaxyFn):
    return galaxyFn[:-4] + '_files'


def getGalaxyFilesFilename(galaxyFn, id):
    """
    id is the relative file hierarchy, encoded as a list of strings
    """
    return os.path.sep.join([getGalaxyFilesDir(galaxyFn)] + id)


def getGalaxyFilesFnFromEncodedDatasetId(encodedId):
    galaxyFn = getGalaxyFnFromEncodedDatasetId(encodedId)
    return getGalaxyFilesDir(galaxyFn)


def createGalaxyFilesFn(galaxyFn, filename):
    return os.path.sep.join([getGalaxyFilesDir(galaxyFn), filename])


def createGalaxyFilesFn(galaxyFn, filename):
    return os.path.sep.join(
        [getGalaxyFilesDir(galaxyFn), filename])


def extractFnFromDatasetInfo(datasetInfo):
    if isinstance(datasetInfo, basestring):
        datasetInfo = datasetInfo.split(':')
    try:
        return getGalaxyFnFromEncodedDatasetId(datasetInfo[2])
    except TypeError:
        # full path, not id
        return datasetInfo[2]


def extractFileSuffixFromDatasetInfo(datasetInfo, fileSuffixFilterList=None):
    if isinstance(datasetInfo, basestring):
        datasetInfo = datasetInfo.split(':')

    suffix = datasetInfo[1]

    if fileSuffixFilterList and not suffix.lower() in fileSuffixFilterList:
        raise Exception('File type "' + suffix + '" is not supported.')

    return suffix


def extractNameFromDatasetInfo(datasetInfo):
    if isinstance(datasetInfo, basestring):
        datasetInfo = datasetInfo.split(':')

    from urllib import unquote
    return unquote(str(datasetInfo[-1])).decode('utf-8')


def getSecureIdAndExtFromDatasetInfoAsStr(datasetInfo):
        if datasetInfo and datasetInfo.startswith('galaxy'):
            sep = datasetInfo[6]
            if sep == ',':
                splitted = datasetInfo.split(',')
                id_sel = splitted[1]
                ext = splitted[2]
            else:
                splitted = datasetInfo.split(':')
                id_sel = splitted[2]
                ext = splitted[1]
        else:
            id_sel = 0
            ext = ''
        return id_sel, ext


def createToolURL(toolId, **kwArgs):
    from proto.tools.GeneralGuiTool import GeneralGuiTool
    return GeneralGuiTool.createGenericGuiToolURL(toolId, tool_choices=kwArgs)


def createGalaxyToolURL(toolId, **kwArgs):
    from proto.config.Config import URL_PREFIX
    if toolId == 'upload1':
        return "javascript:void(0)"
    return URL_PREFIX + '/tool_runner?tool_id=' + toolId + \
            ''.join(['&' + urllib.quote(key) + '=' + urllib.quote(value) for key,value in kwArgs.iteritems()])


def getGalaxyUploadLinkOnclick():
    return "event.preventDefault(); jQuery('#tool-panel-upload-button', " \
           "window.parent.jQuery(window.parent.document)).trigger('click');"


def getLoadToGalaxyHistoryURL(fn, genome='', galaxyDataType='bed', urlPrefix=None,
                              histElementName=None):
    if urlPrefix is None:
        from proto.config.Config import URL_PREFIX
        urlPrefix = URL_PREFIX

    import base64
    encodedFn = base64.urlsafe_b64encode(GALAXY_SECURITY_HELPER_OBJ.encode_guid(fn.encode('utf-8')))

    assert galaxyDataType is not None
    return urlPrefix + '/tool_runner?tool_id=file_import' + \
                       ('&dbkey=' + genome if genome else '') + \
                       '&runtool_btn=yes&input=' + encodedFn + \
                       ('&format=' + galaxyDataType if galaxyDataType is not None else '') + \
                       ('&job_name=' + histElementName if histElementName is not None else '')


def strWithStdFormatting(val, separateThousands=True, floatFormatFlag='g'):
    try:
        assert val != int(val)
        integral, fractional = (('%#.' + str(OUTPUT_PRECISION) + floatFormatFlag) % val).split('.')
    except:
        integral, fractional = str(val), None

    if not separateThousands:
        return integral + ('.' + fractional if fractional is not None else '')
    else:
        try:
            return ('-' if integral[0] == '-' else '') + \
                '{:,}'.format(abs(int(integral))).replace(',', THOUSANDS_SEPARATOR) + \
                ('.' + fractional if fractional is not None else '')
        except:
            return integral


def strWithNatLangFormatting(val, separateThousands=True):
    return strWithStdFormatting(val, separateThousands=separateThousands, floatFormatFlag='f')


def sortDictOfLists(dictOfLists, sortColumnIndex, descending=True):
    return OrderedDict(sorted(
        list(dictOfLists.iteritems()), key=lambda t: (t[1][sortColumnIndex]), reverse=descending))


def smartSortDictOfLists(dictOfLists, sortColumnIndex, descending=True):
    """Sort numbers first than strings, take into account formatted floats"""
    # convert = lambda text: int(text) if text.isdigit() else text
    # alphanum_key = lambda key: [convert(c) for c in re.split('([0-9]+)', key)]
    return OrderedDict(sorted(
        list(dictOfLists.iteritems()), key=lambda t: forceNumericSortingKey(t[1][sortColumnIndex]), reverse=descending))


def _strIsFloat(s):
    try:
        float(s)
        return True
    except:
        return False


def isNan(a):
    import numpy

    try:
        return numpy.isnan(a)
    except (TypeError, NotImplementedError):
        return False


def forceNumericSortingKey(key):
    sortKey1 = 0
    sortKey2 = key
    if isNan(key):
        return [sortKey1, sortKey2]
    if _strIsFloat(str(key).replace(THOUSANDS_SEPARATOR, '')):
        sortKey1 = 1
        sortKey2 = float(str(key).replace(THOUSANDS_SEPARATOR, ''))
    return [sortKey1, sortKey2]


def convertToDictOfLists(dataDict):
    """Convert a dict of tuples or single values to dict of lists"""
    dataDictOfLists = OrderedDict()
    for key, val in dataDict.iteritems():
        if isinstance(val, list):
            dataDictOfLists[key] = val
        elif isinstance(val, tuple):
            dataDictOfLists[key] = list(val)
        else:
            dataDictOfLists[key] = [val]
    return dataDictOfLists


def fromDictOfDictsToDictOfListsAndColumnNameList(dataDict, firstColName=''):
    colNames = []
    convertedDataDict = OrderedDict()
    for key1, val1 in dataDict.iteritems():
        if not colNames:
            colNames = [firstColName] + val1.keys()
        convertedDataDict[key1] = val1.values()
    return convertedDataDict, colNames


def isSamePath(path, otherPath):
    return os.path.abspath(path) == os.path.abspath(otherPath)


def makeUnicodeIfString(obj):
    if not isinstance(obj, basestring):
        return obj
    try:
        return obj.decode('utf-8')
    except (UnicodeDecodeError, UnicodeEncodeError, AttributeError):
        return unicode(obj)


def urlDecodePhrase(phrase, unquotePlus=False):
    if unquotePlus:
        decoded = urllib.unquote_plus(phrase)
    else:
        decoded = urllib.unquote(phrase)

    try:
        try:
            decoded.decode('ascii')
            return decoded
        except (UnicodeDecodeError, UnicodeEncodeError):
            return decoded.decode('utf-8')
    except (UnicodeDecodeError, UnicodeEncodeError):
        return decoded

def formatPhraseWithCorrectChrUsage(phrase, useUrlEncoding=True, notAllowedChars=''):
    corrected = ''
    for char in phrase:
        if char not in ALLOWED_CHARS or char in notAllowedChars:
            if useUrlEncoding:
                if isinstance(phrase, unicode):
                    char = char.encode('utf-8')
                for byte in char:
                    if not isinstance(byte, int):
                        byte = ord(byte)
                    corrected += '%' + '{:0>2X}'.format(byte)
        else:
            corrected += char
    return corrected
