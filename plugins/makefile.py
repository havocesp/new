""" Makefile plugin for New
    Creates a makefile when the C plugin is used.
    -Christopher Welborn 2-20-15
"""

import os.path
from plugins import (
    confirm,
    debug,
    Plugin,
    PostPlugin,
    SignalAction,
    SignalExit
)

# Version number for both plugins (if one changes, usually the other changes)
VERSION = '0.0.4'

# I'm not very good with makefiles. The .replace() is just for my sanity.
# {targets} is set by compiler type, and *then* the whole template is rendered
pre_template = """SHELL=bash
{{compilervar}}={{compiler}}
{{cflagsvar}}={{cflags}}
binary={{binary}}
source={{filename}}

{targets}

.PHONY: clean
clean:
    -@if [[ -e $(binary) ]]; then\\
        if rm -f $(binary); then\\
            echo "Binaries cleaned.";\\
        fi;\\
    else\\
        echo "Binaries already clean.";\\
    fi;

    -@if ls *.o &>/dev/null; then\\
        if rm *.o; then\\
            echo "Objects cleaned.";\\
        fi;\\
    else\\
        echo "Objects already clean.";\\
    fi;
""".replace('    ', '\t')

# Make targets for c/c++.
ctargets = """
all: {objects}
    $({compilervar}) -o $(binary) $({cflagsvar}) -O3 *.o

{objects}: $(source)
    $({compilervar}) -c $(source) $({cflagsvar})

debug: {objects}
    $({compilervar}) -o $(binary) $({cflagsvar}) -Og *.o
""".replace('    ', '\t')

# Make targets for rustc (until I find a better way)
rusttargets = """
all: $(source)
    $({compilervar}) -o $(binary) $({cflagsvar}) $(source)
""".replace('    ', '\t')

# Template options based on compiler name.
coptions = {
    'gcc': {
        'compilervar': 'CC',
        'cflagsvar': 'CFLAGS',
        'cflags': '-std=c11 -Wall',
        'targets': ctargets
    },
    'g++': {
        'compilervar': 'CXX',
        'cflagsvar': 'CXXFLAGS',
        'cflags': '-std=c++11 -Wall',
        'targets': ctargets,
    },
    'rustc': {
        'compilervar': 'RUSTC',
        'cflagsvar': 'RUSTFLAGS',
        'cflags': '',
        'targets': rusttargets
    }
}


def template_render(filepath, makefile=None):
    """ Render the makefile template for a given c source file name. """
    parentdir, filename = os.path.split(filepath)
    fileext = os.path.splitext(filename)[-1]
    makefile = os.path.join(
        parentdir,
        makefile if makefile else 'makefile')
    binary = os.path.splitext(filename)[0]
    objects = '{}.o'.format(binary)

    # Get compiler and make options by file extension (default to gcc).
    compiler = {
        '.c': 'gcc',
        '.cpp': 'g++',
        '.rs': 'rustc'
    }.get(fileext, 'gcc')

    # Create the base template, retrieve compiler-specific settings.
    debug('Rendering makefile template for {}.'.format(compiler))
    compileropts = coptions[compiler]
    template = pre_template.format(targets=compileropts.pop('targets'))

    # Create template args, update with compiler-based options.
    templateargs = {
        'compiler': compiler,
        'binary': binary,
        'filename': filename,
        'objects': objects
    }
    templateargs.update(coptions[compiler])

    # Format the template with compiler-specific settings.
    return makefile, template.format(**templateargs)


class MakefilePost(PostPlugin):
    name = 'automakefile'
    version = VERSION
    description = '\n'.join((
        'Creates a makefile for new C files.',
        'This will not overwrite existing makefiles.'
    ))

    def process(self, plugin, filename):
        """ When a C file is created, create a basic Makefile to go with it.
        """
        if plugin.get_name() not in ('c', 'rust'):
            return None
        self.create_makefile(filename)

    def create_makefile(self, filepath):
        """ Create a basic Makefile with the C file as it's target. """
        parentdir, filename = os.path.split(filepath)
        trynames = 'Makefile', 'makefile'
        for makefilename in trynames:
            fullpath = os.path.join(parentdir, makefilename)
            if os.path.exists(fullpath):
                self.debug('Makefile already exists: {}'.format(fullpath))
                return None
        self.debug('Creating a makefile for: {}'.format(filename))
        config = MakefilePlugin().config
        makefile, content = template_render(
            filepath,
            makefile=config.get('default_filename', 'makefile'))

        with open(makefile, 'w') as f:
            f.write(content)
        print('Makefile created: {}'.format(makefile))
        return makefile


class MakefilePlugin(Plugin):

    """ Creates a basic Makefile for a given c file name. """

    name = ('makefile', 'make')
    extensions = tuple()
    version = VERSION
    ignore_post = {'chmodx'}
    description = '\n'.join((
        'Creates a basic makefile for a given c or rust file name.'
        'The file created is always called "Makefile".'
    ))
    usage = """
    Usage:
        makefile [makefile_filename]

    Options:
        makefile_filename  : Desired file name for the makefile.
                             Can also be set in config as 'default_filename'.
    """

    def __init__(self):
        self.load_config()

    def create(self, filename):
        """ Creates a basic Makefile for a given c file name. """
        if not (self.dryrun or os.path.exists(filename)):
            msg = '\n'.join((
                'The target source file doesn\'t exist: {}',
                'Continue anyway?'
            )).format(filename)
            if not confirm(msg):
                raise SignalExit('User cancelled.')

        defaultfile = (
            self.get_arg(0, self.config.get('default_filename', 'makefile')))

        makefile, content = template_render(
            filename,
            makefile=defaultfile)

        _, basename = os.path.split(filename)
        msg = '\n'.join((
            'Creating a makefile for: {}'.format(basename),
            '              File path: {}'.format(makefile)
        ))
        raise SignalAction(
            message=msg,
            filename=makefile,
            content=content)

exports = (MakefilePost, MakefilePlugin)
