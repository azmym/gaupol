# Copyright (C) 2006-2007 Osmo Salomaa
#
# This file is part of Gaupol.
#
# Gaupol is free software; you can redistribute it and/or modify it under the
# terms of the GNU General Public License as published by the Free Software
# Foundation; either version 2 of the License, or (at your option) any later
# version.
#
# Gaupol is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE.  See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# Gaupol; if not, write to the Free Software Foundation, Inc., 51 Franklin
# Street, Fifth Floor, Boston, MA 02110-1301, USA.


"""Script-specific regular expression patterns.

Module variables:

    _CAP_AFTERS:    Tuple of tuples of script, display name, pattern
    _CLAUSE_SEPS:   Tuple of tuples of script, display name, pattern
    _DIALOGUE_SEPS: Tuple of tuples of script, display name, pattern

Regular expression patterns in 'CLAUSE_SEPS' and 'DIALOGUE_SEPS' are required
to have named groups 'before' and 'after'. Space (or whatever) between those
groups acts as the separator. Either of the groups can be empty.
"""

# TODO: REWRITE AS 'BEFORE' AND 'AFTER' INSTEAD OF SEPARATORS.


import re

from gaupol import util
from gaupol.i18n import _


_CAP_AFTERS = (
    ("latin", _("Latin"), r"((?<!(.\.|\..))\.|\?|\!)(\'|\")?( |$)"),)

_CLAUSE_SEPS = (
    ("latin", _("Latin"),
     r"(?P<before>" + \
         r"(" + \
             r"((?<!(.\.|\..))\.|[\?\!])[\'\"]?" + \
         r"|" + \
             r"(?<!-)" + \
             r" [^ ]+?(\.{2,}|[\,\;\:])[\'\"]?" + \
             r"( [^ ]+?([^\.].\.{3,}|[\,\;\:])[\'\"]?)*" + \
             r"( [^ ]+?([^\.].\.|[\?\!])[\'\"]?)?" + \
             r"( [^ ]+$)?" + \
         r")" + \
     r")" + \
     r"( |$)" + \
     r"(?P<after>)"),
    ("latin-english", _("Latin (English)"),
     r"(?P<before>" + \
         r"(" + \
             r"(" + \
                 r"(?<!\b([Dd]r|[Jj]r|[Mm]r|[Mm]s|[Ss]r|[Ss]t))" + \
                 r"(?<!\b[Mm]rs)" + \
             r"(?<!(.\.|\..))\.|[\?\!])[\'\"]?" + \
         r"|" + \
             r"(?<!-)" + \
             r" [^ ]+?(\.{2,}|[\,\;\:])[\'\"]?" + \
             r"( [^ ]+?([^\.].\.{3,}|[\,\;\:])[\'\"]?)*" + \
             r"( [^ ]+?([^\.].\.|[\?\!])[\'\"]?)?" + \
             r"( [^ ]+$)?" + \
         r")" + \
     r")" + \
     r"( |$)" + \
     r"(?P<after>)"),)

_DIALOGUE_SEPS = (
    ("latin", _("Latin"), r"(?P<before>) (?P<after>- )"),)


def get_capitalize_after_ensure(value, script):
    re.compile(value)

@util.contractual
def get_capitalize_after(script):
    """Get the regular expression to capitalize after for script.

    Return regular expression pattern.
    """
    for seq in _CAP_AFTERS:
        if seq[0] == script:
            return seq[2]
    raise ValueError

def get_clause_separator_ensure(value, script):
    re.compile(value)

@util.contractual
def get_clause_separator(script):
    """Get the regular expression for a clause separator for script.

    Return regular expression pattern.
    """
    for seq in _CLAUSE_SEPS:
        if seq[0] == script:
            return seq[2]
    raise ValueError

def get_dialogue_separator_ensure(value, script):
    re.compile(value)

@util.contractual
def get_dialogue_separator(script):
    """Get the regular expression for a dialogue separator for script.

    Return regular expression pattern.
    """
    for seq in _DIALOGUE_SEPS:
        if seq[0] == script:
            return seq[2]
    raise ValueError
