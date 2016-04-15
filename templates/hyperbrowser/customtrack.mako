<!--
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
-->

<%!
import sys
from cgi import escape
from urllib import quote, unquote

import hyperbrowser.hyper_gui as gui
%>
<%
#reload(gui)

galaxy = gui.GalaxyWrapper(trans)

params = galaxy.params

genomes = hyper.getAllGenomes(galaxy.getUserName())
genome = params.get('dbkey', genomes[0][1])
genomeElement = gui.SelectElement('dbkey', genomes, genome)

customname = params.get('customname', '')
customwinsize = params.get('customwinsize', '1')
customfunction = params.get('customfunction', '')

datasets = []
tracks = gui.TrackWrapper('track1', hyper, [], galaxy, datasets, genome)
tracks.preTracks = [('-- Sequence --', 'sequence', False)]
tracks.legend = 'Original tracks'


formAction = h.url_for('/tool_runner')

%>
<%namespace name="functions" file="functions.mako" />

<%inherit file="base.mako"/>

<%def name="title()">Create a custom track</%def>
<%def name="head()">
    <script type="text/javascript">
        <%include file="common.js"/>
        
        function validate(form) {
            return true;
        }
    </script>
</%def>

<form method="post" action="${formAction}" onsubmit="return validate(this)">

%if hyper.userHasFullAccess(galaxy.getUserName()):    

<p>
    Genome build: ${genomeElement.getHTML()} ${genomeElement.getScript()}    
</p>

${functions.trackChooser(tracks, 0, params)}

    <fieldset><legend>Custom track</legend>
    
    <p><label>Name: <input size="50" name="customname" value="${customname}"></label></p>

    <p><label>Window size (in bps): <input size="20" name="customwinsize" value="${customwinsize}"></label></p>

    <p><label>Function: <br><textarea cols="100" rows="20" name="customfunction">${escape(customfunction)}</textarea></label></p>

    </fieldset>

    <p><input id="start" type="submit" value="Create track"></p>
%else:
        <p>You must be one of us to create custom tracks</p>

%endif


    <INPUT TYPE="HIDDEN" NAME="tool_id" VALUE="hb_customtrack">
    <INPUT TYPE="HIDDEN" NAME="URL" VALUE="http://dummy">

</form>