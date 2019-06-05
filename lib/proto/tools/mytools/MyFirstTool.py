from proto.tools.GeneralGuiTool import GeneralGuiTool


class MyFirstTool(GeneralGuiTool):
    @classmethod
    def getToolName(cls):
        return "This is my first tool"

    @classmethod
    def getInputBoxNames(cls):
        return [('Type some text', 'text'),
                ('Delimiter', 'delimiter'),
                ('Table', 'table')]

    # @classmethod
    # def getInputBoxOrder(cls):
    #     return None
    #
    # @classmethod
    # def getInputBoxGroups(cls, choices=None):
    #     return None

    @classmethod
    def getOptionsBoxText(cls):
        return '', 5

    @classmethod
    def getOptionsBoxDelimiter(cls, prevChoices):
        return ['Space', 'Newline']\

    @classmethod
    def getOptionsBoxTable(cls, prevChoices):
        splitText = cls._getSplitText(prevChoices)
        return [["Splitted text"]] + [[col] for col in splitText]

    @classmethod
    def _getSplitText(cls, prevChoices):
        splitText = prevChoices.text.split(' ' if prevChoices.delimiter == 'Space' else '\n')
        return splitText

    # @classmethod
    # def getInfoForOptionsBoxKey(cls, prevChoices):
    #     return None
    #
    # @classmethod
    # def getDemoSelections(cls):
    #     return ['testChoice1', '..']
    #
    # @classmethod
    # def getExtraHistElements(cls, choices):
    #     return None

    @classmethod
    def execute(cls, choices, galaxyFn=None, username=''):
        print>>open(galaxyFn, 'w'), '\t'.join(cls._getSplitText(choices))

    @classmethod
    def validateAndReturnErrors(cls, choices):
        if not choices.text.strip():
            return 'Please type some text'

    # @classmethod
    # def getSubToolClasses(cls):
    #     return None
    #
    # @classmethod
    # def isPublic(cls):
    #     return False
    #
    # @classmethod
    # def isRedirectTool(cls):
    #     return False
    #
    # @classmethod
    # def getRedirectURL(cls, choices):
    #     return ''
    #
    # @classmethod
    # def isHistoryTool(cls):
    #     return True
    #
    # @classmethod
    # def isDynamic(cls):
    #     return True
    #
    # @classmethod
    # def getResetBoxes(cls):
    #     return []
    #
    # @classmethod
    # def getToolDescription(cls):
    #     return ''
    #
    # @classmethod
    # def getToolIllustration(cls):
    #     return None
    #
    # @classmethod
    # def getFullExampleURL(cls):
    #     return None
    #
    # @classmethod
    # def isDebugMode(cls):
    #     return False
    #
    @classmethod
    def getOutputFormat(cls, choices):
        return 'tabular'
    #
    # @classmethod
    # def getOutputName(cls, choices=None):
    #     return cls.getToolSelectionName()
