""" Open post-processing plugin for New.
    Opens files after they are created.
    -Christopher Welborn 12-25-14
"""
import os
import subprocess

from plugins import debug, DeferredPostPlugin


class OpenPlugin(DeferredPostPlugin):

    def __init__(self):
        self.name = 'open'
        self.load_config()

    def open_file(self, editor, filename):
        """ Open a file using an editor.
            Returns the process from Popen (not really used though..)
        """
        # Open the process, we don't care what happens after.
        cmd = [editor, filename]
        print('\nOpening editor: {}'.format(' '.join(cmd)))
        proc = subprocess.Popen(cmd)
        return proc

    def process(self, path):
        """ Opens the file after creation. """
        editor = self.config.get('editor', os.environ.get('EDITOR', ''))
        if not editor:
            print('open: No editor could be found!')
            helpmsg = 'Set one in {} (editor=/path/editor)'
            print(helpmsg.format(self.config_file))
            return 1
        debug('open: using editor: {}'.format(editor))
        try:
            self.open_file(editor, path)
        except Exception as ex:
            print('Error opening editor: {} {}\n{}'.format(editor, path, ex))
            return 1
        return 0

plugins = (OpenPlugin(),)
