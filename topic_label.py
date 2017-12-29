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

from consts import TopicLabelMode, Key

import gi
gi.require_version("Gtk", "3.0")

from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import Pango
from gi.repository import GObject


class TopicLabel(Gtk.EventBox):

    __gsignals__ = {
        "change-topic": (GObject.SIGNAL_RUN_FIRST, None, [str]),  # Topic
    }

    def __init__(self, topic="(no topic set)"):
        Gtk.EventBox.__init__(self)

        self.topic = topic
        self.mode = None

        self.add_events(Gdk.EventMask.BUTTON_PRESS_MASK)
        self.connect("button-press-event", self._button_press_cb)

        self.label = Gtk.Label(self.topic)
        self.label.props.xalign = 0
        self.label.set_ellipsize(Pango.EllipsizeMode.END)

        self.entry = Gtk.Entry()
        self.entry.set_text(self.topic)
        self.entry.set_placeholder_text(_("Set a topic for this channel"))
        self.entry.connect("key-press-event", self._key_press_cb)
        self.entry.connect("activate", self._activate_cb)

        self.set_mode(TopicLabelMode.SHOWING)

    def set_topic(self, topic):
        self.topic = topic
        self.label.set_text(self.topic)
        self.entry.set_text(self.topic)
        self.set_mode(TopicLabelMode.SHOWING)

    def get_topic(self):
        return self.topic

    def set_mode(self, mode):
        self.mode = mode

        if self.mode == TopicLabelMode.SHOWING:
            if self.entry.get_parent() != None:
                self.remove(self.entry)

            if self.label.get_parent() == None:
                self.add(self.label)

        elif self.mode == TopicLabelMode.EDITING:
            if self.label.get_parent() != None:
                self.remove(self.label)

            if self.entry.get_parent() == None:
                self.add(self.entry)

        self.show_all()
        self.entry.grab_focus()

    def _button_press_cb(self, widget, event):
        if event.button == 1 and self.mode == TopicLabelMode.SHOWING:
            self.set_mode(TopicLabelMode.EDITING)

    def _key_press_cb(self, widget, event):
        if event.keyval == Key.ESCAPE:
            self.set_mode(TopicLabelMode.SHOWING)

    def _activate_cb(self, widget):
        self.emit("change-topic", self.entry.get_text())
        self.set_mode(TopicLabelMode.SHOWING)
