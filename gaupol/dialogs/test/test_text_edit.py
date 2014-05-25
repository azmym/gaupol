# -*- coding: utf-8 -*-

# Copyright (C) 2005 Osmo Salomaa
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

import gaupol

from gi.repository import Gtk


class TestTextEditDialog(gaupol.TestCase):

    def run_dialog(self):
        self.dialog.run()
        self.dialog.destroy()

    def setup_method(self, method):
        gaupol.conf.editor.custom_font = "monospace"
        gaupol.conf.editor.length_unit = gaupol.length_units.CHAR
        gaupol.conf.editor.use_custom_font = True
        text = "etaoin shrdlu etaoin shrdlu etaoin shrdlu etaoin shrdlu"
        self.dialog = gaupol.TextEditDialog(Gtk.Window(), text)
        self.dialog.show()
