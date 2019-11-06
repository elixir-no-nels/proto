from gsuite import GSuiteConstants
from proto.HtmlCore import HtmlCore
from proto.tools.GeneralGuiTool import GeneralGuiTool
from gsuite.CustomExceptions import ShouldNotOccurError
from proto.CommonFunctions import getGSuiteHistoryOutputName, extractFileSuffixFromDatasetInfo, \
    extractFnFromDatasetInfo, writeGSuiteHiddenTrackStorageHtml


# This is a template prototyping GUI that comes together with a corresponding
# web page.

class CompileGSuiteFromArchiveTool(GeneralGuiTool):
    GSUITE_OUTPUT_LOCATION = GSuiteConstants.LOCAL
    GSUITE_OUTPUT_FILE_FORMAT = GSuiteConstants.PRIMARY
    GSUITE_OUTPUT_TRACK_TYPE = GSuiteConstants.UNKNOWN

    @staticmethod
    def getToolName():
        '''
        Specifies a header of the tool, which is displayed at the top of the
        page.
        '''
        return "Compile GSuite from archive (Zip/tar)"

    @staticmethod
    def getInputBoxNames():
        '''
        Specifies a list of headers for the input boxes, and implicitly also the
        number of input boxes to display on the page. The returned list can have
        two syntaxes:

            1) A list of strings denoting the headers for the input boxes in
               numerical order.
            2) A list of tuples of strings, where each tuple has
               two items: a header and a key.

        The contents of each input box must be defined by the function
        getOptionsBoxK, where K is either a number in the range of 1 to the
        number of boxes (case 1), or the specified key (case 2).

        Note: the key has to be camelCase (e.g. "firstKey")
        '''
        return [('', 'basicQuestionId'), \
                ('Select history element with archive file', 'archive'), \
                ('Keep directory hierarchy intact and present as columns in the GSuite file?', 'storeHierarchy')]

    #@staticmethod
    #def getInputBoxOrder():
    #    '''
    #    Specifies the order in which the input boxes should be displayed, as a
    #    list. The input boxes are specified by index (starting with 1) or by
    #    key. If None, the order of the input boxes is in the order specified by
    #    getInputBoxNames.
    #    '''
    #    return None

    @staticmethod
    def getOptionsBoxBasicQuestionId():
        return '__hidden__', None

    @staticmethod
    def getOptionsBoxArchive(prevChoices): # Alternatively: getOptionsBox1()
        '''
        Defines the type and contents of the input box. User selections are
        returned to the tools in the prevChoices and choices attributes to other
        methods. These are lists of results, one for each input box (in the
        order specified by getInputBoxOrder()).

        The input box is defined according to the following syntax:

        Selection box:          ['choice1','choice2']
        - Returns: string

        Text area:              'textbox' | ('textbox',1) | ('textbox',1,False)
        - Tuple syntax: (contents, height (#lines) = 1, read only flag = False)
        - The contents is the default value shown inside the text area
        - Returns: string

        Password field:         '__password__'
        - Returns: string

        Genome selection box:   '__genome__'
        - Returns: string

        Track selection box:    '__track__'
        - Requires genome selection box.
        - Returns: colon-separated string denoting track name

        History selection box:  ('__history__',) | ('__history__', 'bed', 'wig')
        - Only history items of specified types are shown.
        - Returns: colon-separated string denoting galaxy track name, as
                   specified in ExternalTrackManager.py.

        History check box list: ('__multihistory__', ) | ('__multihistory__', 'bed', 'wig')
        - Only history items of specified types are shown.
        - Returns: OrderedDict with galaxy id as key and galaxy track name
                   as value if checked, else None.

        Hidden field:           ('__hidden__', 'Hidden value')
        - Returns: string

        Table:                  [['header1','header2'], ['cell1_1','cell1_2'], ['cell2_1','cell2_2']]
        - Returns: None

        Check box list:         OrderedDict([('key1', True), ('key2', False), ('key3', False)])
        - Returns: OrderedDict from key to selection status (bool).
        '''
        return '__history__', 'gsuite.tar', 'gsuite.zip'

    @staticmethod
    def getOptionsBoxStoreHierarchy(prevChoices): # Alternatively: getOptionsBox2()
        '''
        See getOptionsBoxFirstKey().

        prevChoices is a namedtuple of selections made by the user in the
        previous input boxes (that is, a namedtuple containing only one element
        in this case). The elements can accessed either by index, e.g.
        prevChoices[0] for the result of input box 1, or by key, e.g.
        prevChoices.key (case 2).
        '''
        return ['Yes', 'No']

    #@staticmethod
    #def getOptionsBox3(prevChoices):
    #    return ['']

    #@staticmethod
    #def getOptionsBox4(prevChoices):
    #    return ['']

    #@staticmethod
    #def getInfoForOptionsBoxKey(prevChoices):
    #    '''
    #    If not None, defines the string content of an clickable info box beside
    #    the corresponding input box. HTML is allowed.
    #    '''
    #    return None

    #@staticmethod
    #def getDemoSelections():
    #    return ['testChoice1','..']

    @classmethod
    def _getArchiveReader(cls, choices):
        from gsuite.GSuiteArchiver import TarArchiveReader, ZipArchiveReader
        suffix = extractFileSuffixFromDatasetInfo(choices.archive)
        fn = extractFnFromDatasetInfo(choices.archive)

        if suffix == 'gsuite.tar':
            return TarArchiveReader(fn)
        elif suffix == 'gsuite.zip':
            return ZipArchiveReader(fn)
        else:
            raise ShouldNotOccurError()

    @classmethod
    def getExtraHistElements(cls, choices):
        from proto.tools.GeneralGuiTool import HistElement
        from gsuite.GSuiteConstants import GSUITE_STORAGE_SUFFIX, GSUITE_SUFFIX

        desc = cls._getOutputHistoryDescription(choices)
        fileList = [HistElement(getGSuiteHistoryOutputName('primary', desc), GSUITE_SUFFIX),
                    HistElement(getGSuiteHistoryOutputName('storage', desc),
                                    GSUITE_STORAGE_SUFFIX, hidden=True)]

        # if choices.archive:
            #for archivedFile in cls._getArchiveReader(choices):
            #    fileList.append( HistElement(archivedFile.title, archivedFile.suffix, hidden=True) )

        return fileList

    @classmethod
    def execute(cls, choices, galaxyFn=None, username=''):
        '''
        Is called when execute-button is pushed by web-user. Should print
        output as HTML to standard out, which will be directed to a results page
        in Galaxy history. If getOutputFormat is anything else than HTML, the
        output should be written to the file with path galaxyFn. If needed,
        StaticFile can be used to get a path where additional files can be put
        (e.g. generated image files). choices is a list of selections made by
        web-user in each options box.
        '''

        from gsuite.GSuiteArchiver import ArchiveToGalaxyGSuiteTrackIterator, \
                                               convertArchiveToGSuite
        import gsuite.GSuiteComposer as GSuiteComposer
        # from quick.extra.ProgressViewer import ProgressViewer

        # DebugUtil.insertBreakPoint(username=username, currentUser='boris.simovski@gmail.com')

        archive = cls._getArchiveReader(choices)
        trackCount = sum(1 for file in archive)

        desc = cls._getOutputHistoryDescription(choices)
        # progressViewer = ProgressViewer([('Extract tracks', trackCount)], galaxyFn)

        storeHierarchy = choices.storeHierarchy == 'Yes'
        hiddenStorageFn = cls.extraGalaxyFn[getGSuiteHistoryOutputName('storage', desc)]
        archiveToGSuiteTrackIter = \
            ArchiveToGalaxyGSuiteTrackIterator(archive, hiddenStorageFn, storeHierarchy)
        writeGSuiteHiddenTrackStorageHtml(hiddenStorageFn)

        gSuite = convertArchiveToGSuite(archiveToGSuiteTrackIter)

        GSuiteComposer.composeToFile(gSuite,
            cls.extraGalaxyFn[getGSuiteHistoryOutputName('primary', desc)])

    @classmethod
    def validateAndReturnErrors(cls, choices):
        '''
        Should validate the selected input parameters. If the parameters are not
        valid, an error text explaining the problem should be returned. The GUI
        then shows this text to the user (if not empty) and greys out the
        execute button (even if the text is empty). If all parameters are valid,
        the method should return None, which enables the execute button.
        '''

        if not choices.archive:
            return 'Please select an archive file in your history with file type "gsuite.tar" or "gsuite.zip"'

    @classmethod
    def _getOutputHistoryDescription(cls, choices):
        from proto.CommonFunctions import extractNameFromDatasetInfo
        return 'extracted from archive: ' + extractNameFromDatasetInfo(choices.archive) \
            if choices.archive else ''

    @classmethod
    def getOutputName(cls, choices):
        description = cls._getOutputHistoryDescription(choices)
        return getGSuiteHistoryOutputName('progress', description)

    #@staticmethod
    #def getSubToolClasses():
    #    '''
    #    Specifies a list of classes for subtools of the main tool. These
    #    subtools will be selectable from a selection box at the top of the page.
    #    The input boxes will change according to which subtool is selected.
    #    '''
    #    return None
    #
    @staticmethod
    def isPublic():
        '''
        Specifies whether the tool is accessible to all users. If False, the
        tool is only accessible to a restricted set of users as defined in
        LocalOSConfig.py.
        '''
        return True

    #@staticmethod
    #def isRedirectTool():
    #    '''
    #    Specifies whether the tool should redirect to an URL when the Execute
    #    button is clicked.
    #    '''
    #    return False
    #
    #@staticmethod
    #def getRedirectURL(choices):
    #    '''
    #    This method is called to return an URL if the isRedirectTool method
    #    returns True.
    #    '''
    #    return ''
    #
    #@staticmethod
    #def isHistoryTool():
    #    '''
    #    Specifies if a History item should be created when the Execute button is
    #    clicked.
    #    '''
    #    return True
    #
    #@staticmethod
    #def isDynamic():
    #    '''
    #    Specifies whether changing the content of texboxes causes the page to
    #    reload.
    #    '''
    #    return True
    #
    #@staticmethod
    #def getResetBoxes():
    #    '''
    #    Specifies a list of input boxes which resets the subsequent stored
    #    choices previously made. The input boxes are specified by index
    #    (starting with 1) or by key.
    #    '''
    #    return []
    #
    @classmethod
    def getToolDescription(cls):
        '''
        Specifies a help text in HTML that is displayed below the tool.
        '''

        core = HtmlCore()
        core.paragraph('This tool creates a new GSuite file based upon the contents of an '
                       'archive file. Currently, the tool supports ".tar" (with and without '
                       '".gz") and ".zip" files. To use the tool, please upload an archive file '
                       'to your history using the Galaxy import tool (click the icon to the right '
                       'of the "Tools" header in the top left of the window). You will need to '
                       'manually select the file type as "gsuite.zip" or "gsuite.tar", as '
                       'described below. After uploading, you then open this tool, select the '
                       'archive, and click "Execute".')
        core.divider()
        core.smallHeader('* IMPORTANT *')
        core.paragraph(str(HtmlCore().emphasize(
                       'In order to circumvent Galaxy\'s integrated archive decompresssion (which '
                       'for zip files only extracts a single file), you must manually select '
                       '"gsuite.tar" or "gsuite.zip" in the "Type" column in the upload file '
                       'dialog box.')))
        core.divider()
        core.smallHeader('Keep directory hierarchy intact and present as columns in the GSuite '
                         'file?')
        core.paragraph('By default, any directory structure in the archive is kept intact in '
                       'the file path in the URIs in the output GSuite file. In addition, one '
                       'column is added per level in the directory hierarchy, with the values '
                       'denoting the directory where the file resides. In this way, one can '
                       'make use of the directory structure as metadata categories. Optionally, '
                       'one can ignore the hierarchy, flattening the archive into a single '
                       'directory level, with no extra columns added.')

        cls._addGSuiteFileDescription(core,
                                      outputLocation=cls.GSUITE_OUTPUT_LOCATION,
                                      outputFileFormat=cls.GSUITE_OUTPUT_FILE_FORMAT,
                                      outputTrackType=cls.GSUITE_OUTPUT_TRACK_TYPE,
                                      errorFile=False)

        return str(core)
    #
    #@staticmethod
    #def getToolIllustration():
    #    '''
    #    Specifies an id used by StaticFile.py to reference an illustration file
    #    on disk. The id is a list of optional directory names followed by a file
    #    name. The base directory is STATIC_PATH as defined by Config.py. The
    #    full path is created from the base directory followed by the id.
    #    '''
    #    return None
    #
    #@staticmethod
    #def getFullExampleURL():
    #    return None
    #
    #@classmethod
    #def isBatchTool(cls):
    #    '''
    #    Specifies if this tool could be run from batch using the batch. The
    #    batch run line can be fetched from the info box at the bottom of the
    #    tool.
    #    '''
    #    return cls.isHistoryTool()
    #
    #@staticmethod
    #def isDebugMode():
    #    '''
    #    Specifies whether debug messages are printed.
    #    '''
    #    return False
    #
    @staticmethod
    def getOutputFormat(choices):
        '''
        The format of the history element with the output of the tool. Note
        that html output shows print statements, but that text-based output
        (e.g. bed) only shows text written to the galaxyFn file.In the latter
        case, all all print statements are redirected to the info field of the
        history item box.
        '''
        return 'customhtml'
