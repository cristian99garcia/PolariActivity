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

from new_channel_screen import NewChannelScreen
from channels_listbox import ChannelsListBox
from chat_box import ChatBox
from consts import Screen, STATUS_CHANNEL, ALL_CHANNELS, CURRENT_CHANNEL, UserType
from client import ClientFactory
from afk_manager import AFKManager

import gi
gi.require_version("Gtk", "3.0")

from gi.repository import Gtk
from gi.repository import GObject


class PolariCanvas(Gtk.VBox):

    def __init__(self):
        Gtk.VBox.__init__(self)

        self.screen = None

        self.factory = ClientFactory([])
        self.factory.connect("signed-on", self._signed_on)
        self.factory.connect("joined", self._joined)
        self.factory.connect("system-message", self._system_message)
        self.factory.connect("user-message", self._user_message)
        self.factory.connect("nickname-changed", self._nickname_changed)
        self.factory.connect("user-nickname-changed", self._user_nickname_changed)
        self.factory.connect("user-joined", self._user_joined)
        self.factory.connect("user-left", self._user_left)
        self.factory.connect("user-quit", self._user_quit)
        self.factory.connect("nicknames-list", self._nicknames)
        self.factory.connect("me-command", self._me_command)
        self.factory.connect("status-message", self._status_message)
        self.factory.connect("topic-changed", self._topic_changed)
        self.factory.connect("mode-changed", self._mode_changed)

        self.afk_manager = AFKManager()
        self.afk_manager.connect("user-afk", self._user_afk)
        self.afk_manager.connect("user-back", self._user_back)

        self.channel_screen = NewChannelScreen()
        self.channel_screen.connect("log-in", self._log_in)
        self.channel_screen.connect("new-channel", self._new_channel)
        self.channel_screen.connect("cancel", self._screen_changed, Screen.CHAT)
        self.chat_screen = Gtk.HBox()

        self.channels_listbox = ChannelsListBox()
        self.channels_listbox.connect("channel-selected", self._channel_selected)
        self.channels_listbox.connect("channel-removed", self._channel_removed)
        self.chat_screen.pack_start(self.channels_listbox, False, False, 0)

        self.chat_box = ChatBox()
        self.chat_box.connect("send-message", self._send_message)
        self.chat_box.connect("command", self.run_command)
        self.chat_box.connect("change-nickname", self._change_nickname)
        self.chat_box.connect("query", self._query)
        self.chat_box.connect("change-topic", self._change_topic)
        self.chat_screen.pack_start(self.chat_box, True, True, 0)

        self.set_screen(Screen.NEW_CHANNEL)

    def set_screen(self, screen):
        if screen == self.screen:
            return

        self.screen = screen

        if self.screen == Screen.CHAT:
            if self.channel_screen.get_parent() == self:
                self.remove(self.channel_screen)

            self.pack_start(self.chat_screen, True, True, 0)

        elif self.screen == Screen.NEW_CHANNEL:
            if self.chat_screen.get_parent() == self:
                self.remove(self.chat_screen)

            self.pack_start(self.channel_screen, True, True, 0)

        self.show_all()

    def _send_message(self, widget, channel, message):
        self.send_message(channel, message)

    def send_message(self, channel, message):
        self.factory.client.msg(channel, message)

    def _change_nickname(self, widget, new_nickname):
        self.change_nickname(new_nickname)

    def change_nickname(self, new_nickname):
        self.factory.client.set_nickname(new_nickname)

    def _query(self, widget, nickname):
        self.query(nickname)

    def query(self, nickname):
        self.new_channel(nickname, add_hash=False)

    def _change_topic(self, widget, channel, topic):
        self.change_topic(channel, topic)

    def change_topic(self, channel, topic):
        self.factory.client.topic(channel, topic)

    def run_command(self, widget, channel, command, parameters=""):
        if command == "/join":
            for channel in parameters.split(" "):
                if channel.strip() != "":
                    self.new_channel(channel)

        elif command == "/msg":
            if parameters.split(" ")[0].lower() != "nickserv":
                nickname = parameters.split(" ")[0]
                message = parameters[len(nickname) + 1:]

                if nickname not in self.chat_box.channels:
                    self.new_channel(nickname, add_hash=False)

                self.send_message(nickname, message)
                self.chat_box.add_message_to_view(nickname, self.factory.client.get_nickname(), message, force=True)

            else:
                nickserv = parameters.split(" ")[0]
                action = parameters.split(" ")[1].lower()

                if action == "identify" and len(parameters.split(" ")) == 3:
                    password = parameters.split(" ")[2]
                    self.send_message("NickServ", "identify %s" % password)

                elif action == "identify" and len(parameters.split(" ")) == 4:
                    nickname = parameters.split(" ")[2]
                    password = parameters.split(" ")[3]
                    self.send_message("NickServ", "identify %s %s" % (nickname, password))

        elif command == "/query":
            nickname = parameters.split(" ")[0]

            if nickname not in self.chat_box.channels:
                self.new_channel(nickname, add_hash=False)

        elif command == "/nick":
            self.change_nickname(parameters)

        elif command == "/names":
            self.factory.client.ask_for_names(channel)

        elif command == "/me":
            self.factory.client.me(channel, parameters)
            self._me_command(None, channel, self.factory.client.get_nickname(), parameters)

        elif command == "/topic":
            self.change_topic(channel, parameters)

        elif command == "/away":
            self.factory.client.set_away(True, parameters)

        elif command == "/back":
            self.factory.client.set_away(False)

    def _log_in(self, widget, nick, host, channel, port):
        self.set_screen(Screen.CHAT)
        self.chat_box.set_nickname(nick)
        self.channel_screen.set_logged(True)

        self.factory.protocol.nickname = nick
        if channel.strip() != "":
            self.new_channel(channel)

        self.chat_box.add_system_message(STATUS_CHANNEL, _("Logging in, please wait"))
        self.factory.start_connection(host, port)

    def _new_channel(self, widget, channel):
        if channel.strip() != "":
            self.new_channel(channel)

    def _channel_removed(self, widget, channel):
        self.factory.remove_channel(channel)
        self.chat_box.remove_channel(channel)

        if len(self.factory.channels) == 0:
            self.set_screen(Screen.NEW_CHANNEL)

    def new_channel(self, channel, add_hash=True, show=None):
        self.set_screen(Screen.CHAT)

        if add_hash and not channel.startswith("#"):
            channel = "#" + channel

        if channel in self.chat_box.channels:
            self.chat_box.add_system_message(channel, _("You've already joined %s") % channel)
            return

        self.chat_box.add_channel(channel)
        self.channels_listbox.add_channel(channel, show=show)
        self.factory.add_channel(channel)
        self.chat_box.switch_channel(channel)

    def _channel_selected(self, listbox, channel):
        self.chat_box.switch_channel(channel)

    def _screen_changed(self, widget, screen):
        self.set_screen(screen)

    def _signed_on(self, factory):
        self.chat_box.entry.set_sensitive(True)
        self.chat_box.nicker.set_sensitive(True)
        self.channels_listbox.change_spinner(STATUS_CHANNEL, False)

    def _joined(self, factory, channel):
        if channel not in self.chat_box.channels:
            channel = channel[1:]  # Isn't a channel, is a user (removing #)

        else:
            self.chat_box.add_system_message(channel, _("Joined to: %s") % channel)

        self.channels_listbox.change_spinner(channel, False)

    def _system_message(self, factory, channel, message):
        if channel == CURRENT_CHANNEL:
            channel = self.chat_box.current_channel

        if channel == ALL_CHANNELS:
            for channel in self.chat_box.channels:
                self.chat_box.add_system_message(channel, message)

        else:
            self.chat_box.add_system_message(channel, message)

    def _user_message(self, factory, channel, nickname, message):
        if channel == self.factory.client.get_nickname() and nickname not in self.chat_box.channels:
            self.new_channel(nickname, add_hash=False, show=nickname)

        if channel != self.factory.client.get_nickname():  # Channel message
            self.chat_box.message_recived(channel, nickname, message)

        else:  # Direct message
            self.chat_box.message_recived(nickname, nickname, message)

        self.afk_manager.start_counting(nickname, restart=True)

    def _nickname_changed(self, factory, nickname):
        self.chat_box.set_nickname(nickname)

    def _user_nickname_changed(self, factory, old_nick, new_nick):
        for channel in self.chat_box.channels:
            nicknames = self.chat_box.nicks[channel]
            if old_nick in nicknames:
                self.chat_box.add_system_message(channel, _("{old_nick} has changed nick to {new_nick}").format(old_nick, new_nick))
                self.chat_box.remove_nickname(channel, old_nick)
                self.chat_box.add_nickname(channel, new_nick)

                if old_nick == self.chat_box.nick:
                    self.chat_box.set_nickname(new_nick)

    def _user_joined(self, factory, channel, nickname):
        self.chat_box.add_system_message(channel, _("{nickname} joined.").format(nickname=nickname))
        self.chat_box.add_nickname(channel, nickname)
        self.afk_manager.start_counting(nickname, restart=False)

    def _user_left(self, factory, channel, nickname):
        self.chat_box.add_system_message(channel, _("{nickname} has left.").format(nickname=nickname))
        self.chat_box.remove_nickname(channel, nickname)
        self.afk_manager.remove_nickname(nickname)

    def _user_quit(self, factory, nickname, message):
        for channel in self.chat_box.channels:
            nicknames = self.chat_box.nicks[channel]
            if nickname in nicknames:
                self.chat_box.add_system_message(channel, _("{nickname} has quit. {message}").format(nickname=nickname, message=message))

        self.chat_box.remove_nickname_from_all_channels(nickname)
        self.afk_manager.remove_nickname(nickname)

    def _user_afk(self, manager, nickname):
        self.chat_box.set_user_afk(nickname, True)

    def _user_back(self, manager, nickname):
        self.chat_box.set_user_afk(nickname, False)

    def _nicknames(self, factory, channel, nicknames):
        self.set_nicknames(channel, nicknames.split(" "))

    def set_nicknames(self, channel, nicknames):
        self.chat_box.set_nicknames(channel, nicknames)

        for nickname in nicknames:
            if "@" in nickname:
                nickname, usertype = nickname.split("@")

            self.afk_manager.start_counting(nickname, restart=False)

    def _me_command(self, factory, channel, nickname, message):
        self.chat_box.add_system_message(channel, _(" * {nickname} {message}").format(nickname=nickname, message=message))

    def _status_message(self, factory, message):
        self.chat_box.add_system_message(STATUS_CHANNEL, message)

    def _topic_changed(self, factory, channel, topic):
        self.chat_box.set_topic(channel, topic)

    def _mode_changed(self, factory, channel, usertype, nickname):
        if channel == CURRENT_CHANNEL:
            channel = self.chat_box.current_channel

        self.chat_box.set_user_mode(channel, usertype, nickname)


if __name__ == "__main__":
    def _quit(win):
        from twisted.internet import reactor
        from twisted.internet.error import ReactorNotRunning

        Gtk.main_quit()

        try:
            reactor.stop()
        except ReactorNotRunning:
            pass

    def _clicked(button, polari):
        polari.set_screen(Screen.NEW_CHANNEL)

    win = Gtk.Window()
    win.set_title(_("Polari for Sugar"))
    win.connect("destroy", _quit)

    polari = PolariCanvas()
    win.add(polari)

    button = Gtk.Button.new_with_label(_("Add channel"))
    button.connect("clicked", _clicked, polari)
    polari.pack_end(button, False, False, 0)

    win.show_all()

    Gtk.main()
