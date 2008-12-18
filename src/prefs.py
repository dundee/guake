# -*- coding: utf-8; -*-
#
# Copyright (C) 2008 Lincoln de Sousa <lincoln@minaslivre.org>
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public
# License along with this program; if not, write to the
# Free Software Foundation, Inc., 59 Temple Place - Suite 330,
# Boston, MA 02111-1307, USA.
import re
import os
import warnings

import gtk
import gobject
import gconf

from simplegladeapp import SimpleGladeApp
from guake_globals import GCONF_PATH, KEY
from common import *
import globalhotkeys

# A regular expression to match possible python interpreters when
# filling interpreters combo in preferences
PYTHONS = re.compile('^python\d\.\d$')

# Path to the shells file, it will be used to start to populate
# interpreters combo, see the next variable, its important to fill the
# rest of the combo too.
SHELLS_FILE = '/etc/shells'

# translating our types to vte types
ERASE_BINDINGS = {'ASCII DEL': 'ascii-delete',
                  'Escape sequence': 'delete-sequence',
                  'Control-H': 'ascii-backspace'}

# These tuples are going to be used to build a treeview with the
# hotkeys used in guake preferences.
HKEYS = lambda x:GCONF_PATH + '/keybindings' + x
GHOTKEYS = ((HKEYS('/global/show_hide'), _('Toggle terminal visibility')),)
LHOTKEYS = ((HKEYS('/local/new_tab'), _('New tab'),),
            (HKEYS('/local/close_tab'), _('Close tab')),
            (HKEYS('/local/previous_tab'), _('Go to previous tab')),
            (HKEYS('/local/next_tab'), _('Go to next tab'),),
            (HKEYS('/local/rename_tab'), _('Rename current tab'),),
            (HKEYS('/local/clipboard_copy'), _('Copy text to clipboard'),),
            (HKEYS('/local/clipboard_paste'), _('Paste text from clipboard'),),
            (HKEYS('/local/toggle_fullscreen'), _('Toggle Fullscreen'),),
)

class PrefsCallbacks(object):
    """Holds callbacks that will be used in the PrefsDialg class.
    """

    def __init__(self):
        self.client = gconf.client_get_default()

    # general tab

    def on_default_shell_changed(self, combo):
        """Changes the activity of default_shell in gconf
        """
        citer = combo.get_active_iter()
        if not citer:
            return
        shell = combo.get_model().get_value(citer, 0)
        self.client.set_string(KEY('/general/default_shell'), shell)

    def on_use_login_shell_toggled(self, chk):
        """Changes the activity of use_login_shell in gconf
        """
        self.client.set_bool(KEY('/general/use_login_shell'), chk.get_active())

    def on_use_trayicon_toggled(self, chk):
        """Changes the activity of use_trayicon in gconf
        """
        self.client.set_bool(KEY('/general/use_trayicon'), chk.get_active())

    def on_use_popup_toggled(self, chk):
        """Changes the activity of use_popup in gconf
        """
        self.client.set_bool(KEY('/general/use_popup'), chk.get_active())

    def on_window_ontop_toggled(self, chk):
        """Changes the activity of window_ontop in gconf
        """
        self.client.set_bool(KEY('/general/window_ontop'), chk.get_active())

    def on_window_losefocus_toggled(self, chk):
        """Changes the activity of window_losefocus in gconf
        """
        self.client.set_bool(KEY('/general/window_losefocus'), chk.get_active())

    def on_window_tabbar_toggled(self, chk):
        """Changes the activity of window_tabbar in gconf
        """
        self.client.set_bool(KEY('/general/window_tabbar'), chk.get_active())

    def on_window_size_value_changed(self, hscale):
        """Changes the value of window_size in gconf
        """
        val = hscale.get_value()
        self.client.set_int(KEY('/general/window_size'), int(val))

    # scrolling tab

    def on_use_scrollbar_toggled(self, chk):
        """Changes the activity of use_scrollbar in gconf
        """
        self.client.set_bool(KEY('/general/use_scrollbar'), chk.get_active())

    def on_history_size_value_changed(self, spin):
        """Changes the value of history_size in gconf
        """
        val = int(spin.get_value())
        self.client.set_int(KEY('/general/history_size'), val)

    def on_scroll_output_toggled(self, chk):
        """Changes the activity of scroll_output in gconf
        """
        self.client.set_bool(KEY('/general/scroll_output'), chk.get_active())

    def on_scroll_keystroke_toggled(self, chk):
        """Changes the activity of scroll_keystroke in gconf
        """
        self.client.set_bool(KEY('/general/scroll_keystroke'), chk.get_active())

    # appearance tab

    def on_use_default_font_toggled(self, chk):
        """Changes the activity of use_default_font in gconf
        """
        self.client.set_bool(KEY('/general/use_default_font'), chk.get_active())

    def on_font_style_font_set(self, fbtn):
        """Changes the value of font_style in gconf
        """
        self.client.set_string(KEY('/style/font/style'), fbtn.get_font_name())

    def on_font_color_color_set(self, btn):
        """Changes the value of font_color in gconf
        """
        color = hexify_color(btn.get_color())
        self.client.set_string(KEY('/style/font/color'), color)

    def on_background_color_color_set(self, btn):
        """Changes the value of background_color in gconf
        """
        color = hexify_color(btn.get_color())
        self.client.set_string(KEY('/style/background/color'), color)

    def on_background_image_changed(self, btn):
        """Changes the value of background_image in gconf
        """
        filename = btn.get_filename()
        if os.path.isfile(filename or ''):
            self.client.set_string(KEY('/style/background/image'), filename)

    def on_opacity_value_changed(self, hscale):
        """Changes the value of background_opacity in gconf
        """
        value = hscale.get_value()
        self.client.set_int(KEY('/style/background/opacity'), int(value))

    # compatibility tab

    def on_backspace_binding_changed(self, combo):
        """Changes the value of compat_backspace in gconf
        """
        val = combo.get_active_text()
        self.client.set_string(KEY('/general/compat_backspace'),
                               ERASE_BINDINGS[val])

    def on_delete_binding_changed(self, combo):
        """Changes the value of compat_delete in gconf
        """
        val = combo.get_active_text()
        self.client.set_string(KEY('/general/compat_delete'),
                               ERASE_BINDINGS[val])


