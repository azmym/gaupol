# Copyright (C) 2005-2007 Osmo Salomaa
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


"""Dialog for selecting a subtitle file to save."""


import os

from gaupol.gtk import conf, const, util
from .subtitle import SubtitleFileDialog
from ..glade import GladeDialog


class SaveDialog(GladeDialog, SubtitleFileDialog):

    """Dialog for selecting a subtitle file to save."""

    # pylint: disable-msg=E1101

    def __init__(self, parent, title):

        GladeDialog.__init__(self, "save-dialog")
        SubtitleFileDialog.__init__(self)
        get_widget = self._glade_xml.get_widget
        self._format_combo = get_widget("format_combo")
        self._newline_combo = get_widget("newline_combo")

        self._init_format_combo()
        self._init_newline_combo()
        self._init_values()
        self._init_signal_handlers()
        self.set_title(title)
        self.set_transient_for(parent)

    def _init_format_combo(self):
        """Initialize the format combo box."""

        store = self._format_combo.get_model()
        for name in const.FORMAT.display_names:
            store.append([name])
        self._format_combo.set_active(0)

    def _init_newline_combo(self):
        """Initialize the newline combo box."""

        store = self._newline_combo.get_model()
        for name in const.NEWLINE.display_names:
            store.append([name])
        self._newline_combo.set_active(0)

    def _init_signal_handlers(self):
        """Initialize signal handlers."""

        util.connect(self, self, "response")
        util.connect(self, "_format_combo", "changed")
        util.connect(self, "_encoding_combo", "changed")

        def update_filename(*args):
            self._format_combo.emit("changed")
        save_button = self.action_area.get_children()[0]
        save_button.connect("event", update_filename)

    def _init_values(self):
        """Initialize default values for widgets."""

        if os.path.isdir(conf.file.directory):
            self.set_current_folder(conf.file.directory)
        self.set_encoding(conf.file.encoding)
        self.set_format(conf.file.format)
        self.set_newline(conf.file.newline)

    @util.asserted_return
    def _on_format_combo_changed(self, combo_box):
        """Change the extension of the current filename."""

        path = self.get_filename()
        assert path is not None
        self.unselect_filename(path)
        dirname = os.path.dirname(path)
        basename = os.path.basename(path)
        extensions = const.FORMAT.extensions
        if basename.endswith(tuple(extensions)):
            index = basename.rfind(".")
            basename = basename[:index]
        format = self.get_format()
        basename += format.extension
        path = os.path.join(dirname, basename)
        self.set_current_name(basename)
        self.set_filename(path)

    def _on_response(self, dialog, response):
        """Save widget values."""

        conf.file.encoding = self.get_encoding()
        conf.file.format = self.get_format()
        conf.file.newline = self.get_newline()
        conf.file.directory = self.get_current_folder()

    def get_format(self):
        """Get the selected format."""

        index = self._format_combo.get_active()
        return const.FORMAT.members[index]

    def get_newline(self):
        """Get the selected newline."""

        index = self._newline_combo.get_active()
        return const.NEWLINE.members[index]

    def set_format(self, format):
        """Set the selected format."""

        self._format_combo.set_active(format)

    def set_name(self, path):
        """Set either filename or current name."""

        if os.path.isfile(path):
            return self.set_filename(path)
        return self.set_current_name(path)

    def set_newline(self, newline):
        """Set the selected newline."""

        self._newline_combo.set_active(newline)
