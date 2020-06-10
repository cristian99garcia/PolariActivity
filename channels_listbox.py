#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (C) 2014-2016, Cristian García <cristian99garcia@gmail.com>
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 3 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the
# Free Software Foundation, Inc., 59 Temple Place - Suite 330,
# Boston, MA 02111-1307, USA.

from consts import Color, SUGAR, STATUS_CHANNEL

import gi
gi.require_version("Gtk", "3.0")

from gi.repository import Gtk
from gi.repository import Pango
from gi.repository import GObject


class ChannelItem(Gtk.EventBox):

    __gsignals__ = {
        "selected": (GObject.SIGNAL_RUN_FIRST, None, []),
        "removed": (GObject.SIGNAL_RUN_FIRST, None, []),
    }

    def __init__(self, channel, show=None, close_button=False):
        Gtk.EventBox.__init__(self)

        self.selected = False
        self.channel = channel
        self.use_close_button = close_button

        self.set_size_request(1, 30)
        self.modify_bg(Gtk.StateType.NORMAL, Color.WHITE)
        self.connect("button-press-event", self._press)

        self.hbox = Gtk.HBox()
        self.add(self.hbox)

        self.label = Gtk.Label(show if show else channel)
        self.label.modify_font(Pango.FontDescription("15"))
        self.label.set_margin_left(10)
        self.hbox.pack_start(self.label, False, False, 0)

        self.spinner = Gtk.Spinner()
        self.hbox.pack_end(self.spinner, False, False, 0)

        self.button = Gtk.Button.new_from_icon_name(Gtk.STOCK_REMOVE, Gtk.IconSize.BUTTON)
        self.button.connect("clicked", lambda w: self.emit("removed"))

        self.start_spinner()

    def _press(self, widget, event):
        if event.button == 1:
            if not self.selected:
                self.emit("selected")
                self.selected = True

    def set_selected(self, is_selected):
        self.selected = is_selected
        self.update()

    def get_channel(self):
        return self.label.get_label()

    def update(self):
        if self.selected:
            self.modify_bg(Gtk.StateType.NORMAL, Color.BLUE)

        else:
            if SUGAR:
                self.modify_bg(Gtk.StateType.NORMAL, Color.WHITE)

            else:
                self.modify_bg(Gtk.StateType.NORMAL, None)

    def start_spinner(self):
        if self.button.get_parent() == self.hbox:
            self.hbox.remove(self.button)

        if self.spinner.get_parent() == None:
            self.hbox.pack_end(self.spinner, False, False, 0)

        self.spinner.start()
        self.show_all()

    def stop_spinner(self):
        self.spinner.stop()
        if self.spinner.get_parent() == self.hbox:
            self.hbox.remove(self.spinner)

        if self.button.get_parent() == None and self.use_close_button:
            self.hbox.pack_end(self.button, False, False, 0)

        self.show_all()


class ChannelsListBox(Gtk.ScrolledWindow):

    __gsignals__ = {
        "channel-selected": (GObject.SIGNAL_RUN_FIRST, None, [str]),
        "channel-removed": (GObject.SIGNAL_RUN_FIRST, None, [str]),
    }

    def __init__(self):
        Gtk.ScrolledWindow.__init__(self)

        self.items = []
        self.vbox = Gtk.VBox()

        self.set_size_request(250, -1)

        if SUGAR:
            self.modify_bg(Gtk.StateType.NORMAL, Color.WHITE)

        self.add(self.vbox)
        self.add_status_tab()
        self.show_all()

    def add_status_tab(self):
        self.add_channel(STATUS_CHANNEL, show="Status", close_button=False)

    def add_channel(self, channel, show=None, close_button=True):
        item = ChannelItem(channel, show=show, close_button=close_button)
        item.connect("selected", self.select_item)
        item.connect("removed", self.remove_item)
        self.vbox.pack_start(item, False, False, 0)

        self.items.append(item)
        self.select_item(item)
        self.show_all()

    def remove_item(self, item):
        selected = item.selected
        idx = self.items.index(item)
        self.items.remove(item)
        self.vbox.remove(item)

        self.emit("channel-removed", item.channel)
        item.destroy()

        if idx > 0:
            idx -= 1

        if self.items and selected:
            self.select_item(self.items[idx])

    def select_item(self, item):
        for i in self.items:
            i.set_selected(i == item)

        self.emit("channel-selected", item.channel)

    def select_item_from_string(self, channel):
        for item in self.items:
            if item.channel == channel:
                self.select_item(item)
                break

    def change_spinner(self, channel, active):
        for item in self.items:
            if item.channel == channel:
                if active:
                    item.start_spinner()

                else:
                    item.stop_spinner()

                break
