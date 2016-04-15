from quick.webtools.GeneralGuiTool import GeneralGuiTool
from quick.multitrack.MultiTrackCommon import getGSuiteFromGalaxyTN
from gold.gsuite.GSuiteEditor import selectRowsFromGSuiteByIndex
from gold.gsuite.GSuite import GSuite
from gold.gsuite import GSuiteComposer
from functools import partial
from gold.gsuite.GSuiteConstants import TITLE_COL
from gold.gsuite import GSuiteTrack

# This is a template prototyping GUI that comes together with a corresponding
# web page.

class EditGsuiteMetadataTool(GeneralGuiTool):
    #Defines the maximum number og dynamically generated boxes
    MAX_NUM_OF_TRACKS = 100

    @staticmethod
    def getToolName():
        '''
        Specifies a header of the tool, which is displayed at the top of the
        page.
        '''
        return "Edit a meta-data column in a GSuite"

    @classmethod
    def getInputBoxNames(cls):
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
        #Creates a drop-down list where you can choose the GSuite that you want to work with
        #Creates a drop-down list of the attributes available in the GSuite
        #Creates the MAX_NUM_OF_TRACKS amount of selectAttribute functions, here without any header
        return [('Select GSuite', 'gsuite'), \
                ('Select meta-data column to edit','attrName')] +\
                [('', 'selectAttribute%s' % i) for i \
                 in range((cls.MAX_NUM_OF_TRACKS))]

    #@staticmethod
    #def getInputBoxOrder():
    #    '''
    #    Specifies the order in which the input boxes should be displayed, as a
    #    list. The input boxes are specified by index (starting with 1) or by
    #    key. If None, the order of the input boxes is in the order specified by
    #    getInputBoxNames.
    #    '''
    #    return None

    #Generates a GSuite selection box with galaxy track names
    @staticmethod
    def getOptionsBoxGsuite(): # Alternatively: getOptionsBox1()
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
        return '__history__', 'gsuite'
    
    #Generates a drop-down with a list of attributes from the Gsuite selected in getOptionsBoxGsuite()
    @classmethod
    def getOptionsBoxAttrName(cls, prevChoices): # Alternatively: getOptionsBox2()
        if not prevChoices.gsuite:
            return

        gSuite = getGSuiteFromGalaxyTN(prevChoices.gsuite)
                
        attributeList = gSuite.attributes
        
        return [TITLE_COL] + attributeList
        
    
    #Generates the labels for the editable input boxes by getting the titles from the GSuite chosen in getOptionsBoxGsuite() 
    @classmethod
    def _getOptionsBoxLabel(cls, prevChoices, index):
        
        titlesDict = {}

        if not prevChoices.gsuite or not prevChoices.attrName:
            return
        
        #Create a GSuite form the prevChoices
        gSuite = getGSuiteFromGalaxyTN(prevChoices.gsuite)
                        
        #Makes sure the index will not direct to outside of the length of the list.
        if(index < len(gSuite)*2):
            return '__rawstr__', '<b>Edit value for track nr. %s with title "%s":</b>' % ((index/2)+1, gSuite.getTrackFromIndex(index/2).title)
        
        #return '__rawstr__', 'pony'

    #Generates the input boxes dependent on which attribute was selected in the getOptionsBoxAttrName(cls, prevChoices)
    @classmethod
    def _getOptionsBoxForSelectAttribute(cls, prevChoices, index):
