""" ChmodX plugin for New.
    Makes new files executable (if they have the appropriate extension)
    -Christopher Welborn 01-01-2015
"""
import os
import stat

from plugins import debug, PostPlugin, SignalExit


class ChmodxPlugin(PostPlugin):

    def __init__(self):
        self.name = 'chmodx'

    def process(self, fname):
        """ Makes the newly created file executable. """
        chmod774 = stat.S_IRWXU | stat.S_IRWXG | stat.S_IROTH
        try:
            os.chmod(fname, chmod774)
        except FileNotFoundError:
            # The file was never created, all other plugins will fail.
            raise SignalExit('No file was created: {}'.format(fname))
        except EnvironmentError as ex:
            debug('Error during chmod: {}\n{}'.format(fname, ex))

plugins = (ChmodxPlugin(),)