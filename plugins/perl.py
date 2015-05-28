""" Perl plugin for New.
    -Christopher Welborn 5-21-15
"""
from plugins import Plugin, date

# Not much here right now.
template = """#!/usr/bin/perl

# ...{description}
# {author}{date}

"""


class PerlPlugin(Plugin):

    """ A very basic perl template. """

    def __init__(self):
        self.name = ('perl', 'pl')
        self.extensions = ('.pl', '.perl')
        self.version = '0.0.1'
        self.load_config()

    def create(self, filename):
        """ Creates a basic perl source file. """

        author = self.config.get('author', '')
        description = ' '.join(self.args) if self.args else ''

        return template.format(
            author='-{} '.format(author) if author else author,
            date=date(),
            description=description)


exports = (PerlPlugin(), )