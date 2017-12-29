#!/usr/bin/env python
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

from consts import Color, NEW_CHANNEL_SCREEN_FONT, DEFAULT_NICKNAME, \
                   DEFAULT_SERVER, DEFAULT_PORT, DEFAULT_CHANNEL

import gi
gi.require_version("Gtk", "3.0")

from gi.repository import Gtk
from gi.repository import Pango
from gi.repository import GObject


class Field(Gtk.HBox):

    def __init__(self, label, prepopulate):
        Gtk.HBox.__init__(self)

        self.set_size_request(600, 1)

        label = Gtk.Label(label)
        label.modify_fg(Gtk.StateType.NORMAL, Color.GREY)
        label.modify_font(Pango.FontDescription(NEW_CHANNEL_SCREEN_FONT))
        self.pack_start(label, False, False, 50)

        self.entry = Gtk.Entry()
        self.entry.modify_font(Pango.FontDescription(NEW_CHANNEL_SCREEN_FONT))
        self.entry.set_text(str(prepopulate))
        self.pack_end(self.entry, True, True, 0)

        self.show_all()

    def get_value(self):
        return self.entry.get_text()

    def set_value(self, value):
        self.entry.set_text(str(value))


class AddChannelButton(Gtk.Button):

    def __init__(self, label):
        Gtk.Button.__init__(self, label)

        widget = self.get_children()[0]
        widget.modify_font(Pango.FontDescription(NEW_CHANNEL_SCREEN_FONT))


class NewChannelScreen(Gtk.EventBox):

    __gsignals__ = {
        "log-in": (GObject.SIGNAL_RUN_FIRST, None, [str, str, str, int]),
        "new-channel": (GObject.SIGNAL_RUN_FIRST, None, [str]),
        "cancel": (GObject.SIGNAL_RUN_FIRST, None, []),
    }

    def __init__(self, logged=False, nick=None, host=None, channel=None, port=None, init=False):
        Gtk.EventBox.__init__(self)

        self.logged = logged

        box = Gtk.VBox()
        hbox = Gtk.HBox()
        buttonbox = Gtk.HBox()
        buttonbox.set_spacing(50)

        self.modify_bg(Gtk.StateType.NORMAL, Color.WHITE)

        self.form = Gtk.VBox()

        self.nick = Field(_("Nick"), nick or DEFAULT_NICKNAME)
        self.nick.entry.connect("changed", self.__text_changed)
        self.nick.entry.connect("activate", self.send_data)

        if not self.logged:
            self.form.pack_start(self.nick, False, False, 5)

        self.server = Field(_("Server"), host or DEFAULT_SERVER)
        self.server.entry.connect("changed", self.__text_changed)
        self.server.entry.connect("activate", self.send_data)

        if not self.logged:
            self.form.pack_start(self.server, False, False, 5)

        self.port = Field(_("Port"), port or DEFAULT_PORT)
        self.port.entry.connect("changed", self.__text_changed)
        self.port.entry.connect("activate", self.send_data)

        if not self.logged:
            self.form.pack_start(self.port, False, False, 5)

        self.channels = Field(_("Channel"), channel or DEFAULT_CHANNEL)
        self.channels.entry.connect("changed", self.__text_changed)
        self.channels.entry.connect("activate", self.send_data)
        self.form.pack_start(self.channels, False, False, 5)

        self.cancel = AddChannelButton(_("Cancel"))
        self.cancel.set_sensitive(not init)
        self.cancel.connect("clicked", self.__cancel)
        buttonbox.add(self.cancel)

        self.enter = AddChannelButton(_("Connect!"))
        self.enter.connect("clicked", self.send_data)
        buttonbox.add(self.enter)

        self.form.pack_start(buttonbox, True, True, 20)
        hbox.pack_start(self.form, True, False, 0)
        box.pack_start(hbox, True, False, 0)
        self.add(box)
        self.show_all()

    def get_possible(self):
        if not self.logged:
            return bool(self.nick.get_value()) and \
                   bool(self.server.get_value()) and \
                   self.port.get_value().isdigit()

        else:
            return bool(self.channels.get_value())

    def send_data(self, widget):
        if self.get_possible():
            if not self.logged:
                self.logged = True
                self.emit("log-in",
                    self.nick.get_value(),
                    self.server.get_value(),
                    self.channels.get_value(),
                    int(self.port.get_value()))

            else:
                self.emit("new-channel", self.channels.get_value())

    def set_logged(self, logged):
        self.logged = logged
        if not self.logged:
            # Do something
            pass

        else:
            self.form.remove(self.nick)
            self.form.remove(self.server)
            self.form.remove(self.port)

    def __cancel(self, widget):
        self.emit("cancel")

    def __text_changed(self, *args):
        self.enter.set_sensitive(self.get_possible())
