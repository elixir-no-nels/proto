import os
from collections import namedtuple
from urllib import quote


class HistElement(object):
    def __init__(self, name, format, label=None, hidden=False):
        self.name = name
        self.format = format
        self.label = label
        self.hidden = hidden


BoxGroup = namedtuple('BoxGroup', ['label', 'first', 'last'])


class GeneralGuiTool(object):
    def __init__(self, toolId=None, conda_activate_source=None):
        self.__class__.toolId = toolId
        # In order to activate a tool-specific Conda environment (defined by Conda requirements
        # in the XML file of a tool), just call the cls.conda_activate_source script from a
        # subprocess from the execute method. This script is automatically set as a class
        # variable during Galaxy startup.
        self.__class__.conda_activate_source = conda_activate_source

    # API methods
    @staticmethod
    def getInputBoxNames():
        return []

    @staticmethod
    def getSubToolClasses():
        return None

    @classmethod
    def getToolSelectionName(cls):
        return cls.getToolName()

    @staticmethod
    def isPublic():
        return False

    @staticmethod
    def isRedirectTool(choices=None):
        return False

    @staticmethod
    def isHistoryTool():
        return True

    @staticmethod
    def isDynamic():
        return True

    @staticmethod
    def getResetBoxes():
        return []

    @staticmethod
    def getInputBoxOrder():
        return None

    @classmethod
    def getInputBoxGroups(cls, choices=None):
        if hasattr(super(GeneralGuiTool, cls), 'getInputBoxGroups'):
            return super(GeneralGuiTool, cls).getInputBoxGroups(choices)
        return None

    @staticmethod
    def getToolDescription():
        return ''

    @staticmethod
    def getToolIllustration():
        return None

    @staticmethod
    def getFullExampleURL():
        return None

    @staticmethod
    def isDebugMode():
        return False

    @staticmethod
    def getOutputFormat(choices=None):
        return 'html'

    @classmethod
    def getOutputName(cls, choices=None):
        return cls.getToolSelectionName()

    @staticmethod
    def validateAndReturnErrors(choices):
        return None

    @staticmethod
    def shouldAppendHtmlHeaderAndFooter(outputFormat):
        return outputFormat == 'html'

    # Convenience methods

    @classmethod
    def convertHttpParamsStr(cls, streng):
        strTab = []
        for v in streng.split('\n'):
            if v:
                strTab.append(v)

        return dict([tuple(v.split(':',1)) for v in strTab])

    @classmethod
    def getOptionBoxNames(cls):
        labels = cls.getInputBoxNames()
        #inputOrder = range(len(labels) if not cls.getInputBoxOrder() else cls.getInputBoxOrder()
        boxMal = 'box%i'
        if type(labels[0]).__name__ == 'str':
            return [boxMal%i for i in range(1, len(labels)+1)]
            #return [boxMal % i for i in inputOrder]
        else:
            return [i[0] for i in labels]
            #return [labels[i][0] for i in inputOrder]

    @classmethod
    def getNamedTuple(cls):
        names = cls.getInputBoxNames()
        anyTuples = False
        vals = []
        for i in range(len(names)):
            name = names[i]
            if isinstance(name, tuple):
                anyTuples = True
                vals.append(name[1])
            else:
                vals.append('box' + str(1 + i))

        if anyTuples:
            return namedtuple('ChoiceTuple', vals)
        else:
            return None

    @staticmethod
    def _exampleText(text):
        from proto.HtmlCore import HtmlCore
        core = HtmlCore()
        core.styleInfoBegin(styleClass='debug', linesep=False)
        core.append(text.replace('\t','\\t'))
        core.styleInfoEnd()
        return str(core)

    @classmethod
    def makeHistElement(cls,  galaxyExt='html', title='new Dataset', label='Newly created dataset',):
        import json, glob
        #print 'im in makeHistElement'
        json_params =  cls.runParams
        datasetId = json_params['output_data'][0]['dataset_id'] # dataset_id fra output_data
        hdaId = json_params['output_data'][0]['hda_id'] # # hda_id fra output_data
        metadata_parameter_file = open( json_params['job_config']['TOOL_PROVIDED_JOB_METADATA_FILE'], 'a' )
        newFilePath = json_params['param_dict']['__new_file_path__']
        numFiles = len(glob.glob(newFilePath+'/primary_%i_*'%hdaId))
        #title += str(numFiles+1)
        #print 'datasetId', datasetId
        #print 'newFilePath', newFilePath
        #print 'numFiles', numFiles
        outputFilename = os.path.join(newFilePath , 'primary_%i_%s_visible_%s' % ( hdaId, title, galaxyExt ) )
        #print 'outputFilename', outputFilename
        metadata_parameter_file.write( "%s\n" % json.dumps( dict( type = 'dataset', #new_primary_
                                         dataset_id = datasetId,#base_
                                         ext = galaxyExt,
                                         #filename = outputFilename,
                                         #name = label,
                                         metadata = {'dbkey':['hg18']} )) )
        metadata_parameter_file.close()
        return outputFilename

    @classmethod
    def createGenericGuiToolURL(cls, tool_id, sub_class_name=None, tool_choices=None):
        from proto.ProtoToolRegister import getToolPrototype
        tool = getToolPrototype(tool_id)
        base_url = '?mako=generictool&tool_id=' + tool_id + '&'
        if sub_class_name and isinstance(tool, MultiGeneralGuiTool):
            for subClass in tool.getSubToolClasses():
                if sub_class_name == subClass.__name__:
                    tool = subClass()
                    base_url += 'sub_class_id=' + quote(tool.getToolSelectionName()) + '&'

        #keys = tool.getNamedTuple()._fields
        if not tool_choices:
            args = []
        elif isinstance(tool_choices, dict):
            args = [ '%s=%s' % (k,quote(v)) for k,v in tool_choices.items()]
        elif isinstance(tool_choices, list):
            args = [ '%s=%s' % ('box%d'%(i+1,), quote(tool_choices[i])) for i in range(0, len(tool_choices)) ]

        return base_url + '&'.join(args)

    @staticmethod
    def _checkGenome(genomeChoice):
        if genomeChoice in [None, '']:
            return 'Please select a genome build'

    @classmethod
    def _addGSuiteFileDescription(cls, core, allowedLocations=[], allowedFileFormats=[], allowedTrackTypes=[],
                                  disallowedGenomes=[], outputLocation='',  outputFileFormat='', outputTrackType='',
                                  errorFile=False, alwaysShowRequirements=False, alwaysShowOutputFile=False,
                                  minTrackCount=None, maxTrackCount=None):
        from gsuite.GSuiteConstants import UNKNOWN, MULTIPLE

        if alwaysShowRequirements or any((allowedLocations, allowedFileFormats, allowedTrackTypes, disallowedGenomes)):
            core.divider()
            core.smallHeader('Requirements for GSuite input file')

            core.descriptionLine('Locations', ', '.join(allowedLocations) if allowedLocations else 'any', emphasize=True)
            core.descriptionLine('File formats', ', '.join(allowedFileFormats) if allowedFileFormats else 'any', emphasize=True)
            core.descriptionLine('Track types', ', '.join(allowedTrackTypes) if allowedTrackTypes else 'any', emphasize=True)

            genomeText = 'required' if UNKNOWN in disallowedGenomes else 'optional'
            genomeText += ', only single genome allowed' if MULTIPLE in disallowedGenomes else ', multiple genomes allowed'
            core.descriptionLine('Genome', genomeText, emphasize=True)

        if alwaysShowOutputFile or any((outputLocation, outputFileFormat, outputTrackType)):
            core.divider()
            core.smallHeader('Format of GSuite output file')

            core.descriptionLine('Location', outputLocation if outputLocation else 'as input file', emphasize=True)
            core.descriptionLine('File format', outputFileFormat if outputFileFormat else 'as input file', emphasize=True)
            core.descriptionLine('Track type', outputTrackType if outputTrackType else 'as input file', emphasize=True)

        if errorFile:
            core.divider()
            core.smallHeader('Format of GSuite error file')
            core.paragraph('The error GSuite file contains references to all track lines '
                           'that failed in the execution of the tool. This is a valid GSuite '
                           'file that can be used as input in manipulation tools, if one needs to '
                           'change the contents somehow, or used directly as a '
                           'input in the current tool to reexecute it only on the '
                           'failed tracks.')

            core.descriptionLine('Location', allowedLocations[0] if len(allowedLocations) ==  1 else 'as input file', emphasize=True)
            core.descriptionLine('File format', allowedFileFormats[0] if len(allowedFileFormats) == 1 else  'as input file', emphasize=True)
            core.descriptionLine('Track type', allowedTrackTypes[0] if len(allowedTrackTypes) == 1 else  'as input file', emphasize=True)

        if minTrackCount or maxTrackCount:
            core.divider()
            core.smallHeader('Limitations on number of tracks in input GSuites')

            core.descriptionLine('Minimal number of tracks', str(minTrackCount) if minTrackCount else 'no limit', emphasize=True)


class MultiGeneralGuiTool(GeneralGuiTool):
    @staticmethod
    def getToolName():
        return "-----  Select tool -----"

    @staticmethod
    def getToolSelectionName():
        return "-----  Select tool -----"

    @staticmethod
    def getSubToolSelectionTitle():
        return 'Select subtool:'

    @staticmethod
    def validateAndReturnErrors(choices):
        return ''

    @staticmethod
    def getInputBoxNames():
        return []

    @staticmethod
    def useSubToolPrefix():
        return False
