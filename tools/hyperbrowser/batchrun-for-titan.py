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

import sys, os, getopt,types

# NB: import eggs before galaxy.util
#import galaxy.eggs
#from galaxy.util import restore_text

from gold.application.GalaxyInterface import *

import hyperbrowser.hyper_gui as hg

def main():
    #print "running"
    filename = sys.argv[1]
    
    params = hg.fileToParams(filename)
    
    batch = params['batch'].split('\n')
    genome = params['dbkey']

    sys.stdout = open(filename, "w", 0)

    try:
        print '''
            <html>
            <head>
                <link href="/static/style/base.css" rel="stylesheet" type="text/css" />
                <script type="text/javascript" src="/static/scripts/jquery.js"></script>
                <script type="text/javascript">
                    var done = false;
                    function toggleDebug() {
                        $(".debug").toggle();
                        return false;
                    }
                </script>
            </head>
            <body>
            <p style="text-align:right"><a href="#" onclick="return toggleDebug()">Toggle debug</a></p>
        '''
        #print '''<script type="text/javascript" src="/static/scripts/jquery.js"></script>
        #    <script type="text/javascript">
        #        var done = false;
        #        var job = { filename: "%s", pid: %d };
        #
        #        var dead = document.cookie.indexOf("dead=" + job.pid) >= 0 ? true : false;
        #                                
        #        function check_job() {
        #            if (!done) {
        #                if (!dead) {
        #                    $.getJSON("/hyper/check_job", job, function (status) {
        #                            if (status.running) {
        #                                location.reload(true);
        #                            } else {
        #                                document.cookie = "dead=" + job.pid;
        #                                location.reload(true);
        #                            }
        #                        }
        #                    );
        #                } else {
        #                    alert("This job did not finish successfully: " + job.filename);
        #                }
        #            }
        #        }
        #        
        #        setTimeout("if (!done) check_job();", 2000);
        #    </script>
        #''' % (filename, os.getpid())

        #print 'GalaxyInterface.runBatchLines', (batch, filename, genome)
        GalaxyInterface.runBatchLines(batch, filename, genome)

    finally:
        print '''
            <script type="text/javascript">
                        done = true;
                        $(".debug").hide();
            </script>    
            </body></html>
        '''
        
    
if __name__ == "__main__":
    main()
