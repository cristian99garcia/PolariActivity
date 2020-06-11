What is this?
=============

[Polari](https://wiki.gnome.org/Apps/Polari) is an Internet Relay Chat (IRC) client.

Polari Activity embeds Polari for the Sugar desktop.

How to use?
===========

In Sugar, start Terminal and use `git` to clone to your Activities folder;

```
git clone https://github.com/sugarlabs/PolariActivity.git ~/Activities/Polari.git
```

On Debian and Ubuntu systems, install the dependencies;

```
apt install python3-openssl python3-service-identity python3-twisted
```

Start the activity from the Sugar Home View, set a nickname, and press Connect.

How to upgrade?
===============

Use `git` to pull a new version;

```
(cd ~/Activities/Polari.git && git pull)
```

How to integrate?
=================

Polari Activity depends on Python, [Sugar Toolkit for GTK+ 3](https://github.com/sugarlabs/sugar-toolkit-gtk3), Python OpenSSL, Python Service Identity, and GTK+ 3.

Polari Activity is not packaged by Linux distributions.
