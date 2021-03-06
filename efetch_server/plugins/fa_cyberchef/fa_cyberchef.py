"""
A simple torrent plugin based on torrentparse by Mohan Raj

This code is copied from: 
https://github.com/mohanraj-r/torrentparse/blob/master/torrentparse/torrentparse.py

All terms will be respected when and if applied therefore this plugin
may only be temporary
"""

from base64 import b64encode
from yapsy.IPlugin import IPlugin
from efetch_server.utils.pathspec_helper import PathspecHelper
from flask import render_template
import logging


class FaCyberChef(IPlugin):

    def __init__(self):
        self.display_name = 'CyberChef'
        self.popularity = 1
        self.category = 'common'
        self.cache = False
        self.fast = False
        self.action = False
        self.icon = 'fa-cutlery'
        self.plaintext_mimetypes = [ u'application/xml', u'application/javascript',
                u'application/json', u'application/typescript' ]
        IPlugin.__init__(self)

    def activate(self):
        IPlugin.activate(self)
        return

    def deactivate(self):
        IPlugin.deactivate(self)
        return

    def check(self, evidence, path_on_disk):
        """Checks if the file is compatible with this plugin"""
        return False

    def mimetype(self, mimetype):
        """Returns the mimetype of this plugins get command"""
        return "text/plain"

    def get(self, evidence, helper, path_on_disk, request):
        """Returns the result of this plugin to be displayed in a browser"""
        data = PathspecHelper.read_file(evidence['pathspec'], size=evidence['size'], seek=0)
        
        mimetype = evidence['mimetype'] = helper.pathspec_helper.get_mimetype(evidence['pathspec'])
        decode = mimetype.startswith('text/') or mimetype in self.plaintext_mimetypes

        return render_template('fa_cyberchef.html', data=b64encode(data), decode=decode)
