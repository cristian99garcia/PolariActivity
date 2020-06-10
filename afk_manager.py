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

from consts import AFK_COUNT
from gi.repository import GObject


class AFKManager(GObject.GObject):

    __gsignals__ = {
        "user-afk": (GObject.SIGNAL_RUN_FIRST, None, [str]),  # Nickname
        "user-back": (GObject.SIGNAL_RUN_FIRST, None, [str]),  # Nickname
    }

    def __init__(self):
        GObject.GObject.__init__(self)

        self.timeout_ids = { }  # Nickname: id

    def stop_counting(self, nickname):
        if nickname in list(self.timeout_ids.keys()) and self.timeout_ids[nickname] != None:
            GObject.source_remove(self.timeout_ids[nickname])

    def start_counting(self, nickname, restart=True):
        if not nickname in list(self.timeout_ids.keys()) or restart:
            if nickname in list(self.timeout_ids.keys()):
                self.emit("user-back", nickname)

            self.stop_counting(nickname)
            id = GObject.timeout_add(AFK_COUNT, self._afk_cb, nickname)
            self.timeout_ids[nickname] = id

    def remove_nickname(self, nickname):
        if nickname in list(self.timeout_ids.keys()):
            self.stop_counting(nickname)
            self.timeout_ids.pop(nickname)

    def _afk_cb(self, nickname):
        self.emit("user-afk", nickname)
        self.timeout_ids[nickname] = None

        return False
