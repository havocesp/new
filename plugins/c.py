""" C plugin for New.
    Creates a new C file, and basic Makefile to go with it.
    -Christopher Welborn 2-20-15
"""
import os.path
from plugins import Plugin, date, fix_author

template = """/*  {filename}
    ...
    {author}{date}
*/

#include <{include}>
{namespace}
int main(int argc, char *argv[]) {{

    return 0;
}}
"""

template_lib = """/* {filename}
    ...
    {author}{date}
*/

"""


class CPlugin(Plugin):
    name = ('c', 'cpp', 'c++', 'cc')
    extensions = ('.c', '.cpp', '.cc')
    cpp_extensions = ('.cpp', '.cc')
    version = '0.0.4'
    ignore_post = {'chmodx'}
    description = '\n'.join((
        'Creates a basic C or C++ file for small programs.',
        'If no Makefile exists, it will be created with basic targets.',
        'The Makefile is provided by the automakefile plugin.'
    ))
    usage = """
    Usage:
        c [l]

    Options:
        l,lib  : Treat as a library file, automakefile will not run.
    """

    def __init__(self):
        self.load_config()

    def create(self, filename):
        """ Creates a basic C file.
        """
        # Disable automakefile if asked.
        library = self.has_arg('l(ib)?')
        if library:
            self.debug('Library file mode, no automakefile.')
            self.ignore_post.add('automakefile')

        parentdir, basename = os.path.split(filename)

        fileext = os.path.splitext(filename)[-1].lower()
        if fileext in self.cpp_extensions:
            include = 'iostream'
            namespace = '\nusing std::cout;\nusing std::endl;\n'
        else:
            include = 'stdio.h'
            namespace = ''

        return (template_lib if library else template).format(
            filename=basename,
            author=fix_author(self.config.get('author', None)),
            date=date(),
            include=include,
            namespace=namespace)


exports = (CPlugin,)
