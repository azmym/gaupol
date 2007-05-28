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


"""Dialog for editing preferences."""


import gobject
import gtk
import pango

from gaupol import enclib
from gaupol.base import Delegate
from gaupol.gtk import conf, const, util
from gaupol.i18n import _
from .encoding import EncodingDialog
from .glade import GladeDialog


class _EditorPage(Delegate):

    """Editor preferences page."""

    def __init__(self, master):

        Delegate.__init__(self, master)
        get_widget = self._glade_xml.get_widget
        self._default_font_check = get_widget("editor_default_font_check")
        self._font_button = get_widget("editor_font_button")
        self._font_hbox = get_widget("editor_font_hbox")
        self._length_cell_check = get_widget("editor_length_cell_check")
        self._length_combo = get_widget("editor_length_combo")
        self._length_edit_check = get_widget("editor_length_edit_check")
        self._length_hbox = get_widget("editor_length_hbox")

        self._init_length_combo()
        self._init_values()
        self._init_signal_handlers()

    def _get_custom_font(self):
        """Get custom font as string."""

        context = gtk.Label().get_pango_context()
        font_desc = context.get_font_description()
        custom_font_desc = pango.FontDescription(conf.editor.font)
        font_desc.merge(custom_font_desc, True)
        return font_desc.to_string()

    def _init_length_combo(self):
        """Initialize the line length combo box."""

        store = self._length_combo.get_model()
        for name in const.LENGTH_UNIT.display_names:
            store.append([name])

    def _init_signal_handlers(self):
        """Initialize signal handlers."""

        util.connect(self, "_default_font_check", "toggled")
        util.connect(self, "_font_button", "font-set")
        util.connect(self, "_length_cell_check", "toggled")
        util.connect(self, "_length_combo", "changed")
        util.connect(self, "_length_edit_check", "toggled")

    def _init_values(self):
        """Initialize default values for widgets."""

        use_default = conf.editor.use_default_font
        self._default_font_check.set_active(use_default)
        self._font_hbox.set_sensitive(not use_default)
        self._font_button.set_font_name(self._get_custom_font())

        cell = conf.editor.show_lengths_cell
        edit = conf.editor.show_lengths_edit
        self._length_hbox.set_sensitive(cell or edit)
        self._length_cell_check.set_active(cell)
        self._length_edit_check.set_active(edit)
        self._length_combo.set_active(conf.editor.length_unit)

    def _on_default_font_check_toggled(self, check_button):
        """Save the default font usage."""

        use_default = check_button.get_active()
        conf.editor.use_default_font = use_default
        self._font_hbox.set_sensitive(not use_default)

    def _on_font_button_font_set(self, font_button):
        """Save the custom font."""

        conf.editor.font = font_button.get_font_name()

    def _on_length_cell_check_toggled(self, check_button):
        """Save the line length showage on cells."""

        conf.editor.show_lengths_cell = check_button.get_active()
        cell = conf.editor.show_lengths_cell
        edit = conf.editor.show_lengths_edit
        self._length_hbox.set_sensitive(cell or edit)

    def _on_length_combo_changed(self, combo_box):
        """Save the line length unit."""

        index = combo_box.get_active()
        conf.editor.length_unit = const.LENGTH_UNIT.members[index]

    def _on_length_edit_check_toggled(self, check_button):
        """Save the line length showage on text views."""

        conf.editor.show_lengths_edit = check_button.get_active()
        cell = conf.editor.show_lengths_cell
        edit = conf.editor.show_lengths_edit
        self._length_hbox.set_sensitive(cell or edit)


