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

from consts import Color, SUGAR, ADMIN_PIXBUF, MODERATOR_PIXBUF, \
    NORMAL_PIXBUF, UserType, UserState

import gi

gi.require_version("Gtk", "3.0")

from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import Pango
from gi.repository import GObject


class NicknamesListBox(Gtk.ScrolledWindow):
    __gsignals__ = {
        "query": (GObject.SIGNAL_RUN_FIRST, None, [str]),  # Nickname
    }

    def __init__(self):
        Gtk.ScrolledWindow.__init__(self)

        self.nicknames = []
        self.admins = []
        self.moderators = []
        self.normals = []
        self.model = Gtk.ListStore(str, str, str)  # Type, Nickname, State
        self.selected_nickname = None

        self.set_size_request(150, 1)

        self.view = Gtk.TreeView()
        self.view.set_model(self.model)
        self.view.set_headers_visible(False)
        self.view.add_events(Gdk.EventMask.BUTTON_PRESS_MASK)
        self.view.connect("button-press-event", self._button_press)
        self.add(self.view)

        renderer = Gtk.CellRendererPixbuf()
        column = Gtk.TreeViewColumn("")
        column.pack_start(renderer, False)
        column.set_cell_data_func(renderer, self.__get_tree_pixbuf)

        renderer = Gtk.CellRendererText()
        column.pack_start(renderer, False)
        column.set_cell_data_func(renderer, self.__get_tree_text)

        self.view.append_column(column)

        self.menu = Gtk.Menu()

        item = Gtk.MenuItem("Query")
        item.connect("activate", self._query)
        self.menu.append(item)

    def __get_tree_pixbuf(self, col, cell, model, iter, user_data):
        usertype = self.model.get_value(iter, 0)

        if usertype == UserType.ADMIN:
            cell.set_property("pixbuf", ADMIN_PIXBUF)

        elif usertype == UserType.MODERATOR:
            cell.set_property("pixbuf", MODERATOR_PIXBUF)

        elif usertype == UserType.NORMAL:
            cell.set_property("pixbuf", NORMAL_PIXBUF)

    def __get_tree_text(self, col, cell, model, iter, user_data):
        cell.set_property("text", self.model.get_value(iter, 1))

    def set_list(self, nicknames):
        self.clear()
        nicknames.sort()

        for nick in nicknames:
            usertype = UserType.NORMAL
            if "@" in nick:
                nick, usertype = nick.split("@")

            self.add_nickname(nick, usertype)

    def clear(self):
        while len(self.nicknames) > 0:
            for item in self.nicknames:
                self.nicknames.remove(item)

        self.model.clear()

    def add_nickname(self, nickname, usertype=None):
        self.nicknames.append(nickname)
        self.nicknames = sorted(self.nicknames, key=str.lower)

        usertype = UserType.NORMAL if usertype == None else usertype
        idx = 0

        if usertype == UserType.ADMIN:
            self.admins.append(nickname)
            self.admins = sorted(self.admins, key=str.lower)
            idx = self.admins.index(nickname)

        elif usertype == UserType.MODERATOR:
            self.moderators.append(nickname)
            self.moderators = sorted(self.moderators, key=str.lower)
            idx = len(self.admins) + self.moderators.index(nickname)

        elif usertype == UserType.NORMAL:
            self.normals.append(nickname)
            self.normals = sorted(self.normals, key=str.lower)
            idx = len(self.admins) + len(self.moderators) + self.normals.index(nickname)

        data = [usertype, nickname, UserState.ACTIVE]
        self.model.insert(idx, data)
        self.show_all()

    def remove_nickname(self, nickname):
        iter = self.model.get_iter_first()
        if self.model.get_value(iter, 1) == nickname:
            self.model.remove(iter)

        else:
            while self.model.iter_next(iter):
                iter = self.model.iter_next(iter)
                if self.model.get_value(iter, 1) == nickname:
                    self.model.remove(iter)
                    break

        self.nicknames.remove(nickname)
        if nickname in self.admins:
            self.admins.remove(nickname)

        elif nickname in self.moderators:
            self.moderators.remove(nickname)

        elif nickname in self.normals:
            self.normals.remove(nickname)

    def set_user_type(self, nickname, type):
        if nickname not in self.nicknames:
            return

        self.remove_nickname(nickname)
        self.add_nickname(nickname, type)

    def set_afk(self, nickname, afk):
        if nickname not in self.nicknames:
            return

        nicks = self.admins + self.moderators + self.normals
        idx = nicks.index(nickname)
        iter = self.model.get_iter(idx)
        state = UserState.ACTIVE if not afk else UserState.AFK
        self.model.set_value(iter, 2, state)

    def _button_press(self, widget, event):
        row = self.view.get_dest_row_at_pos(event.x, event.y)
        if row == None:
            self.selected_nickname = None
            return False

        path = row[0]
        iter = self.model.get_iter(path)
        self.selected_nickname = self.model.get_value(iter, 1)

        if event.button == 3:
            self.menu.show_all()
            self.menu.popup(None, None, None, None, event.button, event.time)

        elif event.button == 1 and event.type == Gdk.EventType.DOUBLE_BUTTON_PRESS:
            self.emit("query", self.selected_nickname)

    def _query(self, item):
        if self.selected_nickname != None:
            self.emit("query", self.selected_nickname)
