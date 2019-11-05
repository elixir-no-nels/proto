from collections import namedtuple, OrderedDict

#
# Namedtuples
#

HeaderSpec = namedtuple('HeaderSpec',
                        ['allowed', 'default', 'memberName', 'colName', 'deprecated'])
ColSpec = namedtuple('ColSpec', ['colName', 'memberName', 'headerName', 'deprecated'])

#
# Constants
#

LOCATION_HEADER = 'location'
FILE_FORMAT_HEADER = 'file format'
FILE_TYPE_HEADER = 'file type'
TRACK_TYPE_HEADER = 'track type'
GENOME_HEADER = 'genome'

URI_MEMBER = 'uri'
TITLE_MEMBER = 'title'
LOCATION_MEMBER = 'location'
FILE_FORMAT_MEMBER = 'fileFormat'
TRACK_TYPE_MEMBER = 'trackType'
GENOME_MEMBER = 'genome'

URI_COL = 'uri'
TITLE_COL = 'title'
LOCATION_COL = None
FILE_FORMAT_COL = 'file_format'
FILE_TYPE_COL = 'file_type'
TRACK_TYPE_COL = 'track_type'
GENOME_COL = 'genome'

URI_COL_SPEC = ColSpec(colName=URI_COL,
                       memberName=URI_MEMBER,
                       headerName=None,
                       deprecated=False)
OPTIONAL_STD_COL_SPECS = [ColSpec(colName=TITLE_COL,
                                  memberName=TITLE_MEMBER,
                                  headerName=None,
                                  deprecated=False),
                          ColSpec(colName=FILE_FORMAT_COL,
                                  memberName=FILE_FORMAT_MEMBER,
                                  headerName=FILE_FORMAT_HEADER,
                                  deprecated=False),
                          ColSpec(colName=FILE_TYPE_COL,
                                  memberName=FILE_FORMAT_MEMBER,
                                  headerName=FILE_TYPE_HEADER,
                                  deprecated=True),
                          ColSpec(colName=TRACK_TYPE_COL,
                                  memberName=TRACK_TYPE_MEMBER,
                                  headerName=TRACK_TYPE_HEADER,
                                  deprecated=False),
                          ColSpec(colName=GENOME_COL,
                                  memberName=GENOME_MEMBER,
                                  headerName=GENOME_HEADER,
                                  deprecated=False)]
ALL_STD_COL_SPECS = [URI_COL_SPEC] + OPTIONAL_STD_COL_SPECS

OPTIONAL_STD_COL_NAMES = [colSpec.colName for colSpec in OPTIONAL_STD_COL_SPECS]
ALL_STD_COL_NAMES = [URI_COL_SPEC.colName] + OPTIONAL_STD_COL_NAMES

REMOTE = 'remote'
LOCAL = 'local'
UNKNOWN = 'unknown'
MULTIPLE = 'multiple'
PRIMARY = 'primary'
PREPROCESSED = 'preprocessed'
TEXT = 'text'
BINARY = 'binary'


class EverythingAllowed(object):
    def __contains__(self, key):
        return True


HEADER_VAR_DICT = OrderedDict([

    (LOCATION_HEADER, HeaderSpec(allowed=OrderedDict(zip([REMOTE,
                                                          LOCAL,
                                                          UNKNOWN,
                                                          MULTIPLE], [None]*4)),
                                 default=UNKNOWN,
                                 memberName=LOCATION_MEMBER,
                                 colName=LOCATION_COL,
                                 deprecated=False)),

    (FILE_TYPE_HEADER, HeaderSpec(allowed=OrderedDict(zip([TEXT,
                                                           BINARY,
                                                           UNKNOWN,
                                                           MULTIPLE], [None]*4)),
                                  default=UNKNOWN,
                                  memberName=FILE_FORMAT_MEMBER,
                                  colName=FILE_TYPE_COL,
                                  deprecated=True)),

    (FILE_FORMAT_HEADER, HeaderSpec(allowed=OrderedDict(zip([PRIMARY,
                                                             PREPROCESSED,
                                                             UNKNOWN,
                                                             MULTIPLE], [None]*4)),
                                    default=UNKNOWN,
                                    memberName=FILE_FORMAT_MEMBER,
                                    colName=FILE_FORMAT_COL,
                                    deprecated=False)),

    (TRACK_TYPE_HEADER, HeaderSpec(allowed=OrderedDict(zip([MULTIPLE,
                                                            UNKNOWN], [None]*2)),
                                   default=UNKNOWN,
                                   memberName=TRACK_TYPE_MEMBER,
                                   colName=TRACK_TYPE_COL,
                                   deprecated=False)),

    (GENOME_HEADER, HeaderSpec(allowed=EverythingAllowed(),
                               default=UNKNOWN,
                               memberName=GENOME_MEMBER,
                               colName=GENOME_COL,
                               deprecated=False))
])

BTRACK_SUFFIX = 'btrack'
COMPRESSION_SUFFIXES = ['gz']
ARCHIVE_SUFFIXES = ['tar', 'tar.gz', 'tar.bz2', 'zip']

GSUITE_SUFFIX = 'gsuite'
GSUITE_STORAGE_SUFFIX = 'gsuite_storage'

GSUITE_EXPANDED_WITH_RESULT_COLUMNS_FILENAME = 'GSuite with results'