class _FilePage(Delegate):

    """File preferences page."""

    def __init__(self, master):

        Delegate.__init__(self, master)
        get_widget = self._glade_xml.get_widget
        self._add_button = get_widget("file_add_button")
        self._auto_check = get_widget("file_auto_check")
        self._down_button = get_widget("file_down_button")
        self._tree_view = get_widget("file_tree_view")
        self._locale_check = get_widget("file_locale_check")
        self._remove_button = get_widget("file_remove_button")
        self._up_button = get_widget("file_up_button")

        self._init_tree_view()
        self._init_values()
        self._init_signal_handlers()

    @util.asserted_return
    def _get_selected_row(self):
        """Get the selected row in the tree view or None."""

        selection = self._tree_view.get_selection()
        store, itr = selection.get_selected()
        assert itr is not None
        return store.get_path(itr)[0]

    def _init_signal_handlers(self):
        """Initialize signal handlers."""

        util.connect(self, "_add_button", "clicked")
        util.connect(self, "_auto_check", "toggled")
        util.connect(self, "_down_button", "clicked")
        util.connect(self, "_locale_check", "toggled")
        util.connect(self, "_remove_button", "clicked")
        util.connect(self, "_up_button", "clicked")

        def update(*args):
            self._set_sensitivities()
        selection = self._tree_view.get_selection()
        selection.connect("changed", update)

    def _init_tree_view(self):
        """Initialize the tree view."""

        selection = self._tree_view.get_selection()
        selection.set_mode(gtk.SELECTION_SINGLE)
        store = gtk.ListStore(gobject.TYPE_STRING)
        self._tree_view.set_model(store)
        renderer = gtk.CellRendererText()
        column = gtk.TreeViewColumn("", renderer, text=0)
        self._tree_view.append_column(column)

    def _init_values(self):
        """Initialize default values for widgets."""

        self._auto_check.set_active(conf.encoding.try_auto)
        self._auto_check.set_sensitive(util.chardet_available())
        self._locale_check.set_active(conf.encoding.try_locale)
        self._reload_tree_view()

    @util.asserted_return
    def _on_add_button_clicked(self, *args):
        """Add a new fallback encoding."""

        dialog = EncodingDialog(self._dialog)
        response = self.run_dialog(dialog)
        encoding = dialog.get_encoding()
        dialog.destroy()
        assert response == gtk.RESPONSE_OK
        assert encoding is not None
        assert encoding not in conf.encoding.fallbacks
        conf.encoding.fallbacks.append(encoding)
        self._reload_tree_view()
        self._tree_view.grab_focus()
        store = self._tree_view.get_model()
        self._tree_view.set_cursor(len(store) - 1)

    def _on_auto_check_toggled(self, check_button):
        """Save the encoding auto-detection usage."""

        conf.encoding.try_auto = check_button.get_active()

    def _on_down_button_clicked(self, *args):
        """Move the selected fallback encoding down."""

        row = self._get_selected_row()
        encodings = conf.encoding.fallbacks
        encodings.insert(row + 1, encodings.pop(row))
        self._reload_tree_view()
        self._tree_view.grab_focus()
        self._tree_view.set_cursor(row + 1)

    def _on_locale_check_toggled(self, check_button):
        """Save the locale encoding usage."""

        conf.encoding.try_locale = check_button.get_active()

    @util.asserted_return
    def _on_remove_button_clicked(self, *args):
        """Remove the selected encoding."""

        row = self._get_selected_row()
        conf.encoding.fallbacks.pop(row)
        self._reload_tree_view()
        self._tree_view.grab_focus()
        store = self._tree_view.get_model()
        assert len(store) > 0
        self._tree_view.set_cursor(max(row - 1, 0))

    def _on_up_button_clicked(self, *args):
        """Move the selected encoding up."""

        row = self._get_selected_row()
        encodings = conf.encoding.fallbacks
        encodings.insert(row - 1, encodings.pop(row))
        self._reload_tree_view()
        self._tree_view.grab_focus()
        self._tree_view.set_cursor(row - 1)

    def _reload_tree_view(self):
        """Reload the tree view."""

        store = self._tree_view.get_model()
        store.clear()
        for encoding in conf.encoding.fallbacks:
            store.append([enclib.get_long_name(encoding)])
        self._set_sensitivities()

    def _set_sensitivities(self):
        """Set the tree view button sensitivities."""

        store = self._tree_view.get_model()
        row = self._get_selected_row()
        self._remove_button.set_sensitive(row >= 0)
        self._up_button.set_sensitive(row > 0)
        self._down_button.set_sensitive(0 <= row < len(store) - 1)


class _PreviewPage(Delegate):

    """Preview preferences page."""

    def __init__(self, master):

        Delegate.__init__(self, master)
        get_widget = self._glade_xml.get_widget
        self._app_combo = get_widget("preview_app_combo")
        self._command_entry = get_widget("preview_command_entry")
        self._offset_spin = get_widget("preview_offset_spin")

        self._init_app_combo()
        self._init_values()
        self._init_signal_handlers()

    def _init_app_combo(self):
        """Initialize the application combo box."""

        store = self._app_combo.get_model()
        for name in const.VIDEO_PLAYER.display_names:
            store.append([name])
        store.append([util.COMBO_SEP])
        store.append([_("Custom")])
        self._app_combo.set_row_separator_func(util.separate_combo)

    def _init_signal_handlers(self):
        """Initialize signal handlers."""

        util.connect(self, "_app_combo", "changed")
        util.connect(self, "_command_entry", "changed")
        util.connect(self, "_offset_spin", "value-changed")

    def _init_values(self):
        """Initialize default values for widgets."""

        self._offset_spin.set_value(conf.preview.offset)
        if conf.preview.use_predefined:
            self._app_combo.set_active(conf.preview.video_player)
            self._command_entry.set_text(conf.preview.video_player.command)
            return self._command_entry.set_editable(False)
        store = self._app_combo.get_model()
        self._app_combo.set_active(len(store) - 1)
        self._command_entry.set_text(conf.preview.custom_command)
        self._command_entry.set_editable(True)

    def _on_app_combo_changed(self, combo_box):
        """Save the video player and show it's command."""

        index = combo_box.get_active()
        if index in const.VIDEO_PLAYER.members:
            conf.preview.use_predefined = True
            player = const.VIDEO_PLAYER.members[index]
            conf.preview.video_player = player
            self._command_entry.set_text(player.command)
            return self._command_entry.set_editable(False)
        conf.preview.use_predefined = False
        self._command_entry.set_text(conf.preview.custom_command)
        self._command_entry.set_editable(True)

    @util.asserted_return
    def _on_command_entry_changed(self, entry):
        """Save the custom command."""

        assert not conf.preview.use_predefined
        conf.preview.custom_command = entry.get_text()

    def _on_offset_spin_value_changed(self, spin_button):
        """Save the start position offset."""

        conf.preview.offset = spin_button.get_value()


class PreferencesDialog(GladeDialog):

    """Dialog for editing preferences."""

    def __init__(self):

        GladeDialog.__init__(self, "preferences-dialog")
        self._editor_page = _EditorPage(self)
        self._file_page = _FilePage(self)
        self._preview_page = _PreviewPage(self)

        self.set_transient_for(None)
        self.set_type_hint(gtk.gdk.WINDOW_TYPE_HINT_NORMAL)
        self.set_default_response(gtk.RESPONSE_CLOSE)