#         from quick.application.ExternalTrackManager import ExternalTrackManager

        selectionList = []

        if not prevChoices.gsuite or not prevChoices.attrName:
            return

        gSuite = getGSuiteFromGalaxyTN(prevChoices.gsuite)
        
        attrName = prevChoices.attrName
        
        #Makes sure the index will not direct to outside of the length of the list.
        if(index < len(gSuite)*2):
            if(attrName == TITLE_COL):
                attrValue = gSuite.getTrackFromIndex(int(index/2)).title
            else:
                attrValue = gSuite.getTrackFromIndex(int(index/2)).getAttribute(attrName)
            return str(attrValue)


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
    
    #Generates the dynamic labels and input boxes
    #The MAX_NUM_OF_TRACKS is multiplied by two because we are showing both titles and input boxes
    #The one is added because otherwise there will be a title without the input box since we start counting from 0
    @classmethod
    def setupSelectGSuiteMethods(cls):
        for i in xrange(cls.MAX_NUM_OF_TRACKS*2):
            """setattr(cls, 'getOptionsBoxSelectAttribute%s' % i, partial(cls._getOptionsBoxLabel, index=i))
            setattr(cls, 'getOptionsBoxSelectAttribute%s' % i, partial(cls._getOptionsBoxForSelectAttribute, index=i))"""
            if (i%2 == 0):
                setattr(cls, 'getOptionsBoxSelectAttribute%s' % i, partial(cls._getOptionsBoxLabel, index=i))
            else:
                setattr(cls, 'getOptionsBoxSelectAttribute%s' % i, partial(cls._getOptionsBoxForSelectAttribute, index=i))

    #Writes the information that has been changed in the input boxes to a new GSuite file
    @staticmethod
    def execute(choices, galaxyFn=None, username=''):

        '''
        Is called when execute-button is pushed by web-user. Should print
        output as HTML to standard out, which will be directed to a results page
        in Galaxy history. If getOutputFormat is anything else than HTML, the
        output should be written to the file with path galaxyFn. If needed,
        StaticFile can be used to get a path where additional files can be put
        (e.g. generated image files). choices is a list of selections made by
        web-user in each options box.
        '''
        gSuite = getGSuiteFromGalaxyTN(choices.gsuite)

        attrName = choices.attrName
        
        outputGSuite = GSuite()
             
        #Writes the information that has been changed to a new track but jumps over all the empty strings   
        for i, track in enumerate(gSuite.allTracks()):
            newAttrValue = getattr(choices, 'selectAttribute%s' % ((i*2)+1))
            if(attrName == TITLE_COL):
                track.title = newAttrValue
            else:
                track.setAttribute(attrName, newAttrValue)
            outputGSuite.addTrack(track)
         
        #Creates the new GSuite      
        GSuiteComposer.composeToFile(outputGSuite, galaxyFn)
        

    #Displays an error message before the GSuite is selected in the first drop-down
    @staticmethod
    def validateAndReturnErrors(choices):
        '''
        Should validate the selected input parameters. If the parameters are not
        valid, an error text explaining the problem should be returned. The GUI
        then shows this text to the user (if not empty) and greys out the
        execute button (even if the text is empty). If all parameters are valid,
        the method should return None, which enables the execute button.
        '''
        errorString = GeneralGuiTool._checkGSuiteFile(choices.gsuite)
        
        if errorString:
            return errorString
          
        if not choices.gsuite:
            return
           
        gSuite = getGSuiteFromGalaxyTN(choices.gsuite)
        
        if not gSuite.attributes:
            errorString = "Please choose a GSuite file that contains attributes"
        
        if errorString:
            return errorString


    #@staticmethod
    #def getSubToolClasses():
    #    '''
    #    Specifies a list of classes for subtools of the main tool. These
    #    subtools will be selectable from a selection box at the top of the page.
    #    The input boxes will change according to which subtool is selected.
    #    '''
    #    return None
    #
    #@staticmethod
    #def isPublic():
    #    '''
    #    Specifies whether the tool is accessible to all users. If False, the
    #    tool is only accessible to a restricted set of users as defined in
    #    LocalOSConfig.py.
    #    '''
    #    return False
    #
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
    @staticmethod
    def getResetBoxes():
        '''
        Specifies a list of input boxes which resets the subsequent stored
        choices previously made. The input boxes are specified by index
        (starting with 1) or by key.
        '''
        return ['gsuite', 'attrName']
    
    #Help text generator
    @staticmethod
    def getToolDescription():
        '''
        Specifies a help text in HTML that is displayed below the tool.
        '''
        from gold.result.HtmlCore import HtmlCore

        core = HtmlCore()
        core.paragraph('This tool provides the option of editing contents of medatata'
                       'columns in a GSuite file where the user can edit the titles'
                       'in the file.')
        core.divider()
        core.paragraph('To filter a GSuite file, please follow these steps: ')
        core.orderedList(['Select the input GSuite file from history',
                          'Select the titles of the tracks that should be edited',
                          'Edit the titles of the tracks',
                          'Click the Execute button'])

        '''cls._addGSuiteFileDescription(core,
                                      alwaysShowRequirements=True,
                                      alwaysShowOutputFile=True)'''

        return str(core)

    #@staticmethod
    #def getToolIllustration():
    #    '''
    #    Specifies an id used by StaticFile.py to reference an illustration file
    #    on disk. The id is a list of optional directory names followed by a file
    #    name. The base directory is STATIC_PATH as defined by AutoConfig.py. The
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
        return 'gsuite'

EditGsuiteMetadataTool.setupSelectGSuiteMethods()
