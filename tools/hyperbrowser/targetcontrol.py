# Copyright (C) 2009, Geir Kjetil Sandve, Sveinung Gundersen and Morten Johansen
# This file is part of The Genomic HyperBrowser.
#
#    The Genomic HyperBrowser is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    The Genomic HyperBrowser is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with The Genomic HyperBrowser.  If not, see <http://www.gnu.org/licenses/>.

import sys, os, getopt, types

from gold.application.GalaxyInterface import *

#
# Copied and modified from gops_subtract.py from Galaxy codebase
#
from galaxy import eggs
import pkg_resources
pkg_resources.require( "bx-python" )

import sys, fileinput, tempfile
from bx.intervals.io import NiceReaderWrapper, ParseError
from bx.intervals.operations.subtract import subtract
from galaxy.tools.util.galaxyops import fail, skipped

def subtract_files(fn1, fn2, out_fn):
    g1 = NiceReaderWrapper( fileinput.FileInput( fn1 ),
                            fix_strand=True )
        
    g2 = NiceReaderWrapper( fileinput.FileInput( fn2 ),
                            fix_strand=True )
    
    out_file = open( out_fn, "w" )
    try:
        for feature in subtract( [g1,g2], pieces=True, mincols=1 ):
            out_file.write( "%s\n" % feature )
    except ParseError, exc:
        out_file.close()
        fail( "Invalid file format: %s" % str( exc ) )

    out_file.close()

    if g1.skipped > 0:
        print skipped( g1, filedesc=" of 2nd dataset" )
    if g2.skipped > 0:
        print skipped( g2, filedesc=" of 1st dataset" )
#
#
#

def main():
    target = sys.argv[1]
    control = sys.argv[2]
    output = sys.argv[3]
    
    target_minus_control = tempfile.NamedTemporaryFile()
    control_minus_target = tempfile.NamedTemporaryFile()
    
    subtract_files(target, control, target_minus_control.name)
    subtract_files(control, target, control_minus_target.name)

    #print 'GalaxyInterface.combineToTargetControl', (target_minus_control, control_minus_target, output)
    
    sys.stdout = open(output, "w", 0)
    GalaxyInterface.combineToTargetControl(target_minus_control.name, control_minus_target.name, output)
    
if __name__ == "__main__":
    main()
