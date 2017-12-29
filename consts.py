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

import os
from gettext import gettext as _

import gi
gi.require_version("Gdk", "3.0")

from gi.repository import Gdk
from gi.repository import GdkPixbuf

SUGAR = None
try:
    import sugar3
    SUGAR = True
except ImportError:
    SUGAR = False


CHAT_FONT = None
if SUGAR:
    CHAT_FONT = "Monospace 14"
else:
    CHAT_FONT = "Monospace 12"

LOCAL_PATH = os.path.dirname(os.path.realpath(__file__))
ICONS_DIR = os.path.join(LOCAL_PATH, "icons")

NEW_CHANNEL_SCREEN_FONT = "20"

NICKNAME_USED = _(' is already in use.')
LOST_CONNECTION = _('Lost connection with the server...')
CONNECTION_ERROR = _('Error connecting to the server... closing the socket.')
ALERT_TITLE = _('You already have a session on this host with this channel and with this nickname.')
ALERT_MSG = _('Automatically selected session you tried to create.')

STATUS_CHANNEL = "status.polari"  # Users nicknames can't has a "."
ALL_CHANNELS = "ALLCHANNELS"
CURRENT_CHANNEL = "CURRENT_CHANNEL"

DEFAULT_NICKNAME = "Nickname"
DEFAULT_SERVER = "irc.freenode.net"
DEFAULT_PORT = "6667"
DEFAULT_CHANNEL = "#sugar"

ADMIN_PIXBUF = GdkPixbuf.Pixbuf.new_from_file(os.path.join(ICONS_DIR, "admin.png"))
MODERATOR_PIXBUF = GdkPixbuf.Pixbuf.new_from_file(os.path.join(ICONS_DIR, "moderator.png"))
NORMAL_PIXBUF = GdkPixbuf.Pixbuf.new_from_file(os.path.join(ICONS_DIR, "normal.png"))

AFK_COUNT = 900000  # 15 minutes on miliseconds


class Screen:
    CHAT = 0
    NEW_CHANNEL = 1


class Color:
    BLUE = Gdk.color_parse('#4A90D9')
    WHITE = Gdk.color_parse('#FFFFFF')
    GREY = Gdk.Color(32896, 32896, 32896)

    NICK_TAG = None
    MENTION_TAG = "#FF2020"
    MESSAGE_TAG = None
    MESSAGE_BG_TAG1 = "#000000"
    MESSAGE_BG_TAG2 = "#666666"
    SYS_MESSAGE_TAG = None
    URL_TAG = "#0000FF"

    if SUGAR:
        NICK_TAG = "#005DBF"
        MESSAGE_TAG = "#FFFFFF"
        SYS_MESSAGE_TAG = "#444444"

    else:
        NICK_TAG = "#4A90D9"
        SYS_MESSAGE_TAG = "#AAAAAA"


class IRCState:
    DISCONNECTED = 0
    CONNECTING = 1
    INITIALIZING = 2
    CONNECTED = 3


class Key:
    TAB = 65289
    ESCAPE = 65307


class TopicLabelMode:
    SHOWING = 0
    EDITING = 1


class UserState:
    ACTIVE = "ACTIVE"
    AFK = "AFK"


class UserType:
    ADMIN = "ADMIN"
    MODERATOR = "MODERATOR"
    NORMAL = "NORMAL"
