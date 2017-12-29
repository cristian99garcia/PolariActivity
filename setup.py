#!/usr/bin/python

# Copyright (C) 2006, Red Hat, Inc.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

from sugar3.activity import bundlebuilder

import argparse
import os
import sys
import subprocess
import re

IGNORE_DIRS = ['dist', '.git', 'screenshots']
IGNORE_FILES = ['.gitignore', 'MANIFEST', '*.pyc', '*~', '*.bak', 'pseudo.po']


# Needed In genpot, Imported From Bundlebuilder
def _po_escape(string):
    return re.sub('([\\\\"])', '\\\\\\1', string)


# Modified Version Of genpot In Bundlebuilder
def cmd_genpot(config, options):
    """Generate the gettext pot file"""

    os.chdir(config.source_dir)

    po_path = os.path.join(config.source_dir, 'po')
    if not os.path.isdir(po_path):
        os.mkdir(po_path)

    python_files = []
    for root, dirs_dummy, files in os.walk(config.source_dir):
        for file_name in files:
            if file_name.endswith('.py') and 'twisted' not in root:
                # Ensure Twisted Directory Is Not Translated
                file_path = os.path.relpath(os.path.join(root, file_name),
                                            config.source_dir)
                python_files.append(file_path)
    python_files.sort()
    pot_file = os.path.join('po', '%s.pot' % config.bundle_name)
    escaped_name = _po_escape(config.activity_name)
    f = open(pot_file, 'w')
    f.write('#: activity/activity.info:2\n')
    f.write('msgid "%s"\n' % escaped_name)
    f.write('msgstr ""\n')
    if config.summary is not None:
        escaped_summary = _po_escape(config.summary)
        f.write('#: activity/activity.info:3\n')
        f.write('msgid "%s"\n' % escaped_summary)
        f.write('msgstr ""\n')

    f.close()

    args = ['xgettext', '--join-existing', '--language=Python',
            '--keyword=_', '--add-comments=TRANS:', '--output=%s' % pot_file]

    args += python_files
    retcode = subprocess.call(args)
    if retcode:
        print 'ERROR - xgettext failed with return code %i.' % retcode


def start():
    parser = argparse.ArgumentParser(prog='./setup.py')
    subparsers = parser.add_subparsers(
        dest="command", help="Options for %(prog)s")

    install_parser = subparsers.add_parser(
        "install", help="Install the activity in the system")
    install_parser.add_argument(
        "--prefix", dest="prefix", default=sys.prefix,
        help="Path for installing")
    install_parser.add_argument(
        "--skip-install-mime", dest="install_mime",
        action="store_false", default=True,
        help="Skip the installation of custom mime types in the system")
    install_parser.add_argument(
        "--skip-install-desktop-file", dest="install_desktop_file",
        action="store_false", default=True,
        help="Skip the installation of desktop file in the system")

    check_parser = subparsers.add_parser(
        "check", help="Run tests for the activity")
    check_parser.add_argument("choice", nargs='?',
                              choices=['unit', 'integration'],
                              help="run unit/integration test")
    check_parser.add_argument("--verbosity", "-v", dest="verbose",
                              type=int, choices=range(0, 3),
                              default=1, nargs='?',
                              help="verbosity for the unit tests")

    dist_parser = subparsers.add_parser("dist_xo",
                                        help="Create a xo bundle package")
    dist_parser.add_argument(
        "--no-fail", dest="no_fail", action="store_true", default=False,
        help="continue past failure when building xo file")

    subparsers.add_parser("dist_source", help="Create a tar source package")
    subparsers.add_parser("build", help="Build generated files")
    subparsers.add_parser("genpot", help="Generate the gettext pot file")
    subparsers.add_parser("dev", help="Setup for development")

    options = parser.parse_args()

    if options.command == "genpot":
        source_dir = os.path.abspath(os.path.dirname(sys.argv[0]))
        config = bundlebuilder.Config(source_dir)
        cmd_genpot(config, options)
    else:
        bundlebuilder.start()


if __name__ == '__main__':
    start()