class PrefsDialog(SimpleGladeApp):
    """The Guake Preferences dialog.
    """
    def __init__(self):
        """Setup the preferences dialog interface, loading images,
        adding filters to file choosers and connecting some signals.
        """
        super(PrefsDialog, self).__init__(gladefile('prefs.glade'),
                                          root='config-window')
        self.add_callbacks(PrefsCallbacks())

        self.client = gconf.client_get_default()

        # setting evtbox title bg
        eventbox = self.get_widget('eventbox-title')
        eventbox.modify_bg(gtk.STATE_NORMAL,
                           eventbox.get_colormap().alloc_color("#ffffff"))

        # images
        ipath = pixmapfile('guake-notification.png')
        self.get_widget('image_logo').set_from_file(ipath)

        # the first position in tree will store the keybinding path in gconf,
        # and the user doesn't worry with this, lest hide that =D
        model = gtk.TreeStore(str, str, object, bool)
        treeview = self.get_widget('treeview-keys')
        treeview.set_model(model)
        treeview.set_rules_hint(True)
        treeview.connect('button-press-event', self.start_editing_cb)

        renderer = gtk.CellRendererText()
        column = gtk.TreeViewColumn('keypath', renderer, text=0)
        column.set_visible(False)
        treeview.append_column(column)

        renderer = gtk.CellRendererText()
        column = gtk.TreeViewColumn(_('Action'), renderer, text=1)
        column.set_property('expand', True)
        treeview.append_column(column)

        renderer = gtk.CellRendererAccel()
        renderer.set_property('editable', True)

        renderer.connect('accel-edited', self.on_key_edited, model)
        renderer.connect('accel-cleared', self.on_key_cleared, model)

        column = gtk.TreeViewColumn(_('Shortcut'), renderer)
        column.set_cell_data_func(renderer, self.cell_data_func)
        column.set_property('expand', False)
        treeview.append_column(column)

        self.populate_shell_combo()
        self.populate_keys_tree()
        self.load_configs()
        self.get_widget('config-window').hide()

        # Preview when selecting a bgimage
        self.selection_preview = gtk.Image()
        self.file_filter = gtk.FileFilter()
        self.file_filter.add_pattern("*.jpg")
        self.file_filter.add_pattern("*.png")
        self.file_filter.add_pattern("*.svg")
        self.file_filter.add_pattern("*.jpeg")
        self.bgfilechooser = self.get_widget('background_image')
        self.bgfilechooser.set_preview_widget(self.selection_preview)
        self.bgfilechooser.set_filter(self.file_filter)
        self.bgfilechooser.connect('update-preview', self.update_preview_cb,
                                   self.selection_preview)

    def show(self):
        """Calls the main window show_all method and presents the
        window in the desktop.
        """
        self.get_widget('config-window').show_all()
        self.get_widget('config-window').present()

    def hide(self):
        """Calls the main window hide function.
        """
        self.get_widget('config-window').hide()

    def update_preview_cb(self, file_chooser, preview):
        """Used by filechooser to preview image files
        """
        filename = file_chooser.get_preview_filename()
        if filename and os.path.isfile(filename or ''):
            try:
                mkpb = gtk.gdk.pixbuf_new_from_file_at_size
                pixbuf = mkpb(filename, 256, 256)
                preview.set_from_pixbuf(pixbuf)
                file_chooser.set_preview_widget_active(True)
            except gobject.GError:
                # this exception is raised when user chooses a
                # non-image file or a directory
                warnings.warn('File %s is not an image' % filename)
        else:
            file_chooser.set_preview_widget_active(False)

    def toggle_style_sensitivity(self, chk):
        """If the user chooses to use the gnome default font
        configuration it means that he will not be able to use the
        font selector.
        """
        self.get_widget('font_style').set_sensitive(not chk.get_active())

    def clear_background_image(self, btn):
        """Unset the gconf variable that holds the name of the
        background image of all terminals.
        """
        self.client.unset(KEY('/style/background/image'))
        self.bgfilechooser.unselect_all()

    def on_reset_compat_defaults_clicked(self, bnt):
        """Reset default values to compat_{backspace,delete} gconf
        keys. The default values are retrivied from the guake.schemas
        file.
        """
        self.client.unset(KEY('/general/compat_backspace'))
        self.client.unset(KEY('/general/compat_delete'))
        self.reload_erase_combos()

    def reload_erase_combos(self, btn=None):
        """Read from gconf the value of compat_{backspace,delete} vars
        and select the right option in combos.
        """
        # backspace erase binding
        combo = self.get_widget('backspace-binding-combobox')
        binding = self.client.get_string(KEY('/general/compat_backspace'))
        for i in combo.get_model():
            if ERASE_BINDINGS.get(i[0]) == binding:
                combo.set_active_iter(i.iter)

        # delete erase binding
        combo = self.get_widget('delete-binding-combobox')
        binding = self.client.get_string(KEY('/general/compat_delete'))
        for i in combo.get_model():
            if ERASE_BINDINGS.get(i[0]) == binding:
                combo.set_active_iter(i.iter)

    def load_configs(self):
        """Load configurations for all widgets in General, Scrolling
        and Appearance tabs from gconf.
        """
        # default_shell
        combo = self.get_widget('default_shell')
        for i in combo.get_model():
            if i[0] == self.client.get_string(KEY('/general/default_shell')):
                combo.set_active_iter(i.iter)

        # login shell
        value = self.client.get_bool(KEY('/general/use_login_shell'))
        self.get_widget('use_login_shell').set_active(value)

        # tray icon
        value = self.client.get_bool(KEY('/general/use_trayicon'))
        self.get_widget('use_trayicon').set_active(value)

        # popup
        value = self.client.get_bool(KEY('/general/use_popup'))
        self.get_widget('use_popup').set_active(value)

        # ontop
        value = self.client.get_bool(KEY('/general/window_ontop'))
        self.get_widget('window_ontop').set_active(value)

        # losefocus
        value = self.client.get_bool(KEY('/general/window_losefocus'))
        self.get_widget('window_losefocus').set_active(value)

        # tabbar
        value = self.client.get_bool(KEY('/general/window_tabbar'))
        self.get_widget('window_tabbar').set_active(value)

        # size
        value = float(self.client.get_int(KEY('/general/window_size')))
        self.get_widget('window_size').set_value(value)

        # scrollbar
        value = self.client.get_bool(KEY('/general/use_scrollbar'))
        self.get_widget('use_scrollbar').set_active(value)

        # history size
        value = self.client.get_int(KEY('/general/history_size'))
        self.get_widget('history_size').set_value(value)

        # scroll output
        value = self.client.get_bool(KEY('/general/scroll_output'))
        self.get_widget('scroll_output').set_active(value)

        # scroll keystroke
        value = self.client.get_bool(KEY('/general/scroll_keystroke'))
        self.get_widget('scroll_keystroke').set_active(value)

        # default font
        value = self.client.get_bool(KEY('/general/use_default_font'))
        self.get_widget('use_default_font').set_active(value)
        self.get_widget('font_style').set_sensitive(not value)

        # font
        value = self.client.get_string(KEY('/style/font/style'))
        self.get_widget('font_style').set_font_name(value)

        # font color
        val = self.client.get_string(KEY('/style/font/color'))
        try:
            color = gtk.gdk.color_parse(val)
            self.get_widget('font_color').set_color(color)
        except (ValueError, TypeError):
            warnings.warn('Unable to parse color %s' % val, Warning)

        # background color
        value = self.client.get_string(KEY('/style/background/color'))
        try:
            color = gtk.gdk.color_parse(value)
            self.get_widget('background_color').set_color(color)
        except (ValueError, TypeError):
            warnings.warn('Unable to parse color %s' % val, Warning)

        # background image
        value = self.client.get_string(KEY('/style/background/image'))
        if os.path.isfile(value or ''):
            self.get_widget('background_image').set_filename(value)

        value = self.client.get_int(KEY('/style/background/opacity'))
        self.get_widget('background_opacity').set_value(value)

        # it's a separated method, to be reused.
        self.reload_erase_combos()

    # -- populate functions --

    def populate_shell_combo(self):
        """Read the /etc/shells and looks for installed pythons to
        fill the default_shell combobox.
        """
        cb = self.get_widget('default_shell')
        if os.path.exists(SHELLS_FILE):
            lines = open(SHELLS_FILE).readlines()
            for i in lines:
                possible = i.strip()
                if possible and not possible.startswith('#') and \
                   os.path.exists(possible):
                    cb.append_text(possible)

        for i in os.environ.get('PATH', '').split(os.pathsep):
            if os.path.isdir(i):
                for j in os.listdir(i):
                    if PYTHONS.match(j):
                        cb.append_text(os.path.join(i, j))

    def populate_keys_tree(self):
        model = self.get_widget('treeview-keys').get_model()

        giter = model.append(None)
        model.set(giter, 0, '', 1, _('Global hotkeys'))

        for i in GHOTKEYS:
            child = model.append(giter)
            accel = self.client.get_string(i[0])
            if accel:
                params = gtk.accelerator_parse(accel)
                hotkey = KeyEntry(*params)
            else:
                hotkey = KeyEntry(0, 0)

            model.set(child,
                      0, i[0],
                      1, i[1],
                      2, hotkey,
                      3, True)

        giter = model.append(None)
        model.set(giter, 0, '', 1, _('Local hotkeys'))

        for i in LHOTKEYS:
            child = model.append(giter)
            accel = self.client.get_string(i[0])
            if accel:
                params = gtk.accelerator_parse(accel)
                hotkey = KeyEntry(*params)
            else:
                hotkey = KeyEntry(0, 0)

            model.set(child,
                      0, i[0],
                      1, i[1],
                      2, hotkey,
                      3, True)

        self.get_widget('treeview-keys').expand_all()

    # -----------------------------------------------------------------------

    def on_key_edited(self, renderer, path, keycode, mask, keyval, model):
        giter = model.get_iter(path)
        gconf_path = model.get_value(giter, 0)

        oldkey = model.get_value(giter, 2)
        hotkey = KeyEntry(keycode, mask)
        key = gtk.accelerator_name(keycode, mask)
        keylabel = gtk.accelerator_get_label(keycode, mask)

        # we needn't to change anything, the user is trying to set the
        # same key that is already set.
        if oldkey == hotkey:
            return False

        # looking for already used keybindings
        def each_key(model, path, subiter):
            keyentry = model.get_value(subiter, 2)
            if keyentry and keyentry == hotkey:
                msg = _("The shortcut \"%s\" is already in use.") % keylabel
                raise ShowableError(_('Error setting keybinding.'), msg, -1)
        model.foreach(each_key)

        # avoiding problems with common keys
        if ((mask == 0 and keycode != 0) and (
            (keycode >= ord('a') and keycode <= ord('z')) or
            (keycode >= ord('A') and keycode <= ord('Z')) or
            (keycode >= ord('0') and keycode <= ord('9')))):
            parent = self.get_widget('config-window')
            dialog = gtk.MessageDialog(parent,
                                       gtk.DIALOG_MODAL |
                                       gtk.DIALOG_DESTROY_WITH_PARENT,
                                       gtk.MESSAGE_WARNING,
                                       gtk.BUTTONS_OK,
                                       _("The shortcut \"%s\" cannot be used "
                                         "because it will become impossible to "
                                         "type using this key.\n\n"
                                         "Please try with a key such as "
                                         "Control, Alt or Shift at the same "
                                         "time.\n") % key)
            dialog.run()
            dialog.destroy()
            return False

        giter = model.get_iter(path)
        model.set_value(giter, 2, hotkey)

        # old key, used only to disconnect current shortcuts
        accel = self.client.get_string(gconf_path)
        if gconf_path in [x[0] for x in GHOTKEYS]:
            # ungrabing global keys
            globalhotkeys.unbind(accel)
            if not globalhotkeys.bind(key, self.guake.show_hide):
                globalhotkeys.bind(accel, self.guake.show_hide)
                model.set(giter, 2, accel)
                raise ShowableError(_('key binding error'),
                        _('Unable to bind %s key') % key, -1)
        else:
            # ungrabing local keys
            if accel != 'disabled':
                keynum, mask = gtk.accelerator_parse(accel)
                self.guake.accel_group.disconnect_key(keynum, mask)

        # setting the new value on gconf
        self.client.set_string(gconf_path, key)
        self.guake.load_accelerators()

    def on_key_cleared(self, renderer, path, model):
        giter = model.get_iter(path)
        gconf_path = model.get_value(giter, 0)
        accel = self.client.get_string(gconf_path)
        model.set_value(giter, 2, KeyEntry(0, 0))

        # cleared accel must be unbinded
        accel = self.client.get_string(gconf_path)
        if gconf_path in [x[0] for x in GHOTKEYS]:
            globalhotkeys.unbind(accel)

        keynum, mask = gtk.accelerator_parse(accel)
        if keynum:
            self.guake.accel_group.disconnect_key(keynum, mask)

        self.client.set_string(gconf_path, 'disabled')
        self.guake.load_accelerators()

    def cell_data_func(self, column, renderer, model, giter):
        obj = model.get_value(giter, 2)
        if obj:
            renderer.set_property('visible', True)
            renderer.set_property('accel-key', obj.keycode)
            renderer.set_property('accel-mods', obj.mask)
        else:
            renderer.set_property('visible', False)
            renderer.set_property('accel-key', 0)
            renderer.set_property('accel-mods', 0)

    def start_editing_cb(self, treeview, event):
        """Make the treeview grab the focus and start editing the cell
        that the user has clicked to avoid confusion with two or three
        clicks before editing a keybinding.

        Thanks to gnome-keybinding-properties.c =)
        """
        if event.window != treeview.get_bin_window():
            return False

        x, y = int(event.x), int(event.y)
        ret = treeview.get_path_at_pos(x, y)
        if not ret:
            return False

        path, column, cellx, celly = ret
        if path and len(path) > 1:
            def real_cb():
                treeview.grab_focus()
                treeview.set_cursor(path, column, True)
            treeview.stop_emission('button-press-event')
            gobject.idle_add(real_cb)

        return True

class KeyEntry(object):
    def __init__(self, keycode, mask):
        self.keycode = keycode
        self.mask = mask

    def __repr__(self):
        return u'KeyEntry(%d, %d)' % (
            self.keycode, self.mask)

    def __eq__(self, rval):
        return self.keycode == rval.keycode and \
            self.mask == rval.mask

if __name__ == '__main__':
    PrefsDialog().show()
    gtk.main()