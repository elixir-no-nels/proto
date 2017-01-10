import base64
import os, sys

import shutil

from config.Config import STATIC_PATH, GALAXY_FILE_PATH, GALAXY_BASE_DIR
from proto.tools.hyperbrowser.GeneralGuiTool import GeneralGuiTool


class FileImport(GeneralGuiTool):
    @staticmethod
    def getToolName():
        """
        Specifies a header of the tool, which is displayed at the top of the
        page.
        """
        return "Import file to history"

    @staticmethod
    def getInputBoxNames():
        """
        Specifies a list of headers for the input boxes, and implicitly also
        the number of input boxes to display on the page. The returned list
        can have two syntaxes:

            1) A list of strings denoting the headers for the input boxes in
               numerical order.
            2) A list of tuples of strings, where each tuple has
               two items: a header and a key.

        The contents of each input box must be defined by the function
        getOptionsBoxK, where K is either a number in the range of 1 to the
        number of boxes (case 1), or the specified key (case 2).

        Note: the key has to be camelCase and start with a non-capital letter
              (e.g. "firstKey")
        """
        return [('', 'basicQuestionId'),
                ('Input filename', 'input'),
                ('Format', 'format'),
                ('Datatype', 'datatype')]

    # @staticmethod
    # def getInputBoxOrder():
    #     """
    #     Specifies the order in which the input boxes should be displayed,
    #     as a list. The input boxes are specified by index (starting with 1)
    #     or by key. If None, the order of the input boxes is in the order
    #     specified by getInputBoxNames.
    #     """
    #     return None
    #
    # @staticmethod
    # def getInputBoxGroups(choices=None):
    #     """
    #     Creates a visual separation of groups of consecutive option boxes
    #     from the rest (fieldset). Each such group has an associated label
    #     (string), which is shown to the user. To define groups of option
    #     boxes, return a list of BoxGroup namedtuples with the label, the key
    #     (or index) of the first and last options boxes (inclusive).
    #
    #     Example:
    #        from quick.webtool.GeneralGuiTool import BoxGroup
    #        return [BoxGroup(label='A group of choices', first='firstKey',
    #                         last='secondKey')]
    #     """
    #     return None

    @staticmethod
    def getOptionsBoxBasicQuestionId():  # Alternatively: getOptionsBox1()
        """
        Defines the type and contents of the input box. User selections are
        returned to the tools in the prevChoices and choices attributes to
        other methods. These are lists of results, one for each input box
        (in the order specified by getInputBoxOrder()).

        The input box is defined according to the following syntax:

        Selection box:          ['choice1','choice2']
        - Returns: string

        Text area:              'textbox' | ('textbox',1) | ('textbox',1,False)
        - Tuple syntax: (contents, height (#lines) = 1, read only flag = False)
        - The contents is the default value shown inside the text area
        - Returns: string

        Raw HTML code:          '__rawstr__', 'HTML code'
        - This is mainly intended for read only usage. Even though more
          advanced hacks are possible, it is discouraged.

        Password field:         '__password__'
        - Returns: string

        Genome selection box:   '__genome__'
        - Returns: string

        Track selection box:    '__track__'
        - Requires genome selection box.
        - Returns: colon-separated string denoting track name

        History selection box:  ('__history__',) |
                                ('__history__', 'bed', 'wig')
        - Only history items of specified types are shown.
        - Returns: colon-separated string denoting galaxy track name, as
                   specified in ExternalTrackManager.py.

        History check box list: ('__multihistory__', ) |
                                ('__multihistory__', 'bed', 'wig')
        - Only history items of specified types are shown.
        - Returns: OrderedDict with galaxy id as key and galaxy track name
                   as value if checked, else None.

        Hidden field:           ('__hidden__', 'Hidden value')
        - Returns: string

        Table:                  [['header1','header2'], ['cell1_1','cell1_2'],
                                 ['cell2_1','cell2_2']]
        - Returns: None

        Check box list:         OrderedDict([('key1', True), ('key2', False),
                                             ('key3', False)])
        - Returns: OrderedDict from key to selection status (bool).
        """
        return '__hidden__', ''

    @staticmethod
    def getOptionsBoxInput(prevChoices):  # Alternatively: getOptionsBox2()
        return '__hidden__', ''

    @staticmethod
    def getOptionsBoxDatatype(prevChoices):
        """
        See getOptionsBoxFirstKey().

        prevChoices is a namedtuple of selections made by the user in the
        previous input boxes (that is, a namedtuple containing only one element
        in this case). The elements can accessed either by index, e.g.
        prevChoices[0] for the result of input box 1, or by key, e.g.
        prevChoices.key (case 2).
        """
        return '__hidden__', prevChoices.format if prevChoices.format else 'bed'

    @staticmethod
    def getOptionsBoxFormat(prevChoices):
        return '__hidden__', ''

    # @staticmethod
    # def getInfoForOptionsBoxKey(prevChoices):
    #     """
    #     If not None, defines the string content of an clickable info box
    #     beside the corresponding input box. HTML is allowed.
    #     """
    #     return None
    #
    # @staticmethod
    # def getDemoSelections():
    #     """
    #     Defines a set of demo inputs to the option boxes in the
    #     order defined by getOptionBoxNames and getOptionsBoxOrder.
    #     If not None, a Demo button appears in the interface. Clicking the
    #     button fills the option boxed with the defined demo values.
    #     """
    #     return ['testChoice1', '..']
    #
    # @classmethod
    # def getExtraHistElements(cls, choices):
    #     """
    #     Defines extra history elements to be created when clicking execute.
    #     This is defined by a list of HistElement objects, as in the
    #     following example:
    #
    #        from proto.GeneralGuiTool import HistElement
    #        return [HistElement(cls.HISTORY_TITLE, 'bed', hidden=False)]
    #
    #     It is good practice to use class constants for longer strings.
    #
    #     In the execute() method, one typically needs to fetch the path to
    #     the dataset referred to by the extra history element. To fetch the
    #     path, use the dict cls.extraGalaxyFn with the defined history title
    #     as key, e.g. "cls.extraGalaxyFn[cls.HISTORY_TITLE]".
    #     """
    #     return None

    @staticmethod
    def execute(choices, galaxyFn=None, username=''):
        """
        Is called when execute-button is pushed by web-user. Should print
        output as HTML to standard out, which will be directed to a results
        page in Galaxy history. If getOutputFormat is anything else than
        HTML, the output should be written to the file with path galaxyFn.
        If needed, StaticFile can be used to get a path where additional
        files can be put (e.g. generated image files). choices is a list of
        selections made by web-user in each options box.
        """
        input = str(choices.input)
        if not input.startswith('/'):
            input = base64.urlsafe_b64decode(input)
        input = os.path.abspath(input)
        output = galaxyFn

        input_real = os.path.realpath(input)
        base_real = os.path.realpath(GALAXY_BASE_DIR)
        if not input_real.startswith(base_real):
            input_real = os.path.sep.join([base_real.rstrip(os.path.sep),
                                           input_real.lstrip(os.path.sep)])

        datatype = choices.format if choices.format else choices.datatype

        if (input_real.startswith(os.path.realpath(STATIC_PATH))
            or input_real.startswith(os.path.realpath(GALAXY_FILE_PATH))) \
                and input.endswith('.' + datatype):
            shutil.copy(input_real, output)
        else:
            # print input, input_real, 'not allowed', os.path.realpath(STATIC_PATH), \
            #     os.path.realpath(GALAXY_FILE_PATH), datatype
            raise Exception(input + ' not allowed to import! ')


    @staticmethod
    def validateAndReturnErrors(choices):
        """
        Should validate the selected input parameters. If the parameters are
        not valid, an error text explaining the problem should be returned.
        The GUI then shows this text to the user (if not empty) and greys
        out the execute button (even if the text is empty). If all
        parameters are valid, the method should return None, which enables
        the execute button.
        """
        return ''

    # @staticmethod
    # def getSubToolClasses():
    #     """
    #     Specifies a list of classes for subtools of the main tool. These
    #     subtools will be selectable from a selection box at the top of the
    #     page. The input boxes will change according to which subtool is
    #     selected.
    #     """
    #     return None
    #
    # @staticmethod
    # def isPublic():
    #     """
    #     Specifies whether the tool is accessible to all users. If False, the
    #     tool is only accessible to a restricted set of users as defined in
    #     LocalOSConfig.py.
    #     """
    #     return False
    #
    # @staticmethod
    # def isRedirectTool():
    #     """
    #     Specifies whether the tool should redirect to an URL when the Execute
    #     button is clicked.
    #     """
    #     return False
    #
    # @staticmethod
    # def getRedirectURL(choices):
    #     """
    #     This method is called to return an URL if the isRedirectTool method
    #     returns True.
    #     """
    #     return ''
    #
    # @staticmethod
    # def isHistoryTool():
    #     """
    #     Specifies if a History item should be created when the Execute button
    #     is clicked.
    #     """
    #     return True
    #
    # @classmethod
    # def isBatchTool(cls):
    #     """
    #     Specifies if this tool could be run from batch using the batch. The
    #     batch run line can be fetched from the info box at the bottom of the
    #     tool.
    #     """
    #     return cls.isHistoryTool()
    #
    # @staticmethod
    # def isDynamic():
    #     """
    #     Specifies whether changing the content of texboxes causes the page to
    #     reload.
    #     """
    #     return True
    #
    # @staticmethod
    # def getResetBoxes():
    #     """
    #     Specifies a list of input boxes which resets the subsequent stored
    #     choices previously made. The input boxes are specified by index
    #     (starting with 1) or by key.
    #     """
    #     return []
    #
    # @staticmethod
    # def getToolDescription():
    #     """
    #     Specifies a help text in HTML that is displayed below the tool.
    #     """
    #     return ''
    #
    # @staticmethod
    # def getToolIllustration():
    #     """
    #     Specifies an id used by StaticFile.py to reference an illustration file
    #     on disk. The id is a list of optional directory names followed by a file
    #     name. The base directory is STATIC_PATH as defined by Config.py. The
    #     full path is created from the base directory followed by the id.
    #     """
    #     return None
    #
    # @staticmethod
    # def getFullExampleURL():
    #     """
    #     Specifies an URL to an example page that describes the tool, for
    #     instance a Galaxy page.
    #     """
    #     return None
    #
    # @staticmethod
    # def isDebugMode():
    #     """
    #     Specifies whether the debug mode is turned on.
    #     """
    #     return False
    #

    @staticmethod
    def getOutputFormat(choices):
         return choices.format if choices.format else choices.datatype
