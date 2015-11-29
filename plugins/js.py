""" Node/JS plugin for New
    -Christopher Welborn
"""

import os.path
from plugins import Plugin, date, default_version

SHEBANG = '#!/usr/bin/env node'
HEADER = """
/*  {name}
    ...
    {author}{date}
*/
"""
TEMPLATE = """
/* jshint node:true, esnext:true, moz:true */

'use strict';
var docopt = require('docopt');

var name = '{name}';
var version = '{version}';
var version_str = `${{name}} v. ${{version}}`;
var scriptname = process.argv[1].split('/').slice(-1)[0];
var usage_str = `
    ${{version_str}}

    Usage:
        ${{scriptname}} [-h | -v]

    Options:
        -h,--help     : Show this message.
        -v,--version  : Print version and exit.
`;

function main(argd) {{
    // Main entry point, expects an argument object from docopt.
    console.log('Hello.');
    return 0;
}}

process.exit(
    main(
        docopt.docopt(usage_str, {{'version': version_str}})
    )
);
"""


class JSPlugin(Plugin):

    """ Creates a blank node/js file. """

    def __init__(self):
        self.name = ('js', 'node', 'nodejs')
        self.extensions = ('.js',)
        self.version = '0.0.6'
        self.load_config()
        self.usage = """
    Usage:
        js [-s]

    Options:
        -s,--short  : Only use the comment header.
    """

    def create(self, fname):
        """ Creates a blank js/node file. """
        # Using the node shebang, even though this may not be for node.
        author = self.config.get('author', '')
        basename = os.path.split(fname)[-1]
        name = os.path.splitext(basename)[0]
        use_short = self.has_arg('^((-s)|(--short))$')
        self.debug('Retrieved config..')
        author = '-{} '.format(author) if author else author
        if use_short:
            # Only the comment header.
            return HEADER.format(
                name=name,
                author=author,
                date=date()).lstrip()
        # Full template.
        return ''.join((
            SHEBANG,
            HEADER,
            TEMPLATE)).format(
                name=name,
                author=author,
                date=date(),
                scriptname=basename,
                version=self.config.get('default_version', default_version))

exports = (JSPlugin(),)
